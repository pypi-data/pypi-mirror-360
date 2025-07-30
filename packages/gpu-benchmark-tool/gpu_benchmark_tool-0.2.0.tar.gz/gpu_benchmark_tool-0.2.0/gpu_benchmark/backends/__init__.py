"""GPU Backend Management"""

from typing import Optional, List, Dict
from .base import GPUBackend, GPUMonitor
from .mock import MockBackend

# Import backends with availability checks
backends_available = {
    "mock": True,
    "nvidia": False,
    "amd": False,
    "intel": False
}

# Try to import NVIDIA backend
try:
    from .nvidia import NVIDIABackend
    backends_available["nvidia"] = True
except ImportError:
    NVIDIABackend = None

# Try to import AMD backend
try:
    from .amd import AMDBackend
    backends_available["amd"] = True
except ImportError:
    AMDBackend = None

# Try to import Intel backend
try:
    from .intel import IntelBackend
    backends_available["intel"] = True
except ImportError:
    IntelBackend = None


def get_gpu_backend(backend_type: str = "auto", device_id: int = 0) -> Optional[GPUBackend]:
    """
    Get appropriate GPU backend
    
    Args:
        backend_type: "auto", "nvidia", "amd", "intel", or "mock"
        device_id: GPU device ID
    
    Returns:
        GPUBackend instance or None
    """
    
    if backend_type == "mock":
        return MockBackend()
    
    if backend_type == "auto":
        # Try backends in order of preference
        backend_classes = []
        
        if backends_available["nvidia"] and NVIDIABackend:
            backend_classes.append(NVIDIABackend)
        if backends_available["amd"] and AMDBackend:
            backend_classes.append(AMDBackend)
        if backends_available["intel"] and IntelBackend:
            backend_classes.append(IntelBackend)
            
        for backend_class in backend_classes:
            try:
                backend = backend_class()
                if backend.is_available():
                    return backend
            except Exception:
                continue
        
        # If no real backend available, return mock
        return MockBackend()
    
    elif backend_type == "nvidia" and backends_available["nvidia"] and NVIDIABackend:
        backend = NVIDIABackend()
        if backend.is_available():
            return backend
            
    elif backend_type == "amd" and backends_available["amd"] and AMDBackend:
        backend = AMDBackend()
        if backend.is_available():
            return backend
            
    elif backend_type == "intel" and backends_available["intel"] and IntelBackend:
        backend = IntelBackend()
        if backend.is_available():
            return backend
    
    return None


def list_available_backends() -> List[Dict[str, any]]:
    """List all available GPU backends on this system"""
    available = []
    
    # Always include mock
    mock = MockBackend()
    available.append({
        "type": "mock",
        "device_count": mock.get_device_count()
    })
    
    # Check for real backends
    backend_checks = [
        ("nvidia", NVIDIABackend),
        ("amd", AMDBackend),
        ("intel", IntelBackend)
    ]
    
    for backend_name, backend_class in backend_checks:
        if backends_available[backend_name] and backend_class:
            try:
                backend = backend_class()
                if backend.is_available():
                    available.append({
                        "type": backend_name,
                        "device_count": backend.get_device_count()
                    })
            except Exception:
                pass
    
    return available


__all__ = [
    "GPUBackend",
    "GPUMonitor", 
    "get_gpu_backend",
    "list_available_backends",
    "MockBackend",
    "backends_available"
]
