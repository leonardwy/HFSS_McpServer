"""测试：MCP 服务器在收到请求后的行为"""
import sys

print("[DEBUG] Checking stdin status...")
print(f"[DEBUG] stdin.isatty(): {sys.stdin.isatty()}")
print(f"[DEBUG] stdout.isatty(): {sys.stdout.isatty()}")

# 如果 stdin 被关闭，这会抛出异常
try:
    while True:
        line = sys.stdin.readline()
        if not line:
            print("[DEBUG] stdin.readline() returned empty - stdin closed!")
            break
        print(f"[DEBUG] Received: {line.strip()}")
except Exception as e:
    print(f"[DEBUG] Exception reading stdin: {e}")

print("[DEBUG] Script finished")
