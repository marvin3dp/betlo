"""
Service manager for controlling which services are active
"""

from typing import Dict, List, Optional


class ServiceManager:
    """Manage active services and service selection"""

    def __init__(self, config):
        """
        Initialize service manager

        Args:
            config: Configuration object
        """
        self.config = config
        self.active_service = None
        self.load_active_service()

    def load_active_service(self):
        """Load active service from config"""
        self.active_service = self.config.get("active_service", None)

    def set_active_service(self, service_name: Optional[str] = None):
        """
        Set active service (only this service will be available)

        Args:
            service_name: Service name to activate (None = all services)
        """
        self.active_service = service_name
        self.config.set("active_service", service_name)
        self.config.save_config()

    def get_active_service(self) -> Optional[str]:
        """
        Get current active service

        Returns:
            Active service name or None (all active)
        """
        return self.active_service

    def is_service_active(self, service_name: str) -> bool:
        """
        Check if a service is currently active

        Args:
            service_name: Service name to check

        Returns:
            True if service is active
        """
        # If no active service set, check if enabled
        if self.active_service is None:
            service = self._find_service(service_name)
            if service:
                return service.get("enabled", False)
            return False

        # If active service set, only that service is active
        return service_name == self.active_service

    def get_available_services(self) -> List[Dict]:
        """
        Get list of available services based on active service setting

        Returns:
            List of service configurations
        """
        all_services = self.config.all_services

        if self.active_service is None:
            # Return all enabled services
            return [s for s in all_services if s.get("enabled", False)]
        else:
            # Return only active service if it exists
            active = self._find_service(self.active_service)
            return [active] if active else []

    def get_all_service_names(self) -> List[str]:
        """
        Get all service names

        Returns:
            List of service names
        """
        return [s["name"] for s in self.config.all_services]

    def _find_service(self, service_name: str) -> Optional[Dict]:
        """Find service by name"""
        for service in self.config.all_services:
            if service["name"].lower() == service_name.lower():
                return service
        return None

    def get_service_status_summary(self) -> Dict:
        """
        Get summary of service statuses

        Returns:
            Dictionary with service status info
        """
        all_services = self.config.all_services

        summary = {
            "total_services": len(all_services),
            "enabled_services": len([s for s in all_services if s.get("enabled", False)]),
            "active_service": self.active_service,
            "mode": "Single Service Mode" if self.active_service else "All Services Mode",
            "available_count": len(self.get_available_services()),
        }

        return summary

    def enable_service(self, service_name: str):
        """
        Enable a service

        Args:
            service_name: Service name to enable
        """
        for service in self.config.all_services:
            if service["name"].lower() == service_name.lower():
                service["enabled"] = True
                self.config.save_config()
                return True
        return False

    def disable_service(self, service_name: str):
        """
        Disable a service

        Args:
            service_name: Service name to disable
        """
        for service in self.config.all_services:
            if service["name"].lower() == service_name.lower():
                service["enabled"] = False
                self.config.save_config()
                return True
        return False

    def enable_only_one(self, service_name: str):
        """
        Disable all services except one

        Args:
            service_name: Service name to keep enabled
        """
        for service in self.config.all_services:
            if service["name"].lower() == service_name.lower():
                service["enabled"] = True
            else:
                service["enabled"] = False

        self.config.save_config()

    def switch_to_service(self, service_name: str):
        """
        Switch active service (set as active service and enable it)

        Args:
            service_name: Service name to switch to
        """
        # Set as active service
        self.set_active_service(service_name)

        # Ensure it's enabled
        self.enable_service(service_name)

        return True

    def clear_active_service(self):
        """Clear active service (enable all mode)"""
        self.set_active_service(None)
