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

def test_stk_mins_tiny_fixed():
    print("=== 测试 stk_mins_tiny 接口（修复版） ===\n")
    
    # 设置测试日期
    # end_date = datetime.now().strftime('%Y-%m-%d')
    # start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = '2023-08-25'
    end_date = '2023-08-28'
    
    print(f"测试日期范围: {start_date} 到 {end_date}")
    
    # 测试1: 基本功能
    print("\n1. 测试基本功能...")
    try:
        df = ts.stk_mins_tiny('600000.SH', '30min', start_date, end_date)
        print(df)
        if df is not None and not df.empty:
            print(f"✓ 成功获取数据: {len(df)} 条记录")
            print(f"  数据列: {list(df.columns)}")
            # print(f"  数据类型: {df.dtypes.to_dict()}")
        else:
            print("✗ 未获取到数据")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    test_stk_mins_tiny_fixed() 