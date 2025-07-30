"""NVIDIA GPU Backend"""

from typing import Dict, List, Tuple
from .base import GPUBackend, GPUMonitor

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False


class NVIDIAMonitor(GPUMonitor):
    """NVIDIA GPU monitoring using NVML"""
    
    def __init__(self, handle):
        self.handle = handle
        self.throttle_reasons = {}
        
        if PYNVML_AVAILABLE:
            self.throttle_reasons = {
                pynvml.nvmlClocksThrottleReasonGpuIdle: "GPU Idle",
                pynvml.nvmlClocksThrottleReasonApplicationsClocksSetting: "Applications Clocks Setting",
                pynvml.nvmlClocksThrottleReasonSwPowerCap: "SW Power Cap",
                pynvml.nvmlClocksThrottleReasonHwSlowdown: "HW Slowdown",
                pynvml.nvmlClocksThrottleReasonSyncBoost: "Sync Boost",
                pynvml.nvmlClocksThrottleReasonSwThermalSlowdown: "SW Thermal Slowdown",
                pynvml.nvmlClocksThrottleReasonHwThermalSlowdown: "HW Thermal Slowdown",
                pynvml.nvmlClocksThrottleReasonHwPowerBrakeSlowdown: "HW Power Brake Slowdown",
                pynvml.nvmlClocksThrottleReasonDisplayClocksSetting: "Display Clocks Setting",
            }
    
    def get_temperature(self) -> float:
        try:
            return pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
        except pynvml.NVMLError:
            return -1
    
    def get_power_usage(self) -> float:
        try:
            return pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000
        except pynvml.NVMLError:
            return -1
    
    def get_memory_info(self) -> Dict[str, float]:
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return {
                "used_mb": mem_info.used / (1024**2),
                "total_mb": mem_info.total / (1024**2),
                "free_mb": mem_info.free / (1024**2),
                "utilization_pct": (mem_info.used / mem_info.total) * 100
            }
        except pynvml.NVMLError:
            return {"used_mb": -1, "total_mb": -1, "free_mb": -1, "utilization_pct": -1}
    
    def get_utilization(self) -> float:
        try:
            return pynvml.nvmlDeviceGetUtilizationRates(self.handle).gpu
        except pynvml.NVMLError:
            return -1
    
    def check_throttling(self) -> Tuple[bool, List[str]]:
        """Check if GPU is throttling and return reasons"""
        try:
            throttle_reasons = pynvml.nvmlDeviceGetCurrentClocksThrottleReasons(self.handle)
            active_reasons = []
            
            for reason, name in self.throttle_reasons.items():
                if throttle_reasons & reason:
                    active_reasons.append(name)
            
            return len(active_reasons) > 0, active_reasons
        except pynvml.NVMLError:
            return False, []
    
    def get_memory_bandwidth(self) -> float:
        """Get current memory bandwidth utilization"""
        try:
            return pynvml.nvmlDeviceGetUtilizationRates(self.handle).memory
        except pynvml.NVMLError:
            return -1


class NVIDIABackend(GPUBackend):
    """NVIDIA GPU backend using CUDA/PyTorch"""
    
    def __init__(self):
        self.initialized = False
        
    def _ensure_initialized(self):
        """Ensure NVML is initialized"""
        if not self.initialized and PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.initialized = True
            except pynvml.NVMLError:
                pass
    
    def is_available(self) -> bool:
        """Check if NVIDIA GPUs are available"""
        if not PYNVML_AVAILABLE:
            return False
            
        self._ensure_initialized()
        
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            return device_count > 0
        except pynvml.NVMLError:
            return False
    
    def get_device_count(self) -> int:
        """Get number of NVIDIA GPUs"""
        if not self.is_available():
            return 0
            
        try:
            return pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError:
            return 0
    
    def get_device_info(self, device_id: int) -> Dict[str, any]:
        """Get NVIDIA GPU information"""
        self._ensure_initialized()
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            # Get memory info
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            # Get compute capability if PyTorch is available
            compute_capability = "Unknown"
            cuda_cores = -1
            
            if TORCH_AVAILABLE:
                props = torch.cuda.get_device_properties(device_id)
                compute_capability = f"{props.major}.{props.minor}"
                cuda_cores = props.multi_processor_count * self._get_cuda_cores_per_sm(props.major)
            
            return {
                "name": name,
                "compute_capability": compute_capability,
                "total_memory_gb": mem_info.total / 1e9,
                "cuda_cores": cuda_cores,
                "vendor": "NVIDIA",
                "backend": "CUDA"
            }
            
        except pynvml.NVMLError as e:
            return {"error": str(e)}
    
    def create_monitor(self, device_handle_or_id) -> GPUMonitor:
        """Create NVIDIA GPU monitor"""
        self._ensure_initialized()
        
        # If integer, get handle
        if isinstance(device_handle_or_id, int):
            device_handle_or_id = pynvml.nvmlDeviceGetHandleByIndex(device_handle_or_id)
            
        return NVIDIAMonitor(device_handle_or_id)
    
    def _get_cuda_cores_per_sm(self, major: int) -> int:
        """Get CUDA cores per SM based on compute capability"""
        cuda_cores_per_sm = {
            3: 192,  # Kepler
            5: 128,  # Maxwell
            6: 64,   # Pascal
            7: 64,   # Volta/Turing
            8: 64,   # Ampere
            9: 128   # Hopper
        }
        return cuda_cores_per_sm.get(major, 64)
