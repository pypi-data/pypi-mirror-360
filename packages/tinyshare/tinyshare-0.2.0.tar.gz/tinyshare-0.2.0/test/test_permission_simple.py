#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 tinyshare 权限检查功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import tinyshare as ts
from datetime import datetime, timedelta

def test_permission_system():
    """测试权限系统"""
    
    print("=== 测试 TinyShare 权限检查功能 ===\n")
    
    # 测试用的权限验证码
    test_auth_code = "Pxj5qa7VWRKZHls4tgIDt2Vfk8bFkNg13cm0n6cxu9WK060yhSPpqGom46e2c8b1"
    
    # ts.set_token_tiny(test_auth_code)
    
    try:
        # 设置测试日期
        start_date = '2023-08-25'
        end_date = '2023-08-25'
        
        print(f"测试日期范围: {start_date} 到 {end_date}")
        
        # 调用 stk_mins_tiny 接口
        df = ts.stk_mins_tiny('600000.SH', '5min', start_date, end_date)
        
        if df is not None and not df.empty:
            print(f"✓ 成功获取数据: {len(df)} 条记录")
            print("数据预览:")
            print(df.head())
        else:
            print("✗ 未获取到数据")
            
    except PermissionError as e:
        print(f"✗ 权限检查失败: {e}")
    except Exception as e:
        print(f"✗ 调用接口失败: {e}")
    
    print("测试结束")

if __name__ == "__main__":
    test_permission_system() 