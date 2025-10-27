"""
Main entry point for Zefoy Bot with interactive terminal menu
"""

import signal
import sys
from pathlib import Path
from typing import Optional

import questionary
from questionary import Style

from .bot import ZefoyBot
from .config import Config
from .logger import BotUI, console, get_logger, print_error, print_header, print_info, print_success
from .utils import validate_tiktok_url

# Custom style for questionary
custom_style = Style(
    [
        ("qmark", "fg:#673ab7 bold"),
        ("question", "bold"),
        ("answer", "fg:#2196f3 bold"),
        ("pointer", "fg:#673ab7 bold"),
        ("highlighted", "fg:#673ab7 bold"),
        ("selected", "fg:#2196f3"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]
)


class ZefoyBotCLI:
    """Interactive CLI for Zefoy Bot"""

    def __init__(self):
        """Initialize CLI"""
        self.config = Config()
        self.bot: Optional[ZefoyBot] = None
        self.running = True
        self.logger = get_logger(__name__)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        BotUI.print_warning_panel(
            "\nInterrupt received. Closing bot...\n" "Please wait while we clean up.",
            title="⚠ Interrupted",
        )
        self.cleanup()
        sys.exit(0)

    def run(self):
        """Run the interactive CLI"""
        import time

        from rich import box

        # Show beautiful centered welcome message
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        welcome_content = Text(justify="center")
        welcome_content.append("TikTok Automation Tool\n\n\n", style="bold white")
        welcome_content.append("🚀 Automate TikTok engagement\n", style="green")
        welcome_content.append("✨ Multiple services support\n", style="green")
        welcome_content.append("🎯 Target goals & continuous mode\n", style="green")
        welcome_content.append("⚡ Real-time cooldown tracking", style="green")

        # Clear screen before showing welcome
        console.clear()
        console.print("\n" * 3)
        console.print(
            Panel(
                Align.center(welcome_content),
                title="[bold cyan]👋 Welcome[/bold cyan]",
                title_align="center",
                box=box.ROUNDED,
                style="cyan",
                border_style="cyan",
                padding=(3, 4),
                expand=True,
            )
        )
        console.print("\n" * 3)

        # Wait 3 seconds for user to read welcome message
        time.sleep(3)

        # Clear screen before showing disclaimer
        console.clear()

        # Educational disclaimer
        disclaimer_content = Text(justify="center")
        disclaimer_content.append("⚠️  IMPORTANT DISCLAIMER ⚠️\n\n\n", style="bold yellow")
        disclaimer_content.append("Educational & Testing Purpose Only\n\n", style="bold white")

        disclaimer_content.append("By using this tool, you agree that:\n\n", style="cyan")
        disclaimer_content.append("• ", style="yellow")
        disclaimer_content.append("You will use it responsibly and ethically\n", style="dim white")
        disclaimer_content.append("• ", style="yellow")
        disclaimer_content.append("You understand the risks and consequences\n", style="dim white")
        disclaimer_content.append("• ", style="yellow")
        disclaimer_content.append(
            "You will comply with all applicable laws and TOS\n\n", style="dim white"
        )

        disclaimer_content.append(
            "Use at your own risk. No warranties provided.\n", style="bold red"
        )
        disclaimer_content.append("Not affiliated with TikTok or Zefoy.", style="dim white")

        console.print("\n" * 2)
        console.print(
            Panel(
                Align.center(disclaimer_content),
                title="[bold yellow]⚖️  Legal Notice[/bold yellow]",
                title_align="center",
                box=box.ROUNDED,
                style="yellow",
                border_style="yellow",
                padding=(3, 4),
                expand=True,
            )
        )
        console.print("\n" * 2)

        # Wait 5 seconds for user to read disclaimer
        time.sleep(5)

        # Clear screen
        console.clear()

        # Main menu loop
        while self.running:
            try:
                self._show_main_menu()
            except KeyboardInterrupt:
                BotUI.print_warning_panel("Exiting application...", title="👋 Goodbye")
                break
            except Exception as e:
                print_error(f"Error: {str(e)}")
                if not BotUI.ask_confirm("Continue?", default=True):
                    break

        self.cleanup()

    def _show_main_menu(self):
        """Show main menu"""
        from rich import box
        from rich.panel import Panel
        from rich.text import Text

        # Clear screen before showing main menu
        console.clear()

        # Create menu description panel
        menu_info = Text()
        menu_info.append("Select an action to perform:\n\n", style="cyan")
        menu_info.append("🚀 ", style="bold green")
        menu_info.append("Start Bot", style="bold white")
        menu_info.append(" - Launch the automation bot\n", style="dim white")

        menu_info.append("⚙️  ", style="bold yellow")
        menu_info.append("Configure Settings", style="bold white")
        menu_info.append(" - Adjust bot configuration\n", style="dim white")

        menu_info.append("📊 ", style="bold blue")
        menu_info.append("View Statistics", style="bold white")
        menu_info.append(" - Check bot performance\n", style="dim white")

        menu_info.append("📋 ", style="bold magenta")
        menu_info.append("View Available Services", style="bold white")
        menu_info.append(" - See service status\n", style="dim white")

        menu_info.append("❓ ", style="bold cyan")
        menu_info.append("Help", style="bold white")
        menu_info.append(" - Get help and documentation\n", style="dim white")

        menu_info.append("🚪 ", style="bold red")
        menu_info.append("Exit", style="bold white")
        menu_info.append(" - Close the application", style="dim white")

        console.print()
        console.print(
            Panel(
                menu_info,
                title="[bold cyan]📌 Main Menu Options[/bold cyan]",
                title_align="left",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()

        choices = [
            "🚀 Start Bot",
            "⚙️  Configure Settings",
            "📊 View Statistics",
            "📋 View Available Services",
            "❓ Help",
            "🚪 Exit",
        ]

        choice = questionary.select(
            "What would you like to do?", choices=choices, style=custom_style
        ).ask()

        # Clear screen after user selection
        console.clear()

        if choice == "🚀 Start Bot":
            self._start_bot_workflow()
        elif choice == "⚙️  Configure Settings":
            self._configure_settings()
        elif choice == "📊 View Statistics":
            self._view_statistics()
        elif choice == "📋 View Available Services":
            self._view_services()
        elif choice == "❓ Help":
            self._show_help()
        elif choice == "🚪 Exit":
            self.running = False

    def _start_bot_workflow(self):
        """Start bot workflow"""
        print_header("START BOT")

        # Get headless mode from config (already configured in Settings)
        headless = self.config.browser_headless

        # Check if display is available (VPS detection)
        import os
        import platform

        has_display = True
        if platform.system() in ["Linux", "Darwin"]:
            display = os.environ.get("DISPLAY", "").strip()
            if not display:
                has_display = False

        # Show info about current settings
        if not headless and not has_display:
            browser_info = "Browser Mode: Headless (Auto - No Display Detected)"
        else:
            browser_info = f"Browser Mode: {'Headless (Hidden)' if headless else 'Visible'}"

        if self.config.use_adblock:
            browser_info += "\nAdBlock: Enabled"
        if self.config.get("browser.disable_images", False):
            browser_info += "\nImages: Disabled"

        BotUI.print_info_panel(browser_info, title="🌐 Browser Settings")

        # Initialize bot
        BotUI.print_info_panel(
            "Initializing bot...\n" "Please wait while the browser starts.", title="🚀 Starting Bot"
        )

        self.bot = ZefoyBot(self.config, headless=headless)

        if not self.bot.start():
            BotUI.print_error_panel(
                "Failed to start bot.\n" "Please check the logs for details.",
                title="❌ Startup Failed",
            )
            self.bot = None
            return

        # Clear screen before showing success panel
        console.clear()

        BotUI.print_success_panel(
            "Bot started successfully!\n" "Ready to execute services.", title="✓ Bot Ready"
        )

        # Service selection loop
        while self.bot and self.bot.session_active:
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "▶️  Execute Service",
                    "📊 View Statistics",
                    "🎯 View Target Goals Progress",
                    "🔄 Refresh Page",
                    "◀️  Back to Main Menu",
                ],
                style=custom_style,
            ).ask()

            # Clear screen after user selection
            console.clear()

            if action == "▶️  Execute Service":
                self._execute_service_workflow()
            elif action == "📊 View Statistics":
                if self.bot:
                    self.bot.print_statistics()
            elif action == "🎯 View Target Goals Progress":
                self._view_target_progress()
            elif action == "🔄 Refresh Page":
                self._refresh_bot()
            elif action == "◀️  Back to Main Menu":
                break

        # Close bot
        if self.bot:
            self.bot.close()
            self.bot = None

    def _execute_service_workflow(self):
        """Execute service workflow"""
        if not self.bot or not self.bot.session_active:
            print_error("Bot is not running")
            return

        print_header("EXECUTE SERVICE")

        # Known offline services (based on Zefoy website)
        offline_services = ["Followers", "Live Stream"]

        # Get all services - all enabled services can be used
        all_services = self.config.all_services
        available_services = all_services

        # Get active service for display purposes only (doesn't restrict usage)
        active_service = None
        if self.bot.service_manager:
            active_service = self.bot.service_manager.get_active_service()

            if active_service:
                BotUI.print_info_panel(
                    f"ℹ️ Active Service Marker: {active_service}\n"
                    f"📊 Note: All enabled services can be used!\n"
                    f"    'Active' is just a marker, not a restriction.",
                    title="ℹ Service Info",
                )

        if not available_services:
            BotUI.print_warning_panel("No services are configured!", title="⚠ No Services")
            return

        # Service selection with status labels
        service_choices = []
        service_map = {}  # Map display name to actual name

        for service in available_services:
            service_name = service["name"]
            enabled = service.get("enabled", False)
            is_offline = service_name in offline_services
            is_active_marker = active_service and service_name == active_service

            # Create display name with status
            if is_offline:
                display_name = f"{service_name} [❌ OFFLINE]"
            elif not enabled:
                display_name = f"{service_name} [⚠️ DISABLED]"
            elif is_active_marker:
                display_name = f"{service_name} [🎯 Marked]"  # Just a marker, all can be used
            else:
                display_name = f"{service_name} [✅ Available]"

            # Add to choices - all can be selected and used
            service_choices.append(display_name)
            service_map[display_name] = service_name

        service_choices.append("◀️  Cancel")

        selected_display = questionary.select(
            "Select a service:", choices=service_choices, style=custom_style
        ).ask()

        if selected_display == "◀️  Cancel":
            return

        # Get actual service name
        service_name = service_map.get(selected_display, selected_display)

        # Check if service is offline
        if service_name in offline_services:
            BotUI.print_warning_panel(
                f"{service_name} is currently OFFLINE on Zefoy.\n" f"This service may not work!",
                title="⚠ Service Offline",
            )

            if not BotUI.ask_confirm("Continue anyway?", default=False):
                return

        # Check if service is disabled
        service_config = next((s for s in all_services if s["name"] == service_name), None)
        if service_config and not service_config.get("enabled", False):
            BotUI.print_warning_panel(
                f"{service_name} is DISABLED in configuration.\n"
                f"Enable it in Settings first for best results.",
                title="⚠ Service Disabled",
            )

            if not BotUI.ask_confirm("Continue anyway?", default=False):
                return

        # Note: No longer checking active_service mismatch
        # All enabled services can be used regardless of "active" marker

        # Get video URL
        video_url = questionary.text(
            "Enter TikTok video URL:",
            validate=lambda text: validate_tiktok_url(text) or "Invalid TikTok URL",
            style=custom_style,
        ).ask()

        if not video_url:
            return

        # Ask for mode
        mode = questionary.select(
            "Select execution mode:",
            choices=[
                "Manual Executions (set number of times to execute)",
                "Target Amount (set target views/hearts/etc count)",
                "Goal Mode (use target from config)",
            ],
            style=custom_style,
        ).ask()

        use_target_goals = "Goal Mode" in mode
        use_target_amount = "Target Amount" in mode

        if use_target_goals:
            # Show target from config
            if self.bot.target_tracker:
                progress = self.bot.target_tracker.get_progress(service_name)
                BotUI.print_info_panel(
                    f"Target Goal: {progress['target']:,}\n"
                    f"Current Progress: {progress['current']:,}\n"
                    f"Remaining: {progress['remaining']:,}\n"
                    f"Per Execution: ~{progress['per_execution']:,}",
                    title=f"🎯 {service_name} Goal",
                )

            target = None  # Will be calculated by bot
            target_amount = None
        elif use_target_amount:
            # Ask for target amount (views, hearts, etc)
            amount_str = questionary.text(
                f"Enter target {service_name.lower()} amount (e.g., 10000):",
                validate=lambda text: text.replace(",", "").isdigit()
                and int(text.replace(",", "")) > 0
                or "Must be a positive number",
                style=custom_style,
            ).ask()

            target_amount = int(amount_str.replace(",", "")) if amount_str else 1000

            # Get estimated amount per execution from config
            service_key = service_name.lower().replace(" ", "_")
            per_execution_config = self.config.get("service_targets.per_execution", {})
            avg_per_exec = per_execution_config.get(service_key, 100)  # Default 100 if not found

            # Calculate estimated executions based on real data
            estimated_execs = (target_amount // avg_per_exec) + 1

            BotUI.print_info_panel(
                f"Target Amount: {target_amount:,} {service_name.lower()}\n"
                f"Estimated Executions: ~{estimated_execs}\n"
                f"(Based on ~{avg_per_exec} per execution)\n\n"
                f"Bot will automatically track progress and stop when target is reached!",
                title=f"🎯 {service_name} Target",
            )

            target = None  # Will run until target_amount reached
        else:
            # Ask for manual execution count
            target_str = questionary.text(
                "How many times to execute? (default: 1):",
                default="1",
                validate=lambda text: text.isdigit()
                and int(text) > 0
                or "Must be a positive number",
                style=custom_style,
            ).ask()

            target = int(target_str) if target_str else 1
            target_amount = None

        # Ask for auto-retry
        auto_retry = questionary.confirm(
            "Auto-retry when cooldown is detected?", default=True, style=custom_style
        ).ask()

        # Confirm execution
        if use_target_goals:
            BotUI.print_info_panel(
                f"Service: {service_name}\n"
                f"Video URL: {video_url}\n"
                f"Mode: Goal Mode (Auto-calculated)\n"
                f"Auto-Retry: {'Yes' if auto_retry else 'No'}",
                title="🔍 Confirm Execution",
            )
        elif use_target_amount:
            BotUI.print_info_panel(
                f"Service: {service_name}\n"
                f"Video URL: {video_url}\n"
                f"Mode: Target Amount\n"
                f"Target: {target_amount:,} {service_name.lower()}\n"
                f"Auto-Retry: {'Yes' if auto_retry else 'No'}",
                title="🔍 Confirm Execution",
            )
        else:
            BotUI.print_info_panel(
                f"Service: {service_name}\n"
                f"Video URL: {video_url}\n"
                f"Mode: Manual Executions\n"
                f"Executions: {target}\n"
                f"Auto-Retry: {'Yes' if auto_retry else 'No'}",
                title="🔍 Confirm Execution",
            )

        confirm = BotUI.ask_confirm("Execute this service?", default=True)

        if confirm:
            BotUI.print_info_panel(
                f"Executing service: {service_name}\n" f"Please wait...", title="⏳ Processing"
            )

            success = self.bot.execute_service(
                service_name,
                video_url,
                target=target,
                auto_retry=auto_retry,
                use_target_goals=use_target_goals,
                target_amount=target_amount,
            )

            if success:
                BotUI.print_success_panel(
                    f"Service: {service_name}\n" f"Status: Completed successfully!",
                    title="✓ Success",
                )
            else:
                BotUI.print_error_panel(
                    f"Service: {service_name}\n"
                    f"Status: Execution failed.\n"
                    f"Check logs for details.",
                    title="✗ Failed",
                )

    def _configure_settings(self):
        """Configure bot settings"""
        from rich import box
        from rich.panel import Panel
        from rich.text import Text

        # Clear screen before showing settings
        console.clear()

        # Create settings description panel
        settings_info = Text()
        settings_info.append("Configure bot settings and preferences:\n\n", style="cyan")

        settings_info.append("🌐 ", style="bold cyan")
        settings_info.append("Browser Settings", style="bold white")
        settings_info.append(" - Headless, AdBlock, User Agent\n", style="dim white")

        settings_info.append("⏱️ ", style="bold yellow")
        settings_info.append("Timeout Settings", style="bold white")
        settings_info.append(" - Page load, element wait, delays\n", style="dim white")

        settings_info.append("🔐 ", style="bold green")
        settings_info.append("Captcha & OCR Settings", style="bold white")
        settings_info.append(" - FAST mode / AGGRESSIVE mode, OCR configs\n", style="dim white")

        settings_info.append("📝 ", style="bold blue")
        settings_info.append("Logging Settings", style="bold white")
        settings_info.append(" - Log level (MAIN/DEBUG/INFO), file output\n", style="dim white")

        settings_info.append("🔄 ", style="bold yellow")
        settings_info.append("Retry Settings", style="bold white")
        settings_info.append(" - Auto-retry, max attempts\n", style="dim white")

        settings_info.append("⚙️ ", style="bold cyan")
        settings_info.append("Service Execution", style="bold white")
        settings_info.append(" - Countdown, single mode\n", style="dim white")

        settings_info.append("🎯 ", style="bold green")
        settings_info.append("Service Targets", style="bold white")
        settings_info.append(" - Goal mode targets per service\n", style="dim white")

        settings_info.append("🔌 ", style="bold red")
        settings_info.append("Enable/Disable Services", style="bold white")
        settings_info.append(" - Toggle services on/off\n", style="dim white")

        settings_info.append("📍 ", style="bold magenta")
        settings_info.append("Set Active Service", style="bold white")
        settings_info.append(" - Single service mode marker", style="dim white")

        console.print()
        console.print(
            Panel(
                settings_info,
                title="[bold yellow]⚙️  Configuration Options[/bold yellow]",
                title_align="left",
                border_style="yellow",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
        console.print()

        settings_menu = [
            "🌐 Browser Settings",
            "⏱️ Timeout Settings",
            "🔐 Captcha & OCR Settings",
            "📝 Logging Settings",
            "🔄 Retry Settings",
            "⚙️ Service Execution Settings",
            "🎯 Service Target Goals",
            "🔌 Enable/Disable Services",
            "📍 Set Active Service (Single Mode)",
            "◀️ Back",
        ]

        choice = questionary.select(
            "What would you like to configure?", choices=settings_menu, style=custom_style
        ).ask()

        # Clear screen after user selection
        console.clear()

        if choice == "🌐 Browser Settings":
            self._configure_browser()
        elif choice == "⏱️ Timeout Settings":
            self._configure_timeouts()
        elif choice == "🔐 Captcha & OCR Settings":
            self._configure_captcha_and_ocr()
        elif choice == "📝 Logging Settings":
            self._configure_logging()
        elif choice == "🔄 Retry Settings":
            self._configure_retry()
        elif choice == "⚙️ Service Execution Settings":
            self._configure_service_execution()
        elif choice == "🎯 Service Target Goals":
            self._configure_service_targets()
        elif choice == "🔌 Enable/Disable Services":
            self._configure_services()
        elif choice == "📍 Set Active Service (Single Mode)":
            self._configure_active_service()

    def _generate_user_agent(self, os_type):
        """Generate valid user agent based on OS type"""
        import random

        # Chrome versions (recent)
        chrome_versions = ["120.0.0.0", "121.0.0.0", "122.0.0.0", "123.0.0.0", "124.0.0.0"]
        chrome_ver = random.choice(chrome_versions)

        user_agents = {
            "Windows": [
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
                f"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
                f"Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
            ],
            "macOS": [
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
                f"Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
            ],
            "Linux": [
                f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
                f"Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36",
            ],
            "Android": [
                f"Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36",
                f"Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Mobile Safari/537.36",
            ],
            "iOS": [
                f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{chrome_ver} Mobile/15E148 Safari/604.1",
                f"Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{chrome_ver} Mobile/15E148 Safari/604.1",
            ],
        }

        return random.choice(user_agents.get(os_type, user_agents["Windows"]))

    def _configure_browser(self):
        """Configure browser settings"""
        print_header("BROWSER SETTINGS")

        # Headless mode
        headless = questionary.confirm(
            "Run in headless mode? (No browser UI)",
            default=self.config.browser_headless,
            style=custom_style,
        ).ask()

        # Use adblock
        use_adblock = questionary.confirm(
            "Use AdBlock extension? (Faster loading)",
            default=self.config.use_adblock,
            style=custom_style,
        ).ask()

        # Disable images
        disable_images = questionary.confirm(
            "Disable images? (Even faster loading)",
            default=self.config.get("browser.disable_images", False),
            style=custom_style,
        ).ask()

        # Window size
        current_size = self.config.get("browser.window_size", "1920,1080")
        window_size = questionary.text(
            "Browser window size (width,height):", default=current_size, style=custom_style
        ).ask()

        # User agent configuration
        if BotUI.ask_confirm("Configure User Agent?", default=False):
            ua_choice = questionary.select(
                "How would you like to set User Agent?",
                choices=["🎲 Auto-generate (Recommended)", "✍️  Manual input", "↩️  Keep current"],
                style=custom_style,
            ).ask()

            if ua_choice == "🎲 Auto-generate (Recommended)":
                # Choose OS
                os_type = questionary.select(
                    "Select Operating System:",
                    choices=["🪟 Windows", "🍎 macOS", "🐧 Linux", "📱 Android", "📲 iOS"],
                    style=custom_style,
                ).ask()

                # Map emoji choice to OS type
                os_map = {
                    "🪟 Windows": "Windows",
                    "🍎 macOS": "macOS",
                    "🐧 Linux": "Linux",
                    "📱 Android": "Android",
                    "📲 iOS": "iOS",
                }

                selected_os = os_map[os_type]
                user_agent = self._generate_user_agent(selected_os)

                # Show generated user agent
                from rich import box
                from rich.panel import Panel
                from rich.text import Text

                ua_display = Text()
                ua_display.append("Generated User Agent:\n\n", style="bold cyan")
                ua_display.append(user_agent, style="green")

                console.print()
                console.print(
                    Panel(
                        ua_display,
                        title=f"[bold green]✓ {selected_os} User Agent[/bold green]",
                        title_align="left",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2),
                    )
                )
                console.print()

                if BotUI.ask_confirm("Use this User Agent?", default=True):
                    self.config.set("browser.user_agent", user_agent)
                    print_success(f"User Agent set to {selected_os} Chrome")

            elif ua_choice == "✍️  Manual input":
                current_ua = self.config.get("browser.user_agent", "Mozilla/5.0...")
                user_agent = questionary.text(
                    "User Agent string:", default=current_ua, style=custom_style
                ).ask()

                if user_agent and user_agent != current_ua:
                    self.config.set("browser.user_agent", user_agent)
                    print_success("User Agent updated manually")
            # else: Keep current (do nothing)

        # Save settings
        self.config.set("browser.headless", headless)
        self.config.set("browser.use_adblock", use_adblock)
        self.config.set("browser.disable_images", disable_images)
        self.config.set("browser.window_size", window_size)

        if BotUI.ask_confirm("Save changes to config.yaml?", default=True):
            self.config.save_config()
            print_success("Browser settings saved successfully!")
        else:
            print_info("Changes discarded")

    def _configure_timeouts(self):
        """Configure timeout settings"""
        print_header("TIMEOUT SETTINGS")

        timeouts = {
            "page_load": "Page Load Timeout (seconds)",
            "element_wait": "Element Wait Timeout (seconds)",
            "captcha_solve": "Captcha Solve Timeout (seconds)",
            "between_actions": "Delay Between Actions (seconds)",
            "retry_delay": "Retry Delay on Failure (seconds)",
        }

        for key, label in timeouts.items():
            current = self.config.get(f"timeouts.{key}", 30)
            value = questionary.text(
                f"{label}:",
                default=str(current),
                validate=lambda text: text.isdigit() or "Must be a number",
                style=custom_style,
            ).ask()

            if value:
                self.config.set(f"timeouts.{key}", int(value))

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Timeout settings saved!")

    def _configure_captcha_and_ocr(self):
        """Configure captcha and OCR settings in unified menu"""
        while True:
            # Clear screen before showing menu
            console.clear()

            print_header("CAPTCHA & OCR SETTINGS")

            # Get current mode
            fast_mode_enabled = self.config.get("captcha.fast_mode", True)
            auto_solve_enabled = self.config.get("captcha.auto_solve", False)
            manual_input_enabled = self.config.get("captcha.manual_input", True)
            aggressive_preprocessing = self.config.get(
                "captcha.ocr_advanced.aggressive_preprocessing", False
            )
            aggressive_configs = self.config.get(
                "captcha.ocr_advanced.aggressive_ocr_configs", False
            )

            # Display current status
            from rich import box
            from rich.panel import Panel
            from rich.text import Text

            status_content = Text()
            status_content.append("Current Configuration:\n\n", style="bold white")

            # Auto-solve status
            if auto_solve_enabled:
                status_content.append("✅ ", style="green")
                status_content.append("Auto-solve: ENABLED\n", style="white")
            else:
                status_content.append("❌ ", style="red")
                status_content.append("Auto-solve: DISABLED\n", style="white")

            # Manual input status
            if manual_input_enabled:
                status_content.append("✅ ", style="green")
                status_content.append("Manual Input: ENABLED (fallback)\n", style="white")
            else:
                status_content.append("❌ ", style="red")
                status_content.append("Manual Input: DISABLED\n", style="white")

            # Mode status
            if fast_mode_enabled:
                status_content.append("⚡ ", style="yellow")
                status_content.append("Mode: FAST (~10-20s per try)\n", style="bold yellow")
                status_content.append("   • 5 preprocessing methods\n", style="dim white")
                status_content.append("   • 5 OCR configs\n", style="dim white")
                status_content.append("   • ~30 attempts per captcha image\n", style="dim white")
                status_content.append(
                    "   • 2 OCR retries before manual input\n\n", style="dim white"
                )
            else:
                status_content.append("🐌 ", style="blue")
                status_content.append("Mode: AGGRESSIVE (~3-5min per try)\n", style="bold blue")
                if aggressive_preprocessing:
                    status_content.append("   • 12 preprocessing methods\n", style="dim white")
                else:
                    status_content.append("   • 5 preprocessing methods\n", style="dim white")
                if aggressive_configs:
                    status_content.append("   • 26 OCR configs\n", style="dim white")
                else:
                    status_content.append("   • 5 OCR configs\n", style="dim white")
                total_attempts = 60 if aggressive_preprocessing and aggressive_configs else 25
                if aggressive_preprocessing and aggressive_configs:
                    total_attempts = 312
                elif aggressive_preprocessing or aggressive_configs:
                    total_attempts = 120
                status_content.append(
                    f"   • ~{total_attempts} attempts per captcha image\n", style="dim white"
                )
                status_content.append(
                    "   • 5 OCR retries before manual input\n\n", style="dim white"
                )

            console.print()
            console.print(
                Panel(
                    status_content,
                    title="[bold cyan]📊 Current Status[/bold cyan]",
                    title_align="left",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
            console.print()

            # Menu choices
            captcha_menu = [
                "🤖 Auto-solve Settings (OCR)",
                "⌨️  Manual Captcha Input Settings",
                "⚡ FAST Mode Settings (Quick & Optimized)",
                "🐌 AGGRESSIVE Mode Settings (Thorough & Slower)",
                "◀️  Back to Settings Menu",
            ]

            choice = questionary.select(
                "What would you like to configure?", choices=captcha_menu, style=custom_style
            ).ask()

            # Clear screen after selection
            console.clear()

            if choice == "🤖 Auto-solve Settings (OCR)":
                self._configure_auto_solve()
            elif choice == "⌨️  Manual Captcha Input Settings":
                self._configure_manual_input()
            elif choice == "⚡ FAST Mode Settings (Quick & Optimized)":
                self._configure_fast_mode()
            elif choice == "🐌 AGGRESSIVE Mode Settings (Thorough & Slower)":
                self._configure_aggressive_mode()
            elif choice == "◀️  Back to Settings Menu":
                break

    def _configure_auto_solve(self):
        """Configure auto-solve (OCR) settings"""
        print_header("AUTO-SOLVE (OCR) SETTINGS")

        current_auto_solve = self.config.get("captcha.auto_solve", False)

        BotUI.print_info_panel(
            "🤖 AUTO-SOLVE (OCR) - Automatic Captcha Detection\n\n"
            "When enabled, the bot will automatically attempt to solve captchas using OCR:\n"
            "  • Uses Tesseract OCR engine\n"
            "  • Multiple preprocessing methods\n"
            "  • Multiple OCR configurations\n"
            "  • Retries based on mode (FAST: 2x, AGGRESSIVE: 5x)\n"
            "  • Falls back to manual input if all attempts fail\n\n"
            f"Current Status: {'✅ ENABLED' if current_auto_solve else '❌ DISABLED'}",
            title="🤖 About Auto-solve",
        )

        console.print()

        auto_solve = questionary.confirm(
            "Enable automatic captcha solving with OCR?",
            default=current_auto_solve,
            style=custom_style,
        ).ask()

        # Update config
        self.config.set("captcha.auto_solve", auto_solve)
        self.config.save_config()

        if auto_solve:
            print_success("Auto-solve ENABLED! OCR will attempt to solve captchas automatically.")
        else:
            print_success("Auto-solve DISABLED! You will need to solve captchas manually.")
            BotUI.print_warning_panel(
                "⚠️ Warning: With auto-solve disabled, you must enable manual input\n"
                "or the bot won't be able to solve captchas at all!",
                title="⚠️ Important",
            )

    def _configure_manual_input(self):
        """Configure manual captcha input settings"""
        from rich import box
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        print_header("MANUAL CAPTCHA INPUT SETTINGS")

        current_manual_input = self.config.get("captcha.manual_input", True)
        current_auto_solve = self.config.get("captcha.auto_solve", False)
        current_save_image = self.config.get("captcha.save_image", True)
        current_auto_open = self.config.get("captcha.auto_open_image", False)
        current_upload_cloud = self.config.get("captcha.upload_to_cloud", True)
        current_cloud_url = self.config.get("captcha.cloud_uploader_url", "https://uploader.sh")

        # Show current configuration
        config_text = Text()
        config_text.append("Current Configuration:\n\n", style="bold cyan")
        config_text.append(f"Manual Input: ", style="white")
        config_text.append(
            f"{'✅ ENABLED' if current_manual_input else '❌ DISABLED'}\n",
            style="green" if current_manual_input else "red",
        )
        config_text.append(f"Auto-solve OCR: ", style="white")
        config_text.append(
            f"{'✅ ON' if current_auto_solve else '❌ OFF'}\n",
            style="green" if current_auto_solve else "red",
        )
        config_text.append(f"Save Images: ", style="white")
        config_text.append(
            f"{'✅ YES' if current_save_image else '❌ NO'}\n",
            style="green" if current_save_image else "red",
        )

        if current_upload_cloud:
            config_text.append(f"Display Mode: ", style="white")
            config_text.append("☁️  Cloud/VPS Mode\n", style="cyan bold")
        elif current_auto_open:
            config_text.append(f"Display Mode: ", style="white")
            config_text.append("🖥️  Desktop Mode\n", style="green bold")
        else:
            config_text.append(f"Display Mode: ", style="white")
            config_text.append("📁 Manual Mode\n", style="yellow bold")

        console.print()
        console.print(
            Panel(
                Align.center(config_text),
                title="[bold yellow]📋 Current Settings[/bold yellow]",
                title_align="center",
                box=box.ROUNDED,
                style="yellow",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        console.print()

        # Main settings
        manual_input = questionary.confirm(
            "Enable manual captcha input?", default=current_manual_input, style=custom_style
        ).ask()

        save_image = questionary.confirm(
            "Save captcha images to screenshots folder?",
            default=current_save_image,
            style=custom_style,
        ).ask()

        # Display mode selection
        console.print()
        mode_info = Text()
        mode_info.append("Choose Captcha Display Mode:\n\n", style="bold cyan")
        mode_info.append("☁️  Cloud/VPS Mode\n", style="bold cyan")
        mode_info.append("   • Upload captcha to cloud service\n", style="dim white")
        mode_info.append("   • Access via URL from any device\n", style="dim white")
        mode_info.append("   • Perfect for VPS/remote servers\n\n", style="dim white")
        mode_info.append("🖥️  Desktop Mode\n", style="bold green")
        mode_info.append("   • Auto-open with image viewer\n", style="dim white")
        mode_info.append("   • For local desktop usage\n", style="dim white")
        mode_info.append("   • Not suitable for VPS\n\n", style="dim white")
        mode_info.append("📁 Manual Mode\n", style="bold yellow")
        mode_info.append("   • Save to screenshots folder\n", style="dim white")
        mode_info.append("   • Check folder manually", style="dim white")

        console.print(
            Panel(
                Align.center(mode_info),
                title="[bold cyan]🎯 Display Mode Options[/bold cyan]",
                title_align="center",
                box=box.ROUNDED,
                style="cyan",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print()

        display_mode = questionary.select(
            "Select captcha display mode:",
            choices=[
                "☁️  Cloud/VPS Mode (Recommended for servers)",
                "🖥️  Desktop Mode (Auto-open image viewer)",
                "📁 Manual Mode (Check screenshots folder)",
            ],
            default=(
                "☁️  Cloud/VPS Mode (Recommended for servers)"
                if current_upload_cloud
                else "🖥️  Desktop Mode (Auto-open image viewer)"
                if current_auto_open
                else "📁 Manual Mode (Check screenshots folder)"
            ),
            style=custom_style,
        ).ask()

        # Set upload_to_cloud and auto_open_image based on mode
        upload_to_cloud = False
        auto_open_image = False

        if "Cloud/VPS" in display_mode:
            upload_to_cloud = True
            auto_open_image = False

            # Ask for cloud uploader URL
            console.print()
            change_url = questionary.confirm(
                f"Cloud uploader URL: {current_cloud_url}\nChange URL?",
                default=False,
                style=custom_style,
            ).ask()

            if change_url:
                cloud_url = questionary.text(
                    "Enter cloud uploader URL:",
                    default=current_cloud_url,
                    style=custom_style,
                ).ask()
                self.config.set("captcha.cloud_uploader_url", cloud_url)

        elif "Desktop" in display_mode:
            upload_to_cloud = False
            auto_open_image = True
        else:
            upload_to_cloud = False
            auto_open_image = False

        # OCR mode selection
        console.print()
        manual_only_mode = False
        if manual_input:
            BotUI.print_info_panel(
                "Choose your preferred mode:\n\n"
                "• Hybrid Mode: OCR first, manual as fallback (recommended)\n"
                "• Manual Only: Always manual, no OCR (faster if OCR doesn't work)",
                title="💡 OCR Mode Selection",
            )
            console.print()

            manual_only_mode = questionary.confirm(
                "Use Manual Only Mode? (Disable auto-solve OCR)",
                default=(not current_auto_solve),
                style=custom_style,
            ).ask()

        # Update config
        self.config.set("captcha.manual_input", manual_input)
        self.config.set("captcha.save_image", save_image)
        self.config.set("captcha.auto_open_image", auto_open_image)
        self.config.set("captcha.upload_to_cloud", upload_to_cloud)

        # Update auto_solve based on mode
        if manual_input and manual_only_mode:
            # Manual only mode - disable auto_solve
            self.config.set("captcha.auto_solve", False)
        elif manual_input and not manual_only_mode:
            # Hybrid mode - enable auto_solve if not already
            if not current_auto_solve:
                BotUI.print_info_panel(
                    "💡 Hybrid mode requires auto-solve to be enabled.\n"
                    "Auto-solve will be enabled automatically.",
                    title="💡 Info",
                )
                self.config.set("captcha.auto_solve", True)

        self.config.save_config()

        # Show summary
        console.print()
        summary_text = Text()
        summary_text.append("Configuration Saved!\n\n", style="bold green")
        summary_text.append(f"Manual Input: ", style="white")
        summary_text.append(
            f"{'✅ ENABLED' if manual_input else '❌ DISABLED'}\n",
            style="green" if manual_input else "red",
        )
        summary_text.append(f"Auto-solve OCR: ", style="white")
        summary_text.append(
            f"{'✅ ON' if (not manual_only_mode and manual_input) else '❌ OFF'}\n",
            style="green" if (not manual_only_mode and manual_input) else "red",
        )
        summary_text.append(f"Save Images: ", style="white")
        summary_text.append(
            f"{'✅ YES' if save_image else '❌ NO'}\n\n", style="green" if save_image else "red"
        )

        if upload_to_cloud:
            summary_text.append("Display Mode: ", style="white")
            summary_text.append("☁️  Cloud/VPS Mode\n", style="cyan bold")
            summary_text.append("Captcha will be uploaded to cloud", style="dim white")
        elif auto_open_image:
            summary_text.append("Display Mode: ", style="white")
            summary_text.append("🖥️  Desktop Mode\n", style="green bold")
            summary_text.append("Captcha will auto-open in viewer", style="dim white")
        else:
            summary_text.append("Display Mode: ", style="white")
            summary_text.append("📁 Manual Mode\n", style="yellow bold")
            summary_text.append("Check screenshots folder manually", style="dim white")

        console.print(
            Panel(
                Align.center(summary_text),
                title="[bold green]✓ Configuration Summary[/bold green]",
                title_align="center",
                box=box.ROUNDED,
                style="green",
                border_style="green",
                padding=(1, 2),
            )
        )

    def _configure_fast_mode(self):
        """Configure FAST mode settings"""
        print_header("FAST MODE SETTINGS")

        BotUI.print_info_panel(
            "⚡ FAST MODE - Quick & Optimized OCR\n\n"
            "Optimized for speed with balanced accuracy:\n"
            "  • Processing time: ~10-20 seconds per try\n"
            "  • 5 preprocessing methods\n"
            "  • 5 OCR configurations\n"
            "  • ~30 attempts per captcha image\n"
            "  • 2 OCR retries before manual input\n"
            "  • Recommended for most users\n\n"
            "Configure basic captcha settings below:",
            title="⚡ About FAST Mode",
        )

        console.print()

        # Basic captcha settings
        auto_solve = questionary.confirm(
            "Enable automatic captcha solving? (OCR)",
            default=self.config.get("captcha.auto_solve", False),
            style=custom_style,
        ).ask()

        manual_input = questionary.confirm(
            "Enable manual captcha input? (Fallback if OCR fails)",
            default=self.config.get("captcha.manual_input", True),
            style=custom_style,
        ).ask()

        save_image = questionary.confirm(
            "Save captcha images to screenshots/?",
            default=self.config.get("captcha.save_image", True),
            style=custom_style,
        ).ask()

        auto_open_image = questionary.confirm(
            "Auto-open captcha image? (Useful for headless mode)",
            default=self.config.get("captcha.auto_open_image", True),
            style=custom_style,
        ).ask()

        debug_mode = questionary.confirm(
            "Enable debug mode? (Save all OCR preprocessing images)",
            default=self.config.get("captcha.debug_mode", False),
            style=custom_style,
        ).ask()

        # Save settings
        self.config.set("captcha.auto_solve", auto_solve)
        self.config.set("captcha.fast_mode", True)  # Force FAST mode
        self.config.set("captcha.manual_input", manual_input)
        self.config.set("captcha.save_image", save_image)
        self.config.set("captcha.auto_open_image", auto_open_image)
        self.config.set("captcha.debug_mode", debug_mode)

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("FAST mode settings saved!")

            BotUI.print_info_panel(
                "✓ FAST mode is now ACTIVE\n\n"
                "Your captcha will be solved quickly (~10-20s per try) with:\n"
                "  • 5 preprocessing methods\n"
                "  • 5 OCR configs\n"
                "  • ~30 attempts per captcha image\n"
                "  • 2 OCR retries before manual input\n\n"
                "This is the recommended mode for most users.",
                title="⚡ FAST Mode Active",
            )

            console.print()
            console.print("[bold green]✓ Press Enter to continue...[/bold green]")
            input()

    def _configure_aggressive_mode(self):
        """Configure AGGRESSIVE mode settings"""
        print_header("AGGRESSIVE MODE SETTINGS")

        BotUI.print_warning_panel(
            "🐌 AGGRESSIVE MODE - Thorough & Slower OCR\n\n"
            "Maximum attempts with longer processing time:\n"
            "  • Processing time: ~3-5 minutes per try\n"
            "  • Up to 12 preprocessing methods\n"
            "  • Up to 26 OCR configurations\n"
            "  • 300+ attempts per captcha image\n"
            "  • 5 OCR retries before manual input\n"
            "  • Use when FAST mode fails\n\n"
            "⚠️  This mode is MUCH SLOWER but more thorough.\n"
            "Only use if you have difficult captchas.",
            title="⚠️ About AGGRESSIVE Mode",
        )

        console.print()

        # Confirm switch to aggressive
        if not BotUI.ask_confirm("Switch to AGGRESSIVE mode?", default=False):
            print_info("Staying in current mode.")
            console.print()
            console.print("[bold green]✓ Press Enter to continue...[/bold green]")
            input()
            return

        # Basic captcha settings
        auto_solve = questionary.confirm(
            "Enable automatic captcha solving? (OCR)",
            default=self.config.get("captcha.auto_solve", False),
            style=custom_style,
        ).ask()

        manual_input = questionary.confirm(
            "Enable manual captcha input? (Fallback if OCR fails)",
            default=self.config.get("captcha.manual_input", True),
            style=custom_style,
        ).ask()

        save_image = questionary.confirm(
            "Save captcha images to screenshots/?",
            default=self.config.get("captcha.save_image", True),
            style=custom_style,
        ).ask()

        auto_open_image = questionary.confirm(
            "Auto-open captcha image? (Useful for headless mode)",
            default=self.config.get("captcha.auto_open_image", True),
            style=custom_style,
        ).ask()

        debug_mode = questionary.confirm(
            "Enable debug mode? (Save all OCR preprocessing images)",
            default=self.config.get("captcha.debug_mode", False),
            style=custom_style,
        ).ask()

        console.print()
        print_header("ADVANCED OCR SETTINGS")

        horizontal_reading = questionary.confirm(
            "Enable horizontal reading? (Left→Right like humans)",
            default=self.config.get("captcha.ocr_advanced.horizontal_reading", True),
            style=custom_style,
        ).ask()

        handle_uneven_text = questionary.confirm(
            "Handle uneven/naik-turun text?",
            default=self.config.get("captcha.ocr_advanced.handle_uneven_text", True),
            style=custom_style,
        ).ask()

        aggressive_preprocessing = questionary.confirm(
            "Use aggressive preprocessing? (12 methods vs 5)",
            default=self.config.get("captcha.ocr_advanced.aggressive_preprocessing", True),
            style=custom_style,
        ).ask()

        aggressive_ocr_configs = questionary.confirm(
            "Use aggressive OCR configs? (26 configs vs 5)",
            default=self.config.get("captcha.ocr_advanced.aggressive_ocr_configs", True),
            style=custom_style,
        ).ask()

        # Save settings
        self.config.set("captcha.auto_solve", auto_solve)
        self.config.set("captcha.fast_mode", False)  # Disable FAST mode
        self.config.set("captcha.manual_input", manual_input)
        self.config.set("captcha.save_image", save_image)
        self.config.set("captcha.auto_open_image", auto_open_image)
        self.config.set("captcha.debug_mode", debug_mode)
        self.config.set("captcha.ocr_advanced.horizontal_reading", horizontal_reading)
        self.config.set("captcha.ocr_advanced.handle_uneven_text", handle_uneven_text)
        self.config.set("captcha.ocr_advanced.aggressive_preprocessing", aggressive_preprocessing)
        self.config.set("captcha.ocr_advanced.aggressive_ocr_configs", aggressive_ocr_configs)

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("AGGRESSIVE mode settings saved!")

            total_attempts = 312 if aggressive_preprocessing and aggressive_ocr_configs else 120

            BotUI.print_warning_panel(
                "✓ AGGRESSIVE mode is now ACTIVE\n\n"
                f"Your captcha will take longer (~3-5min per try) with:\n"
                f"  • {12 if aggressive_preprocessing else 5} preprocessing methods\n"
                f"  • {26 if aggressive_ocr_configs else 5} OCR configs\n"
                f"  • ~{total_attempts} attempts per captcha image\n"
                f"  • 5 OCR retries before manual input\n\n"
                "⚠️  This is MUCH SLOWER. Consider using FAST mode for better experience.",
                title="🐌 AGGRESSIVE Mode Active",
            )

            console.print()
            console.print("[bold green]✓ Press Enter to continue...[/bold green]")
            input()

    def _configure_captcha(self):
        """Configure captcha settings (Legacy - kept for compatibility)"""
        print_header("CAPTCHA SETTINGS")

        auto_solve = questionary.confirm(
            "Enable automatic captcha solving? (OCR)",
            default=self.config.get("captcha.auto_solve", False),
            style=custom_style,
        ).ask()

        fast_mode = questionary.confirm(
            "Enable FAST mode? (Faster OCR ~10-20s vs AGGRESSIVE ~3-5min)",
            default=self.config.get("captcha.fast_mode", True),
            style=custom_style,
        ).ask()

        manual_input = questionary.confirm(
            "Enable manual captcha input? (Fallback if OCR fails)",
            default=self.config.get("captcha.manual_input", True),
            style=custom_style,
        ).ask()

        save_image = questionary.confirm(
            "Save captcha images to screenshots/?",
            default=self.config.get("captcha.save_image", True),
            style=custom_style,
        ).ask()

        auto_open_image = questionary.confirm(
            "Auto-open captcha image? (Useful for headless mode)",
            default=self.config.get("captcha.auto_open_image", True),
            style=custom_style,
        ).ask()

        debug_mode = questionary.confirm(
            "Enable debug mode? (Save all OCR preprocessing images)",
            default=self.config.get("captcha.debug_mode", False),
            style=custom_style,
        ).ask()

        self.config.set("captcha.auto_solve", auto_solve)
        self.config.set("captcha.fast_mode", fast_mode)
        self.config.set("captcha.manual_input", manual_input)
        self.config.set("captcha.save_image", save_image)
        self.config.set("captcha.auto_open_image", auto_open_image)
        self.config.set("captcha.debug_mode", debug_mode)

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Captcha settings saved!")

            # Show info about FAST mode impact
            if fast_mode:
                BotUI.print_info_panel(
                    "✓ FAST mode is ENABLED\n\n"
                    "OCR will be faster (~10-20s) with optimized settings:\n"
                    "  • 5 preprocessing methods\n"
                    "  • 5 OCR configs\n"
                    "  • ~30 total attempts\n\n"
                    "Note: Aggressive OCR settings in 'OCR Advanced' will be ignored.",
                    title="⚡ FAST Mode Active",
                )
            else:
                BotUI.print_info_panel(
                    "✓ FAST mode is DISABLED\n\n"
                    "OCR will use settings from 'OCR Advanced':\n"
                    "  • Can use up to 12 preprocessing methods\n"
                    "  • Can use up to 26 OCR configs\n"
                    "  • 300+ total attempts\n"
                    "  • Slower but more thorough (~3-5min)\n\n"
                    "Configure details in: Settings → OCR Advanced Settings",
                    title="🐌 AGGRESSIVE Mode Active",
                )

    def _configure_logging(self):
        """Configure logging settings"""
        print_header("LOGGING SETTINGS")

        BotUI.print_info_panel(
            "📊 Log Level Explanation:\n\n"
            "• MAIN - Clean & simple logs, user-friendly (Recommended) ✨\n"
            "  Shows only: Important actions, success, errors\n"
            "  Hides: Technical details, timestamps, debug info\n\n"
            "• INFO - Standard logs with technical details\n"
            "  Shows: All actions, timestamps, process info\n\n"
            "• DEBUG - Verbose logs for troubleshooting\n"
            "  Shows: Everything including internal processes\n\n"
            "• WARNING/ERROR - Only warnings and errors",
            title="ℹ️ About Log Levels",
        )

        console.print()

        log_level = questionary.select(
            "Select log level:",
            choices=["MAIN", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default=self.config.get("logging.level", "MAIN"),
            style=custom_style,
        ).ask()

        save_to_file = questionary.confirm(
            "Save logs to file?",
            default=self.config.get("logging.save_to_file", True),
            style=custom_style,
        ).ask()

        colorful = questionary.confirm(
            "Enable colorful terminal output?",
            default=self.config.get("logging.colorful", True),
            style=custom_style,
        ).ask()

        self.config.set("logging.level", log_level)
        self.config.set("logging.save_to_file", save_to_file)
        self.config.set("logging.colorful", colorful)

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Logging settings saved!")

            # Show info about selected log level
            if log_level == "MAIN":
                BotUI.print_info_panel(
                    "✓ MAIN log level selected\n\n"
                    "You will see:\n"
                    "  ✓ Clean, simple messages\n"
                    "  ✓ No timestamps or technical details\n"
                    "  ✓ Only important actions\n"
                    "  ✓ User-friendly format\n\n"
                    "Perfect for everyday use! ✨",
                    title="✨ MAIN Log Level Active",
                )
            elif log_level == "DEBUG":
                BotUI.print_info_panel(
                    "✓ DEBUG log level selected\n\n"
                    "You will see:\n"
                    "  • All technical details\n"
                    "  • Timestamps and process info\n"
                    "  • Debug messages\n"
                    "  • Full troubleshooting information\n\n"
                    "Useful for debugging issues.",
                    title="🔍 DEBUG Log Level Active",
                )
            elif log_level == "INFO":
                BotUI.print_info_panel(
                    "✓ INFO log level selected\n\n"
                    "You will see:\n"
                    "  • Standard logs with timestamps\n"
                    "  • All actions and processes\n"
                    "  • Technical details\n\n"
                    "Balanced between detail and clarity.",
                    title="ℹ️ INFO Log Level Active",
                )

    def _configure_ocr_advanced(self):
        """Configure advanced OCR settings"""
        print_header("OCR ADVANCED SETTINGS")

        # Check if FAST mode is enabled
        fast_mode_enabled = self.config.get("captcha.fast_mode", True)

        if fast_mode_enabled:
            BotUI.print_warning_panel(
                "⚡ FAST MODE is currently ENABLED\n\n"
                "Aggressive OCR settings will be IGNORED when FAST mode is active.\n"
                "FAST mode uses optimized settings for speed (~10-20s):\n"
                "  • 5 preprocessing methods (vs 12 in aggressive)\n"
                "  • 5 OCR configs (vs 26 in aggressive)\n"
                "  • ~30 total attempts\n\n"
                "To use aggressive settings below, disable FAST mode first in:\n"
                "Settings → Captcha Settings → FAST mode (set to No)\n\n"
                "You can still configure settings below, but they won't take effect\n"
                "until FAST mode is disabled.",
                title="⚠️ FAST Mode Active",
            )

            # Offer quick switch to AGGRESSIVE mode
            if BotUI.ask_confirm("Switch to AGGRESSIVE mode now?", default=False):
                self.config.set("captcha.fast_mode", False)
                self.config.save_config()
                print_success("Switched to AGGRESSIVE mode! OCR Advanced settings are now active.")
                fast_mode_enabled = False
            else:
                print_info("Continuing with FAST mode. Aggressive settings will be ignored.")
        else:
            BotUI.print_info_panel(
                "🐌 AGGRESSIVE MODE is currently ACTIVE\n\n"
                "Advanced OCR settings for handling uneven/overlapping captcha text.\n"
                "These settings will use more attempts but take longer (~3-5min):\n"
                "  • Up to 12 preprocessing methods\n"
                "  • Up to 26 OCR configurations\n"
                "  • 300+ total attempts\n\n"
                "For faster OCR (~10-20s), enable FAST mode in:\n"
                "Settings → Captcha Settings → FAST mode (set to Yes)",
                title="ℹ️ OCR Advanced Mode",
            )

            # Offer quick switch to FAST mode
            if BotUI.ask_confirm("Switch to FAST mode now?", default=False):
                self.config.set("captcha.fast_mode", True)
                self.config.save_config()
                print_success("Switched to FAST mode! OCR will be faster (~10-20s).")
                fast_mode_enabled = True
                BotUI.print_info_panel(
                    "FAST mode is now enabled. Aggressive settings below will be ignored.",
                    title="⚡ FAST Mode Active",
                )

        console.print()  # Add spacing

        horizontal_reading = questionary.confirm(
            "Enable horizontal reading? (Left→Right like humans)",
            default=self.config.get("captcha.ocr_advanced.horizontal_reading", True),
            style=custom_style,
        ).ask()

        handle_uneven_text = questionary.confirm(
            "Handle uneven/naik-turun text?",
            default=self.config.get("captcha.ocr_advanced.handle_uneven_text", True),
            style=custom_style,
        ).ask()

        # Add note to aggressive settings if FAST mode is on
        preprocessing_note = " [⚠️ IGNORED - FAST mode is ON]" if fast_mode_enabled else ""
        configs_note = " [⚠️ IGNORED - FAST mode is ON]" if fast_mode_enabled else ""

        aggressive_preprocessing = questionary.confirm(
            f"Use aggressive preprocessing? (12 methods vs 5 in FAST){preprocessing_note}",
            default=self.config.get("captcha.ocr_advanced.aggressive_preprocessing", False),
            style=custom_style,
        ).ask()

        aggressive_ocr_configs = questionary.confirm(
            f"Use aggressive OCR configs? (26 configs vs 5 in FAST){configs_note}",
            default=self.config.get("captcha.ocr_advanced.aggressive_ocr_configs", False),
            style=custom_style,
        ).ask()

        # Advanced tolerances
        if BotUI.ask_confirm("Configure advanced tolerances?", default=False):
            char_overlap = questionary.text(
                "Character overlap tolerance (0.0-1.0):",
                default=str(
                    self.config.get("captcha.ocr_advanced.character_overlap_tolerance", 0.5)
                ),
                style=custom_style,
            ).ask()

            vertical_variance = questionary.text(
                "Vertical variance tolerance (0.0-1.0):",
                default=str(
                    self.config.get("captcha.ocr_advanced.vertical_variance_tolerance", 0.8)
                ),
                style=custom_style,
            ).ask()

            self.config.set("captcha.ocr_advanced.character_overlap_tolerance", float(char_overlap))
            self.config.set(
                "captcha.ocr_advanced.vertical_variance_tolerance", float(vertical_variance)
            )

        self.config.set("captcha.ocr_advanced.horizontal_reading", horizontal_reading)
        self.config.set("captcha.ocr_advanced.handle_uneven_text", handle_uneven_text)
        self.config.set("captcha.ocr_advanced.aggressive_preprocessing", aggressive_preprocessing)
        self.config.set("captcha.ocr_advanced.aggressive_ocr_configs", aggressive_ocr_configs)

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("OCR advanced settings saved!")

            # Remind user if FAST mode is still active
            if fast_mode_enabled and (aggressive_preprocessing or aggressive_ocr_configs):
                BotUI.print_warning_panel(
                    "⚠️ REMINDER: FAST mode is still ENABLED!\n\n"
                    "Your aggressive settings will NOT be used until you:\n"
                    "1. Go to: Settings → Captcha Settings\n"
                    "2. Disable FAST mode (set to No)\n"
                    "3. Save changes\n\n"
                    "Current mode: ⚡ FAST (~10-20s, ~30 attempts)",
                    title="⚠️ Settings Saved But Not Active",
                )

    def _configure_retry(self):
        """Configure retry settings"""
        print_header("RETRY SETTINGS")

        auto_retry_on_cooldown = questionary.confirm(
            "Auto retry when service on cooldown?",
            default=self.config.get("retry.auto_retry_on_cooldown", True),
            style=custom_style,
        ).ask()

        max_attempts = questionary.text(
            "Maximum retry attempts:",
            default=str(self.config.get("retry.max_attempts", 3)),
            validate=lambda text: text.isdigit() or "Must be a number",
            style=custom_style,
        ).ask()

        on_captcha_fail = questionary.confirm(
            "Retry on captcha fail?",
            default=self.config.get("retry.on_captcha_fail", True),
            style=custom_style,
        ).ask()

        self.config.set("retry.auto_retry_on_cooldown", auto_retry_on_cooldown)
        self.config.set("retry.max_attempts", int(max_attempts))
        self.config.set("retry.on_captcha_fail", on_captcha_fail)

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Retry settings saved!")

    def _configure_service_execution(self):
        """Configure service execution settings"""
        print_header("SERVICE EXECUTION SETTINGS")

        show_countdown = questionary.confirm(
            "Show countdown timer during cooldown?",
            default=self.config.get("service_execution.show_countdown", True),
            style=custom_style,
        ).ask()

        active_service_only = questionary.confirm(
            "Run active service only? (Single service mode)",
            default=self.config.get("service_execution.active_service_only", False),
            style=custom_style,
        ).ask()

        default_target = questionary.text(
            "Default target URL index (for quick mode):",
            default=str(self.config.get("service_execution.default_target", 1)),
            validate=lambda text: text.isdigit() or "Must be a number",
            style=custom_style,
        ).ask()

        self.config.set("service_execution.show_countdown", show_countdown)
        self.config.set("service_execution.active_service_only", active_service_only)
        self.config.set("service_execution.default_target", int(default_target))

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Service execution settings saved!")

    def _configure_service_targets(self):
        """Configure service target goals"""
        print_header("SERVICE TARGET GOALS")

        BotUI.print_info_panel(
            "Set target goals for Goal Mode.\n"
            "Bot will run continuously until targets are reached.",
            title="ℹ️ Goal Mode Targets",
        )

        services_list = [
            ("hearts", "Hearts"),
            ("views", "Views"),
            ("followers", "Followers"),
            ("shares", "Shares"),
            ("favorites", "Favorites"),
            ("comments_hearts", "Comments Hearts"),
            ("livestream", "Live Stream"),
        ]

        for key, name in services_list:
            current = self.config.get(f"service_targets.{key}", 1000)
            value = questionary.text(
                f"{name} target goal:",
                default=str(current),
                validate=lambda text: text.isdigit() or "Must be a number",
                style=custom_style,
            ).ask()

            if value:
                self.config.set(f"service_targets.{key}", int(value))

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Service target goals saved!")

    def _configure_services(self):
        """Enable/disable services"""
        print_header("CONFIGURE SERVICES")

        services = self.config.all_services

        BotUI.print_info_panel(
            "Select which services to enable/disable.\n"
            "Note: Some services may be unavailable on Zefoy.",
            title="ℹ️ Services Configuration",
        )

        for service in services:
            enabled = questionary.confirm(
                f"Enable {service['name']}?",
                default=service.get("enabled", False),
                style=custom_style,
            ).ask()

            service["enabled"] = enabled

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Services configuration saved!")

    def _view_statistics(self):
        """View bot statistics"""
        import json
        from pathlib import Path

        from rich import box
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        # Clear screen before showing statistics
        console.clear()

        if self.bot:
            # Bot is running - show current session statistics
            self.bot.print_statistics()
        else:
            # Bot not running - show last session or general info
            stats_text = Text()

            # Try to load statistics from target_progress.json
            try:
                # Get project root directory (parent of config file)
                progress_file = self.config.config_path.parent / "target_progress.json"
                if progress_file.exists():
                    with open(progress_file, "r") as f:
                        progress_data = json.load(f)

                    # Get services data
                    services_data = progress_data.get("services", {})
                    last_updated = progress_data.get("last_updated", "Unknown")

                    stats_text.append("📊 Last Session Progress\n\n", style="bold cyan")

                    has_data = False
                    total_executions = 0

                    for service, data in services_data.items():
                        if isinstance(data, dict):
                            current = data.get("current", 0)
                            target = data.get("target", 0)
                            executions = data.get("executions", 0)

                            # Only show services with activity
                            if current > 0 or executions > 0:
                                has_data = True
                                total_executions += executions

                                stats_text.append(f"• {service}:\n", style="bold white")
                                stats_text.append(f"  Current: {current:,}\n", style="cyan")
                                if target > 0:
                                    stats_text.append(f"  Target: {target:,}\n", style="green")
                                    percentage = (current / target) * 100 if target > 0 else 0
                                    stats_text.append(
                                        f"  Progress: {percentage:.1f}%\n", style="yellow"
                                    )
                                stats_text.append(f"  Executions: {executions}\n", style="blue")
                                stats_text.append("\n")

                    if has_data:
                        stats_text.append(
                            f"\nTotal Executions: {total_executions}\n", style="bold green"
                        )
                        stats_text.append(
                            f"Last Updated: {last_updated.split('T')[0] if 'T' in last_updated else last_updated}",
                            style="dim white",
                        )
                    else:
                        stats_text.append("No activity yet.\n", style="yellow")
                        stats_text.append(
                            "Start the bot and execute services to see statistics!",
                            style="dim white",
                        )
                else:
                    stats_text.append("No session data found.\n\n", style="yellow")
                    stats_text.append(
                        "Start the bot and execute services to begin!", style="dim white"
                    )
            except Exception as e:
                stats_text.append("Unable to load statistics.\n\n", style="yellow")
                stats_text.append(f"Error: {str(e)}\n\n", style="dim red")
                stats_text.append("Start the bot to begin tracking statistics!", style="dim white")

            console.print()
            console.print(
                Panel(
                    Align.center(stats_text),
                    title="[bold cyan]📊 Bot Statistics[/bold cyan]",
                    title_align="center",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(2, 4),
                )
            )

            # Show hint to start bot
            hint_text = Text(justify="center")
            hint_text.append("💡 Tip: Start the bot to see live statistics!\n", style="bold blue")
            hint_text.append("Go to: Main Menu → 🚀 Start Bot", style="dim white")

            console.print()
            console.print(
                Panel(Align.center(hint_text), border_style="blue", box=box.ROUNDED, padding=(1, 2))
            )

        # Wait for user to read statistics
        console.print()
        console.print("[bold green]✓ Press Enter to continue...[/bold green]")
        input()

    def _view_services(self):
        """View available services"""
        from rich import box
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        # Clear screen before showing services
        console.clear()

        # Known offline services (based on Zefoy website)
        offline_services = ["Followers", "Live Stream"]

        # Get current active service
        active_service = self.config.get("active_service", None)

        if active_service:
            BotUI.print_info_panel(f"Single Service Mode: {active_service}", title="🎯 Active Mode")
            console.print()

        if self.bot and self.bot.session_active:
            services = self.bot.get_available_services()

            if services:
                # Create beautiful table
                table = Table(
                    show_header=True, header_style="bold cyan", box=box.ROUNDED, border_style="cyan"
                )
                table.add_column("Service", style="white", width=20)
                table.add_column("Status", style="white", width=18)
                table.add_column("Active Mode", style="white", width=15)

                for s in services:
                    name = s["name"]
                    zefoy_status = s["status"]
                    enabled = s["enabled"]
                    is_active = active_service == name
                    is_offline = name in offline_services

                    # Determine overall status
                    if is_offline:
                        overall_status = "❌ OFFLINE"
                    elif zefoy_status == "Available" and enabled:
                        overall_status = "✅ Ready"
                    elif zefoy_status == "Available" and not enabled:
                        overall_status = "⚠️ Not Enabled"
                    elif zefoy_status == "Unavailable":
                        overall_status = "🔒 Unavailable"
                    else:
                        overall_status = zefoy_status

                    # Active mode indicator
                    mode = "🎯 ACTIVE" if is_active else "-"

                    table.add_row(name, overall_status, mode)

                console.print()
                console.print(
                    Panel(
                        table,
                        title="[bold cyan]📊 Services Status (Live from Zefoy)[/bold cyan]",
                        title_align="left",
                        border_style="cyan",
                        box=box.ROUNDED,
                        padding=(1, 2),
                    )
                )

                # Legend in rounded panel
                legend_content = Text()
                legend_content.append("✅ Ready       ", style="green")
                legend_content.append("- Service is available and enabled\n", style="dim white")

                legend_content.append("⚠️  Not Enabled ", style="yellow")
                legend_content.append(
                    "- Available on Zefoy but disabled in config\n", style="dim white"
                )

                legend_content.append("❌ OFFLINE     ", style="red")
                legend_content.append("- Service is offline on Zefoy\n", style="dim white")

                legend_content.append("🔒 Unavailable ", style="yellow")
                legend_content.append("- Service temporarily unavailable\n", style="dim white")

                legend_content.append("🎯 ACTIVE      ", style="blue")
                legend_content.append(
                    "- Marked as 'active' (all enabled services can be used)", style="dim white"
                )

                console.print(
                    Panel(
                        legend_content,
                        title="[bold cyan]ℹ️  Status Legend[/bold cyan]",
                        title_align="left",
                        border_style="cyan",
                        box=box.ROUNDED,
                        padding=(1, 2),
                    )
                )
                console.print()
            else:
                print_error("Could not retrieve services")
        else:
            # Show configured services
            services = self.config.all_services

            # Create beautiful table
            table = Table(
                show_header=True, header_style="bold cyan", box=box.ROUNDED, border_style="cyan"
            )
            table.add_column("Service", style="white", width=20)
            table.add_column("Config Status", style="white", width=18)
            table.add_column("Active Mode", style="white", width=15)

            for s in services:
                name = s["name"]
                enabled = s.get("enabled", False)
                is_active = active_service == name
                is_offline = name in offline_services

                # Determine status
                if is_offline:
                    status = "❌ OFFLINE"
                elif enabled:
                    status = "✅ Enabled"
                else:
                    status = "⚠️ Disabled"

                # Active mode indicator
                mode = "🎯 ACTIVE" if is_active else "-"

                table.add_row(name, status, mode)

            console.print()
            console.print(
                Panel(
                    table,
                    title="[bold cyan]📋 Configured Services (Start bot for live status)[/bold cyan]",
                    title_align="left",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )

            # Legend in rounded panel
            legend_content = Text()
            legend_content.append("✅ Enabled  ", style="green")
            legend_content.append("- Service is enabled in config\n", style="dim white")

            legend_content.append("⚠️  Disabled ", style="yellow")
            legend_content.append("- Service is disabled in config\n", style="dim white")

            legend_content.append("❌ OFFLINE  ", style="red")
            legend_content.append("- Service is known to be offline on Zefoy\n", style="dim white")

            legend_content.append("🎯 ACTIVE   ", style="blue")
            legend_content.append(
                "- Marked as 'active' (all enabled services can be used)", style="dim white"
            )

            console.print(
                Panel(
                    legend_content,
                    title="[bold cyan]ℹ️  Status Legend[/bold cyan]",
                    title_align="left",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
            console.print()

        # Wait for user to read services
        console.print()
        console.print("[bold green]✓ Press Enter to continue...[/bold green]")
        input()

    def _refresh_bot(self):
        """Refresh bot session"""
        # Clear screen before refreshing
        console.clear()

        if not self.bot:
            print_error("Bot is not running")
            return

        BotUI.print_info_panel("Refreshing page...\n" "Please wait.", title="🔄 Refreshing")

        try:
            self.bot.driver.refresh()
            BotUI.print_success_panel("Page refreshed successfully!", title="✓ Refreshed")

            # Re-solve captcha if present
            if self.bot.captcha_solver.is_captcha_present():
                print_info("Captcha detected after refresh, solving...")
                if self.bot.captcha_solver.solve_captcha():
                    print_success("Captcha solved")
                else:
                    print_error("Failed to solve captcha")
        except Exception as e:
            print_error(f"Error refreshing: {str(e)}")

        # Wait for user to read refresh result
        console.print()
        console.print("[bold green]✓ Press Enter to continue...[/bold green]")
        input()

    def _configure_active_service(self):
        """Configure active service (single service mode)"""
        print_header("ACTIVE SERVICE CONFIGURATION")

        BotUI.print_info_panel(
            "Active Service Marker is a visual indicator only.\n"
            "It marks one service but DOES NOT restrict usage.\n"
            "All enabled services can always be used!\n\n"
            "📊 Service Status Legend:\n"
            "  ✅ = Available and ready to use\n"
            "  🎯 = Marked as 'active' (visual marker only)\n"
            "  ⚠️ = Disabled in config (can still try to use)\n"
            "  ❌ = Offline on Zefoy (won't work)",
            title="ℹ️ About Active Service Marker",
        )

        # Get all services from config with their availability status
        all_services_config = self.config.all_services

        # Known offline services (based on Zefoy website)
        offline_services = ["Followers", "Live Stream"]

        # Build service choices with status
        service_choices = ["All Services (Disable Single Mode)"]
        service_map = {}  # Map display name to actual name

        for service in all_services_config:
            service_name = service["name"]
            enabled = service.get("enabled", False)
            is_offline = service_name in offline_services

            # Create display name with status
            if is_offline:
                display_name = f"{service_name} [❌ OFFLINE]"
                status = "❌"
            elif enabled:
                display_name = f"{service_name} [✅ Active]"
                status = "✅"
            else:
                display_name = f"{service_name} [⚠️ Disabled]"
                status = "⚠️"

            service_choices.append(display_name)
            service_map[display_name] = service_name

        # Get current active
        current = self.config.get("active_service", None)
        current_text = current if current else "All Services"

        console.print(f"\n[cyan]Current Active:[/cyan] {current_text}\n")

        choice = questionary.select(
            "Select active service:", choices=service_choices, style=custom_style
        ).ask()

        if choice == "All Services (Disable Single Mode)":
            self.config.set("active_service", None)
            print_success("Active service marker removed - No service marked as 'active'")
        else:
            # Extract actual service name from display name
            actual_service_name = service_map.get(choice, choice)

            # Check if service is offline
            if actual_service_name in offline_services:
                BotUI.print_warning_panel(
                    f"{actual_service_name} is currently OFFLINE on Zefoy.\n"
                    f"This service may not work until Zefoy enables it.",
                    title="⚠ Service Offline",
                )

                if not BotUI.ask_confirm("Mark as active anyway?", default=False):
                    return

            self.config.set("active_service", actual_service_name)
            print_success(
                f"Active service marker set to: {actual_service_name}\nNote: All enabled services can still be used!"
            )

        if BotUI.ask_confirm("Save changes?", default=True):
            self.config.save_config()
            print_success("Configuration saved!")

            BotUI.print_info_panel(
                "No restart needed! Changes are for display only.\n"
                "All enabled services remain usable.",
                title="ℹ Info",
            )

    def _view_target_progress(self):
        """View target goals progress"""
        # Clear screen before showing target progress
        console.clear()

        if not self.bot or not self.bot.target_tracker:
            BotUI.print_warning_panel(
                "Bot is not running or target tracker not initialized", title="⚠ Not Available"
            )
            console.print()
            console.print("[bold green]✓ Press Enter to continue...[/bold green]")
            input()
            return

        # Get all services
        services = [
            "Followers",
            "Hearts",
            "Comments Hearts",
            "Views",
            "Shares",
            "Favorites",
            "Live Stream",
        ]

        rows = []
        for service in services:
            progress = self.bot.target_tracker.get_progress(service)

            if progress["target"] > 0:
                # Color code progress percentage
                percentage = progress["percentage"]
                if percentage >= 100:
                    progress_str = f"[bold green]{percentage:.1f}%[/bold green]"
                elif percentage >= 75:
                    progress_str = f"[green]{percentage:.1f}%[/green]"
                elif percentage >= 50:
                    progress_str = f"[yellow]{percentage:.1f}%[/yellow]"
                elif percentage >= 25:
                    progress_str = f"[orange1]{percentage:.1f}%[/orange1]"
                else:
                    progress_str = f"[red]{percentage:.1f}%[/red]"

                rows.append(
                    [
                        service,
                        f"{progress['current']:,}",
                        f"{progress['target']:,}",
                        progress_str,
                        f"{progress['remaining']:,}",
                        str(progress["executions"]),
                    ]
                )

        if rows:
            # Create beautiful table
            from rich import box
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text

            table = Table(
                show_header=True,
                header_style="bold cyan",
                box=box.ROUNDED,
                border_style="cyan",
                title_style="bold cyan",
            )

            table.add_column("Service", style="white", no_wrap=True)
            table.add_column("Current", style="cyan", justify="right")
            table.add_column("Target", style="green", justify="right")
            table.add_column("Progress", justify="right")  # No default style, using markup colors
            table.add_column("Remaining", style="dim white", justify="right")
            table.add_column("Executions", style="blue", justify="center")

            for row in rows:
                # Add row with markup parsing enabled
                from rich.text import Text

                parsed_row = []
                for i, cell in enumerate(row):
                    if i == 3:  # Progress column has markup
                        parsed_row.append(Text.from_markup(cell))
                    else:
                        parsed_row.append(cell)
                table.add_row(*parsed_row)

            console.print()
            console.print(
                Panel(
                    table,
                    title="[bold cyan]📊 Target Goals Progress[/bold cyan]",
                    title_align="left",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )

            # Show progress bars

            progress_text = Text()
            for service in services:
                progress = self.bot.target_tracker.get_progress(service)
                if progress["target"] > 0:
                    bar = self.bot.target_tracker.format_progress_bar(service, width=40)
                    progress_text.append(f"{service:20s} {bar}\n", style="white")

            if progress_text.plain:
                console.print()
                console.print(
                    Panel(
                        progress_text,
                        title="[bold cyan]📊 Progress Bars[/bold cyan]",
                        title_align="left",
                        border_style="cyan",
                        box=box.ROUNDED,
                        padding=(1, 2),
                    )
                )
        else:
            BotUI.print_info_panel(
                "No target goals configured.\nEdit config.yaml to set target goals.",
                title="ℹ No Targets",
            )

        # Wait for user to read target progress
        console.print()
        console.print("[bold green]✓ Press Enter to continue...[/bold green]")
        input()

    def _show_help(self):
        """Show beautiful and comprehensive help information"""
        from rich import box
        from rich.align import Align
        from rich.columns import Columns
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        # Clear screen already handled by caller
        console.print()

        # Main Features Panel
        features_content = Text()
        features_content.append("🤖 ", style="bold cyan")
        features_content.append("Smart Captcha Solving\n", style="bold white")
        features_content.append(
            "   • Auto OCR with FAST mode (~30 attempts in 10-20s)\n", style="dim white"
        )
        features_content.append(
            "   • AGGRESSIVE mode (~300+ attempts in 3-5min)\n", style="dim white"
        )
        features_content.append(
            "   • Horizontal reading (left→right like humans)\n", style="dim white"
        )
        features_content.append("   • Handles uneven & overlapping text\n", style="dim white")
        features_content.append("   • Manual input fallback\n\n", style="dim white")

        features_content.append("🎯 ", style="bold cyan")
        features_content.append("Multiple Services\n", style="bold white")
        features_content.append("   • Followers, Hearts, Views, Shares\n", style="dim white")
        features_content.append("   • Comments Hearts, Favorites, Live Stream\n", style="dim white")
        features_content.append("   • Real-time cooldown tracking\n", style="dim white")
        features_content.append("   • Target goals & continuous mode\n\n", style="dim white")

        features_content.append("✨ ", style="bold cyan")
        features_content.append("Advanced Features\n", style="bold white")
        features_content.append("   • Undetected Chrome browser\n", style="dim white")
        features_content.append("   • AdBlock support (faster loading)\n", style="dim white")
        features_content.append("   • Beautiful colored terminal UI\n", style="dim white")
        features_content.append("   • Detailed logging & statistics\n", style="dim white")
        features_content.append("   • Headless mode support", style="dim white")

        console.print(
            Panel(
                features_content,
                title="[bold cyan]✨ Key Features[/bold cyan]",
                title_align="left",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        # Quick Start Guide
        quickstart_content = Text()
        quickstart_content.append("1️⃣  ", style="bold green")
        quickstart_content.append("Start Bot", style="bold white")
        quickstart_content.append(" → Select from main menu\n", style="dim white")

        quickstart_content.append("2️⃣  ", style="bold green")
        quickstart_content.append("Captcha Solving", style="bold white")
        quickstart_content.append(" → Auto OCR or manual input\n", style="dim white")

        quickstart_content.append("3️⃣  ", style="bold green")
        quickstart_content.append("Choose Service", style="bold white")
        quickstart_content.append(" → Hearts, Views, Followers, etc.\n", style="dim white")

        quickstart_content.append("4️⃣  ", style="bold green")
        quickstart_content.append("Enter Video URL", style="bold white")
        quickstart_content.append(" → Your TikTok video link\n", style="dim white")

        quickstart_content.append("5️⃣  ", style="bold green")
        quickstart_content.append("Wait & Enjoy", style="bold white")
        quickstart_content.append(" → Bot will handle everything!", style="dim white")

        console.print(
            Panel(
                quickstart_content,
                title="[bold green]🚀 Quick Start Guide[/bold green]",
                title_align="left",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        # Configuration Tips
        config_table = Table(show_header=True, header_style="bold yellow", box=box.SIMPLE)
        config_table.add_column("Setting", style="cyan", width=25)
        config_table.add_column("Location", style="white", width=30)
        config_table.add_column("Description", style="dim white")

        config_table.add_row(
            "🔧 Basic Settings", "Settings Menu (CLI)", "Browser, headless, adblock, etc."
        )
        config_table.add_row("📝 Advanced Config", "config.yaml", "OCR settings, timeouts, targets")
        config_table.add_row(
            "🎯 Service Targets", "config.yaml → service_targets", "Goal mode targets per service"
        )
        config_table.add_row(
            "🔍 OCR Advanced", "config.yaml → ocr_advanced", "Horizontal reading, uneven text"
        )

        console.print(
            Panel(
                config_table,
                title="[bold yellow]⚙️  Configuration[/bold yellow]",
                title_align="left",
                border_style="yellow",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        # Pro Tips
        tips_content = Text()
        tips_content.append("💡 ", style="bold magenta")
        tips_content.append(
            "Enable auto_solve + fast_mode for quick automatic captcha (~10-20s)\n", style="white"
        )

        tips_content.append("💡 ", style="bold magenta")
        tips_content.append("Services have cooldowns - be patient between runs\n", style="white")

        tips_content.append("💡 ", style="bold magenta")
        tips_content.append(
            "Use headless mode for better performance (no browser UI)\n", style="white"
        )

        tips_content.append("💡 ", style="bold magenta")
        tips_content.append("Check logs/ folder for detailed execution logs\n", style="white")

        tips_content.append("💡 ", style="bold magenta")
        tips_content.append("Enable debug_mode to see OCR preprocessing images\n", style="white")

        tips_content.append("💡 ", style="bold magenta")
        tips_content.append("Goal mode runs continuously until target reached", style="white")

        console.print(
            Panel(
                tips_content,
                title="[bold magenta]💡 Pro Tips[/bold magenta]",
                title_align="left",
                border_style="magenta",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        # Troubleshooting
        trouble_table = Table(show_header=True, header_style="bold red", box=box.SIMPLE)
        trouble_table.add_column("Issue", style="yellow", width=30)
        trouble_table.add_column("Solution", style="white")

        trouble_table.add_row(
            "❌ Captcha not solving", "Enable manual_input or check tesseract installation"
        )
        trouble_table.add_row(
            "❌ Service on cooldown", "Wait for cooldown timer or try another service"
        )
        trouble_table.add_row("❌ Chrome not found", "Install Chrome or set correct path in config")
        trouble_table.add_row(
            "❌ OCR low success rate", "Enable debug_mode and check preprocessing images"
        )
        trouble_table.add_row("❌ Bot crashes", "Check logs/ folder for error details")

        console.print(
            Panel(
                trouble_table,
                title="[bold red]🔧 Troubleshooting[/bold red]",
                title_align="left",
                border_style="red",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        # Documentation & Support
        docs_content = Text(justify="center")
        docs_content.append("📚 Full Documentation\n", style="bold blue")
        docs_content.append(
            "README.md • docs/ folder • config.yaml comments\n\n", style="dim white"
        )

        docs_content.append("🆘 Need Help?\n", style="bold blue")
        docs_content.append(
            "Check logs for errors • Review documentation • Ask for support\n\n", style="dim white"
        )

        docs_content.append("⚡ Quick Links\n", style="bold blue")
        docs_content.append("OCR Guide: docs/AGGRESSIVE_OCR_MODE.md\n", style="cyan")
        docs_content.append("Uneven Captcha: docs/UNEVEN_CAPTCHA_HANDLING.md\n", style="cyan")
        docs_content.append("Quick Reference: OCR_QUICK_REFERENCE.md", style="cyan")

        console.print(
            Panel(
                Align.center(docs_content),
                title="[bold blue]📖 Documentation & Support[/bold blue]",
                title_align="center",
                border_style="blue",
                box=box.ROUNDED,
                padding=(1, 4),
            )
        )

        console.print()
        console.print("[bold green]✓ Press Enter to return to main menu...[/bold green]")
        input()

    def cleanup(self):
        """Cleanup resources"""
        if self.bot:
            self.bot.close()
            self.bot = None

        # Clean up screenshots folder
        self._cleanup_screenshots()

        BotUI.print_success_panel(
            "Thank you for using TikTok Automation Tool!\n" "See you next time! 👋",
            title="✓ Goodbye",
        )

    def _cleanup_screenshots(self):
        """Clean up screenshots folder, keeping only .gitkeep"""
        try:
            import shutil
            from pathlib import Path

            screenshots_dir = Path(self.config.screenshot_path)

            if screenshots_dir.exists() and screenshots_dir.is_dir():
                deleted_count = 0

                for file in screenshots_dir.iterdir():
                    # Keep .gitkeep and skip directories
                    if file.is_file() and file.name != ".gitkeep":
                        try:
                            file.unlink()
                            deleted_count += 1
                        except Exception as e:
                            self.logger.debug(f"Could not delete {file.name}: {e}")

                if deleted_count > 0:
                    self.logger.info(
                        f"Cleaned up {deleted_count} screenshot(s) from screenshots folder"
                    )
        except Exception as e:
            self.logger.debug(f"Error cleaning up screenshots: {e}")


def main():
    """Main entry point"""
    try:
        cli = ZefoyBotCLI()
        cli.run()
    except KeyboardInterrupt:
        BotUI.print_warning_panel(
            "\nInterrupted by user.\n" "Exiting gracefully.", title="⚠ Interrupted"
        )
        sys.exit(0)
    except Exception as e:
        BotUI.print_error_panel(
            f"A fatal error occurred:\n\n" f"{str(e)}\n\n" f"Please check the logs for details.",
            title="💀 Fatal Error",
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
