#!/usr/bin/env python3
"""
Test script to demonstrate the responsive UI of E-Pet
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet import Pet
from ui_manager import UIManager

def main():
    # Create test pet
    pet = Pet(name="TestPet", sex="F")
    pet.health = 3
    pet.happiness = 4
    pet.despair = 2
    pet.wealth = 150
    pet.age = 5
    
    ui = UIManager()
    
    print("E-Pet Responsive UI Test")
    print(f"Terminal size: {ui.terminal_width}x{ui.terminal_height}")
    print("=" * 50)
    
    # Test welcome screen
    ui.display_welcome()
    input("\nPress Enter to continue...")
    
    # Test pet status
    ui.clear_screen()
    ui.display_pet_status(pet)
    input("\nPress Enter to continue...")
    
    # Test menu
    ui.clear_screen()
    ui.display_pet_status(pet)
    options = ["Feed", "Play", "Talk", "Pet Care", "Quit"]
    ui.display_menu(options)
    input("\nPress Enter to continue...")
    
    # Test dialog
    ui.clear_screen()
    ui.display_dialog("Your pet looks at you with loving eyes. What would you like to do?", ["Pet them", "Give treats", "Go back"])
    
    print("\nUI test complete!")

if __name__ == "__main__":
    main()