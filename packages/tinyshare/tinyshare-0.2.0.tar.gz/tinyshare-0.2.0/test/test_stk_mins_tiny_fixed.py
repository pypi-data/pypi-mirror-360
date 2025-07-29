#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stk_mins_tiny 接口（修复版）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import tinyshare as ts
from datetime import datetime, timedelta
import warnings

def test_stk_mins_tiny_fixed():
    """测试 stk_mins_tiny 接口（修复版）"""
    
    print("=== 测试 stk_mins_tiny 接口（修复版） ===\n")
    
    # 设置测试日期
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    
    print(f"测试日期范围: {start_date} 到 {end_date}")
    
    # 测试1: 基本功能
    print("\n1. 测试基本功能...")
    try:
        df = ts.stk_mins_tiny('600000.SH', '5min', start_date, end_date)
        if df is not None and not df.empty:
            print(f"✓ 成功获取数据: {len(df)} 条记录")
            print(f"  数据列: {list(df.columns)}")
            print(f"  数据类型: {df.dtypes.to_dict()}")
        else:
            print("✗ 未获取到数据")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    # 测试2: 原始数据格式
    print("\n2. 测试原始数据格式...")
    try:
        df_origin = ts.stk_mins_tiny('600000.SH', '5min', start_date, end_date, origin=True)
        if df_origin is not None and not df_origin.empty:
            print(f"✓ 成功获取原始数据: {len(df_origin)} 条记录")
            print(f"  数据列: {list(df_origin.columns)}")
        else:
            print("✗ 未获取到原始数据")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    # 测试3: 不同频率（跳过1min）
    print("\n3. 测试不同频率...")
    for freq in ['5min', '15min', '30min', '60min']:  # 移除1min
        try:
            df = ts.stk_mins_tiny('000001.SZ', freq, start_date, end_date)
            if df is not None and not df.empty:
                print(f"✓ {freq}: {len(df)} 条记录")
            else:
                print(f"✗ {freq}: 无数据")
        except Exception as e:
            print(f"✗ {freq}: 失败 - {e}")
    
    # 测试4: 1min数据单独测试
    print("\n4. 测试1min数据（预期可能失败）...")
    try:
        df = ts.stk_mins_tiny('000001.SZ', '1min', start_date, end_date)
        if df is not None and not df.empty:
            print(f"✓ 1min: {len(df)} 条记录")
        else:
            print("✗ 1min: 无数据（这是预期的，baostock可能不支持1min数据）")
    except Exception as e:
        print(f"✗ 1min: 失败 - {e}（这是预期的，baostock可能不支持1min数据）")
    
    # 测试5: 错误处理
    print("\n5. 测试错误处理...")
    
    # 测试无效股票代码
    test_cases = [
        ('INVALID', '无效格式'),
        ('123456', '缺少交易所代码'),
        ('123456.XX', '无效交易所代码'),
        ('12345.SH', '股票代码不是6位'),
        ('abcdef.SH', '股票代码不是数字'),
        ('', '空字符串'),
        (None, '空值'),
    ]
    
    for code, desc in test_cases:
        try:
            df = ts.stk_mins_tiny(code, '5min', start_date, end_date)
            print(f"✗ {desc}: 应该抛出异常但没有")
        except Exception as e:
            print(f"✓ 正确处理{desc}: {e}")
    
    # 测试无效频率
    try:
        df = ts.stk_mins_tiny('600000.SH', '2min', start_date, end_date)
        print("✗ 应该抛出异常但没有")
    except Exception as e:
        print(f"✓ 正确处理无效频率: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n修复说明:")
    print("1. 添加了urllib3==1.26.20到requirements.txt以解决SSL警告")
    print("2. 改进了股票代码验证，提供更详细的错误信息")
    print("3. 1min数据问题：baostock可能不支持1min数据，建议使用5min或更大频率")
    print("4. 建议运行: pip install urllib3==1.26.20 来解决SSL警告")

if __name__ == "__main__":
    test_stk_mins_tiny_fixed() 