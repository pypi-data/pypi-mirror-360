"""Mixed precision stress tests"""

import torch
import time
from typing import Dict


class MixedPrecisionTest:
    """Test mixed precision capabilities"""
    
    def __init__(self, device: torch.device):
        self.device = device
        
    def run_test(self, duration: float = 10) -> Dict[str, any]:
        """Test FP32, FP16, and BF16 performance"""
        size = 2048 if self.device.type == "cuda" else 256
        results = {}
        
        # FP32 test
        results["fp32"] = self._test_precision(
            torch.float32, size, duration / 3
        )
        
        # FP16 test
        if self._check_fp16_support():
            results["fp16"] = self._test_precision(
                torch.float16, size, duration / 3
            )
        else:
            results["fp16"] = {"supported": False}
        
        # BF16 test (for newer GPUs)
        if self._check_bf16_support():
            results["bf16"] = self._test_precision(
                torch.bfloat16, size, duration / 3
            )
        else:
            results["bf16"] = {"supported": False}
        
        # Calculate speedups
        if results["fp32"].get("iterations", 0) > 0:
            if "iterations" in results.get("fp16", {}):
                results["fp16_speedup"] = (
                    results["fp16"]["iterations"] / results["fp32"]["iterations"]
                )
            if "iterations" in results.get("bf16", {}):
                results["bf16_speedup"] = (
                    results["bf16"]["iterations"] / results["fp32"]["iterations"]
                )
        
        # Determine mixed precision capability
        results["mixed_precision_ready"] = (
            results.get("fp16", {}).get("supported", False) or
            results.get("bf16", {}).get("supported", False)
        )
        
        return results
    
    def _test_precision(self, dtype: torch.dtype, size: int, duration: float) -> Dict[str, any]:
        """Test specific precision performance"""
        try:
            a = torch.randn((size, size), device=self.device, dtype=dtype)
            b = torch.randn((size, size), device=self.device, dtype=dtype)
            
            start_time = time.time()
            iterations = 0
            
            while time.time() - start_time < duration:
                c = torch.matmul(a, b)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                iterations += 1
            
            elapsed = time.time() - start_time
            
            return {
                "supported": True,
                "iterations": iterations,
                "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
                "dtype": str(dtype)
            }
            
        except Exception as e:
            return {
                "supported": False,
                "error": str(e)
            }
    
    def _check_fp16_support(self) -> bool:
        """Check if GPU supports FP16"""
        if self.device.type == "cpu":
            return False
            
        if not torch.cuda.is_available():
            return False
            
        # Check compute capability
        device_id = self.device.index if self.device.index is not None else 0
        major, minor = torch.cuda.get_device_capability(device_id)
        
        # FP16 requires compute capability 5.3 or higher
        return major > 5 or (major == 5 and minor >= 3)
    
    def _check_bf16_support(self) -> bool:
        """Check if GPU supports BF16"""
        if self.device.type == "cpu":
            # Some CPUs support BF16
            try:
                test = torch.randn(2, 2, dtype=torch.bfloat16)
                return True
            except:
                return False
            
        if not torch.cuda.is_available():
            return False
            
        # BF16 requires Ampere (compute capability 8.0) or newer
        device_id = self.device.index if self.device.index is not None else 0
        major, _ = torch.cuda.get_device_capability(device_id)
        
        return major >= 8
    
    def tensor_core_test(self, duration: float = 10) -> Dict[str, any]:
        """Test Tensor Core performance if available"""
        if self.device.type == "cpu":
            return {"tensor_cores_available": False}
            
        # Tensor cores require specific dimensions (multiples of 8)
        size = 4096
        
        # Check if tensor cores are available
        device_id = self.device.index if self.device.index is not None else 0
        major, _ = torch.cuda.get_device_capability(device_id)
        
        if major < 7:  # Tensor cores introduced in Volta (7.0)
            return {"tensor_cores_available": False}
        
        # Run with tensor core friendly dimensions
        torch.backends.cuda.matmul.allow_tf32 = True
        
        a = torch.randn((size, size), device=self.device, dtype=torch.float32)
        b = torch.randn((size, size), device=self.device, dtype=torch.float32)
        
        start_time = time.time()
        iterations = 0
        
        while time.time() - start_time < duration:
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            iterations += 1
        
        elapsed = time.time() - start_time
        
        return {
            "tensor_cores_available": True,
            "iterations": iterations,
            "tflops": (2 * size**3 * iterations / elapsed) / 1e12,
            "matrix_size": size
        }
