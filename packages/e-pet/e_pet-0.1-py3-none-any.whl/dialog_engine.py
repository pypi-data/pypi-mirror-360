import json
import random
from typing import Dict, List, Any, Optional, Tuple
from pet import Pet


class DialogEngine:
    def __init__(self, dialog_file: str = "dialog_tree.json"):
        self.dialog_file = dialog_file
        self.dialog_tree = {}
        self.current_node = "main_menu"
        self.load_dialog_tree()
    
    def load_dialog_tree(self) -> bool:
        """Load dialog tree from JSON file"""
        try:
            with open(self.dialog_file, 'r', encoding='utf-8') as f:
                self.dialog_tree = json.load(f)
            return True
        except FileNotFoundError:
            print(f"Dialog tree file '{self.dialog_file}' not found!")
            return False
        except json.JSONDecodeError:
            print(f"Invalid JSON in dialog tree file '{self.dialog_file}'!")
            return False
        except Exception as e:
            print(f"Error loading dialog tree: {e}")
            return False
    
    def get_current_node(self) -> Optional[Dict[str, Any]]:
        """Get the current dialog node"""
        return self.dialog_tree.get(self.current_node)
    
    def get_node_text(self) -> str:
        """Get text for the current node"""
        node = self.get_current_node()
        if node:
            return node.get("text", "")
        return ""
    
    def get_processed_options(self) -> List[Dict[str, Any]]:
        """Get options for current node with randomization applied"""
        node = self.get_current_node()
        if not node or "options" not in node:
            return []
        
        options = node["options"]
        if not options:
            return []
        
        # Group options by number
        option_groups = {}
        for option in options:
            number = option.get("number", 1)
            if number not in option_groups:
                option_groups[number] = []
            option_groups[number].append(option)
        
        # Randomly select one option from each number group
        processed_options = []
        for number in sorted(option_groups.keys()):
            selected_option = random.choice(option_groups[number])
            processed_options.append(selected_option)
        
        return processed_options
    
    def get_option_texts(self) -> List[str]:
        """Get list of option texts for display"""
        options = self.get_processed_options()
        return [option.get("text", "") for option in options]
    
    def navigate_to_node(self, node_id: str) -> bool:
        """Navigate to a specific node"""
        if node_id in self.dialog_tree:
            self.current_node = node_id
            return True
        return False
    
    def select_option(self, option_index: int) -> Tuple[bool, Dict[str, Any]]:
        """Select an option and navigate to next node"""
        options = self.get_processed_options()
        
        if option_index < 0 or option_index >= len(options):
            return False, {}
        
        selected_option = options[option_index]
        next_node = selected_option.get("next")
        
        if next_node:
            if self.navigate_to_node(next_node):
                return True, selected_option
        
        return False, {}
    
    def apply_node_effects(self, pet: Pet, node_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply effects from current node to pet"""
        if node_data is None:
            node_data = self.get_current_node()
        
        if not node_data:
            return {}
        
        effects = node_data.get("effects", {})
        special = node_data.get("special")
        
        # Apply attribute effects
        if effects:
            pet.apply_effects(effects)
        
        # Handle special effects
        if special:
            if special == "regenerate_name":
                old_name = pet.name
                new_name = pet.regenerate_name()
                return {"special": "name_changed", "old_name": old_name, "new_name": new_name}
            elif special == "regenerate_sex":
                old_sex = pet.sex
                new_sex = pet.regenerate_sex()
                return {"special": "sex_changed", "old_sex": old_sex, "new_sex": new_sex}
            elif special == "quit_game":
                return {"special": "quit_game"}
        
        return {"effects": effects}
    
    def reset_to_main_menu(self) -> bool:
        """Reset dialog to main menu"""
        return self.navigate_to_node("main_menu")
    
    def is_at_main_menu(self) -> bool:
        """Check if currently at main menu"""
        return self.current_node == "main_menu"
    
    def has_options(self) -> bool:
        """Check if current node has options"""
        options = self.get_processed_options()
        return len(options) > 0
    
    def get_dialog_info(self) -> Dict[str, Any]:
        """Get comprehensive info about current dialog state"""
        return {
            "current_node": self.current_node,
            "text": self.get_node_text(),
            "options": self.get_option_texts(),
            "has_options": self.has_options(),
            "is_main_menu": self.is_at_main_menu()
        }
    
    def validate_dialog_tree(self) -> List[str]:
        """Validate dialog tree structure and return any errors"""
        errors = []
        
        if not self.dialog_tree:
            errors.append("Dialog tree is empty")
            return errors
        
        if "main_menu" not in self.dialog_tree:
            errors.append("Missing main_menu node")
        
        # Check each node
        for node_id, node_data in self.dialog_tree.items():
            if not isinstance(node_data, dict):
                errors.append(f"Node '{node_id}' is not a dictionary")
                continue
            
            if "text" not in node_data:
                errors.append(f"Node '{node_id}' missing text field")
            
            if "options" in node_data:
                options = node_data["options"]
                if not isinstance(options, list):
                    errors.append(f"Node '{node_id}' options is not a list")
                    continue
                
                for i, option in enumerate(options):
                    if not isinstance(option, dict):
                        errors.append(f"Node '{node_id}' option {i} is not a dictionary")
                        continue
                    
                    if "text" not in option:
                        errors.append(f"Node '{node_id}' option {i} missing text")
                    
                    if "next" in option:
                        next_node = option["next"]
                        if next_node not in self.dialog_tree:
                            errors.append(f"Node '{node_id}' option {i} references non-existent node '{next_node}'")
        
        return errors