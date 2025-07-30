from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import sys
import os

# Add src to path to import our hardware detection
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastHDMI.utils.hardware_detection import get_cpu_features, get_best_simd_flag
except ImportError:
    # Fallback if module not available during setup
    def get_cpu_features():
        return {'sse4_2': True}  # Conservative default
    
    def get_best_simd_flag():
        return '-msse4.2'

# Get CPU features
cpu_features = get_cpu_features()
best_simd_flag = get_best_simd_flag()

# Configure the macros and compile/link args based on detected features
macros = []
compile_args = []
link_args = []

# Add the best SIMD flag if available
if best_simd_flag:
    compile_args.append(best_simd_flag)
    link_args.append(best_simd_flag)
    print(f"Using SIMD optimization: {best_simd_flag}")

# Add specific macros for features
if cpu_features.get('avx2'):
    macros.append(('USE_AVX2', None))
    print("The computing platform supports AVX2.")

if cpu_features.get('avx512f'):
    macros.append(('USE_AVX512', None))
    print("The computing platform supports AVX512.")

if cpu_features.get('fma'):
    macros.append(('USE_FMA', None))
    print("The computing platform supports FMA.")

if cpu_features.get('neon'):
    macros.append(('USE_NEON', None))
    print("The computing platform supports ARM NEON.")

# General SIMD support
if any(cpu_features.values()):
    macros.append(('USE_SIMD', None))
    print("The computing platform supports SIMD.")

# Configure the extension
extensions = [
    Extension(
        "fastHDMI.cython_fun",
        ["src/fastHDMI/cython_fun.pyx"],
        define_macros=macros,
        extra_compile_args=compile_args,
        extra_link_args=link_args,
    )
]

setup(
    name="fastHDMI",
    version="1.25.20",
    author="Kai Yang",
    author_email="kai.yang2@mail.mcgill.ca",
    description="Fast mutual information estimation for high-dimensional data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Kaiyangshi-Ito/fastHDMI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=cythonize(extensions, language_level="3"),
)
