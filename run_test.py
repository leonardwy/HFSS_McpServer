"""Direct test of HFSS functionality"""
import sys
print("=" * 50)
print("HFSS Direct Test")
print("=" * 50)

from ansys.aedt import Hfss
print("PyAEDT imported successfully")

try:
    print("\n1. Creating HFSS project...")
    hfss = Hfss(
        project='Test_Project',
        design='TestDesign', 
        solution_type='Terminal',
        new_desktop=True,
        non_graphical=True,
        close_on_exit=False
    )
    print(f"   ✓ Project: {hfss.project_name}")
    print(f"   ✓ Design: {hfss.design_name}")
    
    print("\n2. Creating box (10x10x10 mm)...")
    hfss.modeler.create_box(
        position=[0, 0, 0], 
        dimensions_list=[10, 10, 10], 
        name='MyBox'
    )
    print(f"   ✓ Box created. Objects: {len(hfss.modeler.object_names)}")
    print(f"   ✓ Object names: {hfss.modeler.object_names}")
    
    print("\n3. Saving project...")
    save_path = 'd:/hfss_mcp/Test_Project.aedt'
    hfss.save_project(save_path)
    print(f"   ✓ Saved to: {save_path}")
    
    print("\n4. Cleaning up...")
    hfss.release_desktop()
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()