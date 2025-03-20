from abc import ABC, abstractmethod
from typing import Dict, Any

class CloudProvider(ABC):
    @abstractmethod
    def get_instance_cost(self, instance_type: str) -> float:
        """Get hourly cost for specified instance type"""
        pass

    @abstractmethod
    def get_instance_specs(self, instance_type: str) -> Dict[str, Any]:
        """Get hardware specifications for instance type"""
        pass

