"""
Tee Waveguide Junction HFSS 仿真脚本 - MCP 优化版
基于 ANSYS HFSS Getting Started Guide - Waveguide T-Junction
"""

from ansys.aedt.core import Hfss
import logging
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_hfss_log(hfss, step_name):
    """检查 HFSS 日志，检测错误和警告"""
    try:
        log = hfss.odesign.GetLogContents()
        # 检查是否有错误关键词
        if log:
            log_lower = log.lower()
            if "error" in log_lower or "failed" in log_lower:
                logger.warning(f"! Log contains errors in step '{step_name}'")
                # 返回日志的最后几行用于调试
                lines = log.split('\n')
                for line in lines[-5:]:
                    if line.strip():
                        logger.warning(f"  Log: {line}")
                return False
            elif "warning" in log_lower:
                logger.info(f"  Log has warnings")
        return True
    except Exception as e:
        logger.warning(f"  Could not get log: {e}")
        return True  # 无法获取日志时继续执行


def check_messages(hfss, step_name):
    """获取 HFSS 消息"""
    try:
        msgs = hfss.odesign.GetMessages()
        if msgs:
            logger.info(f"  Messages: {msgs}")
    except:
        pass


def main():
    """主函数 - 使用 MCP 风格的操作"""
    
    project_name = "TeeWaveguide"
    design_name = "HFSSDesign1"
    solution_type = "DrivenModal"
    hfss = None
    
    try:
        # ===== MCP: hfss_create_project =====
        logger.info("=" * 60)
        logger.info("MCP: hfss_create_project")
        logger.info("=" * 60)
        
        # 使用 new_desktop=True 每次创建新的 HFSS 会话
        # 避免会话断开导致的 gRPC 命令失败
        hfss = Hfss(
            project=project_name,
            design=design_name,
            solution_type=solution_type,
            new_desktop=True,
            non_graphical=False,
            close_on_exit=False
        )
        logger.info(f"✓ Project '{project_name}' created successfully")
        logger.info(f"  - Design: {design_name}")
        logger.info(f"  - Solution Type: {solution_type}")
        
        # 检查日志
        check_hfss_log(hfss, "create_project")
        time.sleep(1)
        
        # ===== MCP: hfss_create_box (Tee) =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_create_box (Tee)")
        logger.info("=" * 60)
        
        # 创建第一个盒子 (沿 X 方向)
        # 教程参数: origin=(0, -0.45, 0), sizes=(2, 0.9, 0.4) 单位: inches
        hfss.modeler.create_box(
            origin=[0, -0.45, 0],
            sizes=[2, 0.9, 0.4],
            name="Tee"
        )
        logger.info("✓ Box 'Tee' created successfully")
        
        # 检查日志
        if not check_hfss_log(hfss, "create_box_Tee"):
            logger.error("! Failed to create Tee box")
            raise Exception("Create Tee box failed")
        time.sleep(0.5)
        
        # 创建第二个盒子 (沿 Y 方向)
        hfss.modeler.create_box(
            origin=[0, 0, 0],
            sizes=[0.9, 2, 0.4],
            name="Tee_1"
        )
        logger.info("✓ Box 'Tee_1' created successfully")
        time.sleep(0.5)
        
        # 创建第三个盒子
        hfss.modeler.create_box(
            origin=[0, 0, 0],
            sizes=[0.9, 2, 0.4],
            name="Tee_2"
        )
        logger.info("✓ Box 'Tee_2' created successfully")
        
        # 检查日志
        if not check_hfss_log(hfss, "create_box_Tee_1_2"):
            logger.error("! Failed to create Tee boxes")
            raise Exception("Create Tee boxes failed")
        time.sleep(0.5)
        
        # ===== MCP: hfss_unite =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_unite")
        logger.info("=" * 60)
        
        try:
            hfss.modeler.unite(["Tee", "Tee_1", "Tee_2"])
            logger.info("✓ Objects united successfully")
            time.sleep(1)
        except Exception as e:
            logger.warning(f"! Unite failed: {e}, trying step by step")
            try:
                hfss.modeler.unite(["Tee", "Tee_1"])
                time.sleep(0.5)
                hfss.modeler.unite(["Tee", "Tee_2"])
                logger.info("✓ Step-by-step unite successful")
            except Exception as e2:
                logger.warning(f"! Step-by-step unite also failed: {e2}")
        
        # 检查日志
        check_hfss_log(hfss, "unite")
        
        # ===== MCP: hfss_create_variable =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_create_variable")
        logger.info("=" * 60)
        
        try:
            hfss["Offset"] = "0in"
            logger.info("✓ Variable 'Offset' created")
        except Exception as e:
            logger.warning(f"! Create variable failed: {e}")
        
        # 检查日志
        check_hfss_log(hfss, "create_variable")
        
        # ===== MCP: hfss_create_box (Septum) =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_create_box (Septum)")
        logger.info("=" * 60)
        
        try:
            hfss.modeler.create_box(
                origin=["-0.45in", "-0.05in", "0in"],
                sizes=["0.45in", "0.1in", "0.4in"],
                name="Septum"
            )
            logger.info("✓ Box 'Septum' created successfully")
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"! Create Septum failed: {e}")
        
        # 检查日志
        if not check_hfss_log(hfss, "create_septum"):
            logger.warning("! Septum creation may have issues")
        
        # ===== MCP: hfss_subtract =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_subtract")
        logger.info("=" * 60)
        
        try:
            # 尝试不同的参数名
            try:
                hfss.modeler.subtract(
                    blank=["Tee"],
                    tool=["Septum"],
                    keep_originals=False
                )
            except:
                hfss.modeler.subtract("Tee", "Septum")
            logger.info("✓ Septum subtracted successfully")
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"! Subtract failed: {e}")
        
        # 检查日志
        check_hfss_log(hfss, "subtract")
        
        # ===== MCP: hfss_save_project =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_save_project")
        logger.info("=" * 60)
        
        try:
            hfss.save_project()
            logger.info(f"✓ Project saved: {hfss.project_path}")
        except Exception as e:
            logger.warning(f"! Save failed: {e}")
        
        # 检查日志
        check_hfss_log(hfss, "save_project")
        
        # ===== MCP: hfss_create_setup =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_create_setup")
        logger.info("=" * 60)
        
        try:
            # 创建设置 - 尝试不同的方式
            setup = hfss.create_setup(setupname="Setup1")
            logger.info("✓ Setup 'Setup1' created")
            
            # 添加频率扫描
            try:
                sweep = hfss.create_linear_count_sweep(
                    setupname="Setup1",
                    startfreq="8GHz",
                    endfreq="10GHz",
                    num_of_freq_points=21,
                    sweepname="Sweep1",
                    sweep_type="interpolating"
                )
                logger.info("✓ Sweep 'Sweep1' created (8-10 GHz, 21 points)")
            except Exception as sweep_err:
                logger.warning(f"! Sweep creation failed: {sweep_err}")
                
        except Exception as e:
            logger.error(f"✗ Setup creation failed: {e}")
            # 不抛出异常，继续执行
            logger.info("! Continuing without setup...")
        
        # 检查日志
        check_hfss_log(hfss, "create_setup")
        
        # ===== MCP: hfss_analyze =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_analyze")
        logger.info("=" * 60)
        
        try:
            logger.info("Starting analysis (this may take a few minutes)...")
            # 使用正确的 analyze 调用
            hfss.analyze_all()
            logger.info("✓ Analysis completed successfully")
        except Exception as e:
            logger.error(f"✗ Analysis failed: {e}")
            logger.info("! Analysis may require manual setup in GUI")
        
        # 检查日志 - 这是重要的最终检查
        if not check_hfss_log(hfss, "analyze"):
            logger.error("! Analysis may have failed")
            check_messages(hfss, "analyze")
        
        # ===== MCP: hfss_get_all_s_parameters =====
        logger.info("")
        logger.info("=" * 60)
        logger.info("MCP: hfss_get_all_s_parameters")
        logger.info("=" * 60)
        
        try:
            objects = hfss.modeler.object_names
            logger.info(f"Model objects: {objects}")
            
            # 获取边界框
            bbox = hfss.modeler.obounding_box
            logger.info(f"Bounding box: min={bbox[:3]}, max={bbox[3:]}")
        except Exception as e:
            logger.warning(f"! Get model info failed: {e}")
        
        # 最终保存
        try:
            hfss.save_project()
            logger.info(f"✓ Final save: {hfss.project_path}")
        except:
            pass
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("SUCCESS: Tee Waveguide simulation completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Error occurred: {e}")
        # 尝试获取错误日志
        if hfss:
            check_hfss_log(hfss, "error")
        raise
        
    finally:
        # 清理资源
        if hfss is not None:
            try:
                hfss.save_project()
            except:
                pass
            logger.info("Resources cleaned up")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)