#!/usr/bin/env python3
"""
测试数值稳定性改进的效果
"""
import sys
import numpy as np
import math
sys.path.insert(0, 'src')

from autoreport.utils.geo import haversine, validate_coordinates
from autoreport.utils.numerical import NumericalSafety, safe_divide_vectorized
from autoreport.processor.data.analyzer import _safe_relative_error


def test_coordinate_validation():
    """测试坐标验证功能"""
    print("=== 测试坐标验证 ===")
    
    # 测试正常坐标
    try:
        validate_coordinates(39.9042, 116.4074)  # 北京
        print("✅ 正常坐标验证通过")
    except ValueError as e:
        print(f"❌ 正常坐标验证失败: {e}")
    
    # 测试无效坐标
    test_cases = [
        (float('inf'), 116.4074, "无穷大纬度"),
        (39.9042, float('nan'), "NaN经度"),
        (91.0, 116.4074, "超出范围纬度"),
        (39.9042, 181.0, "超出范围经度"),
    ]
    
    for lat, lon, desc in test_cases:
        try:
            validate_coordinates(lat, lon)
            print(f"❌ {desc} 应该被拒绝但通过了验证")
        except ValueError:
            print(f"✅ {desc} 正确被拒绝")


def test_haversine_stability():
    """测试Haversine函数的数值稳定性"""
    print("\n=== 测试Haversine数值稳定性 ===")
    
    # 测试极近距离
    lat1, lon1 = 39.9042, 116.4074
    lat2, lon2 = 39.9042 + 1e-10, 116.4074 + 1e-10
    
    try:
        distance = haversine(lat1, lon1, lat2, lon2)
        print(f"✅ 极近距离计算: {distance:.6f}米")
    except Exception as e:
        print(f"❌ 极近距离计算失败: {e}")
    
    # 测试相同点
    try:
        distance = haversine(lat1, lon1, lat1, lon1)
        print(f"✅ 相同点距离: {distance:.6f}米")
    except Exception as e:
        print(f"❌ 相同点距离计算失败: {e}")
    
    # 测试对跖点（地球两端）
    try:
        distance = haversine(0, 0, 0, 180)
        print(f"✅ 对跖点距离: {distance:.0f}米 (预期约20003931米)")
    except Exception as e:
        print(f"❌ 对跖点距离计算失败: {e}")


def test_safe_relative_error():
    """测试安全相对误差计算"""
    print("\n=== 测试安全相对误差计算 ===")
    
    test_cases = [
        (100.0, 90.0, "正常情况"),
        (100.0, 0.0, "实际值为零"),
        (100.0, 1e-15, "实际值极小"),
        (float('inf'), 100.0, "预测值无穷大"),
        (100.0, float('nan'), "实际值NaN"),
    ]
    
    for pred, actual, desc in test_cases:
        result = _safe_relative_error(pred, actual)
        print(f"✅ {desc}: {result}")


def test_numerical_safety_class():
    """测试数值安全工具类"""
    print("\n=== 测试数值安全工具类 ===")
    
    # 测试安全除法
    test_cases = [
        (10.0, 2.0, "正常除法"),
        (10.0, 0.0, "除零"),
        (10.0, 1e-15, "除极小数"),
        (float('inf'), 2.0, "无穷大除法"),
    ]
    
    for num, den, desc in test_cases:
        result = NumericalSafety.safe_divide(num, den)
        print(f"✅ {desc}: {num}/{den} = {result}")
    
    # 测试安全平方根
    sqrt_cases = [
        (4.0, "正数"),
        (0.0, "零"),
        (-1e-15, "极小负数"),
        (-1.0, "负数"),
        (float('inf'), "无穷大"),
    ]
    
    for x, desc in sqrt_cases:
        result = NumericalSafety.safe_sqrt(x)
        print(f"✅ sqrt({desc}): sqrt({x}) = {result}")


def test_vectorized_operations():
    """测试向量化安全操作"""
    print("\n=== 测试向量化安全操作 ===")
    
    # 创建测试数据，包含各种边界情况
    numerators = np.array([10.0, 20.0, 30.0, float('inf'), 0.0])
    denominators = np.array([2.0, 0.0, 1e-15, 2.0, 1.0])
    
    results = safe_divide_vectorized(numerators, denominators)
    
    print("分子:", numerators)
    print("分母:", denominators)
    print("结果:", results)
    
    # 测试向量化相对误差
    predicted = np.array([100.0, 200.0, 300.0, float('inf')])
    actual = np.array([90.0, 0.0, 290.0, 250.0])
    
    from autoreport.utils.numerical import safe_relative_error_vectorized
    rel_errors = safe_relative_error_vectorized(predicted, actual)
    
    print("\n预测值:", predicted)
    print("实际值:", actual)
    print("相对误差(%):", rel_errors)


def test_extreme_cases():
    """测试极端情况"""
    print("\n=== 测试极端情况 ===")
    
    # 测试非常接近的坐标
    base_lat, base_lon = 39.9042, 116.4074
    
    # 在不同精度下测试
    epsilons = [1e-6, 1e-10, 1e-14, 1e-16]
    
    for eps in epsilons:
        try:
            dist = haversine(base_lat, base_lon, 
                           base_lat + eps, base_lon + eps)
            print(f"✅ ε={eps}: 距离 = {dist:.10f}米")
        except Exception as e:
            print(f"❌ ε={eps}: 失败 - {e}")


if __name__ == "__main__":
    print("🔍 数值稳定性测试开始")
    print("=" * 50)
    
    test_coordinate_validation()
    test_haversine_stability()
    test_safe_relative_error()
    test_numerical_safety_class()
    test_vectorized_operations()
    test_extreme_cases()
    
    print("\n" + "=" * 50)
    print("🎯 数值稳定性测试完成!")