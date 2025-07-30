import os
import sys
import ctypes
import importlib.util

# Get package directory and lib path
package_dir = os.path.dirname(__file__)
lib_path = os.path.join(package_dir, "lib")


os.environ["OPAL_PREFIX"] = package_dir

_loaded_libs = {}

# Use dlopen via ctypes.CDLL
for so_file in sorted(os.listdir(lib_path)):
    if so_file.endswith(".so") or ".so." in so_file:
        so_path = os.path.join(lib_path, so_file)
        try:
            # Otherwise unloading will lead to a crash at the exit
            if "mfem" in so_file:
                continue

            _loaded_libs[so_file] = ctypes.CDLL(so_path, mode=ctypes.RTLD_GLOBAL)
        except OSError as e:
            print(f"Warning: Could not load {so_path}: {e}")

# Explicitly load libmfem.so and store reference
mfem_so_path = os.path.join(lib_path, "libmfem.so")
if os.path.exists(mfem_so_path):
    _loaded_libs["libmfem.so"] = ctypes.CDLL(mfem_so_path, mode=ctypes.RTLD_LOCAL)
else:
    raise ImportError(f"Could not find {mfem_so_path}")

# Explicitly load mufem.so
mufem_so_path = os.path.join(package_dir, "mufem.so")
if not os.path.exists(mufem_so_path):
    raise ImportError(f"Could not find {mufem_so_path}")

# Load the Python module from mufem.so
spec = importlib.util.spec_from_file_location("mufem", mufem_so_path)
mufem = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mufem)

# Expose mufem to package users
sys.modules["mufem"] = mufem
