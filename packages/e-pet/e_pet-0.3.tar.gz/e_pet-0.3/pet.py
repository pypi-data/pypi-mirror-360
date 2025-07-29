import random
import os
from typing import Dict, Any, Optional, List


class Pet:
    def __init__(self, name: Optional[str] = None, sex: Optional[str] = None):
        self.name = name if name else self._generate_name()
        self.age = 0
        self.sex = sex if sex else self._generate_sex()
        self.health = 5
        self.happiness = 5
        self.despair = 0
        self.wealth = 100
        self.skill = 0
        self.action_count = 0
    
    def _generate_name(self) -> str:
        """Generate a random pet name from pet_names.txt file"""
        names = self._load_pet_names()
        return random.choice(names)
    
    def _generate_sex(self) -> str:
        """Generate random sex assignment"""
        return random.choice(["M", "F", "??"])
    
    def _load_pet_names(self) -> List[str]:
        """Load pet names from pet_names.txt file"""
        names_file = "pet_names.txt"
        
        # Try to find the file relative to the script location first
        if not os.path.isabs(names_file):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bundled_file = os.path.join(script_dir, names_file)
            if os.path.exists(bundled_file):
                names_file = bundled_file
        
        if not os.path.exists(names_file):
            raise FileNotFoundError(f"Pet names file '{names_file}' not found. Please ensure the file exists in the current directory.")
        
        try:
            with open(names_file, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f.readlines() if line.strip()]
            
            if not names:
                raise ValueError(f"Pet names file '{names_file}' is empty or contains no valid names. Please add at least one name to the file.")
            
            return names
            
        except (IOError, OSError) as e:
            raise IOError(f"Could not read pet names file '{names_file}': {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Pet names file '{names_file}' contains invalid characters: {e}")
    
    def regenerate_name(self) -> str:
        """Regenerate pet name and return new name"""
        self.name = self._generate_name()
        return self.name
    
    def regenerate_sex(self) -> str:
        """Regenerate pet sex and return new sex"""
        self.sex = self._generate_sex()
        return self.sex
    
    def modify_attribute(self, attribute: str, value: int) -> bool:
        """Modify a pet attribute with bounds checking"""
        if attribute == "health":
            self.health = max(0, min(5, self.health + value))
        elif attribute == "happiness":
            self.happiness = max(0, min(5, self.happiness + value))
        elif attribute == "despair":
            self.despair = max(0, min(5, self.despair + value))
        elif attribute == "skill":
            self.skill = max(0, min(5, self.skill + value))
        elif attribute == "wealth":
            self.wealth = max(0, self.wealth + value)
        elif attribute == "age":
            self.age = max(0, self.age + value)
        else:
            return False
        return True
    
    def increment_action_count(self) -> int:
        """Increment action count and return current count"""
        self.action_count += 1
        return self.action_count
    
    def reset_action_count(self) -> None:
        """Reset action count to 0"""
        self.action_count = 0
    
    def apply_effects(self, effects: Dict[str, int]) -> None:
        """Apply multiple attribute effects at once"""
        for attribute, value in effects.items():
            self.modify_attribute(attribute, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize pet to dictionary for saving"""
        return {
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "health": self.health,
            "happiness": self.happiness,
            "despair": self.despair,
            "wealth": self.wealth,
            "skill": self.skill,
            "action_count": self.action_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pet':
        """Create pet from dictionary data"""
        pet = cls(name=data["name"], sex=data["sex"])
        pet.age = data["age"]
        pet.health = data["health"]
        pet.happiness = data["happiness"]
        pet.despair = data["despair"]
        pet.wealth = data["wealth"]
        pet.skill = data.get("skill", 0)  # Default to 0 for backward compatibility
        pet.action_count = data["action_count"]
        return pet
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pet status for display"""
        return {
            "name": self.name,
            "age": self.age,
            "sex": self.sex,
            "health": self.health,
            "happiness": self.happiness,
            "despair": self.despair,
            "wealth": self.wealth,
            "skill": self.skill
        }