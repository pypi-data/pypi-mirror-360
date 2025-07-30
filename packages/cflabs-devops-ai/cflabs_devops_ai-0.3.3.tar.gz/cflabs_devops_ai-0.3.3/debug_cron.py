#!/usr/bin/env python3
"""Debug script to see what cron expression is generated."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'devops_ai_eventbridge'))

from cron_converter import CronConverter

def debug_cron():
    """Debug the cron generation for the failing case."""
    converter = CronConverter()
    
    test_input = "every friday at 9pm ist"
    print(f"Input: {test_input}")
    
    try:
        result = converter.text_to_cron(test_input)
        print(f"Output: {result}")
        
        # Check if it's valid
        is_valid = converter.validate_cron(result)
        print(f"Valid: {is_valid}")
        
        # Show the expected format
        print(f"Expected: cron(30 15 ? * 5 *)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cron() 