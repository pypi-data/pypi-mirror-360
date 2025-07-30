class DualStackSettings:
    """Manages dual stack (IPv4/DualStack) user settings"""

    _instance = None

    def __init__(self):
        self._is_enabled = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_is_enabled(self, domain_details: dict) -> bool:
        """
        Sets the dualstack flag based on domain details.

        Args:
            domain_details (dict): Dictionary containing domain configuration

        Returns:
            bool: True if dualstack is enabled, False otherwise
        """
        if not isinstance(domain_details, dict) or domain_details is None:
            self._is_enabled = False
            return False

        ip_address_type = domain_details.get("IpAddressType")
        if not isinstance(ip_address_type, str):
            self._is_enabled = False
            return False

        self._is_enabled = ip_address_type.lower() == "dualstack"
        return self._is_enabled

    def is_enabled(self) -> bool:
        """
        Gets the dualstack flag status.

        Returns:
            bool: True if dualstack is enabled, False otherwise
        """
        return self._is_enabled
