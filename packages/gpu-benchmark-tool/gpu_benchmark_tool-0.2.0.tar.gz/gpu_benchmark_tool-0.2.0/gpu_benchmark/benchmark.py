from .monitor import stress_gpu_with_monitoring, enhanced_stress_test
from .scoring import score_gpu_health
from .diagnostics import get_gpu_info
from .backends import get_gpu_backend
import json
from datetime import datetime

def run_full_benchmark(handle, duration=60, enhanced=True, device_id=0):
    """
    Run diagnostics, stress test, and scoring on a single GPU.
    
    Args:
        handle: NVML handle to the GPU (for backward compatibility)
        duration: Stress test duration in seconds
        enhanced: Use enhanced stress testing with more metrics
        device_id: GPU device ID (default 0)
    
    Returns:
        dict: Full report with metadata, stress metrics, and score
    """
    
    # Get GPU info
    info = get_gpu_info(handle)
    
    # Run stress test
    if enhanced:
        # Use enhanced monitoring with backend detection
        backend = get_gpu_backend(backend_type="nvidia", device_id=device_id)
        if backend and hasattr(backend, 'create_monitor'):
            try:
                monitor = backend.create_monitor(handle)
                metrics = enhanced_stress_test(monitor, duration, device_id)
            except Exception as e:
                print(f"Enhanced monitoring failed: {e}, falling back to basic")
                metrics = stress_gpu_with_monitoring(handle, duration)
        else:
            # Fallback to original monitoring
            print("Enhanced monitoring not available, using basic monitoring")
            metrics = stress_gpu_with_monitoring(handle, duration)
    else:
        metrics = stress_gpu_with_monitoring(handle, duration)
    
    # Score GPU health
    if enhanced and "temperature_stability" in metrics:
        result = score_gpu_health(
            baseline_temp=metrics["baseline_temp"],
            max_temp=metrics["max_temp"],
            power_draw=metrics["max_power"],
            utilization=metrics.get("avg_utilization", metrics.get("utilization", -1)),
            throttled=len(metrics.get("throttle_events", [])) > 0,
            errors=len(metrics.get("errors", [])) > 0,
            throttle_events=metrics.get("throttle_events", []),
            temperature_stability=metrics.get("temperature_stability"),
            enhanced_metrics=metrics.get("stress_test_results")
        )
        if len(result) == 4:
            score, status, recommendation, details = result
        else:
            score, status, recommendation = result
            details = {}
    else:
        # Basic scoring for backward compatibility
        result = score_gpu_health(
            baseline_temp=metrics["baseline_temp"],
            max_temp=metrics["max_temp"],
            power_draw=metrics["max_power"],
            utilization=metrics["utilization"]
        )
        if len(result) == 4:
            score, status, recommendation, details = result
        else:
            score, status, recommendation = result
            details = {}
    
    # Build comprehensive report
    report = {
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "duration": duration,
            "enhanced_mode": enhanced
        },
        "gpu_info": info,
        "metrics": metrics,
        "health_score": {
            "score": score,
            "status": status,
            "recommendation": recommendation,
            "details": details
        }
    }
    
    # Add enhanced test results if available
    if enhanced and "stress_test_results" in metrics:
        report["performance_tests"] = metrics["stress_test_results"]
    
    return report


def run_multi_gpu_benchmark(duration=60, enhanced=True):
    """
    Run benchmark on all available GPUs
    
    Returns:
        dict: Results for all GPUs
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
    except:
        return {"error": "NVIDIA GPU support not available"}
    
    if device_count == 0:
        return {"error": "No NVIDIA GPUs found"}
    
    results = {}
    
    for i in range(device_count):
        print(f"\nBenchmarking GPU {i}...")
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        
        try:
            result = run_full_benchmark(handle, duration, enhanced, i)
            results[f"gpu_{i}"] = result
        except Exception as e:
            results[f"gpu_{i}"] = {"error": str(e)}
    
    return {
        "device_count": device_count,
        "results": results,
        "summary": _generate_summary(results)
    }


def _generate_summary(results):
    """Generate summary of multi-GPU benchmark results"""
    summary = {
        "total_gpus": len(results),
        "healthy_gpus": 0,
        "warnings": [],
        "recommendations": []
    }
    
    for gpu_id, result in results.items():
        if "error" in result:
            summary["warnings"].append(f"{gpu_id}: {result['error']}")
            continue
        
        health = result.get("health_score", {})
        if health.get("status") == "healthy":
            summary["healthy_gpus"] += 1
        elif health.get("status") in ["warning", "critical"]:
            summary["warnings"].append(
                f"{gpu_id}: {health.get('status')} - {health.get('recommendation')}"
            )
    
    summary["health_percentage"] = (summary["healthy_gpus"] / summary["total_gpus"]) * 100 if summary["total_gpus"] > 0 else 0
    
    return summary


def export_results(results, filename=None):
    """Export benchmark results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gpu_benchmark_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results exported to {filename}")
    return filename
