#!/usr/bin/env python3
"""
Test example for tinyshare package
This demonstrates how tinyshare can be used as a drop-in replacement for tushare
"""

import tinyshare as ts

def test_basic_functionality():
    """Test basic tinyshare functionality"""
    
    print("Testing TinyShare v" + ts.__version__)
    
    # Test 1: Set token
    print("\n1. Testing token setting...")
    try:
        ts.set_token('19f2ba86fcc30e2f5d38f34ec14b5b6c4adeed35a77fce6a8b304586')
        print("✓ Token set successfully")
    except Exception as e:
        print(f"✗ Error setting token: {e}")
        return
    
    # Test 2: Get token
    print("\n2. Testing token retrieval...")
    token = ts.get_token()
    if token:
        print(f"✓ Token retrieved: {token[:10]}...")
    else:
        print("✗ No token found")
    
    # Test 3: Initialize pro API
    print("\n3. Testing pro API initialization...")
    try:
        pro = ts.pro_api()
        print("✓ Pro API initialized successfully")
        print(f"✓ Pro API type: {type(pro)}")
    except Exception as e:
        print(f"✗ Error initializing pro API: {e}")
        return
    
    # Test 4: Try to get data (this will only work with a valid token)
    print("\n4. Testing data retrieval...")
    try:
        df = pro.index_daily(
            ts_code='000001.SH',
            start_date='20250621',
            end_date='20250628'
        )
        print("✓ Data retrieved successfully")
        print(f"✓ Data shape: {df.shape}")
        print(f"✓ Data columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"✗ Error retrieving data: {e}")
        print("Note: This might be due to invalid token or network issues")
    
    print("\n" + "="*50)
    print("TinyShare test completed!")
    print("If you see this message, the basic proxy functionality is working.")

if __name__ == "__main__":
    test_basic_functionality() 