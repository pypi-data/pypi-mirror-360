import time
from typing import Optional
from pet import Pet
from save_manager import SaveManager
from ui_manager import UIManager
from dialog_engine import DialogEngine
from settings_manager import SettingsManager, DecaySystem
from input_handler import MenuNavigator


class GameEngine:
    def __init__(self):
        self.pet: Optional[Pet] = None
        self.save_manager = SaveManager()
        self.ui_manager = UIManager()
        self.dialog_engine = DialogEngine()
        self.settings_manager = SettingsManager()
        self.decay_system = DecaySystem(self.settings_manager)
        self.menu_navigator = MenuNavigator()
        self.running = True
        self.game_initialized = False
        self.validation_failed = False
    
    def initialize_game(self) -> bool:
        """Initialize the game and load/create a pet"""
        try:
            # FIRST: Validate dialog tree before any user interaction
            validation_passed = self.validate_dialog_system()
            if not validation_passed:
                return False
            
            # Get list of saved pets
            saved_pets = self.save_manager.list_saved_pets()
            
            # Create menu options for save selection
            options = self.ui_manager.display_welcome_with_save_selection(saved_pets)
            
            # Let user select save file or create new pet 
            # (MenuNavigator defaults to selecting the first option, which is the most recent save)
            selected_index = self.menu_navigator.navigate_menu(
                options, 
                self.ui_manager, 
                title="Load a pet:",
                show_welcome=True
            )
            
            if selected_index is None:
                return False  # User quit
            
            # Handle user selection
            if saved_pets and selected_index < len(saved_pets):
                # Load existing pet (saves are first in the list)
                selected_pet = saved_pets[selected_index]
                self.pet = self.save_manager.load_pet(selected_pet)
                if self.pet:
                    self.ui_manager.display_message(f"Loaded {self.pet.name}!", "success")
                    time.sleep(1)
                else:
                    self.ui_manager.display_message("Failed to load pet, creating new one.", "warning")
                    self.pet = self.save_manager.create_new_pet()
                    time.sleep(1)
            else:
                # Create new pet (last option)
                self.pet = self.save_manager.create_new_pet()
                self.ui_manager.display_message(f"Created new pet: {self.pet.name}!", "success")
                time.sleep(1)
            
            self.game_initialized = True
            return True
            
        except Exception as e:
            self.ui_manager.display_message(f"Failed to initialize game: {e}", "error")
            return False
    
    def validate_dialog_system(self) -> bool:
        """Comprehensive validation of the dialog system before game launch"""
        # Validate dialog tree structure and routing
        errors = self.dialog_engine.validate_dialog_tree()
        
        if errors:
            self.validation_failed = True
            self.ui_manager.display_message("Dialog validation failed!", "error")
            error_count = len(errors)
            
            # Show first 5 errors to avoid overwhelming output
            display_errors = errors[:5]
            for i, error in enumerate(display_errors, 1):
                self.ui_manager.display_message(f"{i}. {error}", "error")
                time.sleep(0.5)
            
            if error_count > 5:
                self.ui_manager.display_message(f"... and {error_count - 5} more errors", "error")
            
            self.ui_manager.display_message("Please fix dialog tree before launching game.", "error")
            return False
        
        # Additional validation - test conditional routing with sample pet
        validation_errors = self._test_conditional_routing()
        if validation_errors:
            self.validation_failed = True
            self.ui_manager.display_message("Conditional routing validation failed!", "error")
            for error in validation_errors[:3]:  # Show first 3 routing errors
                self.ui_manager.display_message(error, "error")
                time.sleep(0.5)
            return False
        
        # Validation passed - proceed silently
        return True
    
    def _test_conditional_routing(self) -> list:
        """Test conditional routing with various pet states"""
        errors = []
        
        try:
            # Create test pet with different attribute values
            from pet import Pet
            test_pet = Pet()
            
            # Test each node that has conditional routing
            for node_id, node_data in self.dialog_engine.dialog_tree.items():
                if "options" not in node_data:
                    continue
                
                for i, option in enumerate(node_data["options"]):
                    if "next" not in option or not isinstance(option["next"], dict):
                        continue
                    
                    # Test conditional routing with different pet states
                    test_states = [
                        {"health": 1, "wealth": 1, "happiness": 1, "despair": 1, "age": 1, "skill": 1},
                        {"health": 3, "wealth": 3, "happiness": 3, "despair": 3, "age": 3, "skill": 3},
                        {"health": 5, "wealth": 5, "happiness": 5, "despair": 5, "age": 5, "skill": 5},
                    ]
                    
                    for state in test_states:
                        # Set test pet attributes
                        for attr, value in state.items():
                            setattr(test_pet, attr, value)
                        
                        try:
                            # Test if conditional routing works
                            result_node = self.dialog_engine.evaluate_conditional_routing(option["next"], test_pet)
                            
                            # Verify result node exists
                            if result_node not in self.dialog_engine.dialog_tree:
                                errors.append(f"Node '{node_id}' option {i} conditional routing with state {state} returns non-existent node '{result_node}'")
                        
                        except Exception as e:
                            errors.append(f"Node '{node_id}' option {i} conditional routing failed with state {state}: {e}")
        
        except Exception as e:
            errors.append(f"Conditional routing test failed: {e}")
        
        return errors
    
    def handle_decay(self) -> bool:
        """Check and apply natural attribute decay"""
        if not self.pet:
            return False
        
        if self.decay_system.should_apply_decay(self.pet.action_count):
            decay_effects = self.decay_system.apply_decay(self.pet)
            
            # Show decay message if effects were applied
            if decay_effects:
                decay_msg = "Time has passed... "
                if decay_effects.get("health", 0) < 0:
                    decay_msg += "Your pet's health has declined. "
                if decay_effects.get("happiness", 0) < 0:
                    decay_msg += "Your pet seems less happy. "
                if decay_effects.get("despair", 0) > 0:
                    decay_msg += "Your pet is feeling more despair. "
                if decay_effects.get("skill", 0) < 0:
                    decay_msg += "Your pet has forgotten some skills. "
                
                self.ui_manager.display_message(decay_msg, "warning")
                time.sleep(2)
            
            return True
        
        return False
    
    def auto_save(self) -> bool:
        """Auto-save the pet if enabled"""
        if not self.pet:
            return False
        
        if self.settings_manager.get("game_settings.auto_save", True):
            return self.save_manager.auto_save(self.pet)
        
        return True
    
    def process_input(self) -> bool:
        """Process user input and return whether to continue"""
        try:
            if not self.pet:
                return False
                
            options = self.dialog_engine.get_option_texts(self.pet)
            
            if not options:
                return False
            
            # Get dialog info for menu title
            dialog_info = self.dialog_engine.get_dialog_info(self.pet)
            
            # Use menu navigator for arrow key support
            selected_index = self.menu_navigator.navigate_menu(
                options,
                self.ui_manager,
                self.pet,
                dialog_info["text"]
            )
            
            if selected_index is None:
                return False  # User quit
                
            return self.process_choice(selected_index)
                
        except Exception as e:
            self.ui_manager.display_message(f"Input error: {e}", "error")
            time.sleep(1)
            return True
    
    def process_choice(self, choice_index: int) -> bool:
        """Process a menu choice"""
        try:
            if not self.pet:
                return False
                
            # Navigate to next node
            success, _ = self.dialog_engine.select_option(choice_index, self.pet)
            
            if not success:
                self.ui_manager.display_message("Invalid choice.", "error")
                time.sleep(1)
                return True
            
            # Apply effects from the new node
            current_node = self.dialog_engine.get_current_node()
            if current_node:
                effects_result = self.dialog_engine.apply_node_effects(self.pet, current_node)
                
                # Display effects if they exist and are not empty
                if "effects" in effects_result and effects_result["effects"]:
                    self.ui_manager.display_effects(effects_result["effects"])
                    time.sleep(1.5)  # Brief pause to let user see effects
                
                # Handle special effects
                if effects_result.get("special") == "quit_game":
                    return False
                elif effects_result.get("special") == "name_changed":
                    self.ui_manager.display_message(
                        f"Pet name changed from {effects_result['old_name']} to {effects_result['new_name']}!",
                        "success"
                    )
                    time.sleep(1)
                elif effects_result.get("special") == "sex_changed":
                    self.ui_manager.display_message(
                        f"Pet sex changed from {effects_result['old_sex']} to {effects_result['new_sex']}!",
                        "success"
                    )
                    time.sleep(1)
                
            
            # Increment action count
            self.pet.increment_action_count()
            
            # Auto-save
            self.auto_save()
            
            return True
            
        except Exception as e:
            self.ui_manager.display_message(f"Error processing choice: {e}", "error")
            time.sleep(1)
            return True
    
    def check_game_over_conditions(self) -> bool:
        """Check if game over conditions are met"""
        if not self.pet:
            return True
        
        # Check if pet is in critical condition
        if self.pet.health <= 0:
            self.ui_manager.display_game_over(self.pet, "Your pet's health reached zero.")
            return True
        
        if self.pet.despair >= 5:
            self.ui_manager.display_game_over(self.pet, "Your pet became too despairing.")
            return True
        
        return False
    
    def run(self) -> None:
        """Main game loop"""
        try:
            if not self.initialize_game():
                return
            
            while self.running:
                # Check game over conditions
                if self.check_game_over_conditions():
                    break
                
                # Handle natural decay
                self.handle_decay()
                
                # Process user input
                if not self.process_input():
                    break
            
            # Final save before exit
            if self.pet:
                self.save_manager.save_pet(self.pet)
                self.ui_manager.display_message(f"Game saved. Thanks for playing with {self.pet.name}!", "success")
            
        except KeyboardInterrupt:
            if self.pet:
                self.save_manager.save_pet(self.pet)
                self.ui_manager.display_message(f"\nGame interrupted. {self.pet.name} has been saved.", "info")
        except Exception as e:
            self.ui_manager.display_message(f"Game error: {e}", "error")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        # Only clear screen on normal exit, not when validation failed
        if not self.validation_failed:
            self.ui_manager.clear_screen()
        print("Goodbye!")
    
    def quit_game(self) -> None:
        """Quit the game"""
        self.running = False


def main():
    """Main entry point"""
    game = GameEngine()
    game.run()


if __name__ == "__main__":
    main()