import os
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
import textwrap
from pet import Pet


class UIManager:
    def __init__(self):
        self.console = Console()
        self.selected_option = 0
        self.pet_art = self._get_pet_art()
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
    
    def _get_pet_art(self, compact: bool = False) -> str:
        """Get ASCII art for the pet"""
        if compact:
            return """
     ∩---∩
    (  o   o  )
     ∪-(_)-∪
      (  ◡  )
       \\___/
    ~~~~~~~~~~
            """
        else:
            return """
        ∩---∩
       (  o   o  )
        ∪-(_)-∪
         /   \\
        /     \\
       (  ◡   ◡  )
        \\     /
         \\___/
      ~~~~~~~~~~~~~~
        """
    
    def _create_attribute_bar(self, value: int, max_value: int = 5, width: int = 10) -> str:
        """Create a visual bar for attributes"""
        filled = int((value / max_value) * width)
        empty = width - filled
        return "█" * filled + "░" * empty
    
    def _get_attribute_color(self, value: int, max_value: int = 5) -> str:
        """Get color for attribute based on value"""
        ratio = value / max_value
        if ratio > 0.7:
            return "green"
        elif ratio > 0.3:
            return "yellow"
        else:
            return "red"
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    
    def display_pet_status(self, pet: Pet):
        """Display pet status with ASCII art and attribute bars"""
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        # Use full layout (with boxes) unless terminal is very small
        # The full layout now handles both stacked and side-by-side internally
        if self.terminal_height < 18 or self.terminal_width < 50:
            self._display_compact_status(pet)
        else:
            self._display_full_status(pet)
    
    def _display_compact_status(self, pet: Pet):
        """Display compact pet status for small terminals"""
        # Ultra height-optimized layout - no ASCII art, minimal spacing
        
        # Single line with name and key info
        info_line = f"[bold cyan]{pet.name}[/bold cyan] | Age: {pet.age} | Sex: {pet.sex} | Wealth: ${pet.wealth}"
        self.console.print(info_line)
        
        # Compact attribute display - very short bars
        health_bar = self._create_attribute_bar(pet.health, width=4)
        health_color = self._get_attribute_color(pet.health)
        
        happiness_bar = self._create_attribute_bar(pet.happiness, width=4)
        happiness_color = self._get_attribute_color(pet.happiness)
        
        despair_bar = self._create_attribute_bar(pet.despair, width=4)
        despair_color = self._get_attribute_color(5 - pet.despair)
        
        skill_bar = self._create_attribute_bar(pet.skill, width=4)
        skill_color = self._get_attribute_color(pet.skill)
        
        # Display all stats in 2 compact lines
        stats_line1 = f"Health: [{health_color}]{health_bar}[/{health_color}] {pet.health}/5   Happy: [{happiness_color}]{happiness_bar}[/{happiness_color}] {pet.happiness}/5"
        stats_line2 = f"Despair: [{despair_color}]{despair_bar}[/{despair_color}] {pet.despair}/5   Skill: [{skill_color}]{skill_bar}[/{skill_color}] {pet.skill}/5"
        
        self.console.print(stats_line1)
        self.console.print(stats_line2)
    
    def _display_full_status(self, pet: Pet):
        """Display full pet status for larger terminals"""
        # Create ASCII art panel
        compact_art = self._get_pet_art(compact=True)
        pet_panel = Panel(
            compact_art.strip(),
            title=f"[bold cyan]{pet.name}[/bold cyan]",
            border_style="cyan",
            padding=(0, 1),
            expand=False
        )
        
        # Create stats panel
        stats_table = Table(show_header=False, box=None, padding=(0, 1))
        stats_table.add_column("Attribute", style="bold")
        stats_table.add_column("Value")
        
        # Basic info
        stats_table.add_row("Age:", f"{pet.age}")
        stats_table.add_row("Sex:", f"{pet.sex}")
        stats_table.add_row("Wealth:", f"${pet.wealth}")
        
        # Attribute bars
        health_bar = self._create_attribute_bar(pet.health, width=8)
        health_color = self._get_attribute_color(pet.health)
        stats_table.add_row("Health:", f"[{health_color}]{health_bar}[/{health_color}] {pet.health}/5")
        
        happiness_bar = self._create_attribute_bar(pet.happiness, width=8)
        happiness_color = self._get_attribute_color(pet.happiness)
        stats_table.add_row("Happy:", f"[{happiness_color}]{happiness_bar}[/{happiness_color}] {pet.happiness}/5")
        
        despair_bar = self._create_attribute_bar(pet.despair, width=8)
        despair_color = self._get_attribute_color(5 - pet.despair)
        stats_table.add_row("Despair:", f"[{despair_color}]{despair_bar}[/{despair_color}] {pet.despair}/5")
        
        skill_bar = self._create_attribute_bar(pet.skill, width=8)
        skill_color = self._get_attribute_color(pet.skill)
        stats_table.add_row("Skill:", f"[{skill_color}]{skill_bar}[/{skill_color}] {pet.skill}/5")
        
        stats_panel = Panel(
            stats_table, 
            title="[bold green]Stats[/bold green]", 
            border_style="green", 
            padding=(0, 1),
            expand=False
        )
        
        # Choose layout based on terminal width
        if self.terminal_width >= 100:
            # Wide screen: side by side
            columns = Columns([pet_panel, stats_panel], equal=False, expand=True)
            self.console.print(columns)
        else:
            # Narrow screen: stacked vertically
            self.console.print(pet_panel)
            self.console.print(stats_panel)
    
    def display_menu(self, options: List[str], title: str = "What would you like to do?", show_welcome: bool = False):
        """Display menu with selectable options"""
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        # Display welcome message with reasonable thresholds
        if show_welcome:
            if self.terminal_height >= 25 and self.terminal_width >= 80:
                # Full welcome screen for reasonably sized terminals
                welcome_text = """
[bold cyan]Welcome to E-Pet![/bold cyan]

Your virtual pet companion awaits!

Take care of your pet by feeding, playing, and talking with them.
Watch their attributes and keep them happy and healthy.

Good luck!
                """
                
                # Wrap the welcome text
                wrapped_welcome = self._wrap_text(welcome_text.strip(), self.terminal_width)
                
                panel = Panel(
                    wrapped_welcome,
                    title="[bold green]E-Pet Virtual Companion[/bold green]",
                    border_style="green",
                    expand=False,
                    padding=(0, 2)  # Reduced padding
                )
                self.console.print(Align.center(panel))
            else:
                # Compact welcome for smaller screens
                self.console.print("[bold cyan]Welcome to E-Pet![/bold cyan]")
                self.console.print("Your virtual pet companion!")
        
        # Use compact menu for smaller terminals
        use_compact = self.terminal_height < 25
        
        if use_compact:
            # Compact menu - wrap options if needed
            option_text = " | ".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
            wrapped_title = self._wrap_text(title, self.terminal_width)
            wrapped_options = self._wrap_text(option_text, self.terminal_width)
            self.console.print(f"[bold yellow]{wrapped_title}[/bold yellow]")
            self.console.print(wrapped_options)
        else:
            # Full menu layout
            menu_table = Table(show_header=False, box=None, padding=(0, 1))
            menu_table.add_column("Option", style="bold")
            
            for i, option in enumerate(options):
                option_num = i + 1
                # Wrap long option text
                wrapped_option = self._wrap_text(option, self.terminal_width - 10)
                
                if i == self.selected_option:
                    # Highlighted option
                    menu_table.add_row(f"[black on white]► {option_num}. {wrapped_option}[/black on white]")
                else:
                    menu_table.add_row(f"  {option_num}. {wrapped_option}")
            
            # Wrap title text and check if it needs special handling
            wrapped_title = self._wrap_text(title, self.terminal_width - 6)
            
            # Check if title is too long for panel title (contains newlines after wrapping)
            if '\n' in wrapped_title:
                # Display title as content above the menu instead of as panel title
                self.console.print(f"[bold yellow]{wrapped_title}[/bold yellow]")
                menu_panel = Panel(
                    menu_table,
                    border_style="yellow"
                )
            else:
                # Short title can be displayed as panel title
                menu_panel = Panel(
                    menu_table,
                    title=f"[bold yellow]{wrapped_title}[/bold yellow]",
                    border_style="yellow"
                )
            
            self.console.print(menu_panel)
            
        self.console.print("[dim]Use ↑↓ arrows, Enter to select, or press number keys. 'q' to quit[/dim]")
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to fit within specified width"""
        # Account for panel borders and padding
        effective_width = max(width - 6, 20)  # Leave room for borders and padding
        wrapped_lines = []
        
        # Split by existing newlines first
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if paragraph.strip():  # Non-empty paragraph
                # Wrap each paragraph
                wrapped = textwrap.fill(paragraph.strip(), width=effective_width)
                wrapped_lines.append(wrapped)
            else:  # Empty line
                wrapped_lines.append('')
        
        return '\n'.join(wrapped_lines)
    
    def display_dialog(self, text: str, options: Optional[List[str]] = None):
        """Display dialog text with optional options"""
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        # Always wrap text to fit terminal width
        wrapped_text = self._wrap_text(text, self.terminal_width)
        
        if self.terminal_width < 60:
            # Very compact display for very small screens
            self.console.print(f"[bold magenta]Dialog:[/bold magenta]")
            self.console.print(wrapped_text)
        else:
            # Panel display with proper text wrapping
            dialog_panel = Panel(
                wrapped_text,
                title="[bold magenta]Dialog[/bold magenta]",
                border_style="magenta",
                expand=False
            )
            self.console.print(dialog_panel)
        
        if options:
            self.display_menu(options, "Choose your response:")
    
    def display_save_selection(self, saves: List[str]):
        """Display save file selection menu"""
        if not saves:
            self.console.print(Panel(
                "[yellow]No saved pets found. A new pet will be created.[/yellow]",
                title="[bold red]No Saves[/bold red]",
                border_style="red"
            ))
            return
        
        save_table = Table(show_header=True, box=None)
        save_table.add_column("Pet Name", style="cyan")
        save_table.add_column("Quick Info", style="dim")
        
        for save in saves:
            save_table.add_row(save, "Pet save file")
        
        save_panel = Panel(
            save_table,
            title="[bold green]Select Pet to Load[/bold green]",
            border_style="green"
        )
        self.console.print(save_panel)
    
    def display_message(self, message: str, style: str = "info"):
        """Display a message with specified style"""
        style_colors = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red"
        }
        
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        # Wrap message text
        wrapped_message = self._wrap_text(message, self.terminal_width)
        
        color = style_colors.get(style, "white")
        
        if self.terminal_width < 50:
            # Simple display for very small screens
            self.console.print(f"[{color}]{wrapped_message}[/{color}]")
        else:
            # Panel display
            panel = Panel(
                wrapped_message,
                border_style=color,
                expand=False
            )
            self.console.print(panel)
    
    def display_loading(self, message: str = "Loading..."):
        """Display loading message"""
        self.console.print(f"[dim]{message}[/dim]")
    
    def set_selected_option(self, index: int):
        """Set the currently selected menu option"""
        self.selected_option = index
    
    def get_selected_option(self) -> int:
        """Get the currently selected menu option"""
        return self.selected_option
    
    def display_full_interface(self, pet: Pet, menu_options: List[str], menu_title: str = "What would you like to do?"):
        """Display complete interface with pet status and menu"""
        self.clear_screen()
        self.display_pet_status(pet)
        
        # Only add spacing for taller terminals
        if self.terminal_height >= 25:
            self.console.print()  # Add spacing
            
        self.display_menu(menu_options, menu_title)
    
    def display_game_over(self, pet: Pet, reason: str = ""):
        """Display game over screen"""
        self.clear_screen()
        
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        if self.terminal_height < 15 or self.terminal_width < 60:
            # Compact game over for small screens
            self.console.print("[bold red]GAME OVER[/bold red]")
            self.console.print(f"{pet.name} - Age: {pet.age}, Health: {pet.health}/5")
            self.console.print(f"Final: Happy {pet.happiness}/5, Despair {pet.despair}/5, Wealth ${pet.wealth}")
            if reason:
                wrapped_reason = self._wrap_text(reason, self.terminal_width)
                self.console.print(wrapped_reason)
            self.console.print("Thanks for playing!")
        else:
            # Full game over screen with text wrapping
            game_over_text = f"""
[bold red]GAME OVER[/bold red]

{pet.name} has reached the end of their journey.

{reason}

Final Stats:
Age: {pet.age}
Health: {pet.health}/5
Happiness: {pet.happiness}/5
Despair: {pet.despair}/5
Wealth: ${pet.wealth}

Thank you for playing!
            """
            
            # Wrap the game over text
            wrapped_game_over = self._wrap_text(game_over_text.strip(), self.terminal_width)
            
            panel = Panel(
                wrapped_game_over,
                title="[bold red]Game Over[/bold red]",
                border_style="red",
                expand=False
            )
            self.console.print(Align.center(panel))
    
    def display_welcome(self):
        """Display welcome screen"""
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        if self.terminal_height < 15 or self.terminal_width < 60:
            # Compact welcome for small screens
            self.console.print("[bold cyan]Welcome to E-Pet![/bold cyan]")
            self.console.print("Your virtual pet companion!")
        else:
            # Full welcome screen with text wrapping
            welcome_text = """
[bold cyan]Welcome to E-Pet![/bold cyan]

Your virtual pet companion awaits!

Take care of your pet by feeding, playing, and talking with them.
Watch their attributes and keep them happy and healthy.

Good luck!
            """
            
            # Wrap the welcome text
            wrapped_welcome = self._wrap_text(welcome_text.strip(), self.terminal_width)
            
            panel = Panel(
                wrapped_welcome,
                title="[bold green]E-Pet Virtual Companion[/bold green]",
                border_style="green",
                expand=False
            )
            self.console.print(Align.center(panel))
    
    def display_welcome_with_save_selection(self, saves: List[str]) -> List[str]:
        """Create menu options for save selection (welcome text is displayed by menu)"""
        # Create menu options - put existing saves first, then Create New Pet at bottom
        options = []
        if saves:
            for save in saves:
                options.append(save)  # Just the pet name, no "Load" prefix
            options.append("Create New Pet")
        else:
            options.append("Create New Pet")
        
        return options
    
    def display_effects(self, effects: Dict[str, int]) -> None:
        """Display the effects of an action briefly"""
        if not effects:
            return
        
        # Update terminal size
        self.terminal_height = self.console.size.height
        self.terminal_width = self.console.size.width
        
        # Format effects for display
        effect_text = self._format_effects(effects)
        
        if self.terminal_width < 50:
            # Simple display for very small screens
            self.console.print(f"[cyan]Effects: {effect_text}[/cyan]")
        else:
            # Panel display
            panel = Panel(
                effect_text,
                title="[bold cyan]Effects[/bold cyan]",
                border_style="cyan",
                expand=False
            )
            self.console.print(panel)
    
    def _format_effects(self, effects: Dict[str, int]) -> str:
        """Format effects dictionary into a readable string"""
        effect_parts = []
        
        # Define attribute display names and symbols
        attribute_info = {
            "health": ("Health", "❤️"),
            "happiness": ("Happiness", "😊"),
            "despair": ("Despair", "😰"), 
            "skill": ("Skill", "🎯"),
            "wealth": ("Wealth", "💰"),
            "age": ("Age", "📅")
        }
        
        # Sort effects for consistent display order
        sorted_effects = sorted(effects.items())
        
        for attribute, value in sorted_effects:
            if value != 0:  # Only show attributes that changed
                info = attribute_info.get(attribute, (attribute.capitalize(), ""))
                name, symbol = info
                
                if value > 0:
                    # Positive change
                    effect_parts.append(f"{symbol} {name} +{value}")
                else:
                    # Negative change
                    effect_parts.append(f"{symbol} {name} {value}")
        
        return " | ".join(effect_parts) if effect_parts else "No changes"