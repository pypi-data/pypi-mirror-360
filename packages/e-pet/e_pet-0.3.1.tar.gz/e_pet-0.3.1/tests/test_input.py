#!/usr/bin/env python3
"""
Test script for arrow key input handling
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from input_handler import InputHandler, MenuNavigator
from ui_manager import UIManager

def test_input_handler():
    """Test the input handler directly"""
    print("Testing Input Handler")
    print("=" * 30)
    
    handler = InputHandler()
    
    print("Testing raw input detection...")
    print(f"Is TTY: {sys.stdin.isatty()}")
    
    if sys.stdin.isatty():
        print("TTY detected - arrow keys should work!")
        print("Try pressing arrow keys, Enter, or 'q' to quit")
        
        try:
            handler.setup_raw_input()
            
            while True:
                key = handler.get_key()
                print(f"Key pressed: {key}")
                
                if key == 'q' or key == 'CTRL_C':
                    break
                    
        finally:
            handler.restore_input()
    else:
        print("Non-TTY environment - falling back to regular input")
        action, selection = handler.get_fallback_input(3, 0)
        print(f"Action: {action}, Selection: {selection}")

def test_menu_navigator():
    """Test menu navigation"""
    print("\nTesting Menu Navigator")
    print("=" * 30)
    
    ui = UIManager()
    navigator = MenuNavigator()
    
    options = ["Test Option 1", "Test Option 2", "Test Option 3"]
    
    print("Navigate with arrow keys, Enter to select, 'q' to quit")
    
    selected = navigator.navigate_menu(options, ui, title="Test Menu")
    
    if selected is not None:
        print(f"Selected option {selected + 1}: {options[selected]}")
    else:
        print("User quit")

if __name__ == "__main__":
    test_input_handler()
    test_menu_navigator()