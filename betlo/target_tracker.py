"""
Target tracker for managing service goals
"""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple


class TargetTracker:
    """Track progress toward service targets"""

    def __init__(self, config):
        """
        Initialize target tracker

        Args:
            config: Configuration object
        """
        self.config = config
        self.targets = {}
        self.current_progress = {}
        self.load_targets()

    def load_targets(self):
        """Load targets from configuration"""
        targets_config = self.config.get("service_targets", {})

        # Map service names to config keys
        service_map = {
            "Followers": "followers",
            "Hearts": "hearts",
            "Comments Hearts": "comments_hearts",
            "Views": "views",
            "Shares": "shares",
            "Favorites": "favorites",
            "Live Stream": "livestream",
        }

        for service_name, config_key in service_map.items():
            target = targets_config.get(config_key, 0)
            per_exec = targets_config.get("per_execution", {}).get(config_key, 100)

            self.targets[service_name] = {
                "target": target,
                "per_execution": per_exec,
                "current": 0,
                "executions": 0,
            }

    def get_target(self, service_name: str) -> int:
        """
        Get target for service

        Args:
            service_name: Service name

        Returns:
            Target amount (0 if no target set)
        """
        if service_name in self.targets:
            return self.targets[service_name]["target"]
        return 0

    def get_estimated_executions(self, service_name: str) -> int:
        """
        Calculate estimated number of executions needed to reach target

        Args:
            service_name: Service name

        Returns:
            Estimated executions needed
        """
        if service_name not in self.targets:
            return 1

        target_data = self.targets[service_name]
        target = target_data["target"]
        current = target_data["current"]
        per_exec = target_data["per_execution"]

        if target == 0 or per_exec == 0:
            return 1

        remaining = max(0, target - current)
        executions_needed = (remaining + per_exec - 1) // per_exec  # Ceiling division

        return max(1, executions_needed)

    def update_progress(self, service_name: str, amount: int):
        """
        Update progress for service

        Args:
            service_name: Service name
            amount: Amount to add to progress
        """
        if service_name in self.targets:
            self.targets[service_name]["current"] += amount
            self.targets[service_name]["executions"] += 1

    def get_progress(self, service_name: str) -> Dict:
        """
        Get progress information for service

        Args:
            service_name: Service name

        Returns:
            Dict with target, current, percentage, etc
        """
        if service_name not in self.targets:
            return {"target": 0, "current": 0, "percentage": 0, "remaining": 0, "executions": 0}

        data = self.targets[service_name]
        target = data["target"]
        current = data["current"]

        if target == 0:
            percentage = 0
            remaining = 0
        else:
            percentage = min(100, (current / target) * 100)
            remaining = max(0, target - current)

        return {
            "target": target,
            "current": current,
            "percentage": percentage,
            "remaining": remaining,
            "executions": data["executions"],
            "per_execution": data["per_execution"],
        }

    def is_target_reached(self, service_name: str) -> bool:
        """
        Check if target is reached for service

        Args:
            service_name: Service name

        Returns:
            True if target reached or no target set
        """
        if service_name not in self.targets:
            return False

        data = self.targets[service_name]

        # No target set (0 = unlimited)
        if data["target"] == 0:
            return False

        return data["current"] >= data["target"]

    def extract_amount_from_response(self, response_text: str, service_name: str) -> int:
        """
        Extract amount sent from response text

        Args:
            response_text: Response text from server
            service_name: Service name

        Returns:
            Amount extracted (or estimated amount if can't parse)
        """
        # Try to extract numbers from response
        # Common patterns: "100 hearts sent", "Sent 1000 views", "+50 followers"
        patterns = [
            r"(\d+)\s*(?:hearts?|likes?|views?|shares?|favorites?|followers?)\s+(?:sent|added)",
            r"(?:sent|added)\s+(\d+)",
            r"\+\s*(\d+)",
            r"successfully.*?(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text.lower())
            if match:
                try:
                    return int(match.group(1))
                except BaseException:
                    pass

        # If can't extract, use estimated per_execution amount
        if service_name in self.targets:
            return self.targets[service_name]["per_execution"]

        return 100  # Default fallback

    def format_progress_bar(self, service_name: str, width: int = 40) -> str:
        """
        Generate progress bar string

        Args:
            service_name: Service name
            width: Width of progress bar

        Returns:
            Formatted progress bar
        """
        progress = self.get_progress(service_name)
        percentage = progress["percentage"]

        filled = int((percentage / 100) * width)
        empty = width - filled

        bar = "█" * filled + "░" * empty

        return f"[{bar}] {percentage:.1f}%"

    def get_summary(self, service_name: str) -> str:
        """
        Get summary string for service

        Args:
            service_name: Service name

        Returns:
            Summary string
        """
        progress = self.get_progress(service_name)

        if progress["target"] == 0:
            return f"Current: {progress['current']:,} (No target set)"

        return (
            f"{progress['current']:,} / {progress['target']:,} "
            f"({progress['percentage']:.1f}%) - "
            f"Remaining: {progress['remaining']:,}"
        )

    def reset_progress(self, service_name: Optional[str] = None):
        """
        Reset progress for service or all services

        Args:
            service_name: Service name (None = reset all)
        """
        if service_name:
            if service_name in self.targets:
                self.targets[service_name]["current"] = 0
                self.targets[service_name]["executions"] = 0
        else:
            for service in self.targets:
                self.targets[service]["current"] = 0
                self.targets[service]["executions"] = 0

    def save_progress(self, filepath: str = "target_progress.json"):
        """
        Save progress to file

        Args:
            filepath: Path to save file
        """
        import json
        from pathlib import Path

        data = {"last_updated": datetime.now().isoformat(), "services": self.targets}

        Path(filepath).write_text(json.dumps(data, indent=2))

    def load_progress(self, filepath: str = "target_progress.json"):
        """
        Load progress from file

        Args:
            filepath: Path to load file
        """
        import json
        from pathlib import Path

        try:
            if Path(filepath).exists():
                data = json.loads(Path(filepath).read_text())

                # Merge saved progress with current targets
                for service_name, saved_data in data.get("services", {}).items():
                    if service_name in self.targets:
                        self.targets[service_name]["current"] = saved_data.get("current", 0)
                        self.targets[service_name]["executions"] = saved_data.get("executions", 0)
        except Exception as e:
            # Silently fail if can't load
            pass
