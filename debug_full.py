"""完整测试：模拟 MCP 服务器处理请求后的行为"""
import sys
import gc

# 全局引用
_hfss_ref = None

print("[DEBUG] Phase 1: Import and create Hfss")
from ansys.aedt.core import Hfss

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

# 模拟 MCP 调用完成 - 清除局部变量
del hfss_app

# 尝试再次访问
try:
    print(f"[DEBUG] Can access via _hfss_ref: {_hfss_ref.project_name}")
    print(f"[DEBUG] Objects: {_hfss_ref.modeler.object_names}")
except Exception as e:
    print(f"[DEBUG] ERROR: {e}")

print("[DEBUG] Phase 2: Checking stdin...")
print(f"[DEBUG] stdin.isatty(): {sys.stdin.isatty()}")

# 读取一行
line = sys.stdin.readline()
if line:
    print(f"[DEBUG] Received: {line.strip()}")
else:
    print("[DEBUG] stdin closed (no more input)")

print("[DEBUG] Phase 3: Script about to exit...")

# 注意：这里不调用 sys.exit()，让脚本自然退出
# Python 会执行 atexit 回调
