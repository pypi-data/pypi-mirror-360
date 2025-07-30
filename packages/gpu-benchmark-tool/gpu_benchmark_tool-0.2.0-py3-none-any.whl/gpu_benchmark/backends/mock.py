"""Mock GPU backend for testing"""

import random
import time
from typing import Dict, List, Tuple
from .base import GPUBackend, GPUMonitor

class MockGPUMonitor(GPUMonitor):
    """Simulated GPU monitor"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.base_temp = 45.0
        self.start_time = time.time()
        
    def get_temperature(self) -> float:
        elapsed = time.time() - self.start_time
        temp_rise = min(elapsed * 0.5, 30)
        return self.base_temp + temp_rise + random.uniform(-2, 2)
    
    def get_power_usage(self) -> float:
        base_power = 50.0
        elapsed = time.time() - self.start_time
        load_power = min(elapsed * 2, 100)
        return base_power + load_power + random.uniform(-5, 5)
    
    def get_memory_info(self) -> Dict[str, float]:
        return {
            "used_mb": 4096,
            "total_mb": 8192,
            "free_mb": 4096,
            "utilization_pct": 50.0
        }
    
    def get_utilization(self) -> float:
        elapsed = time.time() - self.start_time
        if elapsed < 5:
            return random.uniform(0, 20)
        else:
            return random.uniform(85, 99)
    
    def check_throttling(self) -> Tuple[bool, List[str]]:
        temp = self.get_temperature()
        if temp > 80:
            return True, ["Thermal limit (simulated)"]
        return False, []

class MockBackend(GPUBackend):
    """Mock GPU backend"""
    
    def is_available(self) -> bool:
        return True
    
    def get_device_count(self) -> int:
        return 1
    
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        return {
            "name": f"Mock GPU {device_id}",
            "compute_capability": "8.6",
            "total_memory_gb": 8.0,
            "vendor": "Mock",
            "backend": "Simulation"
        }
    
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        device_id = device_handle_or_id if isinstance(device_handle_or_id, int) else 0
        return MockGPUMonitor(device_id)
