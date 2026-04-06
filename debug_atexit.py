"""测试 atexit 是否被成功禁用"""
# 在导入 ansys 之前禁用 atexit
import atexit
_original_register = atexit.register

def _no_op_register(*args, **kwargs):
    """空的注册函数，防止 PyAEDT 注册 atexit 回调"""
    pass

atexit.register = _no_op_register

print("[DEBUG] atexit.register has been replaced")

# 现在导入 ansys
from ansys.aedt.core import Hfss
import psutil
import sys

# 全局引用
_global_hfss = None

print("[DEBUG] Phase 1: Check HFSS process...")
hfss_found = False
for proc in psutil.process_iter(['pid', 'name']):
    try:
        if 'ansysedt' in proc.info['name'].lower():
            print(f"[DEBUG] Found HFSS process: {proc.info}")
            hfss_found = True
            break
    except:
        pass

if not hfss_found:
    print("[DEBUG] No HFSS process found!")
    sys.exit(1)

print("[DEBUG] Phase 2: Create Hfss instance...")
hfss_app = Hfss(
    project=None,
    design=None,
    new_desktop=False,
    close_on_exit=False
)
_global_hfss = hfss_app
print(f"[DEBUG] Hfss created: {hfss_app.project_name}")
print(f"[DEBUG] Objects: {hfss_app.modeler.object_names}")

print("[DEBUG] Phase 3: Script about to exit...")
print("[DEBUG] =============== RESULT ===============")
print("[DEBUG] 如果看到 'Desktop has been released' 则修复失败")
print("[DEBUG] 如果没有看到则修复成功")
print("[DEBUG] =======================================")
