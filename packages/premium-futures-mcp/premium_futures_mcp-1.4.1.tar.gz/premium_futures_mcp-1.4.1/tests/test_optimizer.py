#!/usr/bin/env python3
"""
Test script untuk mengecek ResponseOptimizer fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from premium_futures_mcp.response_optimizer import ResponseOptimizer

def test_optimizer():
    """Test ResponseOptimizer dengan berbagai format data"""
    
    print("🧪 Testing ResponseOptimizer.optimize_balance()...")
    
    # Test 1: Normal data
    print("\n1. Testing normal balance data:")
    normal_data = [
        {
            "asset": "USDT",
            "walletBalance": "81.50000000",
            "unrealizedProfit": "0.00000000",
            "availableBalance": "81.50000000"
        },
        {
            "asset": "BTC", 
            "walletBalance": "0.00000000",
            "unrealizedProfit": "0.00000000",
            "availableBalance": "0.00000000"
        }
    ]
    
    result1 = ResponseOptimizer.optimize_balance(normal_data)
    print(f"Normal data result: {result1}")
    
    # Test 2: Data dengan format berbeda
    print("\n2. Testing alternative format:")
    alt_data = [
        {
            "asset": "USDT",
            "balance": "81.50",  # Different field name
            "free": "81.50"
        }
    ]
    
    result2 = ResponseOptimizer.optimize_balance(alt_data)
    print(f"Alternative format result: {result2}")
    
    # Test 3: Data dengan tipe berbeda
    print("\n3. Testing different data types:")
    mixed_data = [
        {
            "asset": "USDT",
            "walletBalance": 81.5,  # Number instead of string
            "unrealizedProfit": None,
            "availableBalance": "81.5"
        }
    ]
    
    result3 = ResponseOptimizer.optimize_balance(mixed_data)
    print(f"Mixed types result: {result3}")
    
    # Test 4: Data yang rusak
    print("\n4. Testing corrupted data:")
    bad_data = [
        "not_a_dict",
        None,
        {
            "asset": "USDT",
            "walletBalance": "invalid_number"
        }
    ]
    
    result4 = ResponseOptimizer.optimize_balance(bad_data)
    print(f"Corrupted data result: {result4}")
    
    # Test 5: Data kosong
    print("\n5. Testing empty data:")
    result5 = ResponseOptimizer.optimize_balance([])
    print(f"Empty data result: {result5}")

if __name__ == "__main__":
    test_optimizer()
