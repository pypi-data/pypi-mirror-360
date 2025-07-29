#!/usr/bin/env python3
"""
Test script for text wrapping functionality
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_manager import UIManager
from pet import Pet

def test_text_wrapping():
    """Test text wrapping with various text lengths"""
    print("Testing Text Wrapping")
    print("=" * 40)
    
    ui = UIManager()
    
    # Test short text
    short_text = "This is a short message."
    print("Short text:")
    ui.display_dialog(short_text)
    input("Press Enter to continue...")
    
    # Test medium text
    medium_text = "This is a medium length message that should wrap properly when displayed in a narrow terminal window. It contains multiple sentences to test the wrapping functionality."
    print("\nMedium text:")
    ui.display_dialog(medium_text)
    input("Press Enter to continue...")
    
    # Test long text with line breaks
    long_text = """This is a very long message that tests the text wrapping functionality.

It contains multiple paragraphs with line breaks.

This paragraph is specifically designed to be quite lengthy and should demonstrate how the text wrapping system handles extended content that would normally overflow the terminal boundaries and become unreadable without proper wrapping.

The system should maintain readability across different terminal sizes."""
    
    print("\nLong text with paragraphs:")
    ui.display_dialog(long_text)
    input("Press Enter to continue...")
    
    # Test message display
    print("\nTesting message display:")
    ui.display_message("This is a success message that might be quite long and needs to wrap properly in narrow terminals.", "success")
    input("Press Enter to continue...")
    
    ui.display_message("This is an error message with a very long description that explains what went wrong in great detail and should wrap nicely.", "error")
    
    print("\nText wrapping test complete!")

def test_with_pet():
    """Test with a pet to show full interface"""
    print("\nTesting with pet interface:")
    
    pet = Pet(name="WrapTest", sex="F")
    pet.age = 3
    pet.health = 2
    pet.happiness = 4
    pet.despair = 1
    pet.wealth = 200
    
    ui = UIManager()
    
    # Test with pet interface
    options = ["Feed the pet", "Play with the pet", "Have a conversation", "Take care of pet", "Quit game"]
    title = "This is a very long menu title that should wrap properly when displayed in narrow terminal windows to maintain readability"
    
    ui.display_full_interface(pet, options, title)
    
    print("Pet interface test complete!")

if __name__ == "__main__":
    test_text_wrapping()
    test_with_pet()