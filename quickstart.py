#!/usr/bin/env python
"""
Quick start script for HFSS MCP Server with automated modeling knowledge base.

Usage:
    python quickstart.py build   # Build KB from ANSYS docs
    python quickstart.py status  # Check KB status
    python quickstart.py server  # Start MCP server
"""

import sys
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
VENV_PYTHON = SCRIPT_DIR / ".venv" / "Scripts" / "python.exe"
KB_SCRIPT = SCRIPT_DIR / "scripts" / "build_hfss_kb.py"
SERVER_SCRIPT = SCRIPT_DIR / "hfss_server.py"
KB_FILE = SCRIPT_DIR / "hfss_modeling_knowledge_base.json"
DOC_ROOT = Path("E:/download/ANSYS2026R1/ANSYS2026R1_ProductDocPDF/v261")


def build_kb():
    """Build HFSS modeling knowledge base from ANSYS PDFs."""
    print("[*] Building HFSS modeling knowledge base...")
    if not DOC_ROOT.exists():
        print(f"[!] Document root not found: {DOC_ROOT}")
        print("    Please update DOC_ROOT in this script or provide via --doc-root")
        return False
    
    cmd = [
        str(VENV_PYTHON),
        str(KB_SCRIPT),
        "--doc-root", str(DOC_ROOT),
        "--output", str(KB_FILE),
        "--max-files", "120",
    ]
    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    return result.returncode == 0


def check_status():
    """Check knowledge base status."""
    if not KB_FILE.exists():
        print("[!] Knowledge base not found. Run 'python quickstart.py build' first.")
        return False
    
    import json
    with KB_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    meta = data.get("metadata", {})
    entries = data.get("entries", [])
    
    print("[+] HFSS Modeling Knowledge Base Status")
    print(f"    Generated at: {meta.get('generated_at', 'N/A')}")
    print(f"    Source root: {meta.get('source_root', 'N/A')}")
    print(f"    Scanned files: {meta.get('scanned_files', 0)}")
    print(f"    Total entries: {len(entries)}")
    print(f"    Tags in use:")
    tags_set = set()
    for entry in entries:
        tags_set.update(entry.get("tags", []))
    for tag in sorted(tags_set):
        print(f"      - {tag}")
    return True


def start_server():
    """Start HFSS MCP server."""
    print("[*] Starting HFSS MCP Server...")
    if not KB_FILE.exists():
        print("[!] Knowledge base not found. Run 'python quickstart.py build' first.")
        return False
    
    cmd = [str(VENV_PYTHON), str(SERVER_SCRIPT)]
    print(f"    Command: {' '.join(cmd)}")
    print("    Press Ctrl+C to stop the server.")
    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python quickstart.py [build|status|server]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "build":
        if build_kb():
            print("[+] Knowledge base built successfully.")
            sys.exit(0)
        else:
            print("[!] Failed to build knowledge base.")
            sys.exit(1)
    
    elif command == "status":
        if check_status():
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif command == "server":
        if start_server():
            sys.exit(0)
        else:
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print("Usage: python quickstart.py [build|status|server]")
        sys.exit(1)


if __name__ == "__main__":
    main()
