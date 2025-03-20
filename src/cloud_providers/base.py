from abc import ABC, abstractmethod
from typing import Dict, Any

class CloudProvider(ABC):
    @abstractmethod
    def scale_out(self, count: int) -> None:
        """Scale out by specified number of nodes"""
        pass

    @abstractmethod
    def scale_in(self, count: int) -> None:
        """Scale in by specified number of nodes"""
        pass

    @abstractmethod
    def get_current_nodes(self) -> int:
        """Get current number of nodes in scaling group"""
        pass

    @abstractmethod
    def get_pricing_data(self) -> Dict[str, float]:
        """Return cloud-specific pricing information"""
        pass

    @abstractmethod
    def get_instance_lifecycle(self) -> Dict[str, float]:
        """Return instance lifecycle statistics"""
        pass

