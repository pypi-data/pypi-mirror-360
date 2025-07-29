import random
import json
from typing import Dict, Any


class Pet:
    def __init__(self, name: str = None, sex: str = None):
        self.name = name if name else self._generate_name()
        self.age = 0
        self.sex = sex if sex else self._generate_sex()
        self.health = 5
        self.happiness = 5
        self.despair = 0
        self.wealth = 100
        self.action_count = 0
    
    def _generate_name(self) -> str:
        """Generate a random pet name"""
        names = [
            "Fluffy", "Buddy", "Max", "Bella", "Charlie", "Lucy", "Cooper", "Daisy",
            "Rocky", "Molly", "Bear", "Sadie", "Duke", "Maggie", "Jack", "Sophie",
            "Tucker", "Chloe", "Oliver", "Lola", "Zeus", "Penny", "Benny", "Zoey",
            "Milo", "Ruby", "Toby", "Lily", "Leo", "Rosie", "Shadow", "Princess",
            "Simba", "Stella", "Gus", "Luna", "Oscar", "Nala", "Rusty", "Coco"
        ]
        return random.choice(names)
    
    def _generate_sex(self) -> str:
        """Generate random sex assignment"""
        return random.choice(["M", "F", "??"])
    
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
            "wealth": self.wealth
        }