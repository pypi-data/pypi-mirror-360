"""Compute stress tests"""

import torch
import time
from typing import Dict


class ComputeStressTest:
    """GPU compute stress tests"""
    
    def __init__(self, device: torch.device):
        self.device = device
        
    def matrix_multiply_stress(self, size: int = 4096, duration: float = 10) -> Dict[str, float]:
        """Traditional matrix multiplication stress test"""
        # Adjust size for CPU or limited memory
        if self.device.type == "cpu":
            size = min(size, 512)
        elif self.device.type == "cuda":
            # Check available memory
            try:
                mem_free = torch.cuda.mem_get_info(self.device.index)[0]
                mem_needed = size * size * 4 * 3  # 3 matrices, 4 bytes per float
                if mem_needed > mem_free * 0.8:  # Use only 80% of free memory
                    size = int((mem_free * 0.8 / (4 * 3)) ** 0.5)
            except:
                size = min(size, 2048)
        
        a = torch.randn((size, size), device=self.device)
        b = torch.randn((size, size), device=self.device)
        
        start_time = time.time()
        iterations = 0
        flops = 0
        
        while time.time() - start_time < duration:
            c = torch.matmul(a, b)
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            iterations += 1
            flops += 2 * size**3  # Approximate FLOPs for matrix multiply
        
        elapsed = time.time() - start_time
        return {
            "iterations": iterations,
            "tflops": (flops / elapsed) / 1e12,
            "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
            "matrix_size": size
        }
    
    def conv2d_stress(self, duration: float = 10) -> Dict[str, float]:
        """Convolution stress test (common in AI workloads)"""
        if self.device.type == "cpu":
            batch_size = 4
            channels = 16
            height, width = 64, 64
        else:
            batch_size = 32
            channels = 64
            height, width = 224, 224
        
        kernel_size = 3
        
        # Create conv layer
        conv = torch.nn.Conv2d(channels, channels, kernel_size, padding=1).to(self.device)
        x = torch.randn(batch_size, channels, height, width, device=self.device)
        
        start_time = time.time()
        iterations = 0
        
        while time.time() - start_time < duration:
            y = conv(x)
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            iterations += 1
        
        elapsed = time.time() - start_time
        return {
            "iterations": iterations,
            "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
            "batch_size": batch_size,
            "resolution": f"{height}x{width}"
        }
    
    def transformer_stress(self, duration: float = 10) -> Dict[str, float]:
        """Transformer attention stress test"""
        if self.device.type == "cpu":
            seq_length = 64
            batch_size = 4
            d_model = 128
            n_heads = 4
        else:
            seq_length = 512
            batch_size = 16
            d_model = 768
            n_heads = 12
        
        # Create multi-head attention
        mha = torch.nn.MultiheadAttention(d_model, n_heads).to(self.device)
        x = torch.randn(seq_length, batch_size, d_model, device=self.device)
        
        start_time = time.time()
        iterations = 0
        
        while time.time() - start_time < duration:
            attn_output, _ = mha(x, x, x)
            if self.device.type == "cuda":
                torch.cuda.synchronize()
            iterations += 1
        
        elapsed = time.time() - start_time
        return {
            "iterations": iterations,
            "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
            "seq_length": seq_length,
            "batch_size": batch_size,
            "d_model": d_model
        }
