#!/usr/bin/env python3
"""
测试GPS对齐和底图范围修复效果
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, 'src')

from autoreport.processor.maps import enhanced_interpolation_with_neighborhood


def test_gps_alignment():
    """测试GPS对齐修复"""
    print("=== 测试GPS对齐修复 ===")
    
    # 创建测试数据
    np.random.seed(42)
    data = pd.DataFrame({
        'longitude': np.random.uniform(120.05, 120.15, 20),
        'latitude': np.random.uniform(30.03, 30.07, 20),
        'cod': np.random.uniform(4.5, 7.0, 20)
    })
    
    # 模拟卫星图边界（比数据范围大）
    satellite_bounds = [120.0, 30.0, 120.2, 30.1]  # [min_lon, min_lat, max_lon, max_lat]
    
    print(f"数据边界: 经度 {data['longitude'].min():.3f} - {data['longitude'].max():.3f}")
    print(f"         纬度 {data['latitude'].min():.3f} - {data['latitude'].max():.3f}")
    print(f"卫星图边界: 经度 {satellite_bounds[0]} - {satellite_bounds[2]}")
    print(f"           纬度 {satellite_bounds[1]} - {satellite_bounds[3]}")
    
    # 测试不使用固定边界（原有行为）
    print("\n--- 不使用固定边界 ---")
    grid_values1, grid_lon1, grid_lat1, _, _ = enhanced_interpolation_with_neighborhood(
        data,
        grid_resolution=100,
        method='linear',
        boundary_method='alpha_shape',
        indicator_col='cod',
        fixed_bounds=None
    )
    
    print(f"插值网格范围: 经度 {grid_lon1.min():.3f} - {grid_lon1.max():.3f}")
    print(f"             纬度 {grid_lat1.min():.3f} - {grid_lat1.max():.3f}")
    
    # 测试使用固定边界（新行为）
    print("\n--- 使用卫星图固定边界 ---")
    grid_values2, grid_lon2, grid_lat2, _, _ = enhanced_interpolation_with_neighborhood(
        data,
        grid_resolution=100,
        method='linear',
        boundary_method='alpha_shape',
        indicator_col='cod',
        fixed_bounds=satellite_bounds
    )
    
    print(f"插值网格范围: 经度 {grid_lon2.min():.3f} - {grid_lon2.max():.3f}")
    print(f"             纬度 {grid_lat2.min():.3f} - {grid_lat2.max():.3f}")
    
    # 验证对齐效果
    print("\n--- 对齐效果验证 ---")
    lon_aligned = np.isclose(grid_lon2.min(), satellite_bounds[0], atol=1e-3) and \
                  np.isclose(grid_lon2.max(), satellite_bounds[2], atol=1e-3)
    lat_aligned = np.isclose(grid_lat2.min(), satellite_bounds[1], atol=1e-3) and \
                  np.isclose(grid_lat2.max(), satellite_bounds[3], atol=1e-3)
    
    print(f"经度对齐: {'✅' if lon_aligned else '❌'}")
    print(f"纬度对齐: {'✅' if lat_aligned else '❌'}")
    
    if lon_aligned and lat_aligned:
        print("🎯 GPS对齐修复成功！插值网格完全匹配卫星图边界")
    else:
        print("❌ GPS对齐修复失败")
    
    # 检查数据覆盖率
    valid_points1 = np.sum(~np.isnan(grid_values1))
    valid_points2 = np.sum(~np.isnan(grid_values2))
    
    print(f"\n--- 数据覆盖率 ---")
    print(f"原有方法有效点数: {valid_points1}/{grid_values1.size} ({valid_points1/grid_values1.size*100:.1f}%)")
    print(f"修复后有效点数: {valid_points2}/{grid_values2.size} ({valid_points2/grid_values2.size*100:.1f}%)")


if __name__ == "__main__":
    print("🔍 GPS对齐和底图范围修复测试")
    print("=" * 50)
    
    test_gps_alignment()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成!")
    print("\n修复说明:")
    print("1. interpolation图现在使用卫星图边界作为插值范围")
    print("2. 插值网格与卫星图完全对齐，解决GPS偏移问题")
    print("3. 移除了错误的坐标范围重设，保持底图完整显示")