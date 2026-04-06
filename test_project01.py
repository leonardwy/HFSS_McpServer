"""
测试脚本：创建工程 testProject01，绘制边长1cm的立方体，设置金属材料，保存工程
"""

from ansys.aedt.core import Hfss
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主测试函数"""
    
    # ===== 步骤1: 创建工程 =====
    logger.info("=" * 50)
    logger.info("步骤1: 创建工程 'testProject01'")
    logger.info("=" * 50)
    
    project_name = "testProject01"
    design_name = "HFSSDesign1"
    solution_type = "Terminal"
    
    try:
        # 使用 new_desktop=False 复用已打开的 Desktop
        # 如果已有打开的 Desktop，则不会启动新进程
        hfss = Hfss(
            project=project_name,
            design=design_name,
            solution_type=solution_type,
            new_desktop=False,
            non_graphical=False,
            close_on_exit=False
        )
        logger.info(f"✓ 工程 '{project_name}' 创建成功")
        logger.info(f"  - Design: {design_name}")
        logger.info(f"  - Solution Type: {solution_type}")
    except Exception as e:
        logger.error(f"✗ 创建工程失败: {e}")
        raise
    
    # ===== 步骤2: 绘制边长1cm的立方体 =====
    logger.info("")
    logger.info("=" * 50)
    logger.info("步骤2: 绘制边长1cm的立方体")
    logger.info("=" * 50)
    
    # 边长1cm = 10mm (HFSS默认单位是mm)
    cube_size_mm = 10  # 10mm = 1cm
    center_position = [0, 0, 0]  # 立方体中心在原点
    box_name = "Cube1"
    
    try:
        hfss.modeler.create_box(
            origin=center_position,
            sizes=[cube_size_mm, cube_size_mm, cube_size_mm],
            name=box_name
        )
        logger.info(f"✓ 立方体 '{box_name}' 创建成功")
        logger.info(f"  - 中心位置: {center_position}")
        logger.info(f"  - 尺寸: {cube_size_mm}mm x {cube_size_mm}mm x {cube_size_mm}mm")
    except Exception as e:
        logger.error(f"✗ 创建立方体失败: {e}")
        raise
    
    # ===== 步骤3: 设置材料为金属 =====
    logger.info("")
    logger.info("=" * 50)
    logger.info("步骤3: 设置材料为金属 (copper)")
    logger.info("=" * 50)
    
    # 使用 copper (铜) 作为金属材料
    material = "copper"
    
    try:
        hfss.assign_material(box_name, material)
        logger.info(f"✓ 材料 '{material}' 分配成功")
        logger.info(f"  - 对象: {box_name}")
    except Exception as e:
        logger.error(f"✗ 分配材料失败: {e}")
        raise
    
    # ===== 步骤4: 保存工程 =====
    logger.info("")
    logger.info("=" * 50)
    logger.info("步骤4: 保存工程")
    logger.info("=" * 50)
    
    try:
        hfss.save_project()
        logger.info(f"✓ 工程保存成功")
        logger.info(f"  - 路径: {hfss.project_path}")
    except Exception as e:
        logger.error(f"✗ 保存工程失败: {e}")
        raise
    
    # ===== 验证结果 =====
    logger.info("")
    logger.info("=" * 50)
    logger.info("验证结果")
    logger.info("=" * 50)
    
    try:
        # 获取模型信息
        objects = hfss.modeler.object_names
        logger.info(f"对象列表: {objects}")
        
        # 获取立方体的边界框
        bbox = hfss.modeler.obounding_box
        logger.info(f"立方体边界框:")
        logger.info(f"  - 最小点: {bbox[:3]}")
        logger.info(f"  - 最大点: {bbox[3:]}")
        
        # 获取材料信息
        mat = hfss.materials[box_name]
        logger.info(f"材料: {mat}")
        
        logger.info("")
        logger.info("=" * 50)
        logger.info("测试完成!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"✗ 验证失败: {e}")
        raise
    
    return hfss


if __name__ == "__main__":
    hfss_app = main()
    # 不自动关闭 Desktop，保持会话以便用户在 GUI 中查看
    logger.info("工程已创建完成，请查看结果。")
