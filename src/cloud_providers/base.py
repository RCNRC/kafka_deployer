from abc import ABC, abstractmethod
from typing import Dict, Any

class CloudProvider(ABC):
    """Abstract base class for cloud provider implementations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def provision_infrastructure(self) -> Dict[str, str]:
        """Provision cloud infrastructure and return connection details"""
        pass
    
    @abstractmethod
    def configure_kafka_cluster(self) -> None:
        """Configure managed Kafka service or equivalent"""
        pass
    
    @abstractmethod
    def cleanup_resources(self) -> None:
        """Cleanup all provisioned resources"""
        pass

class CloudError(Exception):
    """Base exception for cloud provider errors"""
    def __init__(self, code: int, message: str):
        super().__init__(f"[CLOUD-{code}] {message}")
        self.error_code = code
