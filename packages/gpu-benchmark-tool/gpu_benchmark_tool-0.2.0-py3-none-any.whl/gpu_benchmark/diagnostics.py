# baseline info & thresholds

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

def get_gpu_info(handle):
    """Get GPU information"""
    if not PYNVML_AVAILABLE:
        return {
            "Temperature (C)": -1,
            "Power Usage (W)": -1,
            "Memory Used (MB)": -1,
            "Memory Total (MB)": -1,
            "Fan Speed (%)": "Not available"
        }
        
    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    try:
        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
    except pynvml.NVMLError:
        fan_speed = "Not supported"

    info = {
        "Temperature (C)": temperature,
        "Power Usage (W)": power_usage,
        "Memory Used (MB)": memory_info.used // (1024**2),
        "Memory Total (MB)": memory_info.total // (1024**2),
        "Fan Speed (%)": fan_speed,
    }
    return info

def print_temperature_thresholds(handle):
    """Print temperature thresholds"""
    if not PYNVML_AVAILABLE:
        print("NVIDIA GPU monitoring not available")
        return
        
    try:
        slowdown = pynvml.nvmlDeviceGetTemperatureThreshold(
            handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)
        print(f"⚠️  Slowdown Threshold: {slowdown} °C")
    except pynvml.NVMLError as e:
        print(f"Slowdown Threshold: Not supported ({str(e)})")

    try:
        shutdown = pynvml.nvmlDeviceGetTemperatureThreshold(
            handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)
        print(f"🔥 Shutdown Threshold: {shutdown} °C")
    except pynvml.NVMLError as e:
        print(f"Shutdown Threshold: Not supported ({str(e)})")
