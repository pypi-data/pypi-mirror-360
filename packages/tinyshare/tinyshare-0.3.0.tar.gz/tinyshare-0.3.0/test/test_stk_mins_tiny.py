#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 stk_mins_tiny 接口
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import tinyshare as ts
from datetime import datetime, timedelta

def test_stk_mins_tiny():
    """测试 stk_mins_tiny 接口"""
    
    print("=== 测试 stk_mins_tiny 接口 ===\n")
    
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
    
    # 测试3: 不同频率
    print("\n3. 测试不同频率...")
    for freq in ['1min', '15min', '30min', '60min']:
        try:
            df = ts.stk_mins_tiny('000001.SZ', freq, start_date, end_date)
            if df is not None and not df.empty:
                print(f"✓ {freq}: {len(df)} 条记录")
            else:
                print(f"✗ {freq}: 无数据")
        except Exception as e:
            print(f"✗ {freq}: 失败 - {e}")
    
    # 测试4: 错误处理
    print("\n4. 测试错误处理...")
    try:
        # 测试无效股票代码
        df = ts.stk_mins_tiny('INVALID', '5min', start_date, end_date)
        print("✗ 应该抛出异常但没有")
    except Exception as e:
        print(f"✓ 正确处理无效股票代码: {e}")
    
    try:
        # 测试无效频率
        df = ts.stk_mins_tiny('600000.SH', '2min', start_date, end_date)
        print("✗ 应该抛出异常但没有")
    except Exception as e:
        print(f"✓ 正确处理无效频率: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_stk_mins_tiny() 