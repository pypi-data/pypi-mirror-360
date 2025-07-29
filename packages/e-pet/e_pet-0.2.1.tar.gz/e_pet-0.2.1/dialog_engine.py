import json
import random
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from pet import Pet

try:
    # Python 3.9+
    from importlib import resources
except ImportError:
    # Python 3.7-3.8
    import importlib_resources as resources


class DialogEngine:
    def __init__(self, dialog_file: str = "dialog_tree.json"):
        self.dialog_file = dialog_file
        self.dialog_tree = {}
        self.current_node = "main_menu"
        self.load_dialog_tree()
    
    def load_dialog_tree(self) -> bool:
        """Load dialog tree from JSON file"""
        try:
            # Try multiple locations for the dialog tree file
            content = None
            
            # 1. Try current working directory
            if os.path.exists(self.dialog_file):
                with open(self.dialog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # 2. Try relative to script location
            elif not os.path.isabs(self.dialog_file):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(script_dir, self.dialog_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
            
            # 3. Try package resources (for installed packages)
            if content is None:
                try:
                    # Get the package name from the current module
                    package_name = __name__.split('.')[0] if '.' in __name__ else None
                    if package_name:
                        content = resources.read_text(package_name, self.dialog_file)
                    else:
                        # Fallback: try to read from the same directory as this file
                        try:
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            with resources.path(sys.modules[__name__].__package__ or __name__, self.dialog_file) as resource_path:
                                content = resource_path.read_text(encoding='utf-8')
                        except:
                            # Last resort: try reading from __file__ directory
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            resource_file = os.path.join(script_dir, self.dialog_file)
                            if os.path.exists(resource_file):
                                with open(resource_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                except Exception:
                    pass
            
            if content is None:
                print(f"Dialog tree file '{self.dialog_file}' not found!")
                return False
            
            self.dialog_tree = json.loads(content)
            return True
            
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
    
    def get_processed_options(self, pet: Optional[Pet] = None) -> List[Dict[str, Any]]:
        """Get options for current node with randomization and conditional filtering applied"""
        node = self.get_current_node()
        if not node or "options" not in node:
            return []
        
        options = node["options"]
        if not options:
            return []
        
        # Filter options based on conditions if pet is provided
        if pet:
            filtered_options = []
            for option in options:
                if "condition" in option:
                    # Check if condition is met
                    if self.evaluate_condition(option["condition"], pet):
                        filtered_options.append(option)
                else:
                    # No condition, always include
                    filtered_options.append(option)
            options = filtered_options
        
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
    
    def get_option_texts(self, pet: Optional[Pet] = None) -> List[str]:
        """Get list of option texts for display"""
        options = self.get_processed_options(pet)
        return [option.get("text", "") for option in options]
    
    def navigate_to_node(self, node_id: str) -> bool:
        """Navigate to a specific node"""
        if node_id in self.dialog_tree:
            self.current_node = node_id
            return True
        return False
    
    def evaluate_conditional_routing(self, next_node: Any, pet: Pet) -> str:
        """Evaluate conditional routing based on pet attributes"""
        if isinstance(next_node, str):
            # Simple string routing
            return next_node
        elif isinstance(next_node, dict):
            # Conditional routing
            for condition, target_node in next_node.items():
                if condition == "else":
                    continue  # Handle 'else' last
                
                # Parse condition (e.g., "health<5", "happiness>=3", "despair==0")
                if self.evaluate_condition(condition, pet):
                    return target_node
            
            # If no conditions matched, use 'else' if available
            if "else" in next_node:
                return next_node["else"]
            
            # Fallback: use the first value if no 'else' specified
            return list(next_node.values())[0]
        
        return "main_menu"  # Fallback
    
    def evaluate_condition(self, condition: str, pet: Pet) -> bool:
        """Evaluate a condition string with support for compound conditions like 'health<5&wealth<3' or 'happiness>=4|despair<=1'"""
        try:
            condition = condition.strip()
            
            # Handle compound conditions with & (AND) and | (OR)
            if '&' in condition:
                # AND condition - all parts must be true
                parts = condition.split('&')
                return all(self.evaluate_single_condition(part.strip(), pet) for part in parts)
            elif '|' in condition:
                # OR condition - at least one part must be true
                parts = condition.split('|')
                return any(self.evaluate_single_condition(part.strip(), pet) for part in parts)
            else:
                # Single condition
                return self.evaluate_single_condition(condition, pet)
                
        except (ValueError, AttributeError):
            return False
        
        return False
    
    def evaluate_single_condition(self, condition: str, pet: Pet) -> bool:
        """Evaluate a single condition string like 'health<5' or 'happiness>=3'"""
        try:
            # Parse the condition
            condition = condition.strip()
            
            # Find the operator
            operators = ['<=', '>=', '==', '!=', '<', '>']
            operator = None
            attribute = None
            value = None
            
            for op in operators:
                if op in condition:
                    parts = condition.split(op, 1)
                    if len(parts) == 2:
                        attribute = parts[0].strip()
                        value = int(parts[1].strip())
                        operator = op
                        break
            
            if not operator or not attribute or value is None:
                return False
            
            # Get pet attribute value
            pet_value = getattr(pet, attribute, 0)
            if pet_value is None:
                pet_value = 0
            
            # Ensure we have valid integers for comparison
            try:
                pet_value = int(pet_value)
                value = int(value)
            except (ValueError, TypeError):
                return False
            
            # Evaluate condition
            if operator == '<':
                return pet_value < value
            elif operator == '<=':
                return pet_value <= value
            elif operator == '>':
                return pet_value > value
            elif operator == '>=':
                return pet_value >= value
            elif operator == '==':
                return pet_value == value
            elif operator == '!=':
                return pet_value != value
            
        except (ValueError, AttributeError):
            return False
        
        return False

    def select_option(self, option_index: int, pet: Optional[Pet] = None) -> Tuple[bool, Dict[str, Any]]:
        """Select an option and navigate to next node"""
        options = self.get_processed_options(pet)
        
        if option_index < 0 or option_index >= len(options):
            return False, {}
        
        selected_option = options[option_index]
        next_node_raw = selected_option.get("next")
        
        if next_node_raw:
            # Evaluate conditional routing if pet is provided
            if pet:
                next_node = self.evaluate_conditional_routing(next_node_raw, pet)
            else:
                # Fallback for simple string routing
                next_node = next_node_raw if isinstance(next_node_raw, str) else "main_menu"
            
            if self.navigate_to_node(next_node):
                return True, selected_option
        
        return False, {}
    
    def apply_node_effects(self, pet: Pet, node_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
    
    def has_options(self, pet: Optional[Pet] = None) -> bool:
        """Check if current node has options"""
        options = self.get_processed_options(pet)
        return len(options) > 0
    
    def get_dialog_info(self, pet: Optional[Pet] = None) -> Dict[str, Any]:
        """Get comprehensive info about current dialog state"""
        return {
            "current_node": self.current_node,
            "text": self.get_node_text(),
            "options": self.get_option_texts(pet),
            "has_options": self.has_options(pet),
            "is_main_menu": self.is_at_main_menu()
        }
    
    def validate_dialog_tree(self) -> List[str]:
        """Validate dialog tree structure, conditions, and routing"""
        errors = []
        
        if not self.dialog_tree:
            errors.append("Dialog tree is empty")
            return errors
        
        if "main_menu" not in self.dialog_tree:
            errors.append("Missing main_menu node")
        
        # Get valid pet attributes for validation
        valid_attributes = self._get_valid_pet_attributes()
        
        # Check each node
        for node_id, node_data in self.dialog_tree.items():
            if not isinstance(node_data, dict):
                errors.append(f"Node '{node_id}' is not a dictionary")
                continue
            
            if "text" not in node_data:
                errors.append(f"Node '{node_id}' missing text field")
            
            # Validate effects if present
            if "effects" in node_data:
                effects_errors = self._validate_effects(node_id, node_data["effects"], valid_attributes)
                errors.extend(effects_errors)
            
            # Validate special effects if present
            if "special" in node_data:
                special_errors = self._validate_special_effects(node_id, node_data["special"])
                errors.extend(special_errors)
            
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
                    
                    # Validate condition syntax if present
                    if "condition" in option:
                        condition_errors = self._validate_condition_syntax(node_id, i, option["condition"], valid_attributes)
                        errors.extend(condition_errors)
                    
                    if "next" in option:
                        next_errors = self._validate_next_routing(node_id, i, option["next"], valid_attributes)
                        errors.extend(next_errors)
        
        return errors
    
    def _get_valid_pet_attributes(self) -> set:
        """Get list of valid pet attributes for validation"""
        # Import Pet class to get valid attributes
        try:
            from pet import Pet
            pet_instance = Pet()
            # Get all numeric attributes that can be used in conditions
            valid_attrs = set()
            for attr in ['health', 'happiness', 'despair', 'wealth', 'age', 'skill']:
                if hasattr(pet_instance, attr):
                    valid_attrs.add(attr)
            return valid_attrs
        except:
            # Fallback list if Pet class can't be imported
            return {'health', 'happiness', 'despair', 'wealth', 'age', 'skill'}
    
    def _validate_effects(self, node_id: str, effects: Any, valid_attributes: set) -> List[str]:
        """Validate effects object"""
        errors = []
        
        if not isinstance(effects, dict):
            errors.append(f"Node '{node_id}' effects must be a dictionary")
            return errors
        
        for attr, value in effects.items():
            if attr not in valid_attributes:
                errors.append(f"Node '{node_id}' effects references invalid attribute '{attr}'")
            
            try:
                int(value)  # Check if value is numeric
            except (ValueError, TypeError):
                errors.append(f"Node '{node_id}' effects['{attr}'] must be a number, got '{value}'")
        
        return errors
    
    def _validate_special_effects(self, node_id: str, special: Any) -> List[str]:
        """Validate special effects"""
        errors = []
        
        if not isinstance(special, str):
            errors.append(f"Node '{node_id}' special must be a string")
            return errors
        
        valid_specials = {'regenerate_name', 'regenerate_sex', 'quit_game'}
        if special not in valid_specials:
            errors.append(f"Node '{node_id}' special effect '{special}' is not valid. Valid options: {valid_specials}")
        
        return errors
    
    def _validate_next_routing(self, node_id: str, option_index: int, next_node: Any, valid_attributes: set) -> List[str]:
        """Validate next routing (simple or conditional)"""
        errors = []
        
        if isinstance(next_node, str):
            # Simple string routing
            if next_node not in self.dialog_tree:
                errors.append(f"Node '{node_id}' option {option_index} references non-existent node '{next_node}'")
        elif isinstance(next_node, dict):
            # Conditional routing
            has_else = False
            for condition, target_node in next_node.items():
                if condition == "else":
                    has_else = True
                    if target_node not in self.dialog_tree:
                        errors.append(f"Node '{node_id}' option {option_index} 'else' references non-existent node '{target_node}'")
                else:
                    # Validate condition syntax
                    condition_errors = self._validate_condition_syntax(node_id, option_index, condition, valid_attributes)
                    errors.extend(condition_errors)
                    
                    # Validate target node exists
                    if target_node not in self.dialog_tree:
                        errors.append(f"Node '{node_id}' option {option_index} condition '{condition}' references non-existent node '{target_node}'")
            
            if not has_else and len(next_node) > 0:
                errors.append(f"Node '{node_id}' option {option_index} conditional routing should include an 'else' fallback")
        else:
            errors.append(f"Node '{node_id}' option {option_index} 'next' field must be a string or dictionary")
        
        return errors
    
    def _validate_condition_syntax(self, node_id: str, option_index: int, condition: str, valid_attributes: set) -> List[str]:
        """Validate condition syntax and attribute references"""
        errors = []
        
        try:
            # Handle compound conditions
            if '&' in condition:
                parts = condition.split('&')
                for part in parts:
                    part_errors = self._validate_single_condition_syntax(node_id, option_index, part.strip(), valid_attributes)
                    errors.extend(part_errors)
            elif '|' in condition:
                parts = condition.split('|')
                for part in parts:
                    part_errors = self._validate_single_condition_syntax(node_id, option_index, part.strip(), valid_attributes)
                    errors.extend(part_errors)
            else:
                # Single condition
                part_errors = self._validate_single_condition_syntax(node_id, option_index, condition, valid_attributes)
                errors.extend(part_errors)
        except Exception as e:
            errors.append(f"Node '{node_id}' option {option_index} condition '{condition}' validation error: {e}")
        
        return errors
    
    def _validate_single_condition_syntax(self, node_id: str, option_index: int, condition: str, valid_attributes: set) -> List[str]:
        """Validate a single condition's syntax"""
        errors = []
        
        condition = condition.strip()
        if not condition:
            errors.append(f"Node '{node_id}' option {option_index} has empty condition")
            return errors
        
        # Find operator
        operators = ['<=', '>=', '==', '!=', '<', '>']
        operator_found = None
        attribute = None
        value = None
        
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    attribute = parts[0].strip()
                    value_str = parts[1].strip()
                    operator_found = op
                    
                    # Validate attribute
                    if attribute not in valid_attributes:
                        errors.append(f"Node '{node_id}' option {option_index} condition '{condition}' uses invalid attribute '{attribute}'. Valid: {valid_attributes}")
                    
                    # Validate value is numeric
                    try:
                        value = int(value_str)
                    except ValueError:
                        errors.append(f"Node '{node_id}' option {option_index} condition '{condition}' value '{value_str}' must be a number")
                    
                    break
        
        if not operator_found:
            errors.append(f"Node '{node_id}' option {option_index} condition '{condition}' has invalid syntax. Must use operators: {operators}")
        
        return errors