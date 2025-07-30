"""Base classes for GPU backends"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class GPUMonitor(ABC):
    """Abstract base class for GPU monitoring"""
    
    @abstractmethod
    def get_temperature(self) -> float:
        pass
    
    @abstractmethod
    def get_power_usage(self) -> float:
        pass
    
    @abstractmethod
    def get_memory_info(self) -> Dict[str, float]:
        pass
    
    @abstractmethod
    def get_utilization(self) -> float:
        pass
    
    @abstractmethod
    def check_throttling(self) -> Tuple[bool, List[str]]:
        pass

class GPUBackend(ABC):
    """Abstract base class for GPU backends"""
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_device_count(self) -> int:
        pass
    
    @abstractmethod
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        pass
    
    @abstractmethod
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        pass
