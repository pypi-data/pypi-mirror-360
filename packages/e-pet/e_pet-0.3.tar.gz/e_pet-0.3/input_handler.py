import sys
from typing import Optional, Tuple

# Platform-specific imports
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    # Windows doesn't have termios/tty modules
    termios = None
    tty = None
    HAS_TERMIOS = False

class InputHandler:
    def __init__(self):
        self.original_settings = None
    
    def setup_raw_input(self):
        """Setup raw input mode for capturing arrow keys"""
        if HAS_TERMIOS and sys.stdin.isatty():
            self.original_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
    
    def restore_input(self):
        """Restore normal input mode"""
        if HAS_TERMIOS and self.original_settings and sys.stdin.isatty():
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_settings)
    
    def get_key(self) -> str:
        """Get a single key press including arrow keys"""
        if not HAS_TERMIOS or not sys.stdin.isatty():
            # Fallback for non-interactive environments or Windows
            return input().strip()
        
        key = sys.stdin.read(1)
        
        # Handle escape sequences (arrow keys)
        if ord(key) == 27:  # ESC
            # Read the next two characters
            next1 = sys.stdin.read(1)
            next2 = sys.stdin.read(1)
            
            if next1 == '[':
                if next2 == 'A':
                    return 'UP'
                elif next2 == 'B':
                    return 'DOWN'
                elif next2 == 'C':
                    return 'RIGHT'
                elif next2 == 'D':
                    return 'LEFT'
        
        # Handle regular keys
        if ord(key) == 10 or ord(key) == 13:  # Enter
            return 'ENTER'
        elif ord(key) == 27:  # ESC
            return 'ESC'
        elif ord(key) == 3:  # Ctrl+C
            return 'CTRL_C'
        elif ord(key) == 127:  # Backspace
            return 'BACKSPACE'
        else:
            return key
    
    def get_menu_input(self, num_options: int, current_selection: int = 0) -> Tuple[str, int]:
        """
        Get input for menu navigation
        Returns: (action, new_selection)
        Actions: 'SELECT', 'QUIT', 'NUMBER', 'CONTINUE'
        """
        try:
            self.setup_raw_input()
            
            while True:
                key = self.get_key()
                
                if key == 'UP':
                    new_selection = (current_selection - 1) % num_options
                    return 'MOVE', new_selection
                elif key == 'DOWN':
                    new_selection = (current_selection + 1) % num_options
                    return 'MOVE', new_selection
                elif key == 'ENTER':
                    return 'SELECT', current_selection
                elif key == 'ESC' or key.lower() == 'q':
                    return 'QUIT', current_selection
                elif key == 'CTRL_C':
                    return 'QUIT', current_selection
                elif key.isdigit():
                    digit = int(key)
                    if 1 <= digit <= num_options:
                        return 'SELECT', digit - 1
                    # Invalid number, continue
                    continue
                else:
                    # Unknown key, continue
                    continue
                    
        except Exception:
            # Fallback to regular input if raw mode fails
            return self.get_fallback_input(num_options, current_selection)
        finally:
            self.restore_input()
    
    def get_fallback_input(self, num_options: int, current_selection: int = 0) -> Tuple[str, int]:
        """Fallback input method for environments that don't support raw input"""
        try:
            user_input = input(f"\nEnter choice (1-{num_options}) or 'q' to quit: ").strip().lower()
            
            if user_input == 'q' or user_input == 'quit':
                return 'QUIT', current_selection
            
            try:
                choice = int(user_input)
                if 1 <= choice <= num_options:
                    return 'SELECT', choice - 1
                else:
                    print(f"Please enter a number between 1 and {num_options}")
                    return 'CONTINUE', current_selection
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
                return 'CONTINUE', current_selection
                
        except (EOFError, KeyboardInterrupt):
            return 'QUIT', current_selection


class MenuNavigator:
    def __init__(self):
        self.input_handler = InputHandler()
        self.current_selection = 0
    
    def navigate_menu(self, options: list, ui_manager, pet=None, title: str = "Choose an option:", show_welcome: bool = False) -> Optional[int]:
        """
        Navigate a menu with arrow keys
        Returns the selected option index or None if quit
        """
        self.current_selection = 0
        
        while True:
            # Update UI selection
            ui_manager.set_selected_option(self.current_selection)
            
            # Display the interface
            if pet:
                ui_manager.display_full_interface(pet, options, title)
            else:
                ui_manager.clear_screen()
                ui_manager.display_menu(options, title, show_welcome)
            
            # Get user input
            action, new_selection = self.input_handler.get_menu_input(
                len(options), 
                self.current_selection
            )
            
            if action == 'SELECT':
                return new_selection
            elif action == 'QUIT':
                return None
            elif action == 'MOVE':
                self.current_selection = new_selection
                # Continue the loop to redraw with new selection
            elif action == 'CONTINUE':
                # Continue the loop (used for fallback mode)
                continue
    
    def get_confirmation(self, message: str, ui_manager) -> bool:
        """Get yes/no confirmation"""
        options = ["Yes", "No"]
        result = self.navigate_menu(options, ui_manager, title=message)
        return result == 0 if result is not None else False