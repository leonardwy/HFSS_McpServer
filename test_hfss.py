"""Quick test to verify PyAEDT can connect to running AEDT"""
import os
import sys

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"AEDT_PATH env: {os.environ.get('AEDT_PATH', 'NOT SET')}")
print(f"AEDT_INSTALL_DIR env: {os.environ.get('AEDT_INSTALL_DIR', 'NOT SET')}")
print(f"ANSYSEM_ROOT_DIR env: {os.environ.get('ANSYSEM_ROOT_DIR', 'NOT SET')}")

os.environ["AEDT_PATH"] = r"D:\Program Files\ANSYS Inc\v261\AnsysEM"
os.environ["AEDT_INSTALL_DIR"] = r"D:\Program Files\ANSYS Inc\v261\AnsysEM"
os.environ["ANSYSEM_ROOT_DIR"] = r"D:\Program Files\ANSYS Inc\v261\AnsysEM"

print(f"\nAfter setting:")
print(f"AEDT_PATH = {os.environ.get('AEDT_PATH')}")

from ansys.aedt.core import Hfss

print("\nCreating Hfss instance...")
try:
    h = Hfss(project="QuickTest", new_desktop=False, non_graphical=True, close_on_exit=False)
    print(f"SUCCESS! Connected to: {h}")
    h.release_desktop()
    print("Desktop released.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
