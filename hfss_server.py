"""
ANSYS HFSS MCP Server - 持久化 Session 版本
==========================================
支持持久化 HFSS 连接，不会每次调用后断开。

Usage:
    python hfss_server.py

Requirements:
    - ansys-aedt-core (PyAEDT)
    - mcp (Model Context Protocol)
"""

# 禁用 atexit.register 防止 PyAEDT 注册退出回调（在导入 ansys 之前）
import atexit
_original_register = atexit.register

def _no_op_register(*args, **kwargs):
    """空的注册函数，防止 PyAEDT 注册 atexit 回调"""
    pass

atexit.register = _no_op_register

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, TextContent
from ansys.aedt.core import Hfss
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import os
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
app = Server("HfssMcp")


@dataclass
class ProjectSession:
    """Represents an active HFSS project session"""
    name: str
    design_name: str
    solution_type: str
    hfss_app: Optional[Hfss] = None
    is_active: bool = False
    
    def __post_init__(self):
        if self.hfss_app is not None:
            self.is_active = True


class HfssSessionManager:
    """Manages HFSS project sessions - 持久化 session 模式"""
    
    def __init__(self):
        self._current_session: Optional[ProjectSession] = None
        self._sessions: Dict[str, ProjectSession] = {}
        self._initialized: bool = False
    
    @property
    def current(self) -> Optional[ProjectSession]:
        return self._current_session
    
    @property
    def is_connected(self) -> bool:
        return (
            self._current_session is not None 
            and self._current_session.is_active 
            and self._current_session.hfss_app is not None
        )
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    def is_valid(self) -> bool:
        """检查连接是否有效"""
        if not self.is_connected:
            return False
        # 检查 HFSS 进程是否还存在
        if not self._check_existing_hfss_processes():
            return False
        try:
            # 尝试访问项目名检测连接是否有效
            _ = self._current_session.hfss_app.project_name
            return True
        except:
            return False
    
    def _check_existing_hfss_processes(self) -> bool:
        """检查是否有现有的 HFSS 进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'ansysedt' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False
    
    def init_session(self) -> bool:
        """初始化 session - 只复用现有进程，不创建新后台"""
        if self._initialized:
            logger.info("Session already initialized")
            return True
        
        # 先检查是否有现有的 HFSS 进程
        if not self._check_existing_hfss_processes():
            logger.warning("No existing HFSS process found. Please open HFSS first.")
            self._initialized = False
            return False
        
        try:
            logger.info("Initializing HFSS session (connecting to existing)...")
            # 连接现有 HFSS 进程
            hfss_app = Hfss(
                project=None,
                design=None,
                new_desktop=False,
                close_on_exit=False
            )
            
            # 保存到全局变量，防止被垃圾回收！
            global _global_hfss
            _global_hfss = hfss_app
            
            session = ProjectSession(
                name=hfss_app.project_name,
                design_name=hfss_app.design_name,
                solution_type="Terminal",
                hfss_app=hfss_app,
                is_active=True
            )
            
            session_id = f"{hfss_app.project_name}/{hfss_app.design_name}"
            self._sessions[session_id] = session
            self._current_session = session
            self._initialized = True
            
            logger.info(f"Session initialized: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to init session: {e}")
            self._initialized = False
            return False
    
    def reconnect(self) -> bool:
        """重新连接 - 断线后调用"""
        if self.is_valid():
            logger.info("Connection is still valid")
            return True
        
        logger.info("Attempting to reconnect...")
        self._current_session = None
        self._sessions = {}
        
        return self.init_session()
    
    def create_session(
        self, 
        project_name: str = "HFSS_project", 
        design_name: str = "HFSSDesign1",
        solution_type: str = "Terminal",
        designated: bool = False,
        non_graphical: bool = True
    ) -> ProjectSession:
        """Create or reuse HFSS session"""
        # 如果已初始化且有效，检查是否需要切换项目
        if self.is_valid():
            current_project = self._current_session.hfss_app.project_name
            current_design = self._current_session.hfss_app.design_name
            
            # 如果请求的项目/设计与当前相同，直接返回
            if current_project == project_name and current_design == design_name:
                logger.info(f"Same session: {project_name}/{design_name}")
                return self._current_session
            
            # 切换到指定项目
            logger.info(f"Switching from {current_project}/{current_design} to {project_name}/{design_name}")
            try:
                self._current_session.hfss_app.load_project(project_name)
                self._current_session.hfss_app.set_active_design(design_name)
                self._current_session.name = project_name
                self._current_session.design_name = design_name
                session_id = f"{project_name}/{design_name}"
                self._sessions = {session_id: self._current_session}
                logger.info(f"Switched to: {session_id}")
                return self._current_session
            except Exception as e:
                logger.error(f"Failed to switch project: {e}")
                # 如果切换失败，创建新 session
                pass
        
        session_id = f"{project_name}/{design_name}"
        
        # 尝试重连
        if self.reconnect():
            # 重连后再次尝试切换
            try:
                self._current_session.hfss_app.load_project(project_name)
                self._current_session.hfss_app.set_active_design(design_name)
                self._current_session.name = project_name
                self._current_session.design_name = design_name
                session_id = f"{project_name}/{design_name}"
                self._sessions = {session_id: self._current_session}
                logger.info(f"Switched to: {session_id}")
                return self._current_session
            except:
                pass
        
        # 必须有现有 HFSS 进程才能创建 session
        if not self._check_existing_hfss_processes():
            logger.error("Cannot create session: No existing HFSS process. Please open HFSS first.")
            raise Exception("No existing HFSS process")
        
        logger.info(f"Creating session: {session_id}")
        
        try:
            hfss_app = Hfss(
                project=project_name,
                design=design_name,
                solution_type=solution_type,
                new_desktop=False,
                close_on_exit=False
            )
            
            # 保存到全局变量，防止被垃圾回收！
            global _global_hfss
            _global_hfss = hfss_app
            
            session = ProjectSession(
                name=project_name,
                design_name=design_name,
                solution_type=solution_type,
                hfss_app=hfss_app,
                is_active=True
            )
            
            self._sessions[session_id] = session
            self._current_session = session
            self._initialized = True
            
            logger.info(f"Session created: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def close_session(self, release_resources: bool = True) -> bool:
        """关闭 session"""
        if not self._current_session:
            logger.info("No active session to close")
            return False
        
        session_id = f"{self._current_session.name}/{self._current_session.design_name}"
        
        if release_resources and self._current_session.hfss_app:
            try:
                self._current_session.hfss_app.release_desktop()
                logger.info("Desktop resources released")
            except Exception as e:
                logger.warning(f"Failed to release desktop: {e}")
        
        self._current_session.is_active = False
        self._current_session = None
        self._sessions = {}
        self._initialized = False
        
        logger.info(f"Session closed: {session_id}")
        return True
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [
            {
                "id": f"{s.name}/{s.design_name}",
                "project": s.name,
                "design": s.design_name,
                "solution_type": s.solution_type,
                "active": s.is_active,
                "current": s is self._current_session
            }
            for s in self._sessions.values()
        ]


# Global session manager
session_manager = HfssSessionManager()

# Global hfss_app reference - 防止被垃圾回收！
_global_hfss: Optional[Hfss] = None

# State persistence
STATE_FILE = "hfss_session_state.json"

def save_session_state():
    """保存会话状态到文件"""
    import json
    try:
        state = {
            "initialized": session_manager._initialized,
            "project_name": session_manager._current_session.name if session_manager._current_session else None,
            "design_name": session_manager._current_session.design_name if session_manager._current_session else None,
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        logger.info(f"Session state saved: {state}")
    except Exception as e:
        logger.warning(f"Failed to save session state: {e}")

def load_session_state() -> dict:
    """从文件加载会话状态"""
    import json
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def restore_session():
    """尝试恢复之前的会话"""
    state = load_session_state()
    if state.get("initialized"):
        project_name = state.get("project_name")
        design_name = state.get("design_name")
        if project_name and design_name:
            logger.info(f"Attempting to restore session: {project_name}/{design_name}")
            try:
                session_manager._initialized = True
                session_manager.create_session(project_name, design_name)
                session_manager._initialized = True
                logger.info("Session restored successfully")
                return True
            except Exception as e:
                logger.warning(f"Failed to restore session: {e}")
                session_manager._initialized = False
    return False


def ensure_connection() -> Optional[Hfss]:
    """确保有有效连接，返回 hfss_app（不自动重连）"""
    if session_manager.is_valid():
        return session_manager.current.hfss_app
    return None


# ============================================================================
# MCP TOOLS DEFINITION
# ============================================================================

def get_tool_definitions() -> List[Tool]:
    """Return all available MCP tools"""
    return [
        Tool(
            name="hfss_create_project",
            description="Create a new HFSS project. Returns project info on success.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Project name", "default": "HFSS_project"},
                    "design_name": {"type": "string", "description": "Design name", "default": "HFSSDesign1"},
                    "solution_type": {"type": "string", "description": "Solution type", "enum": ["Terminal", "DrivenModal", "Driven", "Eigenmode", "Transient"], "default": "Terminal"}
                }
            }
        ),
        Tool(
            name="hfss_create_box",
            description="Create a box/rectangular prism",
            inputSchema={
                "type": "object",
                "properties": {
                    "center_position": {"type": "array", "items": {"type": "number"}, "description": "[x, y, z] center position", "minItems": 3, "maxItems": 3},
                    "dimensions": {"type": "array", "items": {"type": "number"}, "description": "[dx, dy, dz] dimensions", "minItems": 3, "maxItems": 3},
                    "name": {"type": "string", "description": "Object name"},
                    "material": {"type": "string", "description": "Material name", "default": "vacuum"}
                },
            "required": ["center_position", "dimensions"]
            }
        ),
        Tool(
            name="hfss_list_objects",
            description="List all objects in the modeler",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {"type": "string", "description": "Filter by material or name pattern"}
                }
            }
        ),
        Tool(
            name="hfss_save_project",
            description="Save the current project",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Save path (optional)"}
                }
            }
        ),
        Tool(
            name="hfss_close_project",
            description="Close current project (session stays active)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="hfss_list_projects",
            description="List all active HFSS sessions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="hfss_get_session_status",
            description="Get detailed status of current HFSS session",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="hfss_get_process_status",
            description="Get HFSS process/application status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="hfss_get_messages",
            description="Get HFSS messages/logs from the current session",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of recent messages to return", "default": 50}
                }
            }
        ),
        Tool(
            name="hfss_start_app",
            description="Connect to existing HFSS application (no new session created)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="hfss_launch_app",
            description="Launch a new HFSS application with GUI (creates new session)",
            inputSchema={
                "type": "object",
                "properties": {
                    "non_graphical": {"type": "boolean", "description": "Run in non-graphical mode", "default": False}
                }
            }
        ),
        Tool(
            name="hfss_stop_app",
            description="Stop/Close HFSS application and release resources",
            inputSchema={
                "type": "object",
                "properties": {
                    "force": {"type": "boolean", "description": "Force close HFSS process", "default": False}
                }
            }
        ),
        Tool(
            name="hfss_restart_app",
            description="Restart HFSS application",
            inputSchema={
                "type": "object",
                "properties": {
                    "non_graphical": {"type": "boolean", "description": "Run in non-graphical mode", "default": True}
                }
            }
        ),
    ]


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> str:
    """Handle tool calls and dispatch to appropriate handler"""
    
    def success(msg: str) -> str:
        return f"[OK] {msg}"
    
    def error(msg: str) -> str:
        return f"[ERROR] {msg}"
    
    try:
        if name == "hfss_create_project":
            project_name = arguments.get("project_name", "HFSS_project")
            design_name = arguments.get("design_name", "HFSSDesign1")
            solution_type = arguments.get("solution_type", "Terminal")
            
            session = session_manager.create_session(
                project_name=project_name,
                design_name=design_name,
                solution_type=solution_type
            )
            return success(f"Project created: {project_name}/{design_name} (Solution: {solution_type})")
        
        elif name == "hfss_create_box":
            hfss = ensure_connection()
            if not hfss:
                return error("No active project")
            
            center = arguments["center_position"]
            dims = arguments["dimensions"]
            box_name = arguments.get("name", "Box1")
            material = arguments.get("material", "vacuum")
            
            hfss.modeler.create_box(origin=center, sizes=dims, name=box_name)
            if material != "vacuum":
                hfss.assign_material(box_name, material)
            return success(f"Box '{box_name}' created at {center} with size {dims}")
        
        elif name == "hfss_list_objects":
            hfss = ensure_connection()
            if not hfss:
                return error("No active project")
            
            filter_str = arguments.get("filter", "")
            objects = hfss.modeler.object_names
            
            if filter_str:
                objects = [o for o in objects if filter_str.lower() in o.lower()]
            
            if not objects:
                return "No objects found"
            return "\n".join([f"- {o}" for o in objects])
        
        elif name == "hfss_save_project":
            hfss = ensure_connection()
            if not hfss:
                return error("No active project")
            
            path = arguments.get("path")
            if path:
                hfss.save_project(path)
                return success(f"Project saved to: {path}")
            else:
                hfss.save_project()
                return success("Project saved")
        
        elif name == "hfss_close_project":
            if session_manager.is_valid():
                try:
                    session_manager.current.hfss_app.close_project()
                    return success("Project closed (session active)")
                except Exception as e:
                    return error(f"Failed to close project: {e}")
            return error("No active project")
        
        elif name == "hfss_list_projects":
            sessions = session_manager.list_sessions()
            if not sessions:
                return "No active HFSS sessions"
            result = []
            for s in sessions:
                label = f"- {s['id']} ({s['solution_type']})"
                if s["current"]:
                    label += " [CURRENT]"
                result.append(label)
            return "\n".join(result)
        
        elif name == "hfss_get_session_status":
            hfss = ensure_connection()
            if not hfss:
                return error("No HFSS connection")
            
            status_lines = ["=== HFSS Session Status ==="]
            status_lines.append(f"\nCurrent Design:")
            status_lines.append(f"  Project: {hfss.project_name}")
            status_lines.append(f"  Design: {hfss.design_name}")
            status_lines.append(f"  Solution Type: Terminal")
            status_lines.append(f"  Objects: {len(hfss.modeler.object_names)}")
            
            status_lines.append(f"\nAll Designs in {hfss.project_name}:")
            try:
                designs = hfss.design_list
                if designs:
                    for design_name in designs:
                        is_current = " [CURRENT]" if design_name == hfss.design_name else ""
                        status_lines.append(f"  - {design_name}{is_current}")
                else:
                    status_lines.append(f"  (No designs found)")
            except Exception as e:
                status_lines.append(f"  (Unable to list designs: {e})")
            
            try:
                status_lines.append(f"\nProject Path: {hfss.project_path}")
            except:
                pass
            
            try:
                status_lines.append(f"AEDT Version: {hfss.aedt_version}")
            except:
                pass
            
            return success("\n".join(status_lines))
        
        elif name == "hfss_get_messages":
            hfss = ensure_connection()
            if not hfss:
                return error("No HFSS connection")
            
            limit = arguments.get("limit", 50)
            
            try:
                messages = hfss.odesktop.GetMessages("", "", True)
                
                if not messages:
                    return success("No messages in the log")
                
                recent_messages = messages[-limit:] if len(messages) > limit else messages
                result_lines = [f"=== Last {len(recent_messages)} Messages ==="]
                for msg in recent_messages:
                    clean_msg = msg.strip()
                    if clean_msg:
                        result_lines.append(f"- {clean_msg}")
                
                return success("\n".join(result_lines))
            except Exception as e:
                return error(f"Failed to get messages: {e}")
        
        elif name == "hfss_get_process_status":
            hfss_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if 'ansys' in proc.info['name'].lower() or 'hfss' in proc.info['name'].lower():
                        hfss_processes.append(proc.info)
                except:
                    pass
            
            sessions = session_manager.list_sessions()
            status = f"HFSS Running: {'Yes' if hfss_processes else 'No'} | Sessions: {len(sessions)} | Connected: {'Yes' if session_manager.is_valid() else 'No'}"
            
            return success(status)
        
        elif name == "hfss_start_app":
            if session_manager.is_valid():
                return success(f"HFSS already connected")
            
            if restore_session():
                save_session_state()
                return success(f"HFSS connected (restored)")
            
            if session_manager.reconnect():
                save_session_state()
                return success(f"HFSS connected")
            return error("Failed to connect to HFSS")
        
        elif name == "hfss_stop_app":
            force = arguments.get("force", False)
            
            if not session_manager.is_valid():
                return error("No active HFSS connection")
            
            session_manager.close_session(release_resources=True)
            
            if force:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'ansys' in proc.info['name'].lower() or 'hfss' in proc.info['name'].lower():
                            psutil.Process(proc.info['pid']).kill()
                    except:
                        pass
                return success("HFSS forcefully stopped")
            return success("HFSS stopped and resources released")
        
        elif name == "hfss_restart_app":
            session_manager.close_session(release_resources=True)
            
            if session_manager.init_session():
                return success(f"HFSS restarted")
            return error("Failed to restart HFSS")
        
        elif name == "hfss_launch_app":
            non_graphical = arguments.get("non_graphical", False)
            
            if session_manager.is_valid():
                return success(f"HFSS already connected")
            
            try:
                logger.info(f"Launching new HFSS (non_graphical={non_graphical})...")
                hfss_app = Hfss(
                    project=None,
                    design=None,
                    new_desktop=True,
                    non_graphical=non_graphical,
                    close_on_exit=False
                )
                
                session = ProjectSession(
                    name=hfss_app.project_name,
                    design_name=hfss_app.design_name,
                    solution_type="Terminal",
                    hfss_app=hfss_app,
                    is_active=True
                )
                
                session_id = f"{hfss_app.project_name}/{hfss_app.design_name}"
                session_manager._sessions[session_id] = session
                session_manager._current_session = session
                session_manager._initialized = True
                
                save_session_state()
                return success(f"HFSS launched with GUI (Session: {session_id})")
            except Exception as e:
                logger.error(f"Failed to launch HFSS: {e}")
                return error(f"Failed to launch HFSS: {e}")
        
        else:
            return error(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return error(str(e))


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# 需要连接的工具列表（会自动建立连接）
TOOLS_NEED_CONNECTION = [
    "hfss_create_project", "hfss_create_box", "hfss_list_objects",
    "hfss_save_project", "hfss_close_project", "hfss_list_projects",
    "hfss_get_session_status", "hfss_get_messages"
]

@app.list_tools()
async def list_tools() -> List[Tool]:
    return get_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[dict]:
    # 自动建立连接（仅对需要连接的工具）
    if name in TOOLS_NEED_CONNECTION and not session_manager.is_valid():
        restore_session() or session_manager.reconnect()
    
    result = await handle_tool_call(name, arguments)
    return [{"type": "text", "text": result}]


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for the MCP server"""
    logger.info("Starting ANSYS HFSS MCP Server...")
    logger.info("Available tools:")
    for tool in get_tool_definitions():
        logger.info(f"  - {tool.name}: {tool.description}")
    logger.info("Call hfss_start_app to connect to HFSS...")
    
    try:
        async with stdio_server() as (read, write):
            await app.run(read, write, app.create_initialization_options())
    except KeyboardInterrupt:
        logger.info("Shutting down HFSS MCP Server...")
        session_manager.close_session(release_resources=False)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
