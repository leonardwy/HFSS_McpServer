"""
Tee Waveguide Junction HFSS 仿真脚本 - 优化版
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


def create_tee_waveguide():
    """创建 Tee Waveguide Junction 模型 - 优化版"""
    
    project_name = "TeeWaveguide"
    design_name = "HFSSDesign1"
    solution_type = "DrivenModal"
    
    # ===== 步骤1: 创建工程 =====
    logger.info("=" * 60)
    logger.info("步骤1: 创建工程 'TeeWaveguide'")
    logger.info("=" * 60)
    
    # 使用 new_desktop=True 确保每次创建新会话
    hfss = Hfss(
        project=project_name,
        design=design_name,
        solution_type=solution_type,
        new_desktop=True,
        non_graphical=False,
        close_on_exit=False
    )
    logger.info(f"✓ 工程 '{project_name}' 创建成功")
    logger.info(f"  - Solution Type: {solution_type}")
    
    # 等待一下让对象初始化
    time.sleep(1)
    
    # ===== 步骤2: 绘制 T-Junction 模型 =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤2: 绘制 T-Junction 模型")
    logger.info("=" * 60)
    
    # 绘制第一个盒子 (沿 X 方向)
    # 教程中: 位置 (0, -0.45, 0), 尺寸 (2, 0.9, 0.4)
    hfss.modeler.create_box(
        origin=[0, -0.45, 0],
        sizes=[2, 0.9, 0.4],
        name="Tee"
    )
    logger.info("✓ 第一个盒子 Tee 创建成功")
    time.sleep(0.5)
    
    # 绘制第二个盒子 (沿 Y 方向)
    hfss.modeler.create_box(
        origin=[0, 0, 0],
        sizes=[0.9, 2, 0.4],
        name="Tee_1"
    )
    logger.info("✓ 第二个盒子 Tee_1 创建成功")
    time.sleep(0.5)
    
    # 绘制第三个盒子 (沿 -Y 方向)
    hfss.modeler.create_box(
        origin=[0, 0, 0],
        sizes=[0.9, 2, 0.4],
        name="Tee_2"
    )
    logger.info("✓ 第三个盒子 Tee_2 创建成功")
    time.sleep(0.5)
    
    # ===== 步骤3: 合并盒子 =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤3: 合并盒子")
    logger.info("=" * 60)
    
    # 合并三个盒子
    try:
        # 先保存
        hfss.save_project()
        time.sleep(1)
        
        # 合并
        hfss.modeler.unite(["Tee", "Tee_1", "Tee_2"])
        logger.info("✓ 合并 3 个对象为 Tee")
        time.sleep(1)
    except Exception as e:
        logger.warning(f"合并失败: {e}")
        # 尝试逐个合并
        try:
            hfss.modeler.unite(["Tee", "Tee_1"])
            time.sleep(0.5)
            hfss.modeler.unite(["Tee", "Tee_2"])
            logger.info("✓ 逐步合并成功")
        except Exception as e2:
            logger.warning(f"逐步合并也失败: {e2}")
    
    # ===== 步骤4: 创建 Septum =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤4: 创建 Septum")
    logger.info("=" * 60)
    
    # 创建变量
    try:
        hfss["Offset"] = "0in"
        logger.info("✓ 变量 Offset 创建成功")
    except Exception as e:
        logger.warning(f"创建变量失败: {e}")
    
    # 创建 Septum
    try:
        hfss.modeler.create_box(
            origin=["-0.45in", "-0.05in", "0in"],
            sizes=["0.45in", "0.1in", "0.4in"],
            name="Septum"
        )
        logger.info("✓ Septum 创建成功")
        time.sleep(0.5)
        
        # 减去 Septum - 使用正确的参数名
        try:
            hfss.modeler.subtract(
                blank=["Tee"],
                tool=["Septum"],
                keep_originals=False
            )
            logger.info("✓ Septum 已从 Tee 中减去")
        except Exception as e:
            logger.warning(f"减去 Septum 失败，跳过: {e}")
    except Exception as e:
        logger.warning(f"创建 Septum 失败，跳过: {e}")
    
    # 尝试保存，不强制
    try:
        hfss.save_project()
        logger.info("✓ 工程已保存")
    except:
        logger.warning("保存失败，继续执行...")
    time.sleep(1)
    
    # ===== 步骤5: 获取边界框 =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤5: 获取模型信息")
    logger.info("=" * 60)
    
    try:
        bbox = hfss.modeler.obounding_box
        logger.info(f"模型边界框: min={bbox[:3]}, max={bbox[3:]}")
    except Exception as e:
        logger.warning(f"获取边界框失败: {e}")
    
    objects = hfss.modeler.object_names
    logger.info(f"模型对象: {objects}")
    
    # ===== 步骤6: 设置仿真参数 =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤6: 设置仿真参数")
    logger.info("=" * 60)
    
    try:
        # 创建求解设置
        setup = hfss.create_setup("Setup1")
        setup.props["Frequency"] = "10GHz"
        setup.props["MaximumDeltaS"] = "0.01"
        setup.props["MaximumPasses"] = 6
        logger.info("✓ 求解设置创建成功 (10 GHz)")
        
        # 添加频率扫描
        hfss.create_linear_count_sweep(
            setupname="Setup1",
            startfreq="8GHz",
            endfreq="10GHz",
            num_of_freq_points=21,  # 减少点数加快速度
            sweepname="Sweep1",
            sweep_type="interpolating"
        )
        logger.info("✓ 频率扫描设置成功 (8-10 GHz, 21点)")
        
        hfss.save_project()
        logger.info("✓ 工程保存成功")
        
    except Exception as e:
        logger.error(f"✗ 设置仿真参数失败: {e}")
        raise
    
    # ===== 步骤7: 运行仿真 =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤7: 运行仿真")
    logger.info("=" * 60)
    
    try:
        logger.info("开始分析 (这可能需要几分钟)...")
        hfss.analyze(setupname="Setup1")
        logger.info("✓ 仿真完成")
    except Exception as e:
        logger.error(f"✗ 仿真失败: {e}")
        raise
    
    # ===== 步骤8: 保存并结束 =====
    logger.info("")
    logger.info("=" * 60)
    logger.info("步骤8: 完成")
    logger.info("=" * 60)
    
    hfss.save_project()
    logger.info(f"✓ 工程保存成功")
    logger.info(f"  - 路径: {hfss.project_path}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Tee Waveguide 仿真完成!")
    logger.info("=" * 60)
    
    return hfss


if __name__ == "__main__":
    try:
        hfss_app = create_tee_waveguide()
    except Exception as e:
        logger.error(f"仿真过程出错: {e}")
        sys.exit(1)