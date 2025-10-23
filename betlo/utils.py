"""
Utility functions for Zefoy Bot
"""

import random
import re
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def retry_on_exception(max_attempts: int = 3, delay: int = 2, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on exception

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """
    Random delay between actions

    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def human_typing(element, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
    """
    Type text like a human with random delays

    Args:
        element: Selenium WebElement
        text: Text to type
        min_delay: Minimum delay between keystrokes
        max_delay: Maximum delay between keystrokes
    """
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))


def wait_for_element(driver, by: By, value: str, timeout: int = 10, clickable: bool = False):
    """
    Wait for element to be present or clickable

    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator
        value: Locator value
        timeout: Maximum wait time in seconds
        clickable: Wait for element to be clickable

    Returns:
        WebElement if found, None otherwise
    """
    try:
        wait = WebDriverWait(driver, timeout)
        if clickable:
            element = wait.until(EC.element_to_be_clickable((by, value)))
        else:
            element = wait.until(EC.presence_of_element_located((by, value)))
        return element
    except TimeoutException:
        return None


def wait_for_elements(driver, by: By, value: str, timeout: int = 10):
    """
    Wait for multiple elements to be present

    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator
        value: Locator value
        timeout: Maximum wait time in seconds

    Returns:
        List of WebElements if found, empty list otherwise
    """
    try:
        wait = WebDriverWait(driver, timeout)
        elements = wait.until(EC.presence_of_all_elements_located((by, value)))
        return elements
    except TimeoutException:
        return []


def safe_click(driver, element, retries: int = 3):
    """
    Safely click an element with retries

    Args:
        driver: Selenium WebDriver instance
        element: WebElement to click
        retries: Number of retry attempts

    Returns:
        True if successful, False otherwise
    """
    for attempt in range(retries):
        try:
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            random_delay(0.3, 0.7)

            # Try to click
            element.click()
            return True

        except (StaleElementReferenceException, WebDriverException):
            if attempt < retries - 1:
                time.sleep(0.5)
            else:
                # Try JavaScript click as last resort
                try:
                    driver.execute_script("arguments[0].click();", element)
                    return True
                except BaseException:
                    return False
    return False


def is_element_visible(driver, by: By, value: str, timeout: int = 5) -> bool:
    """
    Check if element is visible

    Args:
        driver: Selenium WebDriver instance
        by: Selenium By locator
        value: Locator value
        timeout: Maximum wait time in seconds

    Returns:
        True if visible, False otherwise
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.visibility_of_element_located((by, value)))
        return True
    except TimeoutException:
        return False


def take_screenshot(driver, filepath: Optional[Path] = None, prefix: str = "screenshot") -> Path:
    """
    Take screenshot and save to file

    Args:
        driver: Selenium WebDriver instance
        filepath: Custom filepath (optional)
        prefix: Filename prefix if filepath not provided

    Returns:
        Path to saved screenshot
    """
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path("screenshots") / f"{prefix}_{timestamp}.png"

    filepath.parent.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(filepath))
    return filepath


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from TikTok URL

    Args:
        url: TikTok video URL

    Returns:
        Video ID if found, None otherwise
    """
    patterns = [
        r"tiktok\.com/@[\w.-]+/video/(\d+)",
        r"tiktok\.com/.*[?&]v=(\d+)",
        r"vm\.tiktok\.com/(\w+)",
        r"vt\.tiktok\.com/(\w+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def validate_tiktok_url(url: str) -> bool:
    """
    Validate TikTok URL format

    Args:
        url: TikTok URL to validate

    Returns:
        True if valid, False otherwise
    """
    patterns = [
        r"^https?://(www\.)?(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)",
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True

    return False


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp for logging

    Args:
        timestamp: Datetime object (uses current time if None)

    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()

    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def parse_time_remaining(text: str) -> Optional[int]:
    """
    Parse time remaining from text (e.g., "5 minutes", "30 seconds", "1 minute(s) 05 second(s)", "2m 16s")
    Supports very large numbers like "525249 minute(s) 38 seconds"

    Args:
        text: Text containing time information

    Returns:
        Time in seconds, None if not found
    """
    # Match patterns like "5 minutes", "30 seconds", "1 hour", "1 minute(s) 05 second(s)", "2m 16s"
    # Supports large numbers for extended cooldowns
    patterns = [
        # Hours - matches: "5 hours", "5 hour(s)", "5h", "5 h"
        (r"(\d+)\s*h(?:our)?(?:\(s\))?\s*", 3600),
        # Minutes - matches: "525249 minutes", "525249 minute(s)", "5m", "5 min"
        (r"(\d+)\s*m(?:in(?:ute)?)?(?:\(s\))?\s*", 60),
        # Seconds - matches: "38 seconds", "38 second(s)", "38s", "38 sec"
        (r"(\d+)\s*s(?:ec(?:ond)?)?(?:\(s\))?\s*", 1),
    ]

    total_seconds = 0
    found = False
    text_lower = text.lower()

    for pattern, multiplier in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                value = int(match)
                total_seconds += value * multiplier
                found = True
            except (ValueError, OverflowError) as e:
                # Handle extremely large numbers that might cause overflow
                import logging

                logging.getLogger(__name__).warning(f"Could not parse time value '{match}': {e}")
                continue

    return total_seconds if found else None


def clean_string(text: str) -> str:
    """
    Clean string by removing extra whitespace and special characters

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = " ".join(text.split())
    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^\w\s.,!?-]", "", text)
    return text.strip()


def get_timestamp_filename(prefix: str = "", extension: str = "txt") -> str:
    """
    Generate filename with timestamp

    Args:
        prefix: Filename prefix
        extension: File extension

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if prefix:
        return f"{prefix}_{timestamp}.{extension}"
    return f"{timestamp}.{extension}"


def scroll_to_bottom(driver, scroll_pause_time: float = 1.0, max_scrolls: int = 10):
    """
    Scroll to bottom of page

    Args:
        driver: Selenium WebDriver instance
        scroll_pause_time: Pause time between scrolls
        max_scrolls: Maximum number of scrolls
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0

    while scrolls < max_scrolls:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        # Calculate new height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height
        scrolls += 1


def create_safe_filename(text: str, max_length: int = 50) -> str:
    """
    Create safe filename from text

    Args:
        text: Text to convert
        max_length: Maximum filename length

    Returns:
        Safe filename
    """
    # Remove invalid characters
    safe_text = re.sub(r'[<>:"/\\|?*]', "", text)
    # Replace spaces with underscores
    safe_text = safe_text.replace(" ", "_")
    # Truncate if too long
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length]

    return safe_text


def countdown_timer(seconds: int, message: str = "Waiting"):
    """
    Display countdown timer in terminal

    Args:
        seconds: Number of seconds to count down
        message: Message to display
    """
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn

    console = Console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TextColumn("[yellow]{task.fields[time_left]}"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task(f"[cyan]{message}...", total=seconds, time_left=f"{seconds}s")

        for i in range(seconds):
            time_left = seconds - i
            mins, secs = divmod(time_left, 60)
            hours, mins = divmod(mins, 60)

            if hours > 0:
                time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            elif mins > 0:
                time_str = f"{mins:02d}:{secs:02d}"
            else:
                time_str = f"{secs}s"

            progress.update(task, completed=i + 1, time_left=time_str)
            time.sleep(1)


def format_time_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string (e.g., "1h 5m 30s")
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def format_time_user_friendly(seconds: int) -> str:
    """
    Format seconds into very user-friendly duration for long cooldowns
    Shows the most significant time units for better readability

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string (e.g., "5 days 3 hours", "2 months 15 days", "1 year 2 months")
    """
    if seconds < 60:
        # Less than 1 minute
        return f"{seconds} second{'s' if seconds != 1 else ''}"

    if seconds < 3600:
        # Less than 1 hour - show minutes and seconds
        minutes = seconds // 60
        secs = seconds % 60
        if secs > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} {secs} second{'s' if secs != 1 else ''}"
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

    if seconds < 86400:
        # Less than 1 day - show hours and minutes
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        return f"{hours} hour{'s' if hours != 1 else ''}"

    if seconds < 2592000:  # Less than 30 days
        # Show days and hours
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        if hours > 0:
            return f"{days} day{'s' if days != 1 else ''} {hours} hour{'s' if hours != 1 else ''}"
        return f"{days} day{'s' if days != 1 else ''}"

    if seconds < 31536000:  # Less than 365 days
        # Show months and days (approximate: 1 month = 30 days)
        months = seconds // 2592000
        days = (seconds % 2592000) // 86400
        if days > 0:
            return (
                f"{months} month{'s' if months != 1 else ''} {days} day{'s' if days != 1 else ''}"
            )
        return f"{months} month{'s' if months != 1 else ''}"

    # 1 year or more - show years and months
    years = seconds // 31536000
    months = (seconds % 31536000) // 2592000
    if months > 0:
        return f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"
    return f"{years} year{'s' if years != 1 else ''}"


class RateLimiter:
    """Simple rate limiter to prevent too many requests"""

    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply rate limiting"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls outside time window
            self.calls = [
                call_time for call_time in self.calls if now - call_time < self.time_window
            ]

            # Check if we've exceeded the limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    self.calls = []

            # Record this call
            self.calls.append(now)

            return func(*args, **kwargs)

        return wrapper

    def wait_if_needed(self):
        """Wait if rate limit is reached"""
        now = time.time()

        # Remove old calls
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.time_window - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.calls = []

        self.calls.append(now)
