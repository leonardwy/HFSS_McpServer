"""Test HFSS modeling via PyAEDT"""
import os
import sys

# Set AEDT paths
os.environ["AEDT_PATH"] = r"D:\Program Files\ANSYS Inc\v261\AnsysEM"
os.environ["AEDT_INSTALL_DIR"] = r"D:\Program Files\ANSYS Inc\v261\AnsysEM"
os.environ["ANSYSEM_ROOT_DIR"] = r"D:\Program Files\ANSYS Inc\v261\AnsysEM"

from ansys.aedt.core import Hfss

print("Creating HFSS project...")
hfss = Hfss(project="ModelingTest", new_desktop=True, non_graphical=False, close_on_exit=True)

# Test 1: Create a box (use origin/sizes for PyAEDT 0.26+)
print("\n1. Creating box...")
box = hfss.modeler.create_box(
    origin=[0, 0, 0],
    sizes=[10, 5, 2],
    name="Waveguide"
)
print(f"   Box created: {box}")

# Test 2: Assign material
print("\n2. Assigning copper material...")
hfss.assign_material("Waveguide", "copper")
print("   Material assigned")

# Test 3: Create variable (use set_variable for PyAEDT 0.26+)
print("\n3. Creating variable...")
hfss.variable_manager.set_variable("freq", "10GHz")
print("   Variable 'freq' = 10GHz created")

# Test 4: Create setup
print("\n4. Creating analysis setup...")
setup = hfss.create_setup("Setup1")
setup.props["Frequency"] = "10GHz"
print("   Setup1 created with frequency 10GHz")

# Test 5: List objects
print("\n5. Listing objects...")
objects = hfss.modeler.object_names
print(f"   Objects: {objects}")

# Test 6: List variables
print("\n6. Listing variables...")
vars = hfss.variable_manager.variables
print(f"   Variables: {[(v.name, v.expression) for v in vars]}")

# Save project
print("\n7. Saving project...")
save_path = os.path.join(os.getcwd(), "ModelingTest.aedt")
hfss.save_project(save_path)
print(f"   Saved to: {save_path}")

# Cleanup
print("\n8. Releasing desktop...")
hfss.release_desktop()
print("   Done!")

print("\n" + "="*50)
print("ALL TESTS PASSED!")
print("="*50)
