"""
Main Zefoy Bot automation logic
"""

import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import undetected_chromedriver as uc
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .captcha_solver import CaptchaSolver
from .config import Config
from .logger import BotUI, console, get_logger
from .service_manager import ServiceManager
from .target_tracker import TargetTracker
from .utils import (
    countdown_timer,
    format_time_duration,
    format_time_user_friendly,
    human_typing,
    parse_time_remaining,
    random_delay,
    retry_on_exception,
    safe_click,
    take_screenshot,
    validate_tiktok_url,
    wait_for_element,
    wait_for_elements,
)


class ZefoyBot:
    """Main Zefoy Bot class"""

    def __init__(self, config: Optional[Config] = None, headless: bool = False):
        """
        Initialize Zefoy Bot

        Args:
            config: Configuration object
            headless: Run browser in headless mode
        """
        self.config = config or Config()

        # Auto-detect VPS/server environment (no display)
        # Priority: Xvfb (with DISPLAY set) > Pure headless
        self.headless = headless or self.config.browser_headless
        self._using_xvfb = False

        if not self.headless and not self._has_display():
            self.headless = True
            # Will log after logger is initialized
            self._auto_headless = True
        else:
            self._auto_headless = False
            # Check if using Xvfb
            import os

            display = os.environ.get("DISPLAY", "")
            if display and ("99" in display or "98" in display):
                self._using_xvfb = True

        # Setup logger
        log_file = self.config.logs_path / f"betlo_{datetime.now().strftime('%Y%m%d')}.log"
        self.logger = get_logger(
            name="ZefoyBot", log_file=str(log_file), level=self.config.get("logging.level", "INFO")
        )

        # Log display mode detection
        if self._using_xvfb:
            self.logger.info("🖥️  Xvfb virtual display detected - Running in visible mode")
            self.logger.info("✓ Best compatibility mode for Zefoy (95%+ success rate)")
        elif self._auto_headless:
            self.logger.warning("⚠ No display detected (VPS/Server environment)")
            self.logger.warning("⚠ Auto-enabling headless mode with stealth")
            self.logger.info("💡 For better Zefoy compatibility, use Xvfb: ./run_xvfb.sh")
        elif self.headless:
            self.logger.info("🎭 Headless mode enabled with stealth scripts")
            self.logger.info("💡 For best Zefoy compatibility, use Xvfb: ./run_xvfb.sh")

        # Initialize driver and captcha solver
        self.driver = None
        self.captcha_solver = None
        self.target_tracker = None
        self.service_manager = None
        self.session_active = False
        self._stealth_script_fallback = None  # For CDP fallback injection

        # Statistics
        self.stats = {
            "started_at": datetime.now(),
            "captchas_solved": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "services_used": {},
        }

    def start(self):
        """Start the bot"""
        from rich import box
        from rich.align import Align
        from rich.live import Live
        from rich.panel import Panel
        from rich.text import Text

        status_messages = []

        def create_status_panel():
            """Create a panel with current status messages"""
            content = Text()
            for msg in status_messages[-8:]:  # Show last 8 messages
                # Parse markup and add to Text object
                content.append(Text.from_markup(msg))
                content.append("\n")

            return Panel(
                Align.center(content)
                if content.plain
                else Align.center(Text("Initializing...", style="cyan")),
                title="[bold cyan]🚀 Starting...[/bold cyan]",
                title_align="center",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )

        success = False
        try:
            with Live(create_status_panel(), console=console, refresh_per_second=4) as live:
                # Banner is shown once in main.py, no need to show again
                status_messages.append("[cyan]🤖 Initializing...[/cyan]")
                live.update(create_status_panel())
                self.logger.info("Initializing...")

                # Setup browser
                status_messages.append("[dim]🌐 Setting up browser...[/dim]")
                live.update(create_status_panel())
                self.logger.info("Setting up browser...")
                self._setup_driver()

                status_messages.append("[green]✓ Browser initialized[/green]")
                live.update(create_status_panel())

                # Navigate to Zefoy
                status_messages.append(f"[cyan]🌐 Navigating to Zefoy...[/cyan]")
                live.update(create_status_panel())
                self.logger.info(f"Navigating to {self.config.zefoy_url}...")
                self.driver.get(self.config.zefoy_url)

                # Wait a moment for initial page structure
                self.logger.info("Waiting for Zefoy page to load...")
                random_delay(2, 3)

                # Inject stealth scripts if CDP failed earlier (must be done early)
                if self._stealth_script_fallback:
                    try:
                        self.logger.debug("Injecting stealth scripts (fallback method)...")
                        self.driver.execute_script(self._stealth_script_fallback)
                        self.logger.info("✓ Stealth scripts injected on page load")
                    except Exception as e:
                        self.logger.warning(f"⚠️  Failed to inject stealth scripts: {e}")

                # Wait for page ready state first
                self.logger.debug("Checking page ready state...")
                self._wait_for_page_ready()

                # Extended wait for Zefoy to fully render (especially in headless)
                if self.headless or self._using_xvfb:
                    self.logger.info("⏳ Headless/Xvfb mode: Extended wait for full rendering...")
                    random_delay(10, 12)  # Even longer for Zefoy in headless
                else:
                    self.logger.info("⏳ Waiting for dynamic content...")
                    random_delay(5, 7)

                # Additional wait specifically for Zefoy's dynamic content
                self.logger.debug("Waiting for Zefoy dynamic elements...")
                random_delay(3, 5)

                # Force a scroll to trigger lazy-loaded elements (important for headless)
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    random_delay(1, 2)
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    self.logger.debug("✓ Page scrolled to trigger lazy-loaded elements")
                except Exception:
                    pass

                status_messages.append("[green]✓ Page loaded[/green]")
                live.update(create_status_panel())

                # Debug: Save page source for diagnosis
                if self.config.get("logging.level") == "DEBUG":
                    self.logger.debug("Saving page source for debugging...")
                    self._debug_save_page_source("initial_load")

                # Handle any alerts that may appear
                self._dismiss_alerts()

                # Solve captcha with extended detection
                status_messages.append("[cyan]🔐 Checking for captcha...[/cyan]")
                live.update(create_status_panel())

                self.captcha_solver = CaptchaSolver(self.driver, self.config, self.logger)

                # Try multiple times to detect captcha (Zefoy loads slowly, especially in headless)
                max_attempts = 5 if (self.headless or self._using_xvfb) else 3
                captcha_found = False

                self.logger.info(
                    f"🔍 Detecting captcha ({max_attempts} attempts, 10s timeout each)..."
                )
                for attempt in range(max_attempts):
                    self.logger.debug(f"Captcha detection attempt {attempt + 1}/{max_attempts}...")

                    # Check with generous timeout
                    if self.captcha_solver.is_captcha_present(timeout=10):
                        captcha_found = True
                        self.logger.info(f"✓ Captcha detected on attempt {attempt + 1}")
                        break

                    # If not found, wait and try again
                    if attempt < max_attempts - 1:
                        wait_time = 5 if (self.headless or self._using_xvfb) else 3
                        self.logger.debug(
                            f"Captcha not found yet, waiting {wait_time}s before retry..."
                        )
                        random_delay(wait_time, wait_time + 2)

                        # Refresh page check (ensure page is still responsive)
                        try:
                            current_url = self.driver.current_url
                            self.logger.debug(f"Current URL: {current_url}")
                        except Exception as e:
                            self.logger.warning(f"Page check failed: {e}")

                if captcha_found:
                    status_messages.append("[yellow]⚠ Captcha detected! Solving...[/yellow]")
                    live.update(create_status_panel())

                    # Pause Live for captcha solving (has its own Live panel)
                    live.stop()
                    captcha_solved = self.captcha_solver.solve_captcha()
                    # Captcha solver has cleared screen, give a moment before resuming
                    random_delay(0.5, 1)
                    live.start()

                    if not captcha_solved:
                        status_messages.append("[red]✗ Failed to solve captcha[/red]")
                        live.update(create_status_panel())
                        random_delay(2, 3)
                        return False

                    status_messages.append("[green]✓ Captcha solved successfully![/green]")
                    live.update(create_status_panel())
                    self.stats["captchas_solved"] += 1
                else:
                    # Captcha not found after multiple attempts
                    self.logger.warning(f"⚠️  Captcha not detected after {max_attempts} attempts")
                    self.logger.warning("")
                    self.logger.warning("💡 Possible reasons:")
                    self.logger.warning(
                        "   1. Captcha already solved (cookies from previous session)"
                    )
                    self.logger.warning("   2. Page didn't load correctly (Cloudflare/rate limit)")
                    self.logger.warning("   3. Zefoy changed their page structure")
                    self.logger.warning("   4. Headless detection blocked the page")
                    self.logger.warning("")

                    # Save page source for diagnosis
                    self.logger.info("📸 Saving diagnostic information...")
                    self._debug_save_page_source("no_captcha_found")

                    # Provide mode-specific recommendations
                    if self.headless and not self._using_xvfb:
                        self.logger.warning("🔧 Recommendations for headless mode:")
                        self.logger.warning("   1. BEST: Use Xvfb instead: ./run_xvfb.sh")
                        self.logger.warning("   2. Check debug/ folder for screenshot")
                        self.logger.warning("   3. Try visible mode if on desktop")
                        self.logger.warning("")
                        self.logger.warning("⚠️  Pure headless has 60-80% success rate with Zefoy")
                        self.logger.warning("   Xvfb provides 95%+ success rate!")
                    else:
                        self.logger.info("🔧 Troubleshooting:")
                        self.logger.info("   1. Check debug/ folder: ls -lh debug/")
                        self.logger.info(
                            "   2. View screenshot: debug/screenshot_no_captcha_found_*.png"
                        )
                        self.logger.info(
                            "   3. Read diagnostic: debug/diagnostic_no_captcha_found_*.txt"
                        )
                        self.logger.info("   4. Run test: ./test_zefoy.sh")

                    status_messages.append(
                        "[yellow]⚠ No captcha detected - Check debug folder[/yellow]"
                    )
                    live.update(create_status_panel())

                # Initialize target tracker
                status_messages.append("[dim]📊 Initializing target tracker...[/dim]")
                live.update(create_status_panel())

                self.target_tracker = TargetTracker(self.config)
                self.target_tracker.load_progress()  # Load previous progress if exists

                status_messages.append("[green]✓ Target tracker loaded[/green]")
                live.update(create_status_panel())

                # Initialize service manager
                status_messages.append("[dim]⚙ Initializing service manager...[/dim]")
                live.update(create_status_panel())

                self.service_manager = ServiceManager(self.config)

                status_messages.append("[green]✓ Service manager ready[/green]")
                live.update(create_status_panel())

                # Show active service info
                active_service = self.service_manager.get_active_service()
                if active_service:
                    status_messages.append(f"[yellow]🎯 Active service: {active_service}[/yellow]")
                    live.update(create_status_panel())
                    self.logger.info(f"Active Service Mode: {active_service} only")

                self.session_active = True

                status_messages.append("\n[bold green]✓ Bot initialized successfully![/bold green]")
                live.update(create_status_panel())
                self.logger.success("Bot initialized successfully!")

                success = True
                random_delay(1.5, 2)  # Show success message briefly

            # Live panel closed, clear screen for clean transition
            # The "Bot Ready" panel will be shown by main.py after this

            # Show active service info panel if exists (after Live closes)
            if active_service:
                console.clear()
                BotUI.print_info_panel(
                    f"Single Service Mode Active\nOnly {active_service} is available",
                    title=f"🎯 {active_service} Mode",
                )

            return True

        except KeyboardInterrupt:
            status_messages.append("[red]⚠ Cancelled by user[/red]")
            random_delay(1, 1.5)
            self.logger.warning("Bot startup cancelled by user")
            raise
        except Exception as e:
            status_messages.append(f"[red]✗ Error: {str(e)[:40]}...[/red]")
            random_delay(2, 3)
            self.logger.error(f"Error starting bot: {str(e)}")
            self._take_error_screenshot("startup_error")
            return False

    def _has_display(self):
        """
        Check if display is available (not VPS/headless server)

        Note: This is called during __init__ BEFORE logger is initialized,
        so it must NOT use self.logger
        """
        import os
        import platform

        # Check $DISPLAY environment variable (Linux/Unix)
        if platform.system() in ["Linux", "Darwin"]:
            display = os.environ.get("DISPLAY", "").strip()
            if display:
                # Display found (don't log here - logger not initialized yet)
                return True

            # Check if Xvfb or other virtual display is running
            try:
                import subprocess

                result = subprocess.run(["pgrep", "-x", "Xvfb"], capture_output=True, timeout=2)
                if result.returncode == 0:
                    return True  # Xvfb is running
            except Exception:
                pass

            return False  # No display found

        # Windows always has display
        return True

    def _kill_zombie_chrome_processes(self):
        """Kill any zombie Chrome/ChromeDriver processes"""
        try:
            import platform
            import subprocess

            if platform.system() == "Linux":
                # Kill Chrome and chromedriver processes
                subprocess.run(["pkill", "-f", "chrome"], stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "chromedriver"], stderr=subprocess.DEVNULL)
                time.sleep(1)
                self.logger.debug("Cleaned up zombie Chrome processes")
        except Exception as e:
            self.logger.debug(f"Could not kill zombie processes: {e}")

    def _check_shm_size(self):
        """Check /dev/shm size and warn if too small for Chrome"""
        try:
            import platform
            import subprocess

            if platform.system() != "Linux":
                return

            result = subprocess.run(
                ["df", "-h", "/dev/shm"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        size = parts[1]
                        self.logger.debug(f"/dev/shm size: {size}")

                        # Warn if less than 64MB
                        if "K" in size or (size.endswith("M") and int(size[:-1]) < 64):
                            self.logger.warning(
                                f"⚠ /dev/shm size is small ({size}). Chrome may crash."
                            )
                            self.logger.warning(
                                "  Consider increasing it or use --disable-dev-shm-usage"
                            )
        except Exception as e:
            self.logger.debug(f"Could not check /dev/shm size: {e}")

    def _find_chrome_binary(self):
        """Find Chrome binary path (especially for VPS/servers)"""
        import os
        import shutil

        # Common Chrome binary locations (Linux VPS)
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/usr/local/bin/google-chrome",
            "/opt/google/chrome/google-chrome",
            "/opt/google/chrome/chrome",
        ]

        # Try to find using 'which' command
        try:
            for cmd in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
                path = shutil.which(cmd)
                if path and os.path.isfile(path):
                    return path
        except Exception:
            pass

        # Check common paths
        for path in chrome_paths:
            if os.path.isfile(path):
                return path

        # If not found, return None (will use system default)
        return None

    def _setup_driver(self):
        """Setup undetected Chrome driver with retry mechanism"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                self.logger.debug(f"Setting up Chrome driver (attempt {attempt}/{max_retries})...")

                # Clean up zombie processes on first attempt
                if attempt == 1:
                    self._kill_zombie_chrome_processes()
                    self._check_shm_size()

                options = uc.ChromeOptions()

                # Find Chrome binary (especially important for VPS/servers)
                chrome_binary = self._find_chrome_binary()
                if chrome_binary:
                    options.binary_location = chrome_binary
                    self.logger.debug(f"Using Chrome binary: {chrome_binary}")
                else:
                    self.logger.warning("Chrome binary not explicitly set, using system default")

                # Basic options
                if self.headless:
                    options.add_argument("--headless=new")
                    # Stealth mode for headless - mimic real browser
                    self.logger.debug("Enabling headless stealth mode")

                options.add_argument(f"--window-size={self.config.browser_window_size}")
                options.add_argument("--start-maximized")  # Important for proper rendering
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-gpu")  # Prevent GPU-related crashes
                options.add_argument("--disable-software-rasterizer")

                # VPS/Server stability improvements
                options.add_argument("--disable-setuid-sandbox")
                options.add_argument("--disable-accelerated-2d-canvas")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-infobars")
                options.add_argument("--disable-login-animations")
                options.add_argument("--disable-notifications")
                options.add_argument("--disable-translate")
                options.add_argument("--no-first-run")
                options.add_argument("--no-default-browser-check")
                options.add_argument("--ignore-certificate-errors")

                # Better stealth - don't disable too many things
                # Removed: --disable-web-security, --disable-extensions, --remote-debugging-port=0
                # These are red flags for bot detection

                # Use single process if on very limited VPS (can be toggled)
                if self.config.get("browser.single_process", False):
                    options.add_argument("--single-process")
                    self.logger.debug("Running Chrome in single-process mode (low RAM VPS)")

                # Crash handling
                options.add_argument("--disable-crash-reporter")
                options.add_argument("--disable-breakpad")

                # Additional stealth arguments for headless
                if self.headless:
                    # Make headless mode look more like regular Chrome
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_argument("--excludeSwitches=['enable-automation']")
                    options.add_argument("--disable-dev-shm-usage")
                    # Set realistic user data directory
                    options.add_argument("--disable-features=IsolateOrigins,site-per-process")

                # Aggressive ad-blocking arguments
                if self.config.use_adblock:
                    # Block third-party cookies and trackers
                    options.add_argument("--block-third-party-cookies")
                    # Disable background networking (prevents ad prefetch)
                    options.add_argument("--disable-background-networking")
                    options.add_argument("--disable-background-timer-throttling")
                    # Disable various Google services and telemetry
                    options.add_argument("--disable-sync")
                    options.add_argument("--disable-client-side-phishing-detection")
                    # Block domains - Google Ads, DoubleClick, AdSense
                    options.add_argument(
                        "--host-resolver-rules=MAP *.doubleclick.net 0.0.0.0, MAP *.googlesyndication.com 0.0.0.0, MAP *.googleadservices.com 0.0.0.0, MAP *.google-analytics.com 0.0.0.0, MAP pagead2.googlesyndication.com 0.0.0.0"
                    )

                # User agent
                user_agent = self.config.get("browser.user_agent")
                if user_agent:
                    options.add_argument(f"user-agent={user_agent}")

                # Setup Chrome preferences
                prefs = {}

                # DNS-based AdBlocking - More reliable than extensions
                # Use DNS over HTTPS with multiple aggressive ad-blocking DNS servers
                if self.config.use_adblock:
                    # Using NextDNS with aggressive ad-blocking (blocks Google Ads, DoubleClick, etc.)
                    # Alternative: dns0.eu for maximum privacy and ad-blocking
                    dns_servers = [
                        "https://dns.nextdns.io/dns-query",  # NextDNS - Very aggressive
                        "https://dns0.eu/dns-query",  # DNS0.eu - Privacy + AdBlock
                        "https://doh.mullvad.net/dns-query",  # Mullvad DNS - AdBlock
                    ]
                    prefs["dns_over_https.mode"] = "secure"
                    prefs["dns_over_https.templates"] = " ".join(dns_servers)

                    # Block third-party ads at browser level
                    prefs["profile.default_content_setting_values.ads"] = 2  # Block all ads
                    prefs["profile.managed_default_content_settings.popups"] = 2  # Block popups

                    self.logger.info(
                        "✓ AdBlock DNS enabled (NextDNS + DNS0.eu + Mullvad - Aggressive Mode)"
                    )

                # Disable images if configured
                if self.config.get("browser.disable_images", False):
                    prefs["profile.managed_default_content_settings.images"] = 2

                # Disable notifications, geolocation, and other permissions
                prefs["profile.default_content_setting_values.notifications"] = 2  # Block
                prefs["profile.default_content_setting_values.geolocation"] = 2
                prefs["profile.default_content_setting_values.media_stream"] = 2

                # Apply all preferences
                if prefs:
                    options.add_experimental_option("prefs", prefs)

                # Create driver with retry-safe parameters
                self.logger.debug("Creating Chrome driver instance...")
                self.driver = uc.Chrome(
                    options=options,
                    version_main=None,
                    use_subprocess=True,  # More stable
                    driver_executable_path=None,
                )

                self.driver.maximize_window()

                # Set timeouts
                self.driver.set_page_load_timeout(self.config.get("timeouts.page_load", 30))

                # Apply stealth scripts for headless mode
                # Note: Must be non-blocking (errors caught internally)
                if self.headless:
                    try:
                        self._apply_stealth_scripts()
                    except Exception as stealth_error:
                        self.logger.debug(f"Stealth scripts skipped: {stealth_error}")

                # Enable ad-blocking via Chrome DevTools Protocol
                # Note: Must be non-blocking (errors caught internally)
                if self.config.use_adblock:
                    try:
                        self._setup_request_interception()
                    except Exception as adblock_error:
                        self.logger.debug(f"AdBlock setup skipped: {adblock_error}")

                self.logger.success("Browser initialized successfully")

                # If we get here, driver is ready
                return

            except WebDriverException as e:
                error_msg = str(e)
                self.logger.warning(
                    f"⚠ Chrome connection failed (attempt {attempt}/{max_retries}): {error_msg[:150]}"
                )

                # Check for specific error types and provide targeted solutions
                if (
                    "chrome not reachable" in error_msg.lower()
                    or "cannot connect to chrome" in error_msg.lower()
                ):
                    self.logger.warning("Chrome started but crashed or became unreachable")
                    if attempt == 1:
                        self.logger.info("💡 VPS/Server tips:")
                        self.logger.info("  - Ensure headless mode is enabled in config.yaml")
                        self.logger.info("  - Check /dev/shm size: df -h /dev/shm")
                        self.logger.info("  - Verify Chrome is installed: google-chrome --version")

                # Cleanup on error
                if self.driver:
                    try:
                        self.driver.quit()
                    except BaseException:
                        pass
                    self.driver = None

                # If this is not the last attempt, wait and retry
                if attempt < max_retries:
                    self.logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    # Kill any remaining processes
                    self._kill_zombie_chrome_processes()
                else:
                    # Last attempt failed
                    self.logger.error("❌ Failed to initialize Chrome after all retries")
                    self.logger.error("")
                    self.logger.error("🔧 VPS/Server Solutions:")
                    self.logger.error("1. Verify Chrome installation:")
                    self.logger.error("   google-chrome --version")
                    self.logger.error("   which google-chrome")
                    self.logger.error("")
                    self.logger.error("2. Enable headless mode in config.yaml:")
                    self.logger.error("   browser:")
                    self.logger.error("     headless: true")
                    self.logger.error("")
                    self.logger.error("3. Check /dev/shm size (should be >64MB):")
                    self.logger.error("   df -h /dev/shm")
                    self.logger.error(
                        "   # If too small, increase it or --disable-dev-shm-usage is already set"
                    )
                    self.logger.error("")
                    self.logger.error("4. Install missing dependencies:")
                    self.logger.error("   ./install_chrome_vps.sh")
                    self.logger.error("")
                    self.logger.error("5. Kill zombie processes:")
                    self.logger.error("   pkill -9 -f chrome")
                    self.logger.error("   pkill -9 -f chromedriver")
                    self.logger.error("")
                    self.logger.error("6. Try running with Xvfb:")
                    self.logger.error("   xvfb-run python run.py")
                    raise

            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Unexpected error setting up driver: {error_msg}")

                # Check if it's a Chrome binary issue
                if "Binary Location" in error_msg or "chrome not found" in error_msg.lower():
                    self.logger.error("Chrome browser not found on this system!")
                    self.logger.error("Solutions for VPS/Server:")
                    self.logger.error("1. Install Chrome:")
                    self.logger.error(
                        "   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
                    )
                    self.logger.error(
                        "   sudo apt install ./google-chrome-stable_current_amd64.deb"
                    )
                    self.logger.error("   OR")
                    self.logger.error("   sudo apt install chromium-browser")
                    self.logger.error("")
                    self.logger.error("2. Verify installation:")
                    self.logger.error("   which google-chrome")
                    self.logger.error("   google-chrome --version")

                if self.driver:
                    try:
                        self.driver.quit()
                    except BaseException:
                        pass
                    self.driver = None

                if attempt >= max_retries:
                    raise
                else:
                    time.sleep(retry_delay)

    def _wait_for_page_ready(self, timeout: int = 30):
        """Wait for page to be fully loaded and ready"""
        try:
            from selenium.webdriver.support.ui import WebDriverWait

            self.logger.debug("Waiting for page ready state...")

            # Wait for document.readyState === 'complete'
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            self.logger.debug("✓ Page ready state: complete")

            # Wait for body to be present
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.body != null")
            )

            self.logger.debug("✓ Document body present")

            # Additional wait for dynamic content
            if self.headless or self._using_xvfb:
                self.logger.debug("Waiting for dynamic content to render...")
                random_delay(3, 5)

        except Exception as e:
            self.logger.warning(f"Could not verify page ready state: {e}")

    def _debug_save_page_source(self, label: str = "debug"):
        """Save page source for debugging (Zefoy diagnosis)"""
        try:
            import time
            from pathlib import Path

            debug_dir = Path("debug")
            debug_dir.mkdir(exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")

            # Save HTML source
            filename = f"page_source_{label}_{timestamp}.html"
            filepath = debug_dir / filename
            page_source = self.driver.page_source
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(page_source)
            self.logger.info(f"📄 Page source saved: {filepath}")

            # Save screenshot
            screenshot_path = debug_dir / f"screenshot_{label}_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_path))
            self.logger.info(f"📸 Screenshot saved: {screenshot_path}")

            # Save diagnostic info
            diagnostic_path = debug_dir / f"diagnostic_{label}_{timestamp}.txt"
            with open(diagnostic_path, "w", encoding="utf-8") as f:
                f.write(f"=== Zefoy Bot Debug Report ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Label: {label}\n")
                f.write(f"Headless: {self.headless}\n")
                f.write(f"Using Xvfb: {self._using_xvfb}\n")
                f.write(f"\n=== Page Info ===\n")
                f.write(f"URL: {self.driver.current_url}\n")
                f.write(f"Title: {self.driver.title}\n")

                # Check for key elements
                f.write(f"\n=== Element Detection ===\n")
                try:
                    # Check captcha
                    captcha = self.driver.find_elements("id", "captchatoken")
                    f.write(
                        f"Captcha element (#captchatoken): {'FOUND' if captcha else 'NOT FOUND'}\n"
                    )

                    # Check common elements
                    body = self.driver.find_elements("tag name", "body")
                    f.write(f"Body tag: {'FOUND' if body else 'NOT FOUND'}\n")

                    forms = self.driver.find_elements("tag name", "form")
                    f.write(f"Forms count: {len(forms)}\n")

                    buttons = self.driver.find_elements("tag name", "button")
                    f.write(f"Buttons count: {len(buttons)}\n")

                except Exception as e:
                    f.write(f"Error checking elements: {e}\n")

                # Page source analysis
                f.write(f"\n=== Page Source Analysis ===\n")
                f.write(f"Length: {len(page_source)} characters\n")
                f.write(
                    f"Contains 'captcha': {'YES' if 'captcha' in page_source.lower() else 'NO'}\n"
                )
                f.write(f"Contains 'zefoy': {'YES' if 'zefoy' in page_source.lower() else 'NO'}\n")

            self.logger.info(f"📋 Diagnostic saved: {diagnostic_path}")
            self.logger.info(f"💡 Check debug/ folder for analysis")

        except Exception as e:
            self.logger.warning(f"Could not save debug info: {e}")

    def _apply_stealth_scripts(self):
        """
        Apply advanced stealth JavaScript to hide headless/automation indicators.

        Note: Provides 60-80% success rate with Zefoy.
        For 95%+ success, use Xvfb: ./run_xvfb.sh

        This function is designed to NEVER throw exceptions to avoid
        disrupting browser setup. All errors are caught and logged only.
        """
        try:
            if not self.headless and not self._using_xvfb:
                # Skip stealth scripts in normal visible mode (not needed)
                self.logger.debug("Skipping stealth scripts (visible mode with real display)")
                return
            self.logger.info("🎭 Applying stealth scripts (backup mode, 60-80% success)")
            self.logger.info("💡 For best results (95%+), use Xvfb: ./run_xvfb.sh")

            # Comprehensive stealth script
            stealth_script = """
            // Hide webdriver (most critical)
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

            // Mock plugins with realistic data
            Object.defineProperty(navigator, 'plugins', {
                get: () => [{
                    name: 'Chrome PDF Plugin',
                    description: 'Portable Document Format',
                    filename: 'internal-pdf-viewer'
                }]
            });

            // Mock mimeTypes
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [{type: 'application/pdf', suffixes: 'pdf'}]
            });

            // Set realistic languages
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});

            // Override permissions
            const origQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (params) => (
                params.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                origQuery(params)
            );

            // Mock chrome.runtime (important!)
            if (!window.chrome) window.chrome = {};
            if (!window.chrome.runtime) {
                window.chrome.runtime = {
                    PlatformOs: {LINUX: 'linux', WIN: 'win', MAC: 'mac'},
                    PlatformArch: {X86_64: 'x86-64'}
                };
            }

            // Set realistic platform/vendor
            Object.defineProperty(navigator, 'platform', {get: () => 'Linux x86_64'});
            Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});

            // Mock hardware (realistic)
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});

            // Mock connection
            Object.defineProperty(navigator, 'connection', {
                get: () => ({effectiveType: '4g', rtt: 50, downlink: 10})
            });

            // Hide automation flags
            delete navigator.__proto__.webdriver;
            """

            # Try CDP first (best method)
            try:
                self.driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument", {"source": stealth_script}
                )
                self.logger.info("✓ Stealth scripts applied via CDP")
                self.logger.debug("Coverage: webdriver, plugins, chrome.runtime, hardware specs")

            except Exception as cdp_error:
                # Fallback: inject on page load (less effective but works)
                self.logger.warning(f"⚠️  CDP injection failed: {cdp_error}")
                self.logger.info("🔄 Using fallback injection method...")

                # Store script to inject on each page load
                self._stealth_script_fallback = stealth_script
                self.logger.info("✓ Stealth scripts prepared (will inject on page load)")

        except Exception as e:
            self.logger.error(f"❌ Failed to apply stealth: {e}")
            self.logger.warning("⚠️  Running without stealth protection!")
            self.logger.warning("🔧 Recommended: Use Xvfb instead: ./run_xvfb.sh")

    def _setup_request_interception(self):
        """
        Setup request interception to block ads using Chrome DevTools Protocol

        Note: This function is designed to NEVER throw exceptions to avoid
        disrupting browser setup. All errors are caught and logged only.
        """
        try:
            # Skip if adblock is disabled
            if not self.config.get("browser.adblock_enabled", True):
                self.logger.debug("AdBlock disabled in config")
                return

            # Load blocklist
            blocklist_path = Path(__file__).parent.parent / "ad_blocklist.txt"
            blocked_domains = []

            if blocklist_path.exists():
                with open(blocklist_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Extract domain from "0.0.0.0 domain.com" format
                            parts = line.split()
                            if len(parts) >= 2:
                                blocked_domains.append(parts[1])

            # Set blocked URL patterns
            blocked_patterns = []
            for domain in blocked_domains[:50]:  # Limit to prevent issues
                blocked_patterns.append(f"*://{domain}/*")
                blocked_patterns.append(f"*://*.{domain}/*")

            # Try CDP-based blocking
            try:
                # Enable Network domain for DevTools
                self.driver.execute_cdp_cmd("Network.enable", {})

                # Block requests matching ad patterns
                self.driver.execute_cdp_cmd(
                    "Network.setBlockedURLs",
                    {"urls": blocked_patterns[:100]},  # Chrome limits to 100 patterns
                )

                self.logger.info(
                    f"✓ AdBlock enabled via CDP - {len(blocked_patterns[:100])} patterns blocked"
                )

            except Exception as cdp_error:
                # CDP might fail on some VPS setups - that's okay
                self.logger.debug(f"CDP-based adblock unavailable: {cdp_error}")
                self.logger.info("✓ AdBlock: Using DNS-based blocking only")
                # DNS-based blocking is already configured in prefs

        except Exception as e:
            # Catch ALL exceptions to prevent browser setup failure
            self.logger.debug(f"AdBlock setup skipped: {str(e)}")
            # Continue without adblock - browser will still work

    def _dismiss_alerts(self, max_attempts: int = 3):
        """Dismiss any alerts that may appear"""
        for attempt in range(max_attempts):
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.logger.info(f"Alert detected: {alert_text}")
                alert.dismiss()  # Or use alert.accept() to click OK
                self.logger.info("Alert dismissed successfully")
                random_delay(0.5, 1)
            except UnexpectedAlertPresentException:
                # Alert still present, try again
                continue
            except Exception:
                # No alert present, break
                break

    def _reset_to_home(self):
        """Reset browser state by navigating back to home page"""
        try:
            current_url = self.driver.current_url

            # If we're not on the main Zefoy page, navigate to it
            if current_url != self.config.zefoy_url:
                self.logger.info("Navigating back to home page...")
                self.driver.get(self.config.zefoy_url)
                random_delay(2, 3)
            else:
                # Refresh the page to reset state
                self.logger.info("Refreshing page to reset state...")
                self.driver.refresh()
                random_delay(2, 3)

            # Dismiss any alerts that may appear after refresh
            self._dismiss_alerts()

            self.logger.info("Page reset successful")
            return True

        except Exception as e:
            self.logger.error(f"Error resetting to home: {str(e)}")
            return False

    def execute_service(
        self,
        service_name: str,
        video_url: str,
        max_retries: int = 3,
        target: int = None,
        auto_retry: bool = True,
        use_target_goals: bool = False,
        target_amount: int = None,
    ) -> bool:
        """
        Execute a service (Followers, Hearts, Views, etc.)

        Args:
            service_name: Name of the service
            video_url: TikTok video URL
            max_retries: Maximum retry attempts
            target: Number of times to execute the service (None = use target_goals if enabled)
            auto_retry: Automatically retry when cooldown is detected
            use_target_goals: Use target goals from config to determine executions
            target_amount: Target amount (views, hearts, etc.) to reach (None = use execution count)

        Returns:
            True if successful, False otherwise
        """
        if not self.session_active:
            self.logger.error("Bot not initialized. Please call start() first.")
            return False

        # Reset to home page to ensure clean state
        self.logger.info("Ensuring we're on home page...")
        if not self._reset_to_home():
            self.logger.warning("Failed to reset to home page, continuing anyway...")

        # Check if service is enabled (not checking active_service anymore - all enabled services can be used)
        service_config = self._find_service(service_name)
        if service_config and not service_config.get("enabled", False):
            self.logger.warning(f"Service {service_name} is disabled in configuration")
            BotUI.print_warning_panel(
                f"Service '{service_name}' is DISABLED in configuration.\n"
                f"Enable it in Settings for best results.\n\n"
                f"You can still try to use it, but it may not work properly.",
                title="⚠ Service Disabled",
            )

            # Ask if user wants to continue anyway
            if not BotUI.ask_confirm("Continue with disabled service?", default=False):
                return False

        # Validate URL
        if not validate_tiktok_url(video_url):
            self.logger.error(f"Invalid TikTok URL: {video_url}")
            BotUI.print_error_panel("Invalid TikTok URL format!")
            return False

        # Find service configuration
        service = self._find_service(service_name)
        if not service:
            self.logger.error(f"Service not found: {service_name}")
            return False

        # Determine target executions and mode
        if use_target_goals and self.target_tracker:
            # Check if target is already reached
            if self.target_tracker.is_target_reached(service_name):
                progress = self.target_tracker.get_progress(service_name)
                BotUI.print_success_panel(
                    f"Target already reached!\n{self.target_tracker.get_summary(service_name)}",
                    title=f"✓ {service_name} Target Reached",
                )
                # Reset to home page before returning
                self._reset_to_home()
                return True

            # Calculate needed executions based on target goal
            target = self.target_tracker.get_estimated_executions(service_name)
            progress = self.target_tracker.get_progress(service_name)

            self.logger.info(f"Executing service: {service_name} (Target Goal Mode)")
            BotUI.print_info_panel(
                f"Starting {service_name} service...\n"
                f"Target Goal: {progress['target']:,}\n"
                f"Current Progress: {progress['current']:,}\n"
                f"Remaining: {progress['remaining']:,}\n"
                f"Estimated Executions Needed: {target}",
                title=f"🎯 {service_name} - Goal Mode",
            )
        elif target_amount is not None:
            # Target Amount Mode - run until specific amount reached
            self.logger.info(
                f"Executing service: {service_name} (Target Amount: {target_amount:,})"
            )
            BotUI.print_info_panel(
                f"Starting {service_name} service...\n"
                f"Target Amount: {target_amount:,} {service_name.lower()}\n"
                f"Current: 0\n"
                f"Bot will run until target is reached!",
                title=f"🎯 {service_name} - Target Amount Mode",
            )
            target = 999999  # Large number, will stop when amount reached
        else:
            # Use manual target or default
            if target is None:
                target = 1

            self.logger.info(f"Executing service: {service_name} (Executions: {target})")
            BotUI.print_info_panel(
                f"Starting {service_name} service...\nTarget: {target} execution(s)",
                title=f"🚀 {service_name}",
            )

        successful_executions = 0
        # Continuous mode: Goals, Target Amount, OR Manual with multiple executions (>1)
        # Single execution (manual 1x) is NOT continuous - will reset to home at end
        is_continuous_mode = use_target_goals or (target_amount is not None) or (target > 1)
        pending_cooldown = 0  # Track cooldown from previous execution

        while successful_executions < target:
            # For continuous mode (Goals/Target Amount/Manual >1x), stay on same page and use search->send flow
            # Single execution mode will be handled at the end
            if successful_executions > 0:
                if is_continuous_mode:
                    # Stay on current page, will use search->send button flow
                    self.logger.info("Continuous mode: Staying on current page...")

                    # Wait for pending cooldown from previous execution
                    if pending_cooldown > 0:
                        wait_time_friendly = format_time_user_friendly(pending_cooldown)
                        self.logger.info(
                            f"Waiting for cooldown before next execution: {wait_time_friendly}"
                        )
                        countdown_timer(pending_cooldown, f"Cooldown for next {service_name}")
                        self.logger.info("Cooldown finished! Ready for next execution...")
                        pending_cooldown = 0  # Reset after waiting
                    else:
                        # Fallback: If no cooldown detected, use minimum default cooldown (60 seconds)
                        # This prevents bot from running too fast if cooldown extraction fails
                        default_cooldown = 60
                        self.logger.warning(
                            f"No cooldown detected from previous execution. Using default: {default_cooldown}s"
                        )
                        countdown_timer(default_cooldown, f"Default cooldown for {service_name}")
                        self.logger.info("Default cooldown finished! Ready for next execution...")
                # Note: Single execution (target=1) doesn't need reset here,
                # will reset at the end to prevent errors in next service

            execution_num = successful_executions + 1
            self.logger.info(f"Execution {execution_num}/{target}")

            for attempt in range(1, max_retries + 1):
                try:
                    self.logger.info(f"Attempt {attempt}/{max_retries}")

                    # For continuous mode after first execution, skip initial setup and go directly to search->send
                    if is_continuous_mode and successful_executions > 0:
                        self.logger.info("Continuous mode: Using search->send flow...")

                        # Directly use search->send button flow
                        result = self._wait_and_click_ready_button(service)

                        # Check if still on cooldown
                        if result.get("wait_time"):
                            wait_seconds = result["wait_time"]
                            wait_time_friendly = format_time_user_friendly(wait_seconds)

                            self.logger.warning(
                                f"Still on cooldown! Additional wait needed: {wait_time_friendly}"
                            )
                            BotUI.print_warning_panel(
                                f"Service still on cooldown\nAdditional wait time: {wait_time_friendly}",
                                title="⏳ Additional Cooldown",
                            )

                            # Wait for the additional cooldown
                            countdown_timer(wait_seconds, f"Additional cooldown for {service_name}")
                            self.logger.info("Additional cooldown finished! Retrying...")

                            # Retry after cooldown
                            if attempt < max_retries:
                                random_delay(1, 2)
                                continue
                            else:
                                return False

                        if not result["success"]:
                            if attempt < max_retries:
                                self.logger.warning("Search->send flow failed, retrying...")
                                random_delay(2, 3)
                                continue
                            else:
                                return False

                        # Extract and log amount sent
                        amount_sent = self._extract_amount_sent(
                            result.get("message", ""), service_name
                        )
                        service_emote = self._get_service_emote(service_name)

                        if amount_sent:
                            self.logger.success(
                                f"{service_emote} Successfully sent +{amount_sent} {service_name.lower()}!"
                            )
                            console.print(
                                f"[bold green]{service_emote} +{amount_sent} {service_name.lower()} delivered![/bold green]"
                            )
                        else:
                            self.logger.success(
                                f"{service_emote} {service_name} sent successfully!"
                            )

                        # Store next cooldown for continuous mode
                        if successful_executions + 1 < target:
                            if result.get("next_cooldown"):
                                pending_cooldown = result["next_cooldown"]
                                self.logger.info(
                                    f"Next cooldown detected: {format_time_duration(pending_cooldown)}"
                                )
                            else:
                                # Fallback: Set default cooldown if not detected
                                pending_cooldown = 120  # Default 2 minutes
                                self.logger.warning(
                                    f"No cooldown detected in response. Using default: {pending_cooldown}s"
                                )

                        # Update counters
                        successful_executions += 1
                        self.stats["tasks_completed"] += 1
                        self.stats["services_used"][service_name] = (
                            self.stats["services_used"].get(service_name, 0) + 1
                        )

                        # Always update target tracker (for statistics and progress tracking)
                        if self.target_tracker:
                            amount = self.target_tracker.extract_amount_from_response(
                                result.get("message", ""), service_name
                            )
                            self.target_tracker.update_progress(service_name, amount)
                            self.target_tracker.save_progress()

                            # Check if target is reached (only matters when using goal mode)
                            if use_target_goals and self.target_tracker.is_target_reached(
                                service_name
                            ):
                                service_emote = self._get_service_emote(service_name)
                                progress = self.target_tracker.get_progress(service_name)

                                # Create beautiful centered finish message
                                from rich import box
                                from rich.align import Align
                                from rich.panel import Panel
                                from rich.text import Text

                                finish_content = Text()
                                finish_content.append(
                                    "🎯 TARGET GOAL REACHED! 🎯\n\n", style="bold yellow"
                                )
                                finish_content.append(
                                    f"{service_emote} Service: ", style="bold white"
                                )
                                finish_content.append(f"{service_name}\n", style="bold cyan")
                                finish_content.append("🎯 Target: ", style="bold white")
                                finish_content.append(f"{progress['target']:,}\n", style="green")
                                finish_content.append("✅ Current: ", style="bold white")
                                finish_content.append(f"{progress['current']:,}\n", style="green")
                                finish_content.append("📊 Progress: ", style="bold white")
                                finish_content.append(
                                    f"{progress['percentage']:.1f}%\n", style="green"
                                )
                                finish_content.append("⏱️  Total Time: ", style="bold white")
                                finish_content.append(
                                    f"{format_time_duration(int((datetime.now() - self.stats['started_at']).total_seconds()))}\n\n",
                                    style="cyan",
                                )
                                finish_content.append(
                                    "🎉 ✨ 🎊 ⭐ 🌟 Congratulations! 🌟 ⭐ 🎊 ✨ 🎉", style="bold magenta"
                                )

                                console.print(
                                    Panel(
                                        Align.center(finish_content),
                                        title=f"[bold green]🎊 {service_name} Goal Complete 🎊[/bold green]",
                                        title_align="center",
                                        box=box.DOUBLE,
                                        style="bold green",
                                        border_style="green",
                                        padding=(1, 4),
                                    )
                                )

                                self.logger.success(
                                    f"🎯 {service_emote} Target goal of {progress['target']:,} {service_name.lower()} reached! 🎯"
                                )
                                BotUI.print_separator()
                                console.print(
                                    f"[bold green]🏆 Fantastic! Goal achieved perfectly! 🏆[/bold green]"
                                )
                                BotUI.print_separator()

                                # Reset to home page before returning
                                self._reset_to_home()
                                return True
                        else:
                            BotUI.print_success_panel(
                                f"Execution {successful_executions}/{target} completed!\n{result.get('message', '')}",
                                title=f"✓ {service_name} Success",
                            )

                        # Break attempt loop, continue target loop
                        break
                    else:
                        # First execution or manual mode: Full flow (click service, submit URL, etc)

                        # Click service button
                        if not self._click_service_button(service):
                            if attempt < max_retries:
                                random_delay(2, 3)
                                continue
                            return False

                        # Wait for service menu to appear
                        if not self._wait_for_service_menu(service):
                            if attempt < max_retries:
                                random_delay(2, 3)
                                continue
                            return False

                        # Submit video URL
                        if not self._submit_video_url(service, video_url):
                            if attempt < max_retries:
                                random_delay(2, 3)
                                continue
                            return False

                        # Handle response (includes cooldown detection and ready button clicking)
                        result = self._handle_service_response(service)

                    if result["success"]:
                        successful_executions += 1
                        self.stats["tasks_completed"] += 1
                        self.stats["services_used"][service_name] = (
                            self.stats["services_used"].get(service_name, 0) + 1
                        )

                        # Extract and log amount sent
                        amount_sent = self._extract_amount_sent(
                            result.get("message", ""), service_name
                        )
                        service_emote = self._get_service_emote(service_name)

                        if amount_sent:
                            self.logger.success(
                                f"{service_emote} Successfully sent +{amount_sent} {service_name.lower()}!"
                            )
                            console.print(
                                f"[bold green]{service_emote} +{amount_sent} {service_name.lower()} delivered![/bold green]"
                            )
                        else:
                            self.logger.success(
                                f"{service_emote} {service_name} sent successfully!"
                            )

                        # Store next cooldown for continuous mode
                        if is_continuous_mode and successful_executions < target:
                            if result.get("next_cooldown"):
                                pending_cooldown = result["next_cooldown"]
                                self.logger.info(
                                    f"Next cooldown detected: {format_time_duration(pending_cooldown)}"
                                )
                            else:
                                # Fallback: Set default cooldown if not detected
                                pending_cooldown = 120  # Default 2 minutes
                                self.logger.warning(
                                    f"No cooldown detected in response. Using default: {pending_cooldown}s"
                                )

                        # For non-continuous mode, wait immediately
                        if not is_continuous_mode and auto_retry and successful_executions < target:
                            if result.get("next_cooldown"):
                                wait_seconds = result["next_cooldown"]
                            else:
                                # Fallback: Use default cooldown if not detected
                                wait_seconds = 120  # Default 2 minutes
                                self.logger.warning(
                                    f"No cooldown detected in response. Using default: {wait_seconds}s"
                                )

                            wait_time_friendly = format_time_user_friendly(wait_seconds)
                            self.logger.info(f"Next cooldown detected: {wait_time_friendly}")
                            BotUI.print_info_panel(
                                f"Cooldown until next execution\nWait time: {wait_time_friendly}",
                                title="⏳ Next Cooldown",
                            )

                            # Show countdown
                            countdown_timer(wait_seconds, f"Cooldown for next {service_name}")
                            self.logger.info("Cooldown finished! Ready for next execution...")

                        # Always update target tracker (for statistics and progress tracking)
                        if self.target_tracker:
                            amount = self.target_tracker.extract_amount_from_response(
                                result.get("message", ""), service_name
                            )
                            self.target_tracker.update_progress(service_name, amount)
                            self.target_tracker.save_progress()  # Auto-save progress

                            # Show progress if using goal mode
                            if use_target_goals:
                                progress = self.target_tracker.get_progress(service_name)
                                progress_bar = self.target_tracker.format_progress_bar(service_name)

                                BotUI.print_success_panel(
                                    f"Execution {successful_executions}/{target} completed!\n"
                                    f"{result.get('message', '')}\n\n"
                                    f"Progress: {self.target_tracker.get_summary(service_name)}\n"
                                    f"{progress_bar}",
                                    title=f"✓ {service_name} Success",
                                )

                            # Check if target goal reached (only when using goal mode)
                            if use_target_goals and self.target_tracker.is_target_reached(
                                service_name
                            ):
                                service_emote = self._get_service_emote(service_name)
                                progress = self.target_tracker.get_progress(service_name)

                                # Create beautiful centered finish message
                                from rich import box
                                from rich.align import Align
                                from rich.panel import Panel
                                from rich.text import Text

                                finish_content = Text()
                                finish_content.append(
                                    "🎯 TARGET GOAL REACHED! 🎯\n\n", style="bold yellow"
                                )
                                finish_content.append(
                                    f"{service_emote} Service: ", style="bold white"
                                )
                                finish_content.append(f"{service_name}\n", style="bold cyan")
                                finish_content.append("🎯 Target: ", style="bold white")
                                finish_content.append(f"{progress['target']:,}\n", style="green")
                                finish_content.append("✅ Current: ", style="bold white")
                                finish_content.append(f"{progress['current']:,}\n", style="green")
                                finish_content.append("📊 Progress: ", style="bold white")
                                finish_content.append(
                                    f"{progress['percentage']:.1f}%\n", style="green"
                                )
                                finish_content.append("⏱️  Total Time: ", style="bold white")
                                finish_content.append(
                                    f"{format_time_duration(int((datetime.now() - self.stats['started_at']).total_seconds()))}\n\n",
                                    style="cyan",
                                )
                                finish_content.append(
                                    "🎉 ✨ 🎊 ⭐ 🌟 Congratulations! 🌟 ⭐ 🎊 ✨ 🎉", style="bold magenta"
                                )

                                console.print(
                                    Panel(
                                        Align.center(finish_content),
                                        title=f"[bold green]🎊 {service_name} Goal Complete 🎊[/bold green]",
                                        title_align="center",
                                        box=box.DOUBLE,
                                        style="bold green",
                                        border_style="green",
                                        padding=(1, 4),
                                    )
                                )

                                self.logger.success(
                                    f"🎯 {service_emote} Target goal of {progress['target']:,} {service_name.lower()} reached! 🎯"
                                )
                                BotUI.print_separator()
                                console.print(
                                    f"[bold green]🏆 Fantastic! Goal achieved perfectly! 🏆[/bold green]"
                                )
                                BotUI.print_separator()

                                # Reset to home page before returning
                                self._reset_to_home()
                                return True
                        else:
                            BotUI.print_success_panel(
                                f"Execution {successful_executions}/{target} completed!\n{result.get('message', '')}",
                                title=f"✓ {service_name} Success",
                            )

                        # Break attempt loop, continue target loop
                        break

                    elif result.get("wait_time"):
                        wait_seconds = result["wait_time"]
                        wait_time_friendly = format_time_user_friendly(wait_seconds)

                        BotUI.print_warning_panel(
                            f"Service on cooldown\nWait time: {wait_time_friendly}\n"
                            f"Progress: {successful_executions}/{target} completed",
                            title="⏳ Cooldown Detected",
                        )

                        if auto_retry:
                            self.logger.info(f"Auto-retry enabled. Waiting {wait_time_friendly}...")

                            # Show countdown
                            countdown_timer(wait_seconds, f"Cooldown for {service_name}")

                            self.logger.info("Cooldown finished! Looking for ready button...")

                            # After cooldown, look for ready button instead of starting over
                            ready_result = self._wait_and_click_ready_button(service)

                            # Check if still on cooldown
                            if ready_result.get("wait_time"):
                                additional_wait = ready_result["wait_time"]
                                wait_time_friendly = format_time_user_friendly(additional_wait)

                                self.logger.warning(
                                    f"Still on cooldown! Additional wait needed: {wait_time_friendly}"
                                )
                                BotUI.print_warning_panel(
                                    f"Service still on cooldown\nAdditional wait time: {wait_time_friendly}",
                                    title="⏳ Additional Cooldown",
                                )

                                # Wait for additional cooldown
                                countdown_timer(
                                    additional_wait, f"Additional cooldown for {service_name}"
                                )
                                self.logger.info("Additional cooldown finished! Retrying...")

                                # Retry clicking ready button
                                ready_result = self._wait_and_click_ready_button(service)

                            if ready_result["success"]:
                                # Treat this as a successful execution
                                successful_executions += 1
                                self.stats["tasks_completed"] += 1
                                self.stats["services_used"][service_name] = (
                                    self.stats["services_used"].get(service_name, 0) + 1
                                )

                                # Extract and log amount sent
                                amount_sent = self._extract_amount_sent(
                                    ready_result.get("message", ""), service_name
                                )
                                service_emote = self._get_service_emote(service_name)

                                if amount_sent:
                                    self.logger.success(
                                        f"{service_emote} Successfully sent +{amount_sent} {service_name.lower()}!"
                                    )
                                    console.print(
                                        f"[bold green]{service_emote} +{amount_sent} {service_name.lower()} delivered![/bold green]"
                                    )
                                else:
                                    self.logger.success(
                                        f"{service_emote} {service_name} sent successfully!"
                                    )

                                # Store next cooldown for continuous mode
                                if is_continuous_mode and successful_executions < target:
                                    if ready_result.get("next_cooldown"):
                                        pending_cooldown = ready_result["next_cooldown"]
                                        self.logger.info(
                                            f"Next cooldown detected: {format_time_duration(pending_cooldown)}"
                                        )
                                    else:
                                        # Fallback: Set default cooldown if not detected
                                        pending_cooldown = 120  # Default 2 minutes
                                        self.logger.warning(
                                            f"No cooldown detected in response. Using default: {pending_cooldown}s"
                                        )

                                # For non-continuous mode, wait immediately
                                if (
                                    not is_continuous_mode
                                    and auto_retry
                                    and successful_executions < target
                                ):
                                    if ready_result.get("next_cooldown"):
                                        wait_seconds = ready_result["next_cooldown"]
                                    else:
                                        # Fallback: Use default cooldown if not detected
                                        wait_seconds = 120  # Default 2 minutes
                                        self.logger.warning(
                                            f"No cooldown detected in response. Using default: {wait_seconds}s"
                                        )

                                    wait_time_friendly = format_time_user_friendly(wait_seconds)
                                    self.logger.info(
                                        f"Next cooldown detected: {wait_time_friendly}"
                                    )
                                    countdown_timer(
                                        wait_seconds, f"Cooldown for next {service_name}"
                                    )
                                    self.logger.info(
                                        "Cooldown finished! Ready for next execution..."
                                    )

                                # Always update target tracker (for statistics and progress tracking)
                                if self.target_tracker:
                                    amount = self.target_tracker.extract_amount_from_response(
                                        ready_result.get("message", ""), service_name
                                    )
                                    self.target_tracker.update_progress(service_name, amount)
                                    self.target_tracker.save_progress()

                                    # Check if target is reached (only matters when using goal mode)
                                    if use_target_goals and self.target_tracker.is_target_reached(
                                        service_name
                                    ):
                                        service_emote = self._get_service_emote(service_name)
                                        progress = self.target_tracker.get_progress(service_name)

                                        # Create beautiful centered finish message
                                        from rich import box
                                        from rich.align import Align
                                        from rich.panel import Panel
                                        from rich.text import Text

                                        finish_content = Text()
                                        finish_content.append(
                                            "🎯 TARGET GOAL REACHED! 🎯\n\n", style="bold yellow"
                                        )
                                        finish_content.append(
                                            f"{service_emote} Service: ", style="bold white"
                                        )
                                        finish_content.append(
                                            f"{service_name}\n", style="bold cyan"
                                        )
                                        finish_content.append("🎯 Target: ", style="bold white")
                                        finish_content.append(
                                            f"{progress['target']:,}\n", style="green"
                                        )
                                        finish_content.append("✅ Current: ", style="bold white")
                                        finish_content.append(
                                            f"{progress['current']:,}\n", style="green"
                                        )
                                        finish_content.append("📊 Progress: ", style="bold white")
                                        finish_content.append(
                                            f"{progress['percentage']:.1f}%\n", style="green"
                                        )
                                        finish_content.append(
                                            "⏱️  Total Time: ", style="bold white"
                                        )
                                        finish_content.append(
                                            f"{format_time_duration(int((datetime.now() - self.stats['started_at']).total_seconds()))}\n\n",
                                            style="cyan",
                                        )
                                        finish_content.append(
                                            "🎉 ✨ 🎊 ⭐ 🌟 Congratulations! 🌟 ⭐ 🎊 ✨ 🎉",
                                            style="bold magenta",
                                        )

                                        console.print(
                                            Panel(
                                                Align.center(finish_content),
                                                title=f"[bold green]🎊 {service_name} Goal Complete 🎊[/bold green]",
                                                title_align="center",
                                                box=box.DOUBLE,
                                                style="bold green",
                                                border_style="green",
                                                padding=(1, 4),
                                            )
                                        )

                                        self.logger.success(
                                            f"🎯 {service_emote} Target goal of {progress['target']:,} {service_name.lower()} reached! 🎯"
                                        )
                                        BotUI.print_separator()
                                        BotUI.print_success_panel(
                                            f"🏆 Fantastic! Goal achieved perfectly! 🏆"
                                        )
                                        BotUI.print_separator()

                                        # Reset to home page before returning
                                        self._reset_to_home()
                                        return True

                                BotUI.print_success_panel(
                                    f"Execution {successful_executions}/{target} completed!\n{ready_result.get('message', '')}",
                                    title=f"✓ {service_name} Success",
                                )
                                break
                            else:
                                # Ready button not found or failed, retry from beginning
                                if attempt < max_retries:
                                    self.logger.warning(
                                        "Ready button not found after cooldown, retrying..."
                                    )
                                    random_delay(2, 3)
                                    continue
                                else:
                                    return False
                        else:
                            return False
                    else:
                        if attempt < max_retries:
                            self.logger.warning(
                                f"Service failed: {result.get('message', 'Unknown error')}"
                            )
                            random_delay(2, 3)
                            continue
                        else:
                            raise Exception(result.get("message", "Unknown error"))

                except Exception as e:
                    self.logger.error(f"Error executing service: {str(e)}")
                    self._take_error_screenshot(f"service_error_{service_name}")

                    if attempt >= max_retries:
                        self.stats["tasks_failed"] += 1
                        BotUI.print_error_panel(
                            f"Failed after {max_retries} attempts: {str(e)}\n"
                            f"Progress: {successful_executions}/{target} completed",
                            title=f"✗ {service_name} Failed",
                        )
                        return False

                    random_delay(2, 3)

        # All targets completed - Show beautiful finish message
        service_emote = self._get_service_emote(service_name)

        # Create beautiful centered finish message
        from rich import box
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        finish_content = Text()
        finish_content.append("🎊 MISSION ACCOMPLISHED! 🎊\n\n", style="bold yellow")
        finish_content.append(f"{service_emote} Service: ", style="bold white")
        finish_content.append(f"{service_name}\n", style="bold cyan")
        finish_content.append("✅ Executions: ", style="bold white")
        finish_content.append(f"{successful_executions}/{target} completed\n", style="green")
        finish_content.append("📊 Success Rate: ", style="bold white")
        finish_content.append("100%\n", style="green")
        finish_content.append("⏱️  Total Time: ", style="bold white")
        finish_content.append(
            f"{format_time_duration(int((datetime.now() - self.stats['started_at']).total_seconds()))}\n\n",
            style="cyan",
        )
        finish_content.append("🎉 ✨ 🎊 ⭐ 🌟", style="bold magenta")

        console.print()
        console.print(
            Panel(
                Align.center(finish_content),
                title=f"[bold green]🎉 {service_name} Complete 🎉[/bold green]",
                title_align="center",
                box=box.DOUBLE,
                style="bold green",
                border_style="green",
                padding=(1, 4),
            )
        )
        console.print()

        # Additional celebration log
        self.logger.success(
            f"🎊 {service_emote} All {target} {service_name} executions completed successfully! 🎊"
        )
        BotUI.print_separator()
        BotUI.print_success_panel(f"🏆 Great job! {service_name} service finished perfectly! 🏆")
        BotUI.print_separator()

        # Reset to home page after completing all executions
        self.logger.info("All executions complete. Resetting to home page...")
        self._reset_to_home()

        return True

    def _find_service(self, service_name: str) -> Optional[Dict]:
        """Find service configuration by name"""
        for service in self.config.all_services:
            if service["name"].lower() == service_name.lower():
                return service
        return None

    def _extract_amount_sent(self, message: str, service_name: str) -> Optional[int]:
        """Extract the amount successfully sent from response message"""
        try:
            # Patterns for extracting amounts like "500 views", "25+ hearts", "Successfully 500 views sent"
            patterns = [
                r"Successfully\s+(\d+)\s+",  # "Successfully 500 views sent"
                r"(\d+)\+?\s+(?:views|hearts|shares|favorites|followers|comments?)",  # "500+ views", "25 hearts"
                r"sent\s+(\d+)",  # "sent 500"
            ]

            for pattern in patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    return int(match.group(1))

            return None
        except BaseException:
            return None

    def _get_service_emote(self, service_name: str) -> str:
        """Get emote for service"""
        emotes = {
            "views": "👁️",
            "hearts": "❤️",
            "comments hearts": "💬",
            "shares": "🔄",
            "favorites": "⭐",
            "followers": "👥",
            "live stream": "🎥",
        }
        return emotes.get(service_name.lower(), "✨")

    def _click_service_button(self, service: Dict) -> bool:
        """Click service button on main page"""
        try:
            button_class = service["button_class"]
            self.logger.debug(f"Looking for button: {button_class}")

            button = wait_for_element(
                self.driver, By.CSS_SELECTOR, f"button.{button_class}", timeout=10, clickable=True
            )

            if not button:
                self.logger.error("Service button not found")
                return False

            # Check if button is disabled
            if button.get_attribute("disabled"):
                self.logger.warning("Service button is disabled (may be unavailable)")
                return False

            # Click button
            if not safe_click(self.driver, button):
                self.logger.error("Failed to click service button")
                return False

            random_delay(1, 2)
            return True

        except Exception as e:
            self.logger.error(f"Error clicking service button: {str(e)}")
            return False

    def _wait_for_service_menu(self, service: Dict, timeout: int = 10) -> bool:
        """Wait for service menu to appear"""
        try:
            menu_class = service["menu_class"]
            self.logger.debug(f"Waiting for menu: {menu_class}")

            menu = wait_for_element(
                self.driver, By.CSS_SELECTOR, f"div.{menu_class}", timeout=timeout
            )

            if not menu:
                self.logger.error("Service menu not found")
                return False

            # Check if menu is visible
            if not menu.is_displayed():
                self.logger.error("Service menu is not visible")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error waiting for service menu: {str(e)}")
            return False

    def _submit_video_url(self, service: Dict, video_url: str) -> bool:
        """Submit video URL to service form"""
        try:
            menu_class = service["menu_class"]

            # Find input field
            input_selectors = [
                f"div.{menu_class} input[type='search']",
                f"div.{menu_class} input[name='8dda2e831b9f609']",
                f"div.{menu_class} input.form-control",
            ]

            input_field = None
            for selector in input_selectors:
                input_field = wait_for_element(self.driver, By.CSS_SELECTOR, selector, timeout=5)
                if input_field:
                    break

            if not input_field:
                self.logger.error("Video URL input field not found")
                return False

            # Enter URL
            self.logger.info("Entering video URL...")
            human_typing(input_field, video_url)
            random_delay(0.5, 1)

            # Find and click search/submit button
            button_selectors = [
                f"div.{menu_class} button.disableButton",
                f"div.{menu_class} button[type='submit']",
                f"div.{menu_class} button.btn-primary",
            ]

            submit_button = None
            for selector in button_selectors:
                submit_button = wait_for_element(
                    self.driver, By.CSS_SELECTOR, selector, timeout=5, clickable=True
                )
                if submit_button:
                    break

            if not submit_button:
                self.logger.error("Submit button not found")
                return False

            # Click submit
            if not safe_click(self.driver, submit_button):
                self.logger.error("Failed to click submit button")
                return False

            self.logger.info("Video URL submitted successfully")
            random_delay(2, 3)
            return True

        except Exception as e:
            self.logger.error(f"Error submitting video URL: {str(e)}")
            return False

    def _wait_and_click_ready_button(self, service: Dict, timeout: int = 15) -> Dict:
        """
        After cooldown: Check if still on cooldown, then click search button and ready/send button

        Args:
            service: Service configuration
            timeout: Maximum wait time in seconds

        Returns:
            Dictionary with 'success', 'message', and optionally 'next_cooldown' or 'wait_time'
        """
        try:
            menu_class = service["menu_class"]
            form_action = service["form_action"]

            # Step 0: First check if there's still a cooldown message in response container
            response_container = wait_for_element(self.driver, By.ID, form_action, timeout=5)

            if response_container:
                response_text = response_container.text.strip()

                # Check for cooldown message before clicking search
                cooldown_keywords = ["wait", "cooldown", "please wait", "next submit"]
                if any(keyword in response_text.lower() for keyword in cooldown_keywords):
                    # Still on cooldown, extract wait time
                    wait_time = parse_time_remaining(response_text)
                    if wait_time and wait_time > 0:
                        self.logger.warning(
                            f"Still on cooldown! Wait time: {format_time_user_friendly(wait_time)}"
                        )
                        return {"success": False, "wait_time": wait_time, "message": response_text}

            self.logger.info("Cooldown finished! Re-submitting search...")

            # Step 1: Click search button again to refresh
            search_button_selectors = [
                f"div.{menu_class} button.disableButton",
                f"div.{menu_class} button[type='submit']",
                f"div.{menu_class} button.btn-primary",
            ]

            search_button = None
            for selector in search_button_selectors:
                search_button = wait_for_element(
                    self.driver, By.CSS_SELECTOR, selector, timeout=5, clickable=True
                )
                if search_button:
                    # Check if it's the search button (has search icon or text)
                    btn_html = search_button.get_attribute("innerHTML")
                    if "search" in btn_html.lower() or "fa-search" in btn_html:
                        break

            if search_button:
                self.logger.info("Clicking search button to refresh...")
                if not safe_click(self.driver, search_button):
                    self.logger.warning("Failed to click search button, continuing anyway...")
                else:
                    self.logger.info("Search button clicked successfully")
                random_delay(2, 3)
            else:
                self.logger.warning("Search button not found, looking for ready button directly...")

            # Step 2: Wait for response container
            response_container = wait_for_element(self.driver, By.ID, form_action, timeout=timeout)

            if not response_container:
                return {"success": False, "message": "Response container not found"}

            # Step 3: Look for ready/send button with view count
            self.logger.info("Looking for ready/send button...")
            ready_button = None
            for check_attempt in range(5):
                random_delay(1, 2)

                # Look for submit buttons in response container
                send_buttons = response_container.find_elements(
                    By.CSS_SELECTOR, "button[type='submit']"
                )

                for btn in send_buttons:
                    try:
                        btn_text = btn.text.strip()
                        # Check if button has numeric content (view count)
                        if re.search(r"\d{1,3}(,\d{3})*", btn_text):
                            ready_button = btn
                            self.logger.info(f"Found ready/send button with count: {btn_text}")
                            break
                    except BaseException:
                        continue

                if ready_button:
                    break

                self.logger.debug(f"Ready button not found yet, attempt {check_attempt + 1}/5")

            if not ready_button:
                self.logger.error("Ready/send button not found after waiting")
                # Log what we found instead
                response_text = response_container.text.strip()
                self.logger.debug(f"Response container content: {response_text[:200]}")
                return {"success": False, "message": "Ready/send button not found"}

            # Step 4: Click the ready/send button
            self.logger.info("Clicking ready/send button...")
            if not safe_click(self.driver, ready_button):
                self.logger.error("Failed to click ready/send button")
                return {"success": False, "message": "Failed to click ready/send button"}

            self.logger.info("Ready/send button clicked successfully")
            random_delay(3, 5)

            # Step 5: Get the response after clicking
            response_text = response_container.text.strip()
            self.logger.debug(f"Response after clicking send button: {response_text}")

            # Check for success
            success_keywords = ["successfully", "sent", "completed", "added"]
            is_success = any(keyword in response_text.lower() for keyword in success_keywords)

            if is_success:
                # Extract next cooldown time from success message
                next_cooldown = parse_time_remaining(response_text)
                result = {"success": True, "message": response_text}
                if next_cooldown:
                    result["next_cooldown"] = next_cooldown
                    self.logger.info(
                        f"Next cooldown extracted: {format_time_duration(next_cooldown)}"
                    )
                return result
            else:
                # Check if there's an error
                error_keywords = ["error", "failed", "invalid"]
                if any(keyword in response_text.lower() for keyword in error_keywords):
                    return {"success": False, "message": response_text}

                # Default to success if no clear error
                return {
                    "success": True,
                    "message": response_text if response_text else "Task completed",
                }

        except Exception as e:
            self.logger.error(f"Error in ready button flow: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def _handle_service_response(self, service: Dict) -> Dict:
        """
        Handle service response after submission

        Returns:
            Dictionary with 'success', 'message', and optionally 'wait_time'
        """
        try:
            menu_class = service["menu_class"]
            form_action = service["form_action"]

            # Wait for response
            random_delay(2, 3)

            # Find response container
            response_container = wait_for_element(self.driver, By.ID, form_action, timeout=10)

            if not response_container:
                return {"success": False, "message": "No response from server"}

            # Get response text
            response_text = response_container.text.strip()
            self.logger.debug(f"Response text: {response_text}")

            # Check for success indicators
            success_keywords = [
                "successfully",
                "sent",
                "completed",
                "added",
                "processing",
            ]

            # Check for error indicators
            error_keywords = [
                "error",
                "failed",
                "invalid",
                "not found",
            ]

            # Check for cooldown
            cooldown_keywords = [
                "please wait",
                "try again later",
                "minutes",
                "seconds",
                "hour",
            ]

            response_lower = response_text.lower()

            # Check for cooldown first (before success check)
            for keyword in cooldown_keywords:
                if keyword in response_lower:
                    wait_time = parse_time_remaining(response_text)
                    return {"success": False, "message": response_text, "wait_time": wait_time}

            # Check for errors
            for keyword in error_keywords:
                if keyword in response_lower:
                    return {"success": False, "message": response_text}

            # Check for success (might have cooldown message after success)
            is_success = False
            for keyword in success_keywords:
                if keyword in response_lower:
                    is_success = True
                    break

            # If response contains a send button (ready button), click it
            send_buttons = response_container.find_elements(
                By.CSS_SELECTOR, "button[type='submit']"
            )
            if send_buttons:
                # Look for the ready button with view count
                ready_button = None
                for btn in send_buttons:
                    btn_text = btn.text.strip()
                    # Check if button has numeric content (view count)
                    if re.search(r"\d{1,3}(,\d{3})*", btn_text):
                        ready_button = btn
                        break

                if ready_button:
                    self.logger.info(f"Found ready button with count: {ready_button.text.strip()}")
                    if safe_click(self.driver, ready_button):
                        random_delay(3, 5)
                        # Re-check response after clicking ready button
                        return self._handle_service_response(service)

            # If we had success keywords, return success with extracted cooldown
            if is_success:
                # Extract cooldown time from success message (e.g., "Please wait 3 minute(s) 50 seconds for your next submit!")
                next_cooldown = parse_time_remaining(response_text)
                result = {"success": True, "message": response_text}
                if next_cooldown:
                    result["next_cooldown"] = next_cooldown
                return result

            # Default: assume success if no errors found
            return {
                "success": True,
                "message": response_text if response_text else "Task submitted",
            }

        except Exception as e:
            self.logger.error(f"Error handling service response: {str(e)}")
            return {"success": False, "message": f"Error processing response: {str(e)}"}

    def get_available_services(self) -> List[Dict]:
        """Get list of available services"""
        try:
            services = []

            # Get ALL services (not limited by active_service)
            # All enabled services can be used
            services_to_check = self.config.all_services

            for service in services_to_check:
                button = wait_for_element(
                    self.driver, By.CSS_SELECTOR, f"button.{service['button_class']}", timeout=3
                )

                if button:
                    is_disabled = button.get_attribute("disabled")
                    status = "Unavailable" if is_disabled else "Available"

                    # For display purposes only - show which service is set as "active" in config
                    # But this doesn't restrict usage - all enabled services can be used
                    active_service = (
                        self.service_manager.get_active_service() if self.service_manager else None
                    )
                    is_marked_active = (
                        (active_service == service["name"]) if active_service else False
                    )

                    services.append(
                        {
                            "name": service["name"],
                            "status": status,
                            "enabled": service.get("enabled", False),
                            "active": is_marked_active,  # Just for display, doesn't restrict usage
                        }
                    )

            return services

        except Exception as e:
            self.logger.error(f"Error getting available services: {str(e)}")
            return []

    def print_statistics(self):
        """Print bot statistics"""
        from rich.text import Text

        uptime = datetime.now() - self.stats["started_at"]

        # Format uptime in a user-friendly way
        total_seconds = int(uptime.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            uptime_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            uptime_str = f"{minutes}m {seconds}s"
        else:
            uptime_str = f"{seconds}s"

        # Create formatted text without extra spacing
        stats_text = Text()
        stats_text.append(f"Uptime: {uptime_str}\n", style="white")
        stats_text.append(f"Captchas Solved: {self.stats['captchas_solved']}\n", style="white")
        stats_text.append(f"Tasks Completed: {self.stats['tasks_completed']}\n", style="white")
        stats_text.append(f"Tasks Failed: {self.stats['tasks_failed']}\n", style="white")

        if self.stats["services_used"]:
            stats_text.append("\nServices Used:\n", style="bold white")
            for service, count in self.stats["services_used"].items():
                stats_text.append(f"  • {service}: {count}\n", style="white")

        from rich import box
        from rich.align import Align
        from rich.panel import Panel

        console.print()
        console.print(
            Panel(
                Align.center(stats_text),
                title="[bold cyan]📊 Bot Statistics[/bold cyan]",
                title_align="center",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

    def _take_error_screenshot(self, prefix: str = "error"):
        """Take screenshot on error"""
        try:
            if self.driver:
                filepath = take_screenshot(self.driver, prefix=prefix)
                self.logger.info(f"Error screenshot saved: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")

    def close(self):
        """Close the bot and cleanup"""
        from rich import box
        from rich.align import Align
        from rich.live import Live
        from rich.panel import Panel
        from rich.text import Text

        status_messages = []

        def create_status_panel():
            """Create a panel with current status messages"""
            content = Text()
            for msg in status_messages:
                # Parse markup and add to Text object
                content.append(Text.from_markup(msg))
                content.append("\n")

            return Panel(
                Align.center(content)
                if content.plain
                else Align.center(Text("Closing...", style="yellow")),
                title="[bold yellow]🚪 Closing Bot[/bold yellow]",
                title_align="center",
                border_style="yellow",
                box=box.ROUNDED,
                padding=(1, 2),
            )

        try:
            with Live(create_status_panel(), console=console, refresh_per_second=4) as live:
                status_messages.append("[cyan]🔄 Closing bot...[/cyan]")
                live.update(create_status_panel())
                self.logger.info("Closing bot...")

                if self.driver:
                    status_messages.append("[dim]🌐 Closing browser...[/dim]")
                    live.update(create_status_panel())

                    self.driver.quit()

                    status_messages.append("[green]✓ Browser closed[/green]")
                    live.update(create_status_panel())
                    self.logger.info("Browser closed")

                self.session_active = False

                status_messages.append("[bold green]✓ Bot closed successfully![/bold green]")
                live.update(create_status_panel())
                self.logger.success("Bot closed successfully")

                random_delay(1, 1.5)  # Show success message briefly

        except Exception as e:
            status_messages.append(f"[red]✗ Error: {str(e)[:40]}...[/red]")
            random_delay(1.5, 2)
            self.logger.error(f"Error closing bot: {str(e)}")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
