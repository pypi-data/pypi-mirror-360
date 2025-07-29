import json
import os
import re
from typing import List, Optional, Dict, Any
from pet import Pet


class SaveManager:
    def __init__(self, save_directory: str = "."):
        self.save_directory = save_directory
        self.save_extension = ".pet"
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize pet name for use as filename"""
        # Remove or replace invalid filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed_pet"
        return sanitized
    
    def _get_save_path(self, pet_name: str) -> str:
        """Get full save file path for a pet"""
        sanitized_name = self._sanitize_filename(pet_name)
        return os.path.join(self.save_directory, f"{sanitized_name}{self.save_extension}")
    
    def save_pet(self, pet: Pet) -> bool:
        """Save pet to JSON file"""
        try:
            save_path = self._get_save_path(pet.name)
            pet_data = pet.to_dict()
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(pet_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving pet: {e}")
            return False
    
    def load_pet(self, pet_name: str) -> Optional[Pet]:
        """Load pet from JSON file"""
        try:
            save_path = self._get_save_path(pet_name)
            
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                pet_data = json.load(f)
            
            return Pet.from_dict(pet_data)
        except Exception as e:
            print(f"Error loading pet: {e}")
            return None
    
    def list_saved_pets(self) -> List[str]:
        """List all available pet save files, sorted by most recent modification time"""
        try:
            pet_files = []
            for filename in os.listdir(self.save_directory):
                if filename.endswith(self.save_extension):
                    # Remove extension to get pet name
                    pet_name = filename[:-len(self.save_extension)]
                    file_path = os.path.join(self.save_directory, filename)
                    mod_time = os.path.getmtime(file_path)
                    pet_files.append((pet_name, mod_time))
            
            # Sort by modification time (most recent first)
            pet_files.sort(key=lambda x: x[1], reverse=True)
            
            # Return just the pet names
            return [pet_name for pet_name, _ in pet_files]
        except Exception as e:
            print(f"Error listing saves: {e}")
            return []
    
    def delete_save(self, pet_name: str) -> bool:
        """Delete a pet save file"""
        try:
            save_path = self._get_save_path(pet_name)
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def save_exists(self, pet_name: str) -> bool:
        """Check if a save file exists for the given pet name"""
        save_path = self._get_save_path(pet_name)
        return os.path.exists(save_path)
    
    def auto_save(self, pet: Pet) -> bool:
        """Auto-save pet after each action"""
        return self.save_pet(pet)
    
    def get_save_info(self, pet_name: str) -> Optional[Dict[str, Any]]:
        """Get basic info about a save file without fully loading the pet"""
        try:
            save_path = self._get_save_path(pet_name)
            
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                pet_data = json.load(f)
            
            return {
                "name": pet_data.get("name", "Unknown"),
                "age": pet_data.get("age", 0),
                "sex": pet_data.get("sex", "??"),
                "health": pet_data.get("health", 0),
                "happiness": pet_data.get("happiness", 0),
                "despair": pet_data.get("despair", 0),
                "wealth": pet_data.get("wealth", 0)
            }
        except Exception as e:
            print(f"Error getting save info: {e}")
            return None
    
    def create_new_pet(self) -> Pet:
        """Create a new pet and save it"""
        pet = Pet()
        self.save_pet(pet)
        return pet