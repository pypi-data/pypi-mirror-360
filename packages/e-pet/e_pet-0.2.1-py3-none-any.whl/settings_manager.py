import json
import os
from typing import Dict, Any, Optional, List


class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.settings = {}
        self.default_settings = {
            "decay": {
                "actions_per_decay": 20,
                "health_decay": -1,
                "happiness_decay": -1,
                "despair_increase": 1,
                "skill_decay": -1
            },
            "pet_defaults": {
                "starting_health": 5,
                "starting_happiness": 5,
                "starting_despair": 0,
                "starting_wealth": 100,
                "starting_age": 0,
                "starting_skill": 0
            },
            "game_settings": {
                "auto_save": True,
                "display_action_count": False,
                "confirm_quit": True
            }
        }
        self.load_settings()
    
    def load_settings(self) -> bool:
        """Load settings from JSON file or create default if not found"""
        try:
            # Try to find the file relative to the script location first
            settings_file = self.settings_file
            if not os.path.isabs(settings_file):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                bundled_file = os.path.join(script_dir, settings_file)
                if os.path.exists(bundled_file):
                    settings_file = bundled_file
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.settings = self._merge_with_defaults(self.settings, self.default_settings)
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
            return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()
            return False
    
    def save_settings(self) -> bool:
        """Save current settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def _merge_with_defaults(self, current: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Merge current settings with defaults, ensuring all default keys exist"""
        merged = defaults.copy()
        
        for key, value in current.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self._merge_with_defaults(value, merged[key])
                else:
                    merged[key] = value
            else:
                merged[key] = value
        
        return merged
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'decay.actions_per_decay')"""
        keys = key_path.split('.')
        current = self.settings
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set a setting value using dot notation"""
        keys = key_path.split('.')
        current = self.settings
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final key
        current[keys[-1]] = value
        return self.save_settings()
    
    def get_decay_settings(self) -> Dict[str, int]:
        """Get decay-related settings"""
        return {
            "actions_per_decay": self.get("decay.actions_per_decay", 20),
            "health_decay": self.get("decay.health_decay", -1),
            "happiness_decay": self.get("decay.happiness_decay", -1),
            "despair_increase": self.get("decay.despair_increase", 1),
            "skill_decay": self.get("decay.skill_decay", -1)
        }
    
    def get_pet_defaults(self) -> Dict[str, int]:
        """Get pet default attribute values"""
        return {
            "starting_health": self.get("pet_defaults.starting_health", 5),
            "starting_happiness": self.get("pet_defaults.starting_happiness", 5),
            "starting_despair": self.get("pet_defaults.starting_despair", 0),
            "starting_wealth": self.get("pet_defaults.starting_wealth", 100),
            "starting_age": self.get("pet_defaults.starting_age", 0),
            "starting_skill": self.get("pet_defaults.starting_skill", 0)
        }
    
    def get_game_settings(self) -> Dict[str, bool]:
        """Get game-related settings"""
        return {
            "auto_save": self.get("game_settings.auto_save", True),
            "display_action_count": self.get("game_settings.display_action_count", False),
            "confirm_quit": self.get("game_settings.confirm_quit", True)
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def validate_settings(self) -> List[str]:
        """Validate current settings and return any errors"""
        errors = []
        
        # Validate decay settings
        decay_actions = self.get("decay.actions_per_decay")
        if not isinstance(decay_actions, int) or decay_actions <= 0:
            errors.append("decay.actions_per_decay must be a positive integer")
        
        # Validate pet defaults
        pet_defaults = self.get_pet_defaults()
        for key, value in pet_defaults.items():
            if not isinstance(value, int) or value < 0:
                errors.append(f"pet_defaults.{key} must be a non-negative integer")
        
        # Validate ranges for bounded attributes
        if pet_defaults["starting_health"] > 5:
            errors.append("pet_defaults.starting_health cannot exceed 5")
        if pet_defaults["starting_happiness"] > 5:
            errors.append("pet_defaults.starting_happiness cannot exceed 5")
        if pet_defaults["starting_despair"] > 5:
            errors.append("pet_defaults.starting_despair cannot exceed 5")
        if pet_defaults["starting_skill"] > 5:
            errors.append("pet_defaults.starting_skill cannot exceed 5")
        
        return errors
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        return self.settings.copy()


class DecaySystem:
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.decay_settings = self.settings.get_decay_settings()
    
    def should_apply_decay(self, action_count: int) -> bool:
        """Check if decay should be applied based on action count"""
        return action_count >= self.decay_settings["actions_per_decay"]
    
    def apply_decay(self, pet) -> Dict[str, int]:
        """Apply natural decay to pet attributes"""
        effects = {}
        
        # Apply health decay
        if self.decay_settings["health_decay"] != 0:
            effects["health"] = self.decay_settings["health_decay"]
        
        # Apply happiness decay
        if self.decay_settings["happiness_decay"] != 0:
            effects["happiness"] = self.decay_settings["happiness_decay"]
        
        # Apply despair increase
        if self.decay_settings["despair_increase"] != 0:
            effects["despair"] = self.decay_settings["despair_increase"]
        
        # Apply skill decay
        if self.decay_settings["skill_decay"] != 0:
            effects["skill"] = self.decay_settings["skill_decay"]
        
        # Apply effects to pet
        if effects:
            pet.apply_effects(effects)
        
        # Reset action count
        pet.reset_action_count()
        
        return effects
    
    def get_decay_info(self) -> Dict[str, Any]:
        """Get information about decay settings"""
        return {
            "actions_until_decay": self.decay_settings["actions_per_decay"],
            "health_decay_amount": self.decay_settings["health_decay"],
            "happiness_decay_amount": self.decay_settings["happiness_decay"],
            "despair_increase_amount": self.decay_settings["despair_increase"],
            "skill_decay_amount": self.decay_settings["skill_decay"]
        }