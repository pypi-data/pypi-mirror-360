"""
卫星图像生成模块
提供基于卫星图像和指标数据生成可视化地图的功能

新功能特性：
1. 增强插值算法：集成Alpha Shape边界检测，支持复杂水域形状
2. 纯净版热力图：支持透明背景和多种格式输出
   - PNG格式：适合栅格图像处理，支持透明背景
   - SVG格式：矢量图形，可无限缩放，文件更小
3. 国标分级：自动应用GB 3838-2002水质标准分级
4. 智能边界：三种边界检测算法（Alpha Shape、凸包、密度边界）

输出文件类型：
- distribution: 散点分布图
- interpolation: 带装饰的插值热力图（卫星底图+坐标轴+标题）
- clean_transparent: 纯净版插值热力图（透明背景，无装饰元素）
- level: 国标等级分布图（仅支持国标指标）

使用示例：
# 生成透明背景PNG版本
generate_clean_interpolation_map(data, 'cod', 'output.png', transparent_bg=True, output_format='png')

# 生成透明背景SVG版本  
generate_clean_interpolation_map(data, 'cod', 'output.svg', transparent_bg=True, output_format='svg')

# 批量生成多种变体
results = generate_clean_interpolation_with_options(data, 'cod', './outputs/')
"""
import os
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from PIL import Image
import matplotlib.image as mpimg
from datetime import datetime
import cv2
from scipy.interpolate import RBFInterpolator, griddata
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull, Delaunay, distance_matrix
from scipy.ndimage import gaussian_filter
from matplotlib.path import Path

plt.rcParams.update({'font.size': 18})
plt.rcParams['font.family'] = 'SimHei'  # 替换为你选择的字体
plt.rcParams['axes.unicode_minus']=False


logger = logging.getLogger(__name__)

# ================== 国标分级映射表（GB 3838-2002） ==================
INDICATOR_GRADE_CONFIG = {
    # COD（化学需氧量，mg/L）
    'cod': {
        'thresholds': [15, 20, 30, 40],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000']
    },
    # 氨氮 NH3-N（mg/L）
    'nh3n': {
        'thresholds': [0.15, 0.5, 1.0, 1.5],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000']
    },
    # 总磷 TP（mg/L）
    'tp': {
        'thresholds': [0.02, 0.1, 0.2, 0.3],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000']
    },
    # 总氮 TN（mg/L）
    'tn': {
        'thresholds': [0.2, 0.5, 1.0, 1.5],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000']
    },
    # 溶解氧 DO（mg/L，越高越好，分级反向）
    'do': {
        'thresholds': [2, 3, 5, 6],  # Ⅴ~Ⅱ类
        'labels': ['Ⅴ类', 'Ⅳ类', 'Ⅲ类', 'Ⅱ类', 'Ⅰ类'],
        'colors': ['#FF0000', '#FFA500', '#FFFF00', '#00FF7F', '#1E90FF'],
        'reverse': True
    },
    # pH
    'ph': {
        'thresholds': [6, 6.5, 8.5, 9],
        'labels': ['Ⅴ类', 'Ⅳ类', 'Ⅲ类', 'Ⅱ类', 'Ⅰ类'],
        'colors': ['#FF0000', '#FFA500', '#FFFF00', '#00FF7F', '#1E90FF'],
        'reverse': True
    },
    # 浊度（NTU，示例）
    'turbidity': {
        'thresholds': [1, 3, 10, 20],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000']
    },
    # 叶绿素a（μg/L，示例）
    'chla': {
        'thresholds': [1, 5, 10, 20],
        'labels': ['Ⅰ类', 'Ⅱ类', 'Ⅲ类', 'Ⅳ类', 'Ⅴ类'],
        'colors': ['#1E90FF', '#00FF7F', '#FFFF00', '#FFA500', '#FF0000']
    },
}

def get_indicator_grade_config(indicator):
    """
    获取指标的国标分级配置（阈值、标签、颜色）
    支持标准化名称（如do、cod、nh3n、tp、tn、ph、turbidity、chla）
    """
    key = indicator.lower()
    return INDICATOR_GRADE_CONFIG.get(key)

# ================== 增强插值算法（从heatmap_generator.py集成） ==================

def compute_convex_hull(points):
    """
    计算散点数据的凸包，返回凸包顶点坐标
    points: 二维数组，每行为一个点的坐标 (lon, lat)
    返回: 凸包顶点坐标数组
    """
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]
    return hull_points

def compute_alpha_shape(points, alpha=None):
    """
    计算Alpha Shape边界，能够处理凹陷形状
    points: 二维数组，每行为一个点的坐标 (lon, lat)
    alpha: Alpha参数，控制边界的"紧密度"，None时自动计算
    返回: 边界点的坐标数组
    """
    if len(points) < 3:
        return points
    
    # 计算Delaunay三角剖分
    tri = Delaunay(points)
    
    # 自动计算alpha值
    if alpha is None:
        # 基于点之间的平均距离来估算alpha
        distances = []
        for i in range(len(points)):
            for j in range(i+1, len(points)):
                dist = np.sqrt(np.sum((points[i] - points[j])**2))
                distances.append(dist)
        
        # 使用距离的某个百分位数作为alpha
        alpha = np.percentile(distances, 30)  # 可调整百分位数
    
    # 找到边界边
    boundary_edges = []
    
    # 遍历所有三角形
    for simplex in tri.simplices:
        # 计算三角形的外接圆半径
        triangle_points = points[simplex]
        
        # 计算外接圆半径
        a = np.linalg.norm(triangle_points[1] - triangle_points[0])
        b = np.linalg.norm(triangle_points[2] - triangle_points[1])
        c = np.linalg.norm(triangle_points[0] - triangle_points[2])
        
        # 半周长
        s = (a + b + c) / 2
        
        # 面积（海伦公式）
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        
        # 外接圆半径
        if area > 1e-10:  # 避免除零
            circumradius = (a * b * c) / (4 * area)
            
            # 如果外接圆半径小于alpha，则该三角形的边可能是边界
            if circumradius < alpha:
                for i in range(3):
                    edge = (simplex[i], simplex[(i+1) % 3])
                    boundary_edges.append(edge)
    
    # 找到只出现一次的边（边界边）
    edge_count = {}
    for edge in boundary_edges:
        edge_sorted = tuple(sorted(edge))
        edge_count[edge_sorted] = edge_count.get(edge_sorted, 0) + 1
    
    # 只保留出现一次的边
    true_boundary_edges = [edge for edge, count in edge_count.items() if count == 1]
    
    if not true_boundary_edges:
        # 如果没有找到边界，回退到凸包
        return compute_convex_hull(points)
    
    # 构建边界路径
    boundary_points = []
    remaining_edges = list(true_boundary_edges)
    
    if remaining_edges:
        # 从第一条边开始
        current_edge = remaining_edges.pop(0)
        boundary_points.extend([current_edge[0], current_edge[1]])
        
        # 尝试连接后续边
        while remaining_edges:
            last_point = boundary_points[-1]
            found_next = False
            
            for i, edge in enumerate(remaining_edges):
                if edge[0] == last_point:
                    boundary_points.append(edge[1])
                    remaining_edges.pop(i)
                    found_next = True
                    break
                elif edge[1] == last_point:
                    boundary_points.append(edge[0])
                    remaining_edges.pop(i)
                    found_next = True
                    break
            
            if not found_next:
                # 如果无法连接，尝试新的起始点
                if remaining_edges:
                    next_edge = remaining_edges.pop(0)
                    boundary_points.extend([next_edge[0], next_edge[1]])
    
    # 转换为坐标数组
    boundary_coords = points[boundary_points]
    
    return boundary_coords

def simple_knn_distances(points, grid_points, k=1):
    """
    简化的KNN距离计算，不依赖sklearn
    """
    distances = np.zeros((len(grid_points), k))
    indices = np.zeros((len(grid_points), k), dtype=int)
    
    for i, grid_point in enumerate(grid_points):
        # 计算到所有数据点的距离
        dists = np.sqrt(np.sum((points - grid_point)**2, axis=1))
        # 找到k个最近的点
        sorted_indices = np.argsort(dists)
        distances[i] = dists[sorted_indices[:k]]
        indices[i] = sorted_indices[:k]
    
    return distances, indices

def compute_density_based_boundary(points, density_threshold=0.5):
    """
    基于密度的边界检测算法（简化版本，不依赖sklearn）
    points: 二维数组，每行为一个点的坐标
    density_threshold: 密度阈值，控制边界的紧密度
    返回: 边界掩码创建函数
    """
    if len(points) < 3:
        return lambda x, y: np.ones_like(x, dtype=bool)
    
    # 计算每个点的局部密度（使用距离矩阵）
    dist_matrix = distance_matrix(points, points)
    n_neighbors = min(5, len(points) - 1)
    
    # 对每个点，找到第k近邻的距离
    local_density = np.zeros(len(points))
    for i in range(len(points)):
        # 排除自己（距离为0）
        distances = dist_matrix[i][dist_matrix[i] > 0]
        if len(distances) >= n_neighbors:
            kth_distance = np.partition(distances, n_neighbors-1)[n_neighbors-1]
            local_density[i] = 1.0 / (kth_distance + 1e-10)
        else:
            local_density[i] = 1.0
    
    density_threshold_value = np.percentile(local_density, density_threshold * 100)
    
    def create_boundary_mask(grid_lon, grid_lat):
        # 将网格坐标转换为点集
        grid_points = np.column_stack((grid_lon.ravel(), grid_lat.ravel()))
        
        # 对每个网格点，计算到最近数据点的距离
        distances_to_data, nearest_indices = simple_knn_distances(points, grid_points, k=1)
        
        # 获取最近数据点的密度
        nearest_densities = local_density[nearest_indices.ravel()]
        
        # 基于密度和距离创建掩码
        max_distance = np.percentile(distances_to_data.ravel(), 90)
        distance_mask = distances_to_data.ravel() < max_distance
        density_mask = nearest_densities > density_threshold_value
        
        # 组合掩码
        combined_mask = distance_mask & density_mask
        
        return combined_mask.reshape(grid_lon.shape)
    
    return create_boundary_mask

def create_convex_hull_mask(grid_lon, grid_lat, hull_points):
    """
    创建凸包掩码，标记网格中哪些点在凸包内
    grid_lon, grid_lat: 网格坐标
    hull_points: 凸包顶点坐标
    返回: 布尔掩码数组
    """
    # 将网格坐标转换为点集
    points = np.column_stack((grid_lon.ravel(), grid_lat.ravel()))
    
    # 创建凸包路径
    hull_path = Path(hull_points)
    
    # 检查每个网格点是否在凸包内
    mask = hull_path.contains_points(points)
    
    # 重新塑形为网格形状
    mask = mask.reshape(grid_lon.shape)
    
    return mask

def enhanced_interpolation_with_neighborhood(all_data, grid_resolution=200, method='linear', 
                                           neighborhood_radius=2, boundary_method='alpha_shape', indicator_col=None):
    """
    基于智能边界的高分辨率插值，包含邻域分析
    all_data: 包含所有文件数据的DataFrame
    grid_resolution: 网格分辨率
    method: 插值方法
    neighborhood_radius: 邻域分析半径(像素)
    boundary_method: 边界检测方法 ('convex_hull', 'alpha_shape', 'density_based')
    indicator_col: 指标列名，如果为None则使用第一个非坐标列
    返回: 插值结果、网格坐标、边界掩码、边界点
    """
    # 提取坐标和数值 - 适配maps.py的数据格式
    if 'longitude' in all_data.columns and 'latitude' in all_data.columns:
        points = all_data[['longitude', 'latitude']].values
    else:
        points = all_data[['lon', 'lat']].values
    
    # 获取指标列
    if indicator_col is not None:
        if indicator_col not in all_data.columns:
            raise ValueError(f"指定的指标列 {indicator_col} 不存在")
        values = all_data[indicator_col].values
    else:
        # 获取指标列（排除坐标列）
        coord_cols = ['longitude', 'latitude', 'lon', 'lat', 'index']
        value_cols = [col for col in all_data.columns if col not in coord_cols]
        
        if len(value_cols) == 0:
            raise ValueError("未找到有效的指标数据列")
        
        # 使用第一个指标列的数据
        values = all_data[value_cols[0]].values
    
    # 根据选择的方法计算边界
    if boundary_method == 'alpha_shape':
        boundary_points = compute_alpha_shape(points)
        # 确定经纬度范围（基于Alpha Shape）
        lon_min, lon_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
        lat_min, lat_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()
    elif boundary_method == 'density_based':
        boundary_mask_func = compute_density_based_boundary(points)
        # 使用全部数据范围
        lon_min, lon_max = points[:, 0].min(), points[:, 0].max()
        lat_min, lat_max = points[:, 1].min(), points[:, 1].max()
        boundary_points = None
    else:  # 默认使用凸包
        boundary_points = compute_convex_hull(points)
        lon_min, lon_max = boundary_points[:, 0].min(), boundary_points[:, 0].max()
        lat_min, lat_max = boundary_points[:, 1].min(), boundary_points[:, 1].max()
    
    # 扩展边界以确保完整覆盖
    lon_range = lon_max - lon_min
    lat_range = lat_max - lat_min
    margin_factor = 0.05  # 5%边界扩展
    
    lon_min -= lon_range * margin_factor
    lon_max += lon_range * margin_factor
    lat_min -= lat_range * margin_factor
    lat_max += lat_range * margin_factor
    
    # 创建高分辨率插值网格
    grid_lat, grid_lon = np.mgrid[lat_min:lat_max:grid_resolution*1j, 
                                 lon_min:lon_max:grid_resolution*1j]
    
    # 执行插值
    grid_values = griddata(points, values, (grid_lon, grid_lat), method=method)
    
    # 创建边界掩码
    if boundary_method == 'density_based':
        boundary_mask = boundary_mask_func(grid_lon, grid_lat)
    else:
        if boundary_points is not None:
            boundary_mask = create_convex_hull_mask(grid_lon, grid_lat, boundary_points)
        else:
            boundary_mask = np.ones_like(grid_lon, dtype=bool)
    
    # 将边界外的区域设为NaN
    grid_values[~boundary_mask] = np.nan
    
    # 邻域分析：使用高斯滤波平滑插值结果
    # 只对有效数据进行滤波
    valid_mask = ~np.isnan(grid_values)
    if np.any(valid_mask):
        # 创建临时数组，将NaN填充为0
        temp_values = np.copy(grid_values)
        temp_values[np.isnan(temp_values)] = 0
        
        # 应用高斯滤波
        smoothed_values = gaussian_filter(temp_values, sigma=neighborhood_radius)
        
        # 应用掩码，只保留边界内的平滑结果
        grid_values[valid_mask] = smoothed_values[valid_mask]
    
    return grid_values, grid_lon, grid_lat, boundary_mask, boundary_points

class SatelliteMapGenerator:
    """卫星图像生成器类"""
    
    def __init__(self, path_manager):
        """
        初始化卫星图像生成器
        
        Args:
            satellite_image_path: 卫星图像文件路径
            geo_bounds: 地理边界坐标 [min_lon, min_lat, max_lon, max_lat]
        """
        self.path_manager = path_manager
        self.satellite_geo_bounds = {}

            
    def init_maps(self, 
                  geo_info: dict,
                  satellite_path: str,
                  data: pd.DataFrame,
                  uav_data: pd.DataFrame
                ) -> Optional[str]:
        """
        生成指标卫星图
        
        Args:
            geo_info: 地理信息字典，包含边界坐标等
            satellite_path: 卫星图像文件路径
            data: 包含指标数据的DataFrame
            
        Returns:
            Optional[str]: 生成的图像文件路径，失败返回None
        """
        # 获取卫星地图边界
        self.satellite_geo_bounds = parse_geo_bounds(geo_info)
        # 获取卫星底图宽、高、读取的图像对象
        self.satellite_info = read_satellite(satellite_path)

        # 获取所有水质指标名称
        if data is not None:
            self.indicator_columns = [col for col in data.columns if col not in ['index', 'latitude', 'longitude']]
        elif uav_data is not None:
            logger.info("使用无人机数据生成指标卫星图")
            self.indicator_columns = [col for col in uav_data.columns if col not in ['index', 'latitude', 'longitude']]
        else:
            logger.error("实测数据 和 无人机数据 不能同时为空")
            raise ValueError("实测数据 和 无人机数据 不能同时为空")

        logging.info(f"检测到的水质指标: {', '.join(self.indicator_columns)}")

        # 获取数据的地理边界
        self.data_geo_bounds = get_data_geo_bounds(data) if data is not None else get_data_geo_bounds(uav_data)
        # 接收反演值数据，如果无实测值，这里传入的data为None，用无人机数据代替
        self.data = data if data is not None else uav_data
        # 接收无人机数据
        self.uav_data = uav_data
        # 获取水体掩膜 - 暂时禁用，使用Alpha Shape边界检测已足够
        self.get_water_mask(self.uav_data)

        if data is not None:
            # 检查多少点位在卫星图外
            points_outside, self.all_points_outside = self.check_points_in_bounds()
        else:
            self.all_points_outside = False
            logger.error("所有点位都在卫星图外，可能是为传递实测数据，或者是实测数据和飞行任务范围偏差太大。")


    def generate_indicator_map(self):
        if not self.all_points_outside:
            logging.info("开始生成各指标反演结果分布图...")

        save_paths = dict()
        for indicator in self.indicator_columns:
            save_paths[indicator] = {}
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 检查指标是否支持国标分级
            grade_cfg = get_indicator_grade_config(indicator)
            supports_grading = grade_cfg is not None

            # 根据是否支持国标分级决定生成哪些类型的图
            if supports_grading:
                map_types = ['distribution', 'interpolation', 'clean_interpolation_png', 'clean_interpolation_svg', 'level']
                logger.info(f"{indicator} 支持国标分级，将生成完整的图表集")
            else:
                map_types = ['distribution', 'interpolation', 'clean_interpolation_png', 'clean_interpolation_svg']
                logger.info(f"{indicator} 不支持国标分级，跳过等级图生成")

            for type in map_types:
                # 根据类型设置文件扩展名
                if type == 'clean_interpolation_svg':
                    map_filename = f"{indicator}_clean_transparent_{timestamp}.svg"
                elif type == 'clean_interpolation_png':
                    map_filename = f"{indicator}_clean_transparent_{timestamp}.png"
                else:
                    map_filename = f"{indicator}_{type}_{timestamp}.png"
                
                save_path = self.path_manager.get_file_path('maps', map_filename)

                if type == 'distribution':
                    result = generate_distribution_indicator_map(
                        self.data, indicator, self.satellite_info, save_path, 
                        self.satellite_geo_bounds, self.data_geo_bounds, self.all_points_outside
                    )
                elif type == 'interpolation':
                    # 生成带装饰的插值热力图
                    result, self.Z = generate_interpolation_indicator_map(
                        self.data, indicator, self.satellite_info, save_path, 
                        self.satellite_geo_bounds, self.data_geo_bounds, self.all_points_outside, self.water_mask
                    )
                elif type == 'clean_interpolation_png':
                    # 生成透明背景PNG版纯净插值热力图
                    result, clean_Z = generate_clean_interpolation_map(
                        self.data, indicator, save_path, 
                        grid_resolution=400, transparent_bg=True, output_format='png'
                    )
                    # 如果没有从interpolation类型获得Z数据，使用clean_interpolation的结果
                    if not hasattr(self, 'Z') or self.Z is None:
                        self.Z = clean_Z
                elif type == 'clean_interpolation_svg':
                    # 生成透明背景SVG版纯净插值热力图
                    result, _ = generate_clean_interpolation_map(
                        self.data, indicator, save_path, 
                        grid_resolution=400, transparent_bg=True, output_format='svg'
                    )
                elif type == 'level':
                    # 使用插值数据生成国标等级图
                    result = generate_level_indicator_map(
                        indicator, self.satellite_info, save_path, 
                        self.satellite_geo_bounds, self.data_geo_bounds, self.all_points_outside, self.Z
                    )
                    # 清理插值数据
                    self.Z = None

                if result and result != "skip":
                    save_paths[indicator][type] = result
                    logging.info(f"{indicator} 指标{type}图创建成功，保存路径: {result}")
                elif result == "skip":
                    logging.info(f"{indicator} 指标{type}图跳过生成（不支持国标分级）")
                else:
                    logging.warning(f"{indicator} 指标{type}图创建失败!")

        return save_paths
            
    def get_water_mask(self, uav_data):
        """获取卫星图像中的水体掩膜
        
        【此功能已暂时禁用】
        使用监督分类方法识别卫星图像中的水体区域。首先从已知的水体采样点提取RGB特征，
        然后使用这些特征训练一个简单的分类器来识别整个图像中的水体区域。
        
        由于Alpha Shape边界检测已能很好地确定插值区域范围，水体掩膜功能暂时禁用，
        避免功能重复和性能浪费。如需重新启用，请取消相关代码的注释。
        
        Returns:
            numpy.ndarray: 二值掩膜图像，水体区域为1，非水体区域为0
        """
        # 暂时禁用水体掩膜功能
        logger.info("水体掩膜功能已暂时禁用，使用Alpha Shape边界检测")
        self.water_mask = None
        return
        
        # 以下代码保留供将来使用
        try:
            # 获取卫星图像
            img_width, img_height, satellite_img = self.satellite_info
            
            # 提取水体采样点的RGB值作为训练数据
            water_samples = []
            for idx, row in uav_data.iterrows():
                lat, lon = row['latitude'], row['longitude']
                x, y, is_inside = geo_to_image_coords(
                    lat, lon,
                    img_width,
                    img_height,
                    self.satellite_geo_bounds
                )
                if is_inside:
                    # 获取该点的RGB值
                    rgb = satellite_img[y, x]
                    water_samples.append(rgb)

            if not water_samples:
                logger.warning("没有找到有效的水体采样点")
                return None
                
            # 将采样点转换为numpy数组
            water_samples = np.array(water_samples)
            
            # 使用随机森林分类器进行水体识别
            from sklearn.ensemble import RandomForestClassifier
            
            # 准备训练数据
            X_train = water_samples
            y_train = np.ones(len(water_samples))  # 水体样本标记为1
            
            # 随机采样非水体区域作为负样本
            non_water_samples = []
            for _ in range(len(water_samples)):
                y = np.random.randint(0, img_height)
                x = np.random.randint(0, img_width)
                non_water_samples.append(satellite_img[y, x])
            
            X_train = np.vstack([X_train, non_water_samples])
            y_train = np.concatenate([y_train, np.zeros(len(non_water_samples))])
            
            # 训练随机森林分类器
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)
            
            # 创建掩膜图像
            mask = np.zeros((img_height, img_width), dtype=np.uint8)
            
            # 对每个像素进行分类
            # 将图像重塑为二维数组，每行代表一个像素的RGB值
            pixels = satellite_img.reshape(-1, 3)
            # 使用随机森林分类器预测所有像素
            predictions = clf.predict(pixels)
            # 将预测结果重塑回原始图像形状
            self.water_mask = predictions.reshape(img_height, img_width).astype(np.uint8)
            
            # 使用形态学操作优化掩膜
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            logger.info("水体掩膜生成成功")
            # 创建子图显示卫星图和掩膜
            plt.figure(figsize=(12, 6))
            
            # 显示原始卫星图像
            plt.subplot(1, 2, 1)
            plt.imshow(cv2.cvtColor(satellite_img, cv2.COLOR_BGR2RGB))
            plt.title('卫星图像')
            plt.axis('off')
            
            # 显示掩膜图像
            plt.subplot(1, 2, 2)
            plt.imshow(self.water_mask, cmap='gray')
            plt.title('水体掩膜')
            plt.axis('off')
            
            # 保存图像
            mask_vis_path = self.path_manager.get_file_path('maps', 'water_mask_visualization.png')
            plt.savefig(mask_vis_path, bbox_inches='tight', dpi=300)
            plt.clf()         # 清除当前 figure 的内容（保持 figure 对象）
            plt.cla()         # 清除当前 axes 的内容（保持 axes 对象）
            plt.close()       # 关闭当前 figure，推荐用于循环中防止内存累积
            
            logger.info(f"水体掩膜可视化已保存至: {mask_vis_path}")
            
        except Exception as e:
            logger.error(f"生成水体掩膜时出错: {str(e)}")
        


    def check_points_in_bounds(self):
            """检查数据点是否在卫星图像范围内
            
            Returns:
                tuple: (超出范围的点数, 是否所有点都在范围内)
            """
            points_outside = 0
            all_points_outside = False
            
            for idx, row in self.data.iterrows():
                lat, lon = row['latitude'], row['longitude']
                _, _, is_inside = geo_to_image_coords(
                    lat, lon, 
                    self.satellite_info[0],  # img_width
                    self.satellite_info[1],  # img_height 
                    self.satellite_geo_bounds
                )
                if not is_inside:
                    points_outside += 1
            
            if points_outside != len(self.data):
                logger.warning(f"有 {points_outside}/{len(self.data)} 个数据点超出卫星图像范围")
            else:
                all_points_outside = True
                
            return points_outside, all_points_outside




# 创建单个以点带面图 - 使用增强插值算法
def generate_interpolation_indicator_map(data, indicator, satellite_info, save_path, satellite_geo_bounds, data_geo_bounds, all_points_outside, water_mask):
    """生成插值热力图 - 使用heatmap_generator的增强插值算法
    
    Args:
        data: 包含经纬度和指标值的数据框
        indicator: 要绘制的指标名称
        satellite_info: 卫星图像信息元组 (宽度, 高度, 图像对象)
        save_path: 保存路径
        satellite_geo_bounds: 卫星图像地理边界
        data_geo_bounds: 数据地理边界
        all_points_outside: 是否所有点都在卫星图像范围外
        water_mask: 水体掩膜
    """
    # 解包卫星数据信息
    img_width, img_height, img_obj = satellite_info
    
    # 准备数据用于增强插值算法
    prepared_data = data.copy()
    prepared_data['longitude'] = data['longitude']
    prepared_data['latitude'] = data['latitude']
    prepared_data[indicator] = data[indicator]
    
    # 使用增强插值算法生成插值数据
    try:
        grid_values, grid_lon, grid_lat, boundary_mask, boundary_points = enhanced_interpolation_with_neighborhood(
            prepared_data,
            grid_resolution=min(300, max(img_width, img_height)) if not all_points_outside else 300,
            method='linear',
            neighborhood_radius=2,
            boundary_method='alpha_shape',
            indicator_col=indicator
        )
    except Exception as e:
        logger.error(f"增强插值算法失败: {str(e)}，回退到原始算法")
        # 回退到原始RBF插值
        geo_bounds = data_geo_bounds if all_points_outside else satellite_geo_bounds
        x = np.linspace(geo_bounds[0], geo_bounds[2], img_width)
        y = np.linspace(geo_bounds[1], geo_bounds[3], img_height)
        X, Y = np.meshgrid(x, y)
        
        points = np.column_stack((data['longitude'], data['latitude']))
        values = data[indicator].values
        
        try:
            rbf = RBFInterpolator(points, values, kernel='thin_plate_spline')
            grid_points = np.column_stack((X.flatten(), Y.flatten()))
            grid_values = rbf(grid_points).reshape(X.shape)
            grid_lon, grid_lat = X, Y
        except Exception as e2:
            logger.error(f"RBF插值也失败: {str(e2)}")
            return None, None
    
    # 应用水体掩膜 - 暂时禁用，Alpha Shape边界检测已足够精确
    # if water_mask is not None and not all_points_outside:
    #     try:
    #         if water_mask.shape != grid_values.shape:
    #             from scipy.ndimage import zoom
    #             zoom_factor = (grid_values.shape[0]/water_mask.shape[0], grid_values.shape[1]/water_mask.shape[1])
    #             resampled_mask = zoom(water_mask, zoom_factor, order=0)
    #             grid_values = np.where(resampled_mask > 0, grid_values, np.nan)
    #             logger.info(f"水体掩膜已调整大小，从{water_mask.shape}到{grid_values.shape}")
    #         else:
    #             grid_values = np.where(water_mask > 0, grid_values, np.nan)
    #     except Exception as e:
    #         logger.warning(f"应用水体掩膜失败: {str(e)}")
    
    # 计算显示范围
    geo_bounds = data_geo_bounds if all_points_outside else satellite_geo_bounds
    
    # 创建图形
    if all_points_outside:
        # 对于没有卫星图像的情况
        fig = plt.figure(figsize=(12, 8))
        main_ax = fig.add_subplot(111)
        main_ax.add_patch(plt.Rectangle((geo_bounds[0], geo_bounds[1]), 
                                        geo_bounds[2]-geo_bounds[0], geo_bounds[3]-geo_bounds[1], 
                                        facecolor='lightgray'))
        dpi = 300
    else:
        # 有卫星图像的情况
        dpi = 100.0
        figsize = (img_width / dpi, img_height / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=True)
        main_ax = fig.add_axes([0.05, 0.1, 0.85, 0.8])
        
        # 显示卫星图像
        main_ax.imshow(img_obj, extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]], 
                       aspect='auto', origin='lower')
    
    # 设置坐标范围和刻度
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])
    
    num_ticks = 5
    lon_ticks = np.linspace(geo_bounds[0], geo_bounds[2], num_ticks)
    lat_ticks = np.linspace(geo_bounds[1], geo_bounds[3], num_ticks)
    
    main_ax.set_xticks(lon_ticks)
    main_ax.set_yticks(lat_ticks)
    main_ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    main_ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    
    # 添加轴标签
    main_ax.set_xlabel('经度', fontsize=20, labelpad=12)
    main_ax.set_ylabel('纬度', fontsize=20, labelpad=12)
    main_ax.tick_params(axis='both', which='major', labelsize=18, direction='out', pad=6)
    
    # 绘制插值热力图
    im = main_ax.imshow(grid_values, 
                       extent=[grid_lon.min(), grid_lon.max(), grid_lat.min(), grid_lat.max()],
                       aspect='auto', origin='lower', cmap='jet', alpha=0.8)
    
    # 添加颜色条
    cbar = fig.colorbar(im, ax=main_ax, fraction=0.05, pad=0.05)
    cbar.set_label(indicator, fontsize=20)
    cbar.ax.tick_params(labelsize=18)
    
    # 添加网格线
    main_ax.grid(True, linestyle='--', alpha=0.3)
    
    # 设置标题
    title = f"水质监测数据 - {indicator} (增强插值热力图)"
    if not all_points_outside:
        title += " - 卫星底图"
    main_ax.set_title(title, fontsize=22, pad=20)
    
    # 保存图像
    if not all_points_outside:
        plt.savefig(save_path, dpi=dpi, bbox_inches=None, pad_inches=0)
    else:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    logger.info(f"增强插值图已保存至: {save_path}")
    
    plt.clf()
    plt.cla()
    plt.close()
    
    return save_path, grid_values

# 创建纯净版插值图
def generate_clean_interpolation_map(data, indicator, save_path, grid_resolution=400, 
                                   transparent_bg=True, output_format='png'):
    """生成纯净版插值热力图，无装饰元素
    
    Args:
        data: 包含经纬度和指标值的数据框
        indicator: 要绘制的指标名称  
        save_path: 保存路径
        grid_resolution: 网格分辨率
        transparent_bg: 是否使用透明背景
        output_format: 输出格式 ('png', 'svg')
    """
    try:
        # 准备数据
        prepared_data = data.copy()
        prepared_data['longitude'] = data['longitude']
        prepared_data['latitude'] = data['latitude']
        prepared_data[indicator] = data[indicator]
        
        # 执行增强插值
        grid_values, grid_lon, grid_lat, boundary_mask, boundary_points = enhanced_interpolation_with_neighborhood(
            prepared_data,
            grid_resolution=grid_resolution,
            method='linear',
            neighborhood_radius=2,
            boundary_method='alpha_shape',
            indicator_col=indicator
        )
        
        # 计算实际的经纬度范围
        lon_min, lon_max = grid_lon.min(), grid_lon.max()
        lat_min, lat_max = grid_lat.min(), grid_lat.max()
        
        # 根据输出格式调整保存路径
        if output_format.lower() == 'svg':
            save_path = save_path.replace('.png', '.svg')
        elif output_format.lower() == 'png':
            save_path = save_path.replace('.svg', '.png')
        
        # 创建纯净图形
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 设置透明背景
        if transparent_bg:
            fig.patch.set_alpha(0.0)  # 设置figure背景透明
            ax.patch.set_alpha(0.0)   # 设置axes背景透明
        
        # 使用imshow绘制热力图，支持NaN透明显示
        im = ax.imshow(grid_values, cmap='jet', aspect='auto', 
                       extent=[lon_min, lon_max, lat_min, lat_max],
                       origin='lower', interpolation='bilinear')
        
        # 移除所有装饰元素
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_title('')
        ax.axis('off')
        
        # 根据中心纬度调整纵横比
        mean_lat = (lat_min + lat_max) / 2
        ax.set_aspect(1/np.cos(np.deg2rad(mean_lat)), adjustable='box')
        
        # 紧密布局，移除边距
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # 根据格式和背景选择保存参数
        save_kwargs = {
            'dpi': 300,
            'bbox_inches': 'tight',
            'pad_inches': 0,
            'edgecolor': 'none'
        }
        
        if transparent_bg:
            save_kwargs['facecolor'] = 'none'  # 透明背景
            save_kwargs['transparent'] = True  # 启用透明度支持
        else:
            save_kwargs['facecolor'] = 'white'  # 白色背景
        
        # 对SVG格式进行特殊处理
        if output_format.lower() == 'svg':
            save_kwargs['format'] = 'svg'
            # SVG不需要DPI设置
            del save_kwargs['dpi']
        
        # 保存纯净图像
        plt.savefig(save_path, **save_kwargs)
        
        format_desc = f"{'透明' if transparent_bg else '白色'}背景的{output_format.upper()}"
        logger.info(f"纯净版插值图({format_desc})已保存至: {save_path}")
        
        plt.clf()
        plt.cla()
        plt.close()
        
        return save_path, grid_values
        
    except Exception as e:
        logger.error(f"生成纯净版插值图失败: {str(e)}")
        return None, None

def generate_clean_interpolation_with_options(data, indicator, save_dir, 
                                            grid_resolution=400, generate_variants=True):
    """生成纯净版插值图的多种变体
    
    Args:
        data: 包含经纬度和指标值的数据框
        indicator: 要绘制的指标名称
        save_dir: 保存目录
        grid_resolution: 网格分辨率
        generate_variants: 是否生成多种变体
        
    Returns:
        dict: 包含各种变体文件路径的字典
    """
    from datetime import datetime
    import os
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {}
    
    variants = [
        ('transparent_png', True, 'png', '透明背景PNG'),
        ('transparent_svg', True, 'svg', '透明背景SVG'),
        ('white_png', False, 'png', '白色背景PNG'),
        ('white_svg', False, 'svg', '白色背景SVG')
    ] if generate_variants else [('transparent_png', True, 'png', '透明背景PNG')]
    
    for variant_name, transparent, format_type, description in variants:
        filename = f"{indicator}_clean_{variant_name}_{timestamp}.{format_type}"
        save_path = os.path.join(save_dir, filename)
        
        try:
            result, _ = generate_clean_interpolation_map(
                data, indicator, save_path,
                grid_resolution=grid_resolution,
                transparent_bg=transparent,
                output_format=format_type
            )
            
            if result:
                results[variant_name] = result
                logger.info(f"生成{description}成功: {filename}")
            
        except Exception as e:
            logger.error(f"生成{description}失败: {str(e)}")
    
    return results

# 创建单个散点图
def generate_distribution_indicator_map(data, indicator, satellite_info, save_path, satellite_geo_bounds, data_geo_bounds, all_points_outside):
    # 默认点大小
    point_size = 20
    # 解包卫星数据信息
    img_width, img_height, img_obj = satellite_info

    # 判断用白色底图还是卫星底图
    if all_points_outside:
        geo_bounds = data_geo_bounds
        img_width = 1200
        img_height = int(img_width * (geo_bounds[3] - geo_bounds[1]) / (geo_bounds[2] - geo_bounds[0]))

        # 对于没有卫星图像的情况，使用更灵活的布局
        fig = plt.figure(figsize=(12, 8))
        main_ax = fig.add_subplot(111)
        
        # 添加空白背景
        main_ax.add_patch(plt.Rectangle((geo_bounds[0], geo_bounds[1]), 
                                        geo_bounds[2]-geo_bounds[0], geo_bounds[3]-geo_bounds[1], 
                                        facecolor='lightgray'))
    else:
        geo_bounds = satellite_geo_bounds
        # 固定的DPI值
        dpi = 100.0
        # 根据图像尺寸计算figsize (英寸)
        figsize = (img_width / dpi, img_height / dpi)
        
        # 创建figure
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=True)
        
        # 创建具有精确尺寸的主要轴
        main_ax = fig.add_axes([0.05, 0.1, 0.85, 0.8])
        
        # 显示卫星图像，修正上下翻转问题
        main_ax.imshow(img_obj, extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]], 
                        aspect='auto', origin='lower')  # 使用origin='lower'与热力图保持一致
    
    # 设置坐标范围
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])  # 修改为不反转y轴，使其与图像保持一致
    
    # 设置经纬度刻度
    num_ticks = 5
    lon_ticks = np.linspace(geo_bounds[0], geo_bounds[2], num_ticks)
    lat_ticks = np.linspace(geo_bounds[1], geo_bounds[3], num_ticks)
    
    main_ax.set_xticks(lon_ticks)
    main_ax.set_yticks(lat_ticks)
    main_ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    main_ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    
    # 添加轴标签
    main_ax.set_xlabel('经度', fontsize=20, labelpad=12)  # 进一步增大字体
    main_ax.set_ylabel('纬度', fontsize=20, labelpad=12)  # 进一步增大字体
    
    # 调整刻度标签
    main_ax.tick_params(axis='both', which='major', labelsize=18, direction='out', pad=6)  # 进一步增大刻度标签
    
    # 准备绘制数据点
    values = data[indicator].values
    norm = Normalize(vmin=min(values), vmax=max(values))
    
    # 根据数据点数量调整点大小，增大基础点大小
    adaptive_point_size = point_size * 10.0  # 将基础点大小显著增大
    if len(data) > 100:
        adaptive_point_size = max(60, int(point_size * 10.0 * 100 / len(data)))  # 确保最小点大小为60
    
    # 准备数据
    x = data['longitude'].values
    y = data['latitude'].values
    z = data[indicator].values

    mappable = main_ax.scatter(x, y, c=z, cmap='jet', 
                                   s=adaptive_point_size, alpha=0.8, 
                                   edgecolors='white', linewidths=2.0)
    
    # 添加颜色条
    cbar = fig.colorbar(mappable, ax=main_ax, fraction=0.05, pad=0.05)
    cbar.set_label(indicator, fontsize=20)  # 进一步增大字体
    cbar.ax.tick_params(labelsize=18)  # 进一步增大刻度字体
    
    title = f"水质监测数据 - {indicator} (散点图)"

    if not all_points_outside:
        title += " - 卫星底图"
    main_ax.set_title(title, fontsize=22, pad=20)  # 进一步增大标题字体
    
    # 添加网格线
    main_ax.grid(True, linestyle='--', alpha=0.3)
    
    # 保存图像
    if not all_points_outside:
        # 保持原始分辨率
        plt.savefig(save_path, dpi=dpi, bbox_inches=None)
    else:
        # 对于生成的图像优化布局
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    # plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    logger.info(f"图像已保存至: {save_path}")
    
    plt.clf()         # 清除当前 figure 的内容（保持 figure 对象）
    plt.cla()         # 清除当前 axes 的内容（保持 axes 对象）
    plt.close()       # 关闭当前 figure，推荐用于循环中防止内存累积
    return save_path


def read_satellite(img_path):
    if os.path.exists(img_path):
        try:
            # 读取卫星图像
            satellite_img = Image.open(img_path)
            img_width, img_height = satellite_img.size
            # 读取原始图像
            original_img = mpimg.imread(img_path)[:, :, :3]

            return [img_width, img_height, original_img]
        except Exception as e:
            logger.error(f"读取或处理卫星图像失败: {str(e)},将使用空白背景绘制点...")
            return [None, None, None]
    else:
        logger.warning(f"找不到卫星图像 {img_path}，将使用空白背景")
        return [None, None, None]

def get_data_geo_bounds(data: pd.DataFrame) -> List[float]:
    """
    获取数据的地理边界坐标
    
    Args:
        data: 包含经纬度数据的DataFrame
        
    Returns:
        List[float]: 地理边界坐标 [min_lon, min_lat, max_lon, max_lat]
    """
    min_lon = data['longitude'].min()
    max_lon = data['longitude'].max()
    min_lat = data['latitude'].min()
    max_lat = data['latitude'].max()
    
    # 为边界添加一些余量
    lon_margin = (max_lon - min_lon) * 0.05
    lat_margin = (max_lat - min_lat) * 0.05
    
    geo_bounds = [
        min_lon - lon_margin,
        min_lat - lat_margin,
        max_lon + lon_margin,
        max_lat + lat_margin
    ]
    
    logger.info(f"数据地理边界: 经度 {geo_bounds[0]} - {geo_bounds[2]}, 纬度 {geo_bounds[1]} - {geo_bounds[3]}")
    
    return geo_bounds

def geo_to_image_coords(lat, lon, image_width, image_height, geo_bounds):
    """
    将经纬度坐标转换为图像坐标
    
    参数:
        lat, lon: 经纬度坐标
        image_width, image_height: 图像尺寸
        geo_bounds: 图像边界经纬度 [min_lon, min_lat, max_lon, max_lat]
    
    返回:
        x, y: 图像坐标
        is_inside: 是否在图像范围内
    """
    min_lon, min_lat, max_lon, max_lat = [
        geo_bounds[0],  # min_lon
        geo_bounds[1],  # min_lat
        geo_bounds[2],  # max_lon
        geo_bounds[3]   # max_lat
    ]
    
    # 检查点是否在地理边界内
    is_inside = (min_lon <= lon <= max_lon) and (min_lat <= lat <= max_lat)
    
    # 计算图像上的相对坐标
    x_ratio = (lon - min_lon) / (max_lon - min_lon) if max_lon > min_lon else 0.5
    y_ratio = 1.0 - (lat - min_lat) / (max_lat - min_lat) if max_lat > min_lat else 0.5  # 图像坐标系y轴方向与地理坐标系相反
    
    # 转换为像素坐标
    x = int(x_ratio * image_width)
    y = int(y_ratio * image_height)
    
    return x, y, is_inside
    
def parse_geo_bounds(geo_bounds):
    """从配置中解析地理边界"""
    try:
        # 尝试从config中获取四个角的坐标
        # 获取坐标字符串
        ne = geo_bounds.get('north_east', '').split(',')
        sw = geo_bounds.get('south_west', '').split(',')
        se = geo_bounds.get('south_east', '').split(',')
        nw = geo_bounds.get('north_west', '').split(',')
        
        if len(ne) != 2 or len(sw) != 2 or len(se) != 2 or len(nw) != 2:
            logging.warning("地理坐标格式不正确，使用默认边界")
            return None
        
        # 转换为浮点数
        ne_lon, ne_lat = float(ne[0]), float(ne[1])
        sw_lon, sw_lat = float(sw[0]), float(sw[1])
        se_lon, se_lat = float(se[0]), float(se[1])
        nw_lon, nw_lat = float(nw[0]), float(nw[1])
        
        # 求最大最小经纬度范围
        min_lon = min(sw_lon, nw_lon)
        max_lon = max(ne_lon, se_lon)
        min_lat = min(sw_lat, se_lat)
        max_lat = max(ne_lat, nw_lat)
        
        return [min_lon, min_lat, max_lon, max_lat]
    except Exception as e:
        logging.error(f"解析地理边界失败: {str(e)}")
        return None

def generate_level_indicator_map(indicator, satellite_info, save_path, satellite_geo_bounds, data_geo_bounds, all_points_outside, Z):
    """
    根据二维指标值Z和分级标准，绘制水质等级分布图
    使用插值数据并应用国标分级标准
    """
    # 检查是否支持该指标的国标分级
    grade_cfg = get_indicator_grade_config(indicator)
    if grade_cfg is None:
        logger.warning(f"未找到{indicator}的国标分级标准，跳过水质等级图生成")
        return "skip"

    if Z is None:
        logger.error(f"插值数据Z为空，无法生成{indicator}的等级图")
        return None

    # 解包卫星数据信息
    img_width, img_height, img_obj = satellite_info
    
    # 获取分级配置
    grade_labels = grade_cfg['labels']
    grade_thresholds = grade_cfg['thresholds']
    grade_colors = grade_cfg['colors']
    is_reverse = grade_cfg.get('reverse', False)
    
    # 创建插值数据的副本用于分级处理
    Z_processed = Z.copy()
    
    # 处理反向分级（如溶解氧，数值越高等级越好）
    if is_reverse:
        Z_processed = -Z_processed
        # 反转阈值、标签和颜色
        grade_thresholds = [-t for t in grade_thresholds[::-1]]
        grade_labels = grade_labels[::-1]
        grade_colors = grade_colors[::-1]

    # 执行分级
    grade_map = np.digitize(Z_processed, bins=grade_thresholds, right=True).astype(float)
    # digitize返回0~len(bins)，调整为1~len(bins)+1的类别编号
    grade_map = grade_map + 1

    # 保持NaN区域
    nan_mask = np.isnan(Z_processed)
    grade_map[nan_mask] = np.nan

    # 计算显示范围
    geo_bounds = data_geo_bounds if all_points_outside else satellite_geo_bounds
    
    # 创建图形
    if all_points_outside:
        fig = plt.figure(figsize=(12, 8))
        main_ax = fig.add_subplot(111)
        main_ax.add_patch(plt.Rectangle((geo_bounds[0], geo_bounds[1]), 
                                        geo_bounds[2]-geo_bounds[0], geo_bounds[3]-geo_bounds[1], 
                                        facecolor='lightgray'))
        dpi = 300
    else:
        dpi = 100.0
        figsize = (img_width / dpi, img_height / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=True)
        main_ax = fig.add_axes([0.05, 0.1, 0.85, 0.8])
        
        # 显示卫星图像
        main_ax.imshow(img_obj, extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]], 
                       aspect='auto', origin='lower')
    
    # 设置坐标范围和刻度
    main_ax.set_xlim(geo_bounds[0], geo_bounds[2])
    main_ax.set_ylim(geo_bounds[1], geo_bounds[3])
    
    num_ticks = 5
    lon_ticks = np.linspace(geo_bounds[0], geo_bounds[2], num_ticks)
    lat_ticks = np.linspace(geo_bounds[1], geo_bounds[3], num_ticks)
    
    main_ax.set_xticks(lon_ticks)
    main_ax.set_yticks(lat_ticks)
    main_ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    main_ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    
    # 添加轴标签
    main_ax.set_xlabel('经度', fontsize=20, labelpad=12)
    main_ax.set_ylabel('纬度', fontsize=20, labelpad=12)
    main_ax.tick_params(axis='both', which='major', labelsize=18, direction='out', pad=6)

    # 创建分级颜色图
    cmap = ListedColormap(grade_colors)
    bounds = list(range(1, len(grade_labels) + 2))
    norm = BoundaryNorm(bounds, cmap.N)

    # 绘制等级图
    im = main_ax.imshow(grade_map, extent=[geo_bounds[0], geo_bounds[2], geo_bounds[1], geo_bounds[3]],
                       aspect='auto', origin='lower', cmap=cmap, norm=norm, alpha=0.8)

    # 添加图例
    patches = [mpatches.Patch(color=grade_colors[i], label=grade_labels[i]) for i in range(len(grade_labels))]
    main_ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=16)

    # 添加网格线
    main_ax.grid(True, linestyle='--', alpha=0.3)
    
    # 设置标题
    title = f"水质监测数据 - {indicator} (国标等级分布图)"
    if not all_points_outside:
        title += " - 卫星底图"
    main_ax.set_title(title, fontsize=22, pad=20)
    
    # 保存图像
    if not all_points_outside:
        plt.savefig(save_path, dpi=dpi, bbox_inches=None, pad_inches=0)
    else:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    logger.info(f"国标等级图已保存至: {save_path}")
    
    plt.clf()
    plt.cla()
    plt.close()
    
    return save_path