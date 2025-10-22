"""
Configuration manager for Zefoy Bot
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


class Config:
    """Configuration class to manage bot settings"""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration

        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"

        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'browser.headless')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'browser.headless')
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save_config(self):
        """Save configuration to YAML file"""
        with open(self.config_path, "w", encoding="utf-8") as file:
            yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)

    @property
    def browser_headless(self) -> bool:
        """Get browser headless setting"""
        return self.get("browser.headless", False)

    @property
    def browser_window_size(self) -> str:
        """Get browser window size"""
        return self.get("browser.window_size", "1920,1080")

    @property
    def use_adblock(self) -> bool:
        """Get adblock usage setting"""
        return self.get("browser.use_adblock", True)

    @property
    def zefoy_url(self) -> str:
        """Get Zefoy URL"""
        return self.get("zefoy.url", "https://zefoy.com")

    @property
    def enabled_services(self) -> list:
        """Get list of enabled services"""
        services = self.get("zefoy.services", [])
        return [s for s in services if s.get("enabled", False)]

    @property
    def all_services(self) -> list:
        """Get all services"""
        return self.get("zefoy.services", [])

    @property
    def screenshot_path(self) -> Path:
        """Get screenshots directory path"""
        path = Path(self.get("paths.screenshots", "screenshots"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_path(self) -> Path:
        """Get logs directory path"""
        path = Path(self.get("paths.logs", "logs"))
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def extensions_path(self) -> Path:
        """Get extensions directory path"""
        path = Path(self.get("paths.extensions", "extensions"))
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global config instance
config = Config()
