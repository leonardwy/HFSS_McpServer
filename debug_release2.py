"""调试脚本：模拟 MCP 服务器的行为"""
import sys
import gc

# 保存全局引用
_hfss_ref = None

# 导入后直接创建
from ansys.aedt.core import Hfss
import psutil

print("[DEBUG] Searching for HFSS process...")
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'ansysedt' in proc.info['name'].lower():
            print(f"[DEBUG] Found: {proc.info}")
    except:
        pass

print("[DEBUG] Creating Hfss instance...")
hfss_app = Hfss(
    project=None,
    design=None,
    new_desktop=False,
    close_on_exit=False
)

# 保存到全局变量
_hfss_ref = hfss_app

print(f"[DEBUG] Hfss created: {hfss_app.project_name}")
print(f"[DEBUG] Object count before gc: {len(gc.get_objects())}")

# 模拟 MCP 调用完成 - 清除局部变量引用
del hfss_app

# 强制垃圾回收看看会不会释放
print("[DEBUG] Running gc.collect()...")
gc.collect()

print(f"[DEBUG] Object count after gc: {len(gc.get_objects())}")
print(f"[DEBUG] _hfss_ref is still valid: {_hfss_ref is not None}")

# 尝试再次访问
try:
    print(f"[DEBUG] Can still access project: {_hfss_ref.project_name}")
    print(f"[DEBUG] Object names: {_hfss_ref.modeler.object_names}")
    print("[DEBUG] SUCCESS: Connection still alive!")
except Exception as e:
    print(f"[DEBUG] ERROR: Connection lost! {e}")

print("[DEBUG] Test completed - keeping process alive")
input("Press Enter to exit...")
