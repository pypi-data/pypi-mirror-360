#!/usr/bin/env python3
"""
Test script to demonstrate text wrapping functionality
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_manager import UIManager
from pet import Pet

def test_text_wrapping():
    """Test text wrapping with long dialog and menu text"""
    ui = UIManager()
    
    print("Text Wrapping Test")
    print(f"Terminal size: {ui.terminal_width}x{ui.terminal_height}")
    print("=" * 50)
    
    # Test long dialog text
    long_dialog = """This is a very long dialog text that should wrap properly across multiple lines when displayed in the terminal. It contains several sentences and should demonstrate how the text wrapping works in different screen sizes. The text should be readable and not cut off at the edges of the terminal window."""
    
    ui.display_dialog(long_dialog)
    
    input("\nPress Enter to test long menu options...")
    
    # Test long menu options
    long_options = [
        "This is a very long menu option that might not fit on a single line",
        "Another extremely long option that definitely needs to be wrapped",
        "Short option",
        "A moderately long option that might wrap depending on terminal size",
        "Back to main menu"
    ]
    
    ui.clear_screen()
    ui.display_menu(long_options, "This is a very long menu title that should also wrap properly when displayed")
    
    input("\nPress Enter to test message wrapping...")
    
    # Test long message
    long_message = "This is a very long message that should demonstrate how the message display function handles text wrapping for different types of messages including success, warning, error, and info messages."
    
    ui.clear_screen()
    ui.display_message(long_message, "info")
    ui.display_message(long_message, "success") 
    ui.display_message(long_message, "warning")
    ui.display_message(long_message, "error")
    
    print("\nText wrapping test complete!")

if __name__ == "__main__":
    test_text_wrapping()