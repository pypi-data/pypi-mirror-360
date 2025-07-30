#!/usr/bin/env python
# coding: utf-8

"""Hardware detection and optimization utilities."""

import platform
import subprocess
import os

def get_cpu_features():
    """Detect available CPU features for optimization."""
    features = {
        'sse': False,
        'sse2': False,
        'sse3': False,
        'ssse3': False,
        'sse4_1': False,
        'sse4_2': False,
        'avx': False,
        'avx2': False,
        'avx512f': False,
        'fma': False,
        'neon': False  # ARM NEON
    }
    
    system = platform.system()
    machine = platform.machine().lower()
    
    # ARM-based systems (like Apple Silicon)
    if 'arm' in machine or 'aarch64' in machine:
        features['neon'] = True
        # Apple Silicon supports advanced SIMD
        if system == 'Darwin':
            features['sse'] = True  # Rosetta 2 emulation
            features['sse2'] = True
            features['sse3'] = True
            features['ssse3'] = True
            features['sse4_1'] = True
            features['sse4_2'] = True
        return features
    
    # x86/x64 systems
    if system == 'Linux':
        try:
            cpuinfo = open('/proc/cpuinfo').read()
            flags = None
            for line in cpuinfo.split('\n'):
                if 'flags' in line:
                    flags = line.split(':')[1].strip().split()
                    break
            
            if flags:
                features['sse'] = 'sse' in flags
                features['sse2'] = 'sse2' in flags
                features['sse3'] = 'sse3' in flags or 'pni' in flags
                features['ssse3'] = 'ssse3' in flags
                features['sse4_1'] = 'sse4_1' in flags
                features['sse4_2'] = 'sse4_2' in flags
                features['avx'] = 'avx' in flags
                features['avx2'] = 'avx2' in flags
                features['avx512f'] = 'avx512f' in flags
                features['fma'] = 'fma' in flags
        except:
            pass
    
    elif system == 'Darwin':  # macOS
        try:
            # Use sysctl to get CPU features
            result = subprocess.run(['sysctl', '-a'], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                # Parse macOS specific feature flags
                features['sse'] = 'hw.optional.sse:' in output and 'hw.optional.sse: 1' in output
                features['sse2'] = 'hw.optional.sse2:' in output and 'hw.optional.sse2: 1' in output
                features['sse3'] = 'hw.optional.sse3:' in output and 'hw.optional.sse3: 1' in output
                features['ssse3'] = 'hw.optional.supplementalsse3:' in output and 'hw.optional.supplementalsse3: 1' in output
                features['sse4_1'] = 'hw.optional.sse4_1:' in output and 'hw.optional.sse4_1: 1' in output
                features['sse4_2'] = 'hw.optional.sse4_2:' in output and 'hw.optional.sse4_2: 1' in output
                features['avx'] = 'hw.optional.avx1_0:' in output and 'hw.optional.avx1_0: 1' in output
                features['avx2'] = 'hw.optional.avx2_0:' in output and 'hw.optional.avx2_0: 1' in output
                features['avx512f'] = 'hw.optional.avx512f:' in output and 'hw.optional.avx512f: 1' in output
                features['fma'] = 'hw.optional.fma:' in output and 'hw.optional.fma: 1' in output
        except:
            pass
    
    elif system == 'Windows':
        # Windows detection would require different approach
        # For now, assume basic features
        features['sse'] = True
        features['sse2'] = True
    
    return features


def get_best_simd_flag():
    """
    Get the best available SIMD compiler flag for the current CPU.
    
    Returns:
        str: Compiler flag for best available SIMD instruction set
    """
    features = get_cpu_features()
    
    # Priority order (best to worst)
    if features.get('avx512f'):
        return '-mavx512f'
    elif features.get('avx2'):
        return '-mavx2'
    elif features.get('avx'):
        return '-mavx'
    elif features.get('sse4_2'):
        return '-msse4.2'
    elif features.get('sse4_1'):
        return '-msse4.1'
    elif features.get('ssse3'):
        return '-mssse3'
    elif features.get('sse3'):
        return '-msse3'
    elif features.get('sse2'):
        return '-msse2'
    elif features.get('sse'):
        return '-msse'
    elif features.get('neon'):
        # ARM NEON doesn't need explicit flags on most modern compilers
        return ''
    else:
        return ''


def supports_simd():
    """
    Check if the CPU supports any SIMD instructions.
    
    Returns:
        bool: True if any SIMD is supported, False otherwise
    """
    features = get_cpu_features()
    return any(features.values())


# Backward compatibility
def supports_avx2():
    """
    Check if the CPU supports AVX2 instructions.
    
    Returns:
        bool: True if AVX2 is supported, False otherwise
    """
    return get_cpu_features().get('avx2', False)