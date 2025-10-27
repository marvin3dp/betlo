"""
Captcha solver for Zefoy Bot
Supports both manual and automatic (OCR) captcha solving
"""

import os
import platform
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    import cv2
    import numpy as np
    import pytesseract
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from .logger import BotUI, console, get_logger
from .utils import human_typing, random_delay, take_screenshot, wait_for_element


class CaptchaSolver:
    """Captcha solver with manual and automatic options"""

    def __init__(self, driver, config, logger=None):
        """
        Initialize captcha solver

        Args:
            driver: Selenium WebDriver instance
            config: Configuration object
            logger: Logger instance
        """
        self.driver = driver
        self.config = config
        self.logger = logger or get_logger()
        self.auto_solve = config.get("captcha.auto_solve", False) and OCR_AVAILABLE
        self.manual_input = config.get("captcha.manual_input", True)
        self.save_image = config.get("captcha.save_image", True)
        self.debug_mode = config.get("captcha.debug_mode", False)

        # Get raw config values
        config_auto_open = config.get("captcha.auto_open_image", False)
        config_upload_cloud = config.get("captcha.upload_to_cloud", True)

        self.fast_mode = config.get(
            "captcha.fast_mode", True
        )  # Fast mode for quicker OCR (less combinations)
        self.cloud_uploader_url = config.get(
            "captcha.cloud_uploader_url", "https://uploader.sh"
        )  # Cloud uploader URL

        # Validate and set captcha display mode
        # IMPORTANT: Cloud mode and auto_open mode are mutually exclusive
        # Cloud mode = Upload to cloud, show URL (for VPS/remote servers)
        # Desktop mode = Auto-open with image viewer (for local desktop)

        if config_upload_cloud and config_auto_open:
            # Both enabled - prioritize cloud mode (VPS use case)
            self.upload_to_cloud = True
            self.auto_open_image = False
            self.logger.warning(
                "⚠️  Both upload_to_cloud and auto_open_image are enabled in config!"
            )
            self.logger.info(
                "✓ Cloud mode prioritized - captcha will be uploaded (auto_open disabled)"
            )
        elif config_upload_cloud:
            # Cloud mode only
            self.upload_to_cloud = True
            self.auto_open_image = False
            self.logger.info("☁️  Captcha Mode: Cloud/VPS - Upload to cloud enabled")
        elif config_auto_open:
            # Desktop mode only
            self.upload_to_cloud = False
            self.auto_open_image = True
            self.logger.info("🖥️  Captcha Mode: Desktop - Auto-open image viewer enabled")
        else:
            # Neither enabled - manual mode
            self.upload_to_cloud = False
            self.auto_open_image = False
            self.logger.info("📁 Captcha Mode: Manual - Check screenshots folder manually")

        # Advanced OCR settings untuk captcha tidak rata / naik turun
        self.horizontal_reading = config.get("captcha.ocr_advanced.horizontal_reading", True)
        self.handle_uneven_text = config.get("captcha.ocr_advanced.handle_uneven_text", True)
        self.char_overlap_tolerance = config.get(
            "captcha.ocr_advanced.character_overlap_tolerance", 0.5
        )
        self.vertical_variance_tolerance = config.get(
            "captcha.ocr_advanced.vertical_variance_tolerance", 0.8
        )
        self.aggressive_preprocessing = config.get(
            "captcha.ocr_advanced.aggressive_preprocessing", False
        )
        self.aggressive_ocr_configs = config.get(
            "captcha.ocr_advanced.aggressive_ocr_configs", False
        )

    def solve_captcha(self, max_attempts: int = None) -> bool:
        """
        Main captcha solving method

        Args:
            max_attempts: Maximum number of attempts (auto-determined by mode if None)

        Returns:
            True if captcha solved successfully, False otherwise
        """
        from rich import box
        from rich.align import Align
        from rich.live import Live
        from rich.panel import Panel
        from rich.text import Text

        # Auto-determine max_attempts based on mode
        if max_attempts is None:
            if self.fast_mode:
                max_attempts = 2  # FAST mode: quick failover to manual (2 OCR attempts)
            else:
                max_attempts = 5  # AGGRESSIVE mode: more OCR retries before manual (5 OCR attempts)

        mode_text = "FAST" if self.fast_mode else "AGGRESSIVE"
        self.logger.info(
            f"Starting captcha solving process ({mode_text} mode, {max_attempts} OCR attempts)..."
        )

        # Create persistent status panel
        status_messages = []

        def create_status_panel():
            """Create a panel with current status messages"""
            content = Text()
            for msg in status_messages[-10:]:  # Show last 10 messages
                # Parse markup and add to Text object
                content.append(Text.from_markup(msg))
                content.append("\n")

            return Panel(
                Align.center(content)
                if content.plain
                else Align.center(Text("Initializing...", style="cyan")),
                title=f"[bold cyan]🔍 Solving Captcha ({mode_text} mode)[/bold cyan]",
                title_align="center",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
            )

        # Clear screen before showing captcha solving panel
        console.clear()

        # Use Live panel for persistent display
        success = False
        try:
            with Live(create_status_panel(), console=console, refresh_per_second=4) as live:
                status_messages.append(f"[cyan]🔍 Starting captcha solving...[/cyan]")

                # Check if auto_solve is disabled - skip to manual input
                if not self.auto_solve and self.manual_input:
                    status_messages.append(f"[yellow]⚠ Auto-solve is disabled[/yellow]")
                    status_messages.append(f"[yellow]⌨  Using manual captcha input...[/yellow]")
                    live.update(create_status_panel())
                    # Will jump to manual input section after the auto loop
                elif self.auto_solve:
                    # Show mode-specific info
                    if self.fast_mode:
                        status_messages.append(
                            f"[dim]🚀 FAST Mode: {max_attempts} OCR attempts (~10-20s each)[/dim]"
                        )
                    else:
                        status_messages.append(
                            f"[dim]🎯 AGGRESSIVE Mode: {max_attempts} OCR attempts (~30-60s each)[/dim]"
                        )
                    status_messages.append(
                        f"[dim]Auto fallback to manual if all attempts fail[/dim]"
                    )
                    live.update(create_status_panel())

                live.update(create_status_panel())

                ocr_attempts_made = 0

                # Auto captcha attempts loop (skip if auto_solve disabled)
                attempt_range = range(1, max_attempts + 1) if self.auto_solve else range(0)
                for attempt in attempt_range:
                    status_messages.append(
                        f"\n[bold cyan]Attempt {attempt}/{max_attempts}[/bold cyan]"
                    )
                    live.update(create_status_panel())

                    try:
                        # Wait for captcha image to load
                        status_messages.append("[dim]⏳ Waiting for captcha image...[/dim]")
                        live.update(create_status_panel())

                        captcha_img = self._wait_for_captcha_image()
                        if not captcha_img:
                            status_messages.append("[red]✗ Captcha image not found[/red]")
                            live.update(create_status_panel())
                            self.logger.error("Captcha image not found")
                            continue

                        # Get captcha text
                        captcha_text = None

                        # Try OCR if auto_solve is enabled
                        if self.auto_solve:
                            status_messages.append(
                                f"[cyan]🤖 Attempting OCR (attempt {attempt}/{max_attempts})...[/cyan]"
                            )
                            live.update(create_status_panel())

                            captcha_text = self._solve_with_ocr(captcha_img)
                            ocr_attempts_made = attempt

                            if captcha_text:
                                status_messages.append(
                                    f"[green]✓ OCR succeeded: '{captcha_text}'[/green]"
                                )
                                live.update(create_status_panel())
                                self.logger.success(
                                    f"✓ OCR succeeded on attempt {attempt}/{max_attempts}"
                                )
                            else:
                                status_messages.append(
                                    f"[yellow]✗ OCR failed on attempt {attempt}/{max_attempts}[/yellow]"
                                )
                                live.update(create_status_panel())
                                self.logger.warning(
                                    f"✗ OCR failed on attempt {attempt}/{max_attempts}"
                                )

                        # If OCR failed, retry if not last attempt
                        if not captcha_text and self.auto_solve:
                            if attempt < max_attempts:
                                # Not the last attempt yet, refresh and retry OCR
                                status_messages.append(
                                    f"[yellow]🔄 Refreshing captcha for retry...[/yellow]"
                                )
                                live.update(create_status_panel())

                                self._refresh_captcha()
                                random_delay(2, 3)
                                continue
                            else:
                                # Last attempt and OCR failed - will fallback to manual after loop
                                self.logger.warning(f"OCR failed all {max_attempts} attempts")
                                break

                        # If auto_solve disabled and no captcha text
                        if not captcha_text and not self.auto_solve:
                            self.logger.info("Auto-solve disabled, will use manual input")
                            break

                        # If still no captcha text (shouldn't reach here normally)
                        if not captcha_text:
                            status_messages.append("[yellow]⚠ No captcha text obtained[/yellow]")
                            live.update(create_status_panel())
                            self.logger.warning("No captcha text obtained")

                            if attempt >= max_attempts:
                                break
                            continue

                        # Submit captcha
                        status_messages.append(f"[cyan]📤 Submitting captcha...[/cyan]")
                        live.update(create_status_panel())

                        if self._submit_captcha(captcha_text):
                            status_messages.append(
                                "[bold green]✓ Captcha solved successfully![/bold green]"
                            )
                            live.update(create_status_panel())

                            self.logger.success("Captcha solved successfully!")
                            success = True
                            random_delay(1, 2)  # Show success message briefly
                            return True
                        else:
                            # Captcha submission failed (wrong captcha)
                            status_messages.append(
                                "[yellow]⚠ Captcha submission failed or incorrect[/yellow]"
                            )
                            status_messages.append("[dim]🔄 Closing error popup...[/dim]")
                            live.update(create_status_panel())

                            self.logger.warning("Captcha submission failed or incorrect")

                            # Wait before retry
                            if attempt < max_attempts:
                                status_messages.append("[dim]🔄 Refreshing captcha...[/dim]")
                                live.update(create_status_panel())

                                self.logger.info("Refreshing captcha...")
                                self._refresh_captcha()
                                random_delay(2, 3)
                            else:
                                # Last attempt failed, will try manual input after loop
                                self.logger.warning(
                                    f"Auto captcha failed all {max_attempts} attempts"
                                )
                                self._refresh_captcha()
                                random_delay(1, 2)

                    except KeyboardInterrupt:
                        status_messages.append("[red]⚠ Cancelled by user[/red]")
                        live.update(create_status_panel())
                        random_delay(1, 1.5)  # Show cancelled message briefly
                        raise
                    except Exception as e:
                        status_messages.append(f"[red]✗ Error: {str(e)[:50]}...[/red]")
                        live.update(create_status_panel())

                        self.logger.error(f"Error during captcha solving: {str(e)}")
                        if attempt < max_attempts:
                            random_delay(2, 3)

                # Auto captcha attempts finished, try manual input if enabled
                if not success and self.manual_input:
                    if self.auto_solve:
                        status_messages.append(
                            f"\n[yellow]⚠ {mode_text} mode failed all {max_attempts} OCR attempts[/yellow]"
                        )
                        status_messages.append(
                            "[yellow]⌨  Switching to manual captcha input...[/yellow]"
                        )
                        live.update(create_status_panel())

                        self.logger.warning(
                            f"{mode_text} mode exhausted all {max_attempts} OCR attempts"
                        )
                        self.logger.info("Switching to manual captcha input...")
                    else:
                        status_messages.append(
                            "\n[yellow]⌨  Starting manual captcha input...[/yellow]"
                        )
                        live.update(create_status_panel())

                    # Manual captcha loop - retry until success or user cancels
                    manual_attempt = 0
                    while not success:
                        manual_attempt += 1
                        status_messages.append(
                            f"\n[bold yellow]Manual Attempt #{manual_attempt}[/bold yellow]"
                        )
                        live.update(create_status_panel())

                        try:
                            # Wait for captcha image
                            status_messages.append("[dim]⏳ Loading captcha image...[/dim]")
                            live.update(create_status_panel())

                            captcha_img = self._wait_for_captcha_image()
                            if not captcha_img:
                                status_messages.append("[red]✗ Captcha image not found[/red]")
                                live.update(create_status_panel())
                                self.logger.error("Captcha image not found for manual input")
                                break

                            # Get manual input
                            status_messages.append(
                                "[yellow]⌨  Please enter captcha manually...[/yellow]"
                            )
                            live.update(create_status_panel())

                            # Pause Live to allow user input
                            live.stop()
                            captcha_text = self._solve_manually(captcha_img)
                            live.start()

                            if not captcha_text:
                                # User cancelled or empty input
                                status_messages.append(
                                    "[red]✗ Manual input cancelled or empty[/red]"
                                )
                                status_messages.append("[red]⚠ Returning to main menu...[/red]")
                                live.update(create_status_panel())

                                self.logger.warning("Manual captcha input cancelled by user")
                                random_delay(2, 3)
                                break

                            status_messages.append(
                                f"[green]✓ Manual input received: '{captcha_text}'[/green]"
                            )
                            live.update(create_status_panel())

                            # Submit manual captcha
                            status_messages.append("[cyan]📤 Submitting manual captcha...[/cyan]")
                            live.update(create_status_panel())

                            if self._submit_captcha(captcha_text):
                                status_messages.append(
                                    "[bold green]✓ Captcha solved successfully![/bold green]"
                                )
                                live.update(create_status_panel())

                                self.logger.success("Manual captcha solved successfully!")
                                success = True
                                random_delay(1, 2)
                                return True
                            else:
                                # Manual captcha also wrong, retry
                                status_messages.append(
                                    "[yellow]⚠ Manual captcha incorrect[/yellow]"
                                )
                                status_messages.append("[dim]🔄 Closing error popup...[/dim]")
                                status_messages.append("[yellow]Please try again...[/yellow]")
                                live.update(create_status_panel())

                                self.logger.warning(
                                    f"Manual captcha incorrect (attempt #{manual_attempt})"
                                )
                                self._refresh_captcha()
                                random_delay(2, 3)
                                # Loop continues for another manual attempt

                        except KeyboardInterrupt:
                            status_messages.append("[red]⚠ Cancelled by user[/red]")
                            status_messages.append("[red]⚠ Returning to main menu...[/red]")
                            live.update(create_status_panel())
                            random_delay(1, 1.5)
                            raise
                        except Exception as e:
                            status_messages.append(f"[red]✗ Error: {str(e)[:50]}...[/red]")
                            live.update(create_status_panel())

                            self.logger.error(f"Error during manual captcha: {str(e)}")
                            random_delay(2, 3)
                            break

                # If still not success after manual attempts (or manual disabled)
                if not success:
                    if not self.manual_input:
                        status_messages.append(
                            "[bold red]✗ Auto captcha failed and manual input is disabled[/bold red]"
                        )
                        status_messages.append("[red]⚠ Returning to main menu...[/red]")
                    else:
                        status_messages.append("[bold red]✗ Failed to solve captcha[/bold red]")
                        status_messages.append("[red]⚠ Returning to main menu...[/red]")

                    live.update(create_status_panel())
                    self.logger.error("Failed to solve captcha")
                    random_delay(2, 3)

            # Live panel closed, clear screen for clean transition
            if success:
                # Successfully solved, clear screen before returning to bot flow
                pass  # Screen will be cleared by bot.py or main.py
            else:
                # Failed to solve, clear screen before returning to main menu
                pass  # Screen will be cleared by main.py

        except KeyboardInterrupt:
            self.logger.warning("Captcha solving cancelled by user")
            raise

        # Clear screen after Live panel closes for clean transition
        console.clear()

        return success

    def _wait_for_captcha_image(self, timeout: int = 10):
        """
        Wait for captcha image to load

        Args:
            timeout: Maximum wait time

        Returns:
            Captcha image element or None
        """
        try:
            # Look for captcha image
            selectors = [
                (By.CSS_SELECTOR, "img.img-thumbnail"),
                (By.CSS_SELECTOR, "img.card-img-top"),
                (By.XPATH, "//img[contains(@src, 'CAPTCHA')]"),
            ]

            for by, selector in selectors:
                img = wait_for_element(self.driver, by, selector, timeout=timeout)
                if img:
                    # Wait for image to fully load
                    time.sleep(1)
                    return img

            return None

        except Exception as e:
            self.logger.error(f"Error waiting for captcha image: {str(e)}")
            return None

    def _solve_with_ocr(self, captcha_img) -> Optional[str]:
        """
        Solve captcha using OCR with multiple preprocessing methods and configurations
        Uses horizontal (right-to-left) character detection for misaligned text

        Args:
            captcha_img: Captcha image element

        Returns:
            Extracted text or None
        """
        if not OCR_AVAILABLE:
            self.logger.warning("OCR libraries not available")
            return None

        try:
            # Save captcha image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = self.config.screenshot_path / f"captcha_{timestamp}.png"

            # Take screenshot of captcha
            captcha_img.screenshot(str(img_path))
            self.logger.debug(f"Captcha image saved to: {img_path}")

            # Get multiple processed versions of the image
            processed_images = self._preprocess_captcha_image(img_path)

            if not processed_images:
                self.logger.warning("Image preprocessing failed")
                return None

            # OCR configurations - Fast mode vs Aggressive mode
            if self.fast_mode or not self.aggressive_ocr_configs:
                # FAST MODE: Only most effective configs (5-6 configs for speed)
                ocr_configs = [
                    # PSM 8: Single word (most common for captcha)
                    "--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 8 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 7: Single line
                    "--psm 7 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 13: Raw line (no layout analysis)
                    "--psm 13 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 11: Sparse text (good for scattered characters)
                    "--psm 11 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                ]
            else:
                # AGGRESSIVE MODE: Many combinations for maximum success rate (26 configs)
                ocr_configs = [
                    # PSM 8: Single word (most common for captcha) - try all engines
                    "--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 8 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 8 --oem 2 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 8 --oem 0 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 7: Single line - all engines
                    "--psm 7 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 7 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 7 --oem 2 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 6: Single block - multiple engines
                    "--psm 6 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 6 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 13: Raw line (no layout analysis)
                    "--psm 13 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 13 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 8 with case insensitive (then convert to lower)
                    "--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                    "--psm 8 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                    # PSM 7 with case insensitive
                    "--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                    "--psm 7 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                    # PSM 10: Single character mode
                    "--psm 10 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 10 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 11: Sparse text (good for scattered characters)
                    "--psm 11 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 11 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # Default with different engines
                    "--oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # More permissive - allow numbers too (sometimes helps)
                    "--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789",
                    "--psm 7 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789",
                ]

            best_result = None
            best_confidence = 0
            results_frequency = {}  # Track how often each result appears

            # Log total combinations to try
            total_combinations = len(processed_images) * len(ocr_configs) + len(
                processed_images
            )  # +horizontal reading
            mode_info = (
                "FAST" if (self.fast_mode or not self.aggressive_ocr_configs) else "AGGRESSIVE"
            )
            self.logger.debug(
                f"OCR {mode_info}: {len(processed_images)} preprocessing methods × {len(ocr_configs)} configs = ~{total_combinations} attempts"
            )

            # Try each preprocessing method with each OCR config
            for idx, processed_img in enumerate(processed_images):
                # Method 1: HORIZONTAL LEFT→RIGHT READING (seperti cara manusia membaca)
                # Baca karakter dari KIRI KE KANAN berdasarkan posisi horizontal
                # Works better for misaligned, uneven, naik-turun captcha text
                if self.horizontal_reading:
                    try:
                        horizontal_text = self._read_horizontal_chars(processed_img)
                        if horizontal_text:
                            # Clean extracted text
                            text = re.sub(r"[^a-zA-Z]", "", horizontal_text.strip())

                            if text:
                                text_lower = text.lower()
                                # Count horizontal detection with extra weight
                                results_frequency[text_lower] = (
                                    results_frequency.get(text_lower, 0) + 2
                                )

                                length_score = len(text) if 3 <= len(text) <= 8 else 0
                                frequency_bonus = (
                                    results_frequency[text_lower] * 3
                                )  # Increased from 2
                                confidence = (
                                    length_score + frequency_bonus + 10
                                )  # Increased bonus from 5 to 10

                                self.logger.debug(
                                    f"OCR horizontal LEFT→RIGHT {idx + 1}: '{text}' "
                                    f"(len:{len(text)}, freq:{results_frequency[text_lower]}, conf:{confidence})"
                                )

                                if confidence > best_confidence:
                                    best_confidence = confidence
                                    best_result = text_lower
                    except Exception as e:
                        self.logger.debug(f"Horizontal char detection {idx + 1} failed: {e}")

                # Method 2: Standard OCR configs
                for config_idx, config in enumerate(ocr_configs):
                    try:
                        # Extract text
                        text = pytesseract.image_to_string(processed_img, config=config)

                        # Clean extracted text
                        text = re.sub(r"[^a-zA-Z]", "", text.strip())

                        if text:
                            # Calculate confidence based on multiple factors
                            length_score = len(text) if 3 <= len(text) <= 8 else 0

                            # Check if text contains repeating patterns (likely noise)
                            unique_chars = len(set(text))
                            pattern_penalty = 0 if unique_chars < 2 else 0

                            # Track frequency - results appearing multiple times are more likely correct
                            text_lower = text.lower()
                            results_frequency[text_lower] = results_frequency.get(text_lower, 0) + 1
                            frequency_bonus = results_frequency[text_lower] * 2

                            confidence = length_score + frequency_bonus - pattern_penalty

                            self.logger.debug(
                                f"OCR attempt {idx + 1}-{config_idx + 1}: '{text}' "
                                f"(len:{len(text)}, freq:{results_frequency[text_lower]}, conf:{confidence})"
                            )

                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_result = text_lower

                    except Exception as e:
                        self.logger.debug(f"OCR attempt {idx + 1}-{config_idx + 1} failed: {e}")
                        continue

            # After all attempts, check if we have a high-frequency result
            if results_frequency:
                most_frequent = max(results_frequency, key=results_frequency.get)
                frequency_count = results_frequency[most_frequent]

                # AGGRESSIVE: Accept result if appears 2+ times (lowered from 3)
                # This increases success rate for difficult captchas
                if frequency_count >= 2 and 3 <= len(most_frequent) <= 8:
                    self.logger.info(
                        f"OCR extracted text (high confidence): {most_frequent} "
                        f"(appeared {frequency_count} times)"
                    )
                    return most_frequent

                # Even more aggressive: if appears only once but from horizontal method
                # and has good length, still try it
                if frequency_count == 1 and 4 <= len(most_frequent) <= 7:
                    self.logger.info(
                        f"OCR extracted text (single match, good length): {most_frequent}"
                    )
                    return most_frequent

            # Calculate total attempts
            total_standard_attempts = len(processed_images) * len(ocr_configs)
            total_horizontal_attempts = len(
                processed_images
            )  # One horizontal attempt per preprocessing
            total_attempts = total_standard_attempts + total_horizontal_attempts

            # Return best result if found
            if best_result:
                self.logger.info(f"✓ OCR SUCCESS: '{best_result}' (confidence: {best_confidence})")
                self.logger.info(
                    f"  Tried {total_attempts} combinations: "
                    f"{len(processed_images)} preprocessing × ({len(ocr_configs)} configs + 1 horizontal)"
                )

                # Log all results for debugging
                if results_frequency and len(results_frequency) > 1:
                    top_results = sorted(
                        results_frequency.items(), key=lambda x: x[1], reverse=True
                    )[:3]
                    self.logger.debug(
                        f"Top OCR results: {', '.join([f'{text}({count}x)' for text, count in top_results])}"
                    )

                return best_result
            else:
                self.logger.warning(
                    f"✗ OCR FAILED after {total_attempts} aggressive attempts "
                    f"({len(processed_images)} preprocessing methods × {len(ocr_configs)} configs "
                    f"+ {total_horizontal_attempts} horizontal detections)"
                )
                return None

        except Exception as e:
            self.logger.error(f"OCR error: {str(e)}")
            import traceback

            self.logger.debug(traceback.format_exc())
            return None

    def _read_horizontal_chars(self, image: np.ndarray) -> Optional[str]:
        """
        Read characters from left to right based on horizontal position (seperti manusia membaca)
        Handles misaligned, uneven, and overlapping characters

        Args:
            image: Preprocessed captcha image

        Returns:
            Extracted text reading left to right, or None
        """
        try:
            # Ensure image is grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # Threshold the image to binary
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Find contours (character regions)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return None

            # Filter and get bounding boxes for each character
            char_boxes = []
            height, width = gray.shape

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)

                # AGGRESSIVE: More permissive filter for character detection
                # Lowered thresholds to catch more characters
                min_height = height * 0.08  # Lowered from 0.1
                max_height = height * 0.9  # Increased from 0.8
                min_width = width * 0.03  # Lowered from 0.05
                max_width = width * 0.6  # Increased from 0.5

                # More permissive filtering
                if h >= min_height and h <= max_height and w >= min_width and w < max_width:
                    # Calculate area to filter out very thin lines
                    area = w * h
                    min_area = (height * width) * 0.005  # At least 0.5% of image

                    if area >= min_area:
                        # Store box with center point for better overlap detection
                        center_x = x + w / 2
                        center_y = y + h / 2
                        char_boxes.append(
                            {
                                "x": x,
                                "y": y,
                                "w": w,
                                "h": h,
                                "center_x": center_x,
                                "center_y": center_y,
                                "area": area,
                            }
                        )

            if not char_boxes:
                self.logger.debug("No valid character boxes found")
                return None

            # UNEVEN TEXT HANDLING: Handle overlapping characters
            if self.handle_uneven_text:
                char_boxes = self._merge_overlapping_boxes(char_boxes, width)

            # Sort boxes by center_x (KIRI KE KANAN - seperti cara manusia membaca)
            char_boxes.sort(key=lambda box: box["center_x"])

            self.logger.debug(
                f"Found {len(char_boxes)} character regions (LEFT→RIGHT reading): "
                f"X positions: {[int(box['center_x']) for box in char_boxes]}"
            )

            # Extract text from each character box
            chars = []
            for idx, box in enumerate(char_boxes):
                x, y, w, h = int(box["x"]), int(box["y"]), int(box["w"]), int(box["h"])
                # Add small padding around character
                padding = 3
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(width, x + w + padding)
                y2 = min(height, y + h + padding)

                # Extract character region
                char_img = gray[y1:y2, x1:x2]

                # AGGRESSIVE: Try multiple preprocessing methods for each character
                char_processed_images = []

                # Method 1: Simple resize + Otsu
                resized = cv2.resize(char_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
                _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                char_processed_images.append(binary)

                # Method 2: Adaptive threshold
                resized2 = cv2.resize(char_img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
                adaptive = cv2.adaptiveThreshold(
                    resized2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                char_processed_images.append(adaptive)

                # Method 3: Inverted
                _, binary_inv = cv2.threshold(
                    resized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
                )
                char_processed_images.append(binary_inv)

                # Method 4: With denoising
                denoised = cv2.fastNlMeansDenoising(resized, None, 10, 7, 21)
                _, binary_clean = cv2.threshold(
                    denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                char_processed_images.append(binary_clean)

                # Method 5: Super upscale
                super_resized = cv2.resize(
                    char_img, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC
                )
                _, super_binary = cv2.threshold(
                    super_resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                char_processed_images.append(super_binary)

                # AGGRESSIVE: Try many OCR configs for single character
                char_configs = [
                    # PSM 10: Single character mode (best for individual chars)
                    "--psm 10 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 10 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 10 --oem 2 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 10 --oem 0 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 8: Single word
                    "--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 8 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # PSM 7: Single line
                    "--psm 7 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    "--psm 7 --oem 1 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz",
                    # With uppercase too
                    "--psm 10 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                    "--psm 10 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                ]

                # Try each preprocessing method with each config
                char_text = None
                char_candidates = {}  # Track character frequency

                for proc_img in char_processed_images:
                    for config in char_configs:
                        try:
                            text = pytesseract.image_to_string(proc_img, config=config)
                            text = re.sub(r"[^a-zA-Z]", "", text.strip())
                            if text and len(text) >= 1:
                                char = text[0].lower()
                                char_candidates[char] = char_candidates.get(char, 0) + 1
                        except BaseException:
                            continue

                # Pick most frequent character
                if char_candidates:
                    char_text = max(char_candidates, key=char_candidates.get)
                    self.logger.debug(
                        f"  Char candidates: {char_candidates}, selected: '{char_text}'"
                    )

                if char_text:
                    chars.append(char_text)
                    self.logger.debug(f"Character {idx + 1} at x={x}: '{char_text}'")
                else:
                    self.logger.debug(f"Character {idx + 1} at x={x}: failed to read")

            # Combine all characters
            if chars:
                result = "".join(chars)
                self.logger.debug(f"Horizontal reading result: '{result}'")
                return result
            else:
                return None

        except Exception as e:
            self.logger.debug(f"Horizontal character reading failed: {str(e)}")
            return None

    def _merge_overlapping_boxes(self, boxes, image_width):
        """
        Merge overlapping character boxes untuk handle captcha yang tidak rata
        Characters yang overlap secara horizontal akan dimerge jika terlalu dekat

        Args:
            boxes: List of character boxes (dict with x, y, w, h, center_x, center_y)
            image_width: Width of the image

        Returns:
            List of merged boxes
        """
        if not boxes or len(boxes) <= 1:
            return boxes

        # Sort by center_x first
        boxes = sorted(boxes, key=lambda b: b["center_x"])

        merged = []
        current_box = boxes[0].copy()

        for i in range(1, len(boxes)):
            next_box = boxes[i]

            # Calculate horizontal overlap
            current_right = current_box["x"] + current_box["w"]
            next_left = next_box["x"]

            # Check if boxes overlap horizontally
            overlap = current_right - next_left
            overlap_ratio = overlap / min(current_box["w"], next_box["w"]) if overlap > 0 else 0

            # Merge if overlap is significant (based on tolerance)
            if overlap_ratio > self.char_overlap_tolerance:
                self.logger.debug(
                    f"Merging overlapping boxes at x={int(current_box['center_x'])} "
                    f"and x={int(next_box['center_x'])} (overlap: {overlap_ratio:.2f})"
                )

                # Merge boxes - take the bounding box that contains both
                min_x = min(current_box["x"], next_box["x"])
                min_y = min(current_box["y"], next_box["y"])
                max_x = max(current_box["x"] + current_box["w"], next_box["x"] + next_box["w"])
                max_y = max(current_box["y"] + current_box["h"], next_box["y"] + next_box["h"])

                current_box = {
                    "x": min_x,
                    "y": min_y,
                    "w": max_x - min_x,
                    "h": max_y - min_y,
                    "center_x": (min_x + max_x) / 2,
                    "center_y": (min_y + max_y) / 2,
                    "area": (max_x - min_x) * (max_y - min_y),
                }
            else:
                # No overlap, save current and move to next
                merged.append(current_box)
                current_box = next_box.copy()

        # Don't forget the last box
        merged.append(current_box)

        self.logger.debug(f"Box merging: {len(boxes)} → {len(merged)} boxes")
        return merged

    def _remove_lines_from_image(self, image: np.ndarray) -> np.ndarray:
        """
        Remove horizontal and vertical lines from captcha image

        Args:
            image: Grayscale image with lines

        Returns:
            Image with lines removed
        """
        try:
            # Create kernels for detecting horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

            # Detect horizontal lines
            detect_horizontal = cv2.morphologyEx(
                image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
            )
            # Detect vertical lines
            detect_vertical = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

            # Combine detected lines
            lines_mask = cv2.add(detect_horizontal, detect_vertical)

            # Remove lines from original image
            result = cv2.subtract(image, lines_mask)

            return result
        except Exception as e:
            self.logger.debug(f"Line removal failed: {e}")
            return image

    def _remove_noise_and_lines(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced noise and line removal using morphological operations

        Args:
            image: Input grayscale image

        Returns:
            Cleaned image
        """
        try:
            # Apply bilateral filter to preserve edges while removing noise
            filtered = cv2.bilateralFilter(image, 9, 75, 75)

            # Threshold the image
            _, binary = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Remove small noise with morphological opening
            kernel_small = np.ones((2, 2), np.uint8)
            opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small, iterations=1)

            # Remove lines
            cleaned = self._remove_lines_from_image(opened)

            # Apply closing to fill gaps in characters
            kernel_close = np.ones((2, 2), np.uint8)
            closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close, iterations=1)

            return closed
        except Exception as e:
            self.logger.debug(f"Noise removal failed: {e}")
            return image

    def _open_image_with_default_app(self, image_path: Path) -> bool:
        """
        Open image with default system application
        Useful for headless mode where user can't see browser

        Args:
            image_path: Path to image file

        Returns:
            True if opened successfully, False otherwise
        """
        try:
            system = platform.system()
            image_path_str = str(image_path.absolute())

            if system == "Linux":
                # Try xdg-open first (works on most Linux desktop environments)
                try:
                    subprocess.Popen(
                        ["xdg-open", image_path_str],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    self.logger.info(f"Captcha image opened with xdg-open: {image_path}")
                    return True
                except FileNotFoundError:
                    # Fallback to specific image viewers
                    viewers = ["eog", "feh", "display", "gwenview", "gthumb", "gpicview"]
                    for viewer in viewers:
                        try:
                            subprocess.Popen(
                                [viewer, image_path_str],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                            self.logger.info(f"Captcha image opened with {viewer}: {image_path}")
                            return True
                        except FileNotFoundError:
                            continue
                    self.logger.warning("No image viewer found. Install xdg-open or eog")
                    return False

            elif system == "Darwin":  # macOS
                subprocess.Popen(
                    ["open", image_path_str], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self.logger.info(f"Captcha image opened with default app: {image_path}")
                return True

            elif system == "Windows":
                os.startfile(image_path_str)  # pylint: disable=no-member
                self.logger.info(f"Captcha image opened with default app: {image_path}")
                return True

            else:
                self.logger.warning(f"Unsupported OS for auto-open: {system}")
                return False

        except Exception as e:
            self.logger.warning(f"Failed to open image with default app: {str(e)}")
            return False

    def _upload_image_to_cloud(self, image_path: Path) -> Optional[str]:
        """
        Upload captcha image to uploader.sh for easy access on VPS

        Args:
            image_path: Path to captcha image file

        Returns:
            URL of uploaded image or None if failed
        """
        try:
            import requests

            # Prepare the upload
            image_name = image_path.name
            upload_url = f"{self.cloud_uploader_url}/{image_name}"

            # Read image file
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Upload using curl-like request
            response = requests.post(
                upload_url,
                data=image_data,
                headers={"Content-Type": "application/octet-stream"},
                timeout=30,
            )

            if response.status_code == 200:
                # uploader.sh returns the URL in the response
                uploaded_url = response.text.strip()
                return uploaded_url
            else:
                self.logger.warning(f"Upload failed with status code: {response.status_code}")
                return None

        except ImportError:
            self.logger.warning(
                "requests library not available. Install with: pip install requests"
            )
            return None
        except Exception as e:
            self.logger.warning(f"Failed to upload image to cloud: {str(e)}")
            return None

    def _preprocess_captcha_image(self, image_path: Path):
        """
        Preprocess captcha image for better OCR accuracy
        Returns multiple processed versions for different OCR attempts
        Includes special handling for captchas with strikethrough lines

        Args:
            image_path: Path to captcha image

        Returns:
            List of processed images as numpy arrays
        """
        # Read image
        img = cv2.imread(str(image_path))

        if img is None:
            self.logger.error(f"Failed to read image: {image_path}")
            return []

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        processed_images = []
        method_names = []

        # Determine how many preprocessing methods to use
        use_fast_preprocessing = self.fast_mode or not self.aggressive_preprocessing

        # Method 1: Line removal with adaptive threshold
        try:
            # Remove lines first
            no_lines = self._remove_noise_and_lines(gray)
            # Apply adaptive threshold
            adaptive = cv2.adaptiveThreshold(
                no_lines, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            # Denoise
            denoised = cv2.fastNlMeansDenoising(adaptive, None, 10, 7, 21)
            # Resize
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("line_removal_adaptive")
        except Exception as e:
            self.logger.debug(f"Line removal + adaptive threshold failed: {e}")

        # Method 2: Heavy morphological line removal + Otsu
        try:
            # Aggressive line removal
            no_lines = self._remove_lines_from_image(gray)
            # Apply Otsu
            _, otsu = cv2.threshold(no_lines, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Clean up with morphology
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(cleaned, None, 10, 7, 21)
            # Resize
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("line_removal_otsu")
        except Exception as e:
            self.logger.debug(f"Heavy line removal failed: {e}")

        # Method 3: Bilateral filter + line removal + CLAHE
        try:
            # Bilateral filter to preserve edges
            bilateral = cv2.bilateralFilter(gray, 11, 75, 75)
            # Remove lines
            no_lines = self._remove_lines_from_image(bilateral)
            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(no_lines)
            # Threshold
            _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Morphological cleanup
            kernel = np.ones((2, 2), np.uint8)
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(morph, None, 10, 7, 21)
            # Resize
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("bilateral_line_removal_clahe")
        except Exception as e:
            self.logger.debug(f"Bilateral + line removal failed: {e}")

        # Method 4: Inverted with line removal
        try:
            inverted = cv2.bitwise_not(gray)
            no_lines = self._remove_noise_and_lines(inverted)
            _, thresh = cv2.threshold(no_lines, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("inverted_line_removal")
        except Exception as e:
            self.logger.debug(f"Inverted line removal failed: {e}")

        # Method 5: Median blur + line removal (good for salt-and-pepper noise)
        try:
            # Median blur
            median = cv2.medianBlur(gray, 3)
            # Remove lines
            no_lines = self._remove_lines_from_image(median)
            # Threshold
            _, thresh = cv2.threshold(no_lines, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            # Resize
            resized = cv2.resize(morph, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("median_line_removal")
        except Exception as e:
            self.logger.debug(f"Median + line removal failed: {e}")

        # FAST MODE: Stop here with 5 methods (faster OCR)
        # AGGRESSIVE MODE: Continue with more methods for maximum success
        if use_fast_preprocessing:
            # Debug images will be saved at the end of the method
            return processed_images

        # Method 6: Erosion-Dilation for thick lines
        try:
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Erode to break thin lines
            kernel_erode = np.ones((2, 2), np.uint8)
            eroded = cv2.erode(binary, kernel_erode, iterations=1)
            # Remove lines
            no_lines = self._remove_lines_from_image(eroded)
            # Dilate to restore character thickness
            kernel_dilate = np.ones((2, 2), np.uint8)
            dilated = cv2.dilate(no_lines, kernel_dilate, iterations=1)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(dilated, None, 10, 7, 21)
            # Resize
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("erosion_dilation")
        except Exception as e:
            self.logger.debug(f"Erosion-dilation failed: {e}")

        # Method 7: Aggressive line removal with multiple passes
        try:
            # Multiple passes of line removal
            temp = gray.copy()
            for _ in range(3):
                temp = self._remove_lines_from_image(temp)
            # Strong threshold
            _, thresh = cv2.threshold(temp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Morphological cleanup
            kernel = np.ones((2, 2), np.uint8)
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(morph, None, 10, 7, 21)
            # Resize larger for better recognition
            resized = cv2.resize(denoised, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("multi_pass_line_removal")
        except Exception as e:
            self.logger.debug(f"Multi-pass line removal failed: {e}")

        # Method 8: Super resolution upscale with sharpening
        try:
            # Gaussian blur + unsharp mask
            blurred = cv2.GaussianBlur(gray, (0, 0), 3)
            sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
            # Remove lines
            no_lines = self._remove_lines_from_image(sharpened)
            # Threshold
            _, thresh = cv2.threshold(no_lines, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Super upscale
            resized = cv2.resize(thresh, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("super_resolution")
        except Exception as e:
            self.logger.debug(f"Super resolution failed: {e}")

        # Method 9: Contrast enhancement + adaptive threshold
        try:
            # CLAHE for contrast
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            # Remove lines
            no_lines = self._remove_lines_from_image(enhanced)
            # Adaptive threshold with larger block
            adaptive = cv2.adaptiveThreshold(
                no_lines, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5
            )
            # Denoise aggressively
            denoised = cv2.fastNlMeansDenoising(adaptive, None, 15, 7, 21)
            # Resize
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("contrast_adaptive")
        except Exception as e:
            self.logger.debug(f"Contrast adaptive failed: {e}")

        # Method 10: Black hat transform (dark text on light background)
        try:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
            blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            # Threshold
            _, thresh = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            # Resize
            resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("blackhat")
        except Exception as e:
            self.logger.debug(f"Blackhat transform failed: {e}")

        # Method 11: Gradient-based edge enhancement
        try:
            # Sobel gradients
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient = np.sqrt(sobelx**2 + sobely**2)
            gradient = np.uint8(gradient / gradient.max() * 255)
            # Combine with original
            combined = cv2.addWeighted(gray, 0.7, gradient, 0.3, 0)
            # Remove lines
            no_lines = self._remove_lines_from_image(combined)
            # Threshold
            _, thresh = cv2.threshold(no_lines, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # Resize
            resized = cv2.resize(thresh, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            processed_images.append(resized)
            method_names.append("gradient_enhanced")
        except Exception as e:
            self.logger.debug(f"Gradient enhancement failed: {e}")

        # Method 12: Multiple threshold levels
        try:
            results = []
            for threshold_val in [100, 120, 140, 160, 180]:
                _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY)
                no_lines = self._remove_lines_from_image(thresh)
                denoised = cv2.fastNlMeansDenoising(no_lines, None, 10, 7, 21)
                resized = cv2.resize(denoised, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
                processed_images.append(resized)
                method_names.append(f"manual_threshold_{threshold_val}")
        except Exception as e:
            self.logger.debug(f"Manual threshold failed: {e}")

        # Save debug images if debug mode is enabled
        if self.debug_mode and processed_images:
            try:
                timestamp = image_path.stem.split("_")[-1]
                # Save original
                cv2.imwrite(
                    str(self.config.screenshot_path / f"captcha_{timestamp}_0_original.png"), gray
                )
                # Save processed versions
                for idx, (proc_img, method_name) in enumerate(zip(processed_images, method_names)):
                    debug_path = (
                        self.config.screenshot_path
                        / f"captcha_{timestamp}_{idx + 1}_{method_name}.png"
                    )
                    cv2.imwrite(str(debug_path), proc_img)
                self.logger.debug(
                    f"Saved original + {len(processed_images)} processed debug images"
                )
            except Exception as e:
                self.logger.debug(f"Failed to save debug images: {e}")

        return processed_images if processed_images else [gray]

    def _solve_manually(self, captcha_img) -> Optional[str]:
        """
        Solve captcha manually with user input

        Args:
            captcha_img: Captcha image element

        Returns:
            User input text or None
        """
        try:
            # Save captcha image for user reference
            img_path = None
            uploaded_url = None

            if self.save_image:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_path = self.config.screenshot_path / f"captcha_manual_{timestamp}.png"
                captcha_img.screenshot(str(img_path))

                # Apply captcha display mode (mutually exclusive)
                # Priority: Cloud > Desktop > Manual

                if self.upload_to_cloud:
                    # Cloud mode: Upload captcha to cloud (for VPS/remote servers)
                    uploaded_url = self._upload_image_to_cloud(img_path)
                    if uploaded_url:
                        self.logger.info("☁️  Captcha uploaded to cloud")
                    else:
                        self.logger.warning("Failed to upload - check screenshots folder")

                elif self.auto_open_image:
                    # Desktop mode: Auto-open image with default viewer (for local use)
                    opened = self._open_image_with_default_app(img_path)
                    if opened:
                        self.logger.info("🖥️  Captcha opened in image viewer")
                    else:
                        self.logger.warning("Could not auto-open - check screenshots folder")
                else:
                    # Manual mode: User needs to check screenshots folder manually
                    self.logger.info(f"📁 Captcha saved: {img_path.name}")

            # Get captcha input from user with beautiful centered panel
            from rich import box
            from rich.align import Align
            from rich.panel import Panel
            from rich.text import Text

            console.print()

            # Show captcha URL in separate rounded panel if uploaded
            if uploaded_url:
                url_content = Text()

                # Parse the uploaded_url response to extract clean URL
                # uploader.sh returns format like:
                # =========================
                # Uploaded 1 file, X bytes
                # wget https://...
                # =========================
                clean_url = uploaded_url
                if "wget " in uploaded_url:
                    # Extract URL from wget command
                    for line in uploaded_url.split("\n"):
                        if line.strip().startswith("wget "):
                            clean_url = line.strip().replace("wget ", "").strip()
                            break
                elif "http" in uploaded_url:
                    # Extract any http URL
                    for line in uploaded_url.split("\n"):
                        if "http" in line:
                            clean_url = line.strip()
                            # Remove any leading/trailing separators
                            clean_url = clean_url.strip("=").strip()
                            if clean_url.startswith("wget "):
                                clean_url = clean_url.replace("wget ", "")
                            break

                # Extract file size info if available
                file_info = ""
                if "Uploaded" in uploaded_url and "bytes" in uploaded_url:
                    for line in uploaded_url.split("\n"):
                        if "Uploaded" in line and "bytes" in line:
                            file_info = line.strip()
                            break

                # Display file info if available
                if file_info:
                    url_content.append(f"{file_info}\n\n", style="dim white")

                # Display CLI format
                url_content.append("CLI:\n", style="bold cyan")
                url_content.append(f"wget {clean_url}\n\n", style="white")

                # Display browser format
                url_content.append("Browser:\n", style="bold cyan")
                url_content.append(clean_url, style="bold white")

                console.print(
                    Panel(
                        Align.center(url_content),
                        title="[bold cyan]🔗 Captcha URL[/bold cyan]",
                        title_align="center",
                        box=box.ROUNDED,
                        style="cyan",
                        border_style="cyan",
                        padding=(1, 2),
                    )
                )
                console.print()

            # Show instruction panel
            captcha_content = Text()

            if uploaded_url:
                # Cloud mode message
                captcha_content.append("☁️  VPS/Cloud Mode\n", style="bold cyan")
                captcha_content.append("Open URL above to view captcha\n\n", style="dim white")
            elif img_path and self.auto_open_image:
                # Desktop mode with auto-open
                captcha_content.append("🖥️  Desktop Mode\n", style="bold green")
                captcha_content.append("Captcha opened in image viewer\n\n", style="dim white")
            elif img_path:
                # Manual mode
                captcha_content.append("📁 Manual Mode\n", style="bold yellow")
                captcha_content.append(f"Check: {img_path.name}\n\n", style="dim white")
            else:
                # Fallback
                captcha_content.append("Look at captcha in browser\n\n", style="bold white")

            captcha_content.append("Enter captcha text (lowercase only)", style="cyan")

            console.print(
                Panel(
                    Align.center(captcha_content),
                    title="[bold yellow]🔐 Manual Captcha Input[/bold yellow]",
                    title_align="center",
                    box=box.ROUNDED,
                    style="yellow",
                    border_style="yellow",
                    padding=(1, 2),
                )
            )
            console.print()

            text = BotUI.ask_input("[yellow]Captcha text[/yellow]")

            # Clean input
            text = re.sub(r"[^a-z]", "", text.lower().strip())

            if text:
                return text
            else:
                self.logger.warning("Empty captcha input")
                return None

        except Exception as e:
            self.logger.error(f"Manual input error: {str(e)}")
            return None

    def _submit_captcha(self, captcha_text: str) -> bool:
        """
        Submit captcha answer

        Args:
            captcha_text: Captcha text to submit

        Returns:
            True if submission successful, False otherwise
        """
        try:
            # Find captcha input field
            input_selectors = [
                (By.ID, "captchatoken"),
                (By.NAME, "captchatoken"),
                (By.CSS_SELECTOR, "input[placeholder*='Enter the word']"),
                (By.CSS_SELECTOR, "input.form-control.text-center"),
            ]

            captcha_input = None
            for by, selector in input_selectors:
                captcha_input = wait_for_element(self.driver, by, selector, timeout=5)
                if captcha_input:
                    break

            if not captcha_input:
                self.logger.error("Captcha input field not found")
                return False

            # Close any blocking modals before typing
            try:
                modal_close_selectors = [
                    (By.CSS_SELECTOR, ".modal .close"),
                    (By.CSS_SELECTOR, "button.close"),
                    (By.XPATH, "//button[@data-dismiss='modal']"),
                ]
                for by, selector in modal_close_selectors:
                    close_btn = wait_for_element(self.driver, by, selector, timeout=1)
                    if close_btn:
                        try:
                            close_btn.click()
                            random_delay(0.5, 1)
                            self.logger.debug("Closed modal before typing")
                            break
                        except BaseException:
                            pass
            except BaseException:
                pass

            # Wait for any loading overlays to disappear
            try:
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait

                # Wait for loading overlay to disappear if present
                WebDriverWait(self.driver, 5).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".vfx-loader"))
                )
                self.logger.debug("Loading overlay disappeared")
            except BaseException:
                pass  # No loading overlay or already gone

            # Scroll input field into view
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                    captcha_input,
                )
                random_delay(0.3, 0.5)
            except BaseException:
                pass

            # Clear field first
            try:
                captcha_input.clear()
                random_delay(0.2, 0.3)
            except BaseException:
                pass

            # Type captcha text
            self.logger.info(f"Submitting captcha: {captcha_text}")
            human_typing(captcha_input, captcha_text)
            random_delay(0.5, 1)

            # Find and click submit button
            submit_selectors = [
                (By.CSS_SELECTOR, "button.submit-captcha"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(@class, 'btn-primary')]"),
            ]

            submit_btn = None
            for by, selector in submit_selectors:
                submit_btn = wait_for_element(self.driver, by, selector, timeout=5)
                if submit_btn:
                    break

            if not submit_btn:
                self.logger.error("Submit button not found")
                return False

            # Close any blocking modals before submitting
            try:
                modal_close_selectors = [
                    (By.CSS_SELECTOR, ".modal .close"),
                    (By.CSS_SELECTOR, "button.close"),
                    (By.XPATH, "//button[@data-dismiss='modal']"),
                    (By.XPATH, "//div[contains(@class, 'modal')]//button"),
                ]
                for by, selector in modal_close_selectors:
                    close_btn = wait_for_element(self.driver, by, selector, timeout=1)
                    if close_btn:
                        try:
                            close_btn.click()
                            random_delay(0.5, 1)
                            self.logger.debug("Closed modal before submit")
                            break
                        except BaseException:
                            pass
            except BaseException:
                pass

            # Wait for any loading overlays to disappear
            try:
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait

                # Wait for loading overlay to disappear if present
                WebDriverWait(self.driver, 3).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".vfx-loader"))
                )
            except BaseException:
                pass  # No loading overlay or already gone

            # Scroll submit button into view
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                    submit_btn,
                )
                random_delay(0.5, 1)
            except BaseException:
                pass

            # Wait for submit button to be clickable
            try:
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait

                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.submit-captcha"))
                )
                self.logger.debug("Submit button is clickable")
            except BaseException:
                self.logger.debug("Submit button clickable check timeout, proceeding anyway")

            # Try to click submit button
            clicked = False
            try:
                # Try normal click first
                submit_btn.click()
                self.logger.debug("Submitted captcha using normal click")
                clicked = True
            except Exception as click_error:
                self.logger.warning(f"Normal click failed: {str(click_error)}")
                # Try JavaScript click as fallback
                try:
                    self.driver.execute_script("arguments[0].click();", submit_btn)
                    self.logger.debug("Submitted captcha using JavaScript click")
                    clicked = True
                except Exception as js_error:
                    self.logger.error(f"JavaScript click also failed: {str(js_error)}")
                    # Last resort: try pressing Enter key on input field
                    try:
                        from selenium.webdriver.common.keys import Keys

                        captcha_input.send_keys(Keys.RETURN)
                        self.logger.debug("Submitted captcha using Enter key")
                        clicked = True
                    except BaseException:
                        pass

            if not clicked:
                self.logger.error("Failed to click submit button with all methods")
                return False

            random_delay(2, 3)

            # Check if captcha was solved successfully
            return self._verify_captcha_solved()

        except Exception as e:
            self.logger.error(f"Error submitting captcha: {str(e)}")
            return False

    def _close_error_modals(self):
        """Close any error modals/popups that appear after incorrect captcha"""
        try:
            self.logger.debug("Checking for error modals/popups...")

            # Wait a moment for modal to appear
            random_delay(0.5, 1)

            # Try multiple methods to close modals
            modal_closed = False

            # Method 1: Click close button with various selectors
            close_selectors = [
                (By.CSS_SELECTOR, ".modal .close"),
                (By.CSS_SELECTOR, "button.close"),
                (By.CSS_SELECTOR, ".close"),
                (By.XPATH, "//button[@data-dismiss='modal']"),
                (By.XPATH, "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]"),
                (By.XPATH, "//button[contains(text(), '×')]"),
                (By.XPATH, "//button[contains(text(), 'Close')]"),
                (By.XPATH, "//button[contains(text(), 'OK')]"),
            ]

            for by, selector in close_selectors:
                try:
                    close_btn = wait_for_element(self.driver, by, selector, timeout=1)
                    if close_btn and close_btn.is_displayed():
                        try:
                            # Try normal click
                            close_btn.click()
                            self.logger.debug(f"Closed modal using selector: {selector}")
                            modal_closed = True
                            random_delay(0.3, 0.5)
                            break
                        except BaseException:
                            # Try JavaScript click
                            try:
                                self.driver.execute_script("arguments[0].click();", close_btn)
                                self.logger.debug(f"Closed modal using JS click: {selector}")
                                modal_closed = True
                                random_delay(0.3, 0.5)
                                break
                            except BaseException:
                                continue
                except BaseException:
                    continue

            # Method 2: Press Escape key to close modal
            if not modal_closed:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    from selenium.webdriver.common.keys import Keys

                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ESCAPE).perform()
                    self.logger.debug("Sent ESC key to close modal")
                    random_delay(0.3, 0.5)
                    modal_closed = True
                except BaseException:
                    pass

            # Method 3: Click modal backdrop to close
            if not modal_closed:
                try:
                    backdrop_selectors = [
                        (By.CSS_SELECTOR, ".modal-backdrop"),
                        (By.CSS_SELECTOR, ".modal-overlay"),
                        (By.XPATH, "//div[contains(@class, 'modal-backdrop')]"),
                    ]

                    for by, selector in backdrop_selectors:
                        backdrop = wait_for_element(self.driver, by, selector, timeout=0.5)
                        if backdrop:
                            try:
                                self.driver.execute_script("arguments[0].click();", backdrop)
                                self.logger.debug("Clicked modal backdrop to close")
                                modal_closed = True
                                random_delay(0.3, 0.5)
                                break
                            except BaseException:
                                continue
                except BaseException:
                    pass

            # Method 4: Remove modal elements with JavaScript (aggressive)
            if not modal_closed:
                try:
                    # Remove modal elements from DOM
                    self.driver.execute_script(
                        """
                        // Remove modals
                        var modals = document.querySelectorAll('.modal, [class*="modal"]');
                        modals.forEach(function(modal) {
                            if (modal.style.display !== 'none') {
                                modal.remove();
                            }
                        });

                        // Remove backdrops
                        var backdrops = document.querySelectorAll('.modal-backdrop, [class*="backdrop"]');
                        backdrops.forEach(function(backdrop) {
                            backdrop.remove();
                        });

                        // Remove body classes that prevent scrolling
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                    """
                    )
                    self.logger.debug("Removed modal elements using JavaScript")
                    modal_closed = True
                    random_delay(0.3, 0.5)
                except Exception as e:
                    self.logger.debug(f"JS modal removal failed: {e}")

            if modal_closed:
                self.logger.debug("✓ Error modal closed successfully")
            else:
                self.logger.debug("No error modal found or already closed")

        except Exception as e:
            self.logger.debug(f"Error closing modals: {str(e)}")

    def _verify_captcha_solved(self, timeout: int = 10) -> bool:
        """
        Verify if captcha was solved successfully

        Args:
            timeout: Maximum wait time

        Returns:
            True if captcha solved, False otherwise
        """
        try:
            # Check for successful indicators
            success_indicators = [
                (By.CSS_SELECTOR, ".t-followers-button"),
                (By.CSS_SELECTOR, ".t-hearts-button"),
                (By.CSS_SELECTOR, ".colsmenu"),
                (By.XPATH, "//h5[contains(text(), 'Followers') or contains(text(), 'Hearts')]"),
            ]

            for by, selector in success_indicators:
                element = wait_for_element(self.driver, by, selector, timeout=timeout)
                if element:
                    return True

            # Check if still on captcha page
            captcha_still_present = wait_for_element(self.driver, By.ID, "captchatoken", timeout=2)

            # If captcha still present, close any error modals first
            if captcha_still_present:
                self.logger.debug("Captcha still present, closing any error modals...")
                self._close_error_modals()

            return not captcha_still_present

        except Exception as e:
            self.logger.error(f"Error verifying captcha: {str(e)}")
            return False

    def _refresh_captcha(self):
        """Refresh captcha image with modal handling"""
        try:
            # First, close any error modals/popups from incorrect captcha
            self.logger.debug("Closing any error modals before refresh...")
            self._close_error_modals()

            # Look for refresh button
            refresh_selectors = [
                (By.CSS_SELECTOR, ".refresh-capthca-btn"),
                (By.CSS_SELECTOR, "a.fa-refresh"),
                (By.XPATH, "//a[contains(@class, 'refresh')]"),
            ]

            for by, selector in refresh_selectors:
                refresh_btn = wait_for_element(self.driver, by, selector, timeout=3)
                if refresh_btn:
                    try:
                        # Scroll into view first
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", refresh_btn
                        )
                        random_delay(0.3, 0.5)

                        # Try normal click first
                        refresh_btn.click()
                        self.logger.debug("Refreshed captcha using normal click")
                        random_delay(1, 2)
                        return
                    except Exception as click_error:
                        # If normal click fails, try JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", refresh_btn)
                            self.logger.debug("Refreshed captcha using JavaScript click")
                            random_delay(1, 2)
                            return
                        except Exception as js_error:
                            self.logger.warning(
                                f"Failed to click refresh button: {str(click_error)}"
                            )
                            continue

            # If no refresh button worked, reload page
            self.logger.info("No refresh button found, reloading page...")
            self.driver.refresh()
            random_delay(2, 3)

        except Exception as e:
            self.logger.error(f"Error refreshing captcha: {str(e)}")
            # Fallback: just reload the page
            try:
                self.logger.info("Attempting page reload as fallback...")
                self.driver.refresh()
                random_delay(2, 3)
            except BaseException:
                pass

    def is_captcha_present(self, timeout: int = 3) -> bool:
        """
        Check if captcha is present on page

        Args:
            timeout: Maximum wait time

        Returns:
            True if captcha present, False otherwise
        """
        captcha_element = wait_for_element(self.driver, By.ID, "captchatoken", timeout=timeout)
        return captcha_element is not None
