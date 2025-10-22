"""
Beautiful colored logger for Zefoy Bot using Rich library
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich import box
from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# Custom log level for MAIN (user-friendly logging)
MAIN_LEVEL = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(MAIN_LEVEL, "MAIN")

# Custom theme for the bot
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "critical": "red bold reverse",
        "success": "green bold",
        "debug": "magenta",
        "highlight": "blue bold",
        "main": "white",  # Simple white for main messages
    }
)

# Create console with custom theme
console = Console(theme=custom_theme)


class MainRichHandler(RichHandler):
    """Custom RichHandler for MAIN level - simpler, cleaner output"""

    def emit(self, record):
        """Emit a record with simplified format for MAIN level"""
        if record.levelno == MAIN_LEVEL:
            # For MAIN level, hide timestamp and level name
            record.show_time = False
            record.show_level = False
            record.show_path = False
        super().emit(record)


class BotLogger:
    """Custom logger with beautiful colored output"""

    def __init__(self, name: str = "ZefoyBot", log_file: Optional[str] = None, level: str = "MAIN"):
        """
        Initialize the logger

        Args:
            name: Logger name
            log_file: Path to log file (optional)
            level: Logging level (MAIN, DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)

        # Handle MAIN level
        if level.upper() == "MAIN":
            self.logger.setLevel(MAIN_LEVEL)
        else:
            self.logger.setLevel(getattr(logging, level.upper()))

        self.logger.handlers.clear()

        # Rich handler for console with custom handler for MAIN level
        rich_handler = MainRichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True,
            show_time=True,
            show_level=True,
            show_path=False,
        )
        rich_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(rich_handler)

        # File handler if log file is specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            self.logger.addHandler(file_handler)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(f"[info]ℹ {message}[/info]", extra={"markup": True}, **kwargs)

    def success(self, message: str, **kwargs):
        """Log success message"""
        self.logger.info(f"[success]✓ {message}[/success]", extra={"markup": True}, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(f"[warning]⚠ {message}[/warning]", extra={"markup": True}, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(f"[error]✗ {message}[/error]", extra={"markup": True}, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(f"[critical]💀 {message}[/critical]", extra={"markup": True}, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(f"[debug]🔍 {message}[/debug]", extra={"markup": True}, **kwargs)

    def main(self, message: str, icon: str = "▶", **kwargs):
        """
        Log main message - simple, clean, user-friendly
        For MAIN level, only essential messages are shown

        Args:
            message: The message to log
            icon: Icon to show (default: ▶)
        """
        self.logger.log(
            MAIN_LEVEL, f"[main]{icon} {message}[/main]", extra={"markup": True}, **kwargs
        )

    def highlight(self, message: str, **kwargs):
        """Log highlighted message"""
        self.logger.info(f"[highlight]★ {message}[/highlight]", extra={"markup": True}, **kwargs)


class BotUI:
    """Beautiful UI components for the bot"""

    @staticmethod
    def print_header(text: str, style: str = "bold blue"):
        """Print section header"""
        console.print()
        console.print(
            Panel(
                Align.center(Text(text, style="bold white")),
                box=box.ROUNDED,
                style=style,
                border_style=style,
                padding=(0, 2),
            )
        )
        console.print()

    @staticmethod
    def print_panel(text: str, title: str = "", style: str = "cyan", expand: bool = False):
        """Print text in a panel"""
        console.print(
            Panel(
                text,
                title=title,
                title_align="left",
                style=style,
                box=box.ROUNDED,
                border_style=style,
                padding=(1, 2),
                expand=expand,
            )
        )

    @staticmethod
    def print_success_panel(text: str, title: str = "✓ Success"):
        """Print success panel"""
        console.print(
            Panel(
                text,
                title=f"[bold green]{title}[/bold green]",
                title_align="left",
                style="green",
                box=box.ROUNDED,
                border_style="bright_green",
                padding=(1, 2),
            )
        )

    @staticmethod
    def print_error_panel(text: str, title: str = "✗ Error"):
        """Print error panel"""
        console.print(
            Panel(
                text,
                title=f"[bold red]{title}[/bold red]",
                title_align="left",
                style="red",
                box=box.ROUNDED,
                border_style="bright_red",
                padding=(1, 2),
            )
        )

    @staticmethod
    def print_warning_panel(text: str, title: str = "⚠ Warning"):
        """Print warning panel"""
        console.print(
            Panel(
                text,
                title=f"[bold yellow]{title}[/bold yellow]",
                title_align="left",
                style="yellow",
                box=box.ROUNDED,
                border_style="bright_yellow",
                padding=(1, 2),
            )
        )

    @staticmethod
    def print_info_panel(text: str, title: str = "ℹ Info"):
        """Print info panel"""
        console.print(
            Panel(
                text,
                title=f"[bold cyan]{title}[/bold cyan]",
                title_align="left",
                style="cyan",
                box=box.ROUNDED,
                border_style="bright_cyan",
                padding=(1, 2),
            )
        )

    @staticmethod
    def print_table(title: str, columns: list, rows: list):
        """Print a table"""
        from rich.table import Table

        table = Table(
            title=f"[bold cyan]{title}[/bold cyan]",
            box=box.HEAVY_HEAD,
            show_header=True,
            header_style="bold white on blue",
            border_style="bright_cyan",
            title_style="bold cyan",
            padding=(0, 1),
            show_lines=True,
        )

        for column in columns:
            table.add_column(column, style="cyan", no_wrap=False)

        for i, row in enumerate(rows):
            # Alternate row colors for better readability
            row_style = "on grey11" if i % 2 == 0 else ""
            table.add_row(*[str(item) for item in row], style=row_style)

        console.print()
        console.print(table)
        console.print()

    @staticmethod
    def print_progress(text: str):
        """Print progress message with spinner-like effect"""
        console.print(
            Panel(f"[cyan]⏳ {text}...[/cyan]", box=box.ROUNDED, border_style="cyan", padding=(0, 2))
        )

    @staticmethod
    def print_separator(style: str = "bright_blue"):
        """Print separator line"""
        console.print(Panel("", box=box.SIMPLE, style=style, border_style=style, padding=(0, 0)))

    @staticmethod
    def print_step(step_num: int, total_steps: int, message: str):
        """Print step progress"""
        step_text = Text()
        step_text.append(f"[{step_num}/{total_steps}] ", style="bold yellow")
        step_text.append(message, style="cyan")

        console.print(Panel(step_text, box=box.ROUNDED, border_style="yellow", padding=(0, 2)))

    @staticmethod
    def clear_screen():
        """Clear the console screen"""
        console.clear()

    @staticmethod
    def ask_confirm(question: str, default: bool = False) -> bool:
        """
        Ask for confirmation

        Args:
            question: Question to ask
            default: Default answer

        Returns:
            User's answer as boolean
        """
        from rich.prompt import Confirm

        return Confirm.ask(question, default=default, console=console)

    @staticmethod
    def ask_input(question: str, default: str = "") -> str:
        """
        Ask for input

        Args:
            question: Question to ask
            default: Default answer

        Returns:
            User's input
        """
        from rich.prompt import Prompt

        return Prompt.ask(question, default=default, console=console)

    @staticmethod
    def ask_choice(question: str, choices: list) -> str:
        """
        Ask for choice from list

        Args:
            question: Question to ask
            choices: List of choices

        Returns:
            Selected choice
        """
        from rich.prompt import Prompt

        return Prompt.ask(question, choices=choices, console=console)


# Create global logger instance
def get_logger(
    name: str = "ZefoyBot", log_file: Optional[str] = None, level: str = "INFO"
) -> BotLogger:
    """
    Get logger instance

    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level

    Returns:
        BotLogger instance
    """
    return BotLogger(name=name, log_file=log_file, level=level)


def print_header(text: str, style: str = "bold blue"):
    """Print section header"""
    BotUI.print_header(text, style)


def print_success(text: str):
    """Print success message in a box"""
    console.print(
        Panel(
            f"[bold green]✓[/bold green] {text}",
            box=box.ROUNDED,
            border_style="bright_green",
            padding=(0, 2),
        )
    )


def print_error(text: str):
    """Print error message in a box"""
    console.print(
        Panel(
            f"[bold red]✗[/bold red] {text}",
            box=box.ROUNDED,
            border_style="bright_red",
            padding=(0, 2),
        )
    )


def print_warning(text: str):
    """Print warning message in a box"""
    console.print(
        Panel(
            f"[bold yellow]⚠[/bold yellow] {text}",
            box=box.ROUNDED,
            border_style="bright_yellow",
            padding=(0, 2),
        )
    )


def print_info(text: str):
    """Print info message in a box"""
    console.print(
        Panel(
            f"[bold cyan]ℹ[/bold cyan] {text}",
            box=box.ROUNDED,
            border_style="bright_cyan",
            padding=(0, 2),
        )
    )
