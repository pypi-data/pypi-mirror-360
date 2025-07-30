#!/usr/bin/env python3
"""
Helper utilities examples for AIWand package
"""

import aiwand


def main():
    """Run helper examples."""
    
    print("🪄 AIWand Helper Utilities Examples")
    print("=" * 40)
    
    # Example 1: Generate random numbers with different lengths
    print("\n🎲 Random Number Generation:")
    print("-" * 30)
    
    # Default 6-digit number
    random_6 = aiwand.generate_random_number()
    print(f"6-digit number (default): {random_6}")
    
    # Custom lengths
    random_4 = aiwand.generate_random_number(4)
    print(f"4-digit number: {random_4}")
    
    random_10 = aiwand.generate_random_number(10)
    print(f"10-digit number: {random_10}")
    
    random_1 = aiwand.generate_random_number(1)
    print(f"1-digit number: {random_1}")
    
    # Example 2: Generate UUIDs
    print("\n🆔 UUID Generation:")
    print("-" * 30)
    
    # Default UUID4
    uuid4_default = aiwand.generate_uuid()
    print(f"UUID4 (default): {uuid4_default}")
    
    # UUID4 uppercase
    uuid4_upper = aiwand.generate_uuid(uppercase=True)
    print(f"UUID4 (uppercase): {uuid4_upper}")
    
    # UUID1
    uuid1_default = aiwand.generate_uuid(version=1)
    print(f"UUID1: {uuid1_default}")
    
    # UUID1 uppercase
    uuid1_upper = aiwand.generate_uuid(version=1, uppercase=True)
    print(f"UUID1 (uppercase): {uuid1_upper}")
    
    # Example 3: Multiple random numbers (useful for testing patterns)
    print("\n🔢 Multiple Random Numbers:")
    print("-" * 30)
    
    for i in range(3):
        num = aiwand.generate_random_number(8)
        print(f"Random 8-digit #{i+1}: {num}")
    
    # Example 4: Multiple UUIDs
    print("\n🆔 Multiple UUIDs:")
    print("-" * 30)
    
    for i in range(3):
        uid = aiwand.generate_uuid()
        print(f"UUID #{i+1}: {uid}")
    
    # Example 5: Error handling
    print("\n❌ Error Handling Examples:")
    print("-" * 30)
    
    try:
        # This should raise an error
        bad_num = aiwand.generate_random_number(0)
    except ValueError as e:
        print(f"Expected error for length 0: {e}")
    
    try:
        # This should raise an error
        bad_uuid = aiwand.generate_uuid(version=5)
    except ValueError as e:
        print(f"Expected error for UUID version 5: {e}")
    
    print("\n✅ All helper utility examples completed!")


if __name__ == "__main__":
    main() 