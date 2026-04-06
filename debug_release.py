"""调试脚本：追踪 HFSS 连接释放的调用路径"""
import sys
import traceback
import atexit

# 替换 atexit.register 来追踪调用
_original_register = atexit.register
_call_stack = []

def trace_register(func, *args, **kwargs):
    """追踪 atexit.register 调用"""
    tb = ''.join(traceback.format_stack())
    print(f"[DEBUG] atexit.register called from:\n{tb[:1000]}", file=sys.stderr)
    return _original_register(func, *args, **kwargs)

atexit.register = trace_register

# 现在导入 ansys
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

print(f"[DEBUG] Hfss created: {hfss_app.project_name}")

# 打印 atexit 回调
print(f"[DEBUG] atexit callbacks: {atexit._exithandlers}")

# 测试对象操作
print(f"[DEBUG] Object names: {hfss_app.modeler.object_names}")

print("[DEBUG] Test completed successfully")
