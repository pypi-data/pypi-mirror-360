"""ASCII art collection for Bible CLI."""

from typing import Dict, Optional
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

# ASCII Art Collection
ASCII_ART = {
    "welcome": """
    _____ _____ ____  _      ______    _____ _      _____
   |  __ \\_   _|  _ \\| |    |  ____|  / ____| |    |_   _|
   | |__) || | | |_) | |    | |__    | |    | |      | |
   |  ___/ | | |  _ <| |    |  __|   | |    | |      | |
   | |    _| |_| |_) | |____| |____  | |____| |____ _| |_
   |_|   |_____|____/|______|______|  \\_____|______|_____|

                    Press ? for help
""",
    
    "praying_hands": """
         _._
       _|  |_
      |      |
      |  /\\  |
      | /  \\ |
      |/    \\|
      /      \\
     /   /\\   \\
    /   /  \\   \\
   /___/    \\___\\
""",
    
    "cross": """
        ✝
      __|__
     |_____|
        |
        |
        |
        |
""",
    
    "dove": """
       _.-.
      /  _ \\
     | >(o)<|
      \\  ‾ /
       |‾‾|
        \\/
""",
    
    "open_book": """
     ____________
    /\\  ________ \\
   /  \\ \\______/\\ \\
  / /\\ \\ \\  / /\\ \\ \\
 / / /\\ \\_\\/ / /\\ \\_\\
/_/ /  \\/_/_/ /  \\/_/
""",
    
    "heart": """
      ♥♥♥    ♥♥♥
    ♥♥♥♥♥♥♥♥♥♥♥♥♥
   ♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
   ♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥
    ♥♥♥♥♥♥♥♥♥♥♥♥♥
     ♥♥♥♥♥♥♥♥♥♥♥
      ♥♥♥♥♥♥♥♥♥
       ♥♥♥♥♥♥♥
        ♥♥♥♥♥
         ♥♥♥
          ♥
""",
    
    "lamb": """
      .--.
     /    \\
    | ^  ^ |
     \\  o  /
      '---'
     /|   |\\
    / |   | \\
   '--|   |--'
      |   |
      |   |
     /|   |\\
    ' '   ' '
""",
    
    "fish": """
           ><(((°>
      ><(((°>
  ><(((°>
      ><(((°>
           ><(((°>
""",
    
    "star": """
        *
       ***
      *****
     *******
    *********
     *******
      *****
       ***
        *
""",
    
    "candle": """
        (
        )
       (
      __|__
     |     |
     |     |
     |     |
     |     |
     |_____|
       | |
       |_|
""",
    
    "bible": """
    ┌─────────────┐
    │  H O L Y    │
    │             │
    │   B I B L E │
    │             │
    │ ┌─────────┐ │
    │ │         │ │
    │ │  α & Ω  │ │
    │ │         │ │
    │ └─────────┘ │
    └─────────────┘
""",
    
    "simple_cross": """
        |
        |
    ----+----
        |
        |
""",
    
    "crown": """
    ∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙
    ∙     ♔ KING ♔     ∙
    ∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙∙
""",
    
    "alpha_omega": """
        α     Ω
       /|\\   /|\\
      / | \\ / | \\
         |   |
         |   |
        /|   |\\
       / |   | \\
""",
    
    "shepherd": """
        .--.
       /    \\
      | ^  ^ |
       \\  -  /
        '---'
         |
         |
        /|\\
       / | \\
      /  |  \\
     '   |   '
         |
        / \\
       /   \\
      '     '
""",
    
    "chalice": """
        \\   /
         \\ /
          Y
         /|\\
        / | \\
       |  |  |
       |  |  |
        \\ | /
         \\|/
          |
         /|\\
        /___\\
""",
    
    "small_cross": """
      |
    --+--
      |
""",
    
    "trinity": """
        △
       /|\\
      / | \\
     /  |  \\
    /   |   \\
   /_   |   _\\
     \\ | /
      \\|/
       ▽
""",
    
    "wheat": """
      ∘∘∘
     ∘∘∘∘∘
    ∘∘∘∘∘∘∘
     ∘∘∘∘∘
      ∘∘∘
       |
       |
       |
       |
""",
    
    "grapes": """
        ∘
       ∘∘∘
      ∘∘∘∘∘
     ∘∘∘∘∘∘∘
      ∘∘∘∘∘
       ∘∘∘
        ∘
        |
       /|\\
      / | \\
""",
    
    "olive_branch": """
       ∘   ∘
      ∘ \\ / ∘
     ∘   |   ∘
      ∘ / \\ ∘
       ∘   ∘
         |
         |
""",
    
    "anchor": """
       .--.
      /    \\
     |  --  |
      \\    /
       '--'
        ||
        ||
      .-||-.
     /  ||  \\
    |   ||   |
     \\ /  \\ /
      '    '
""",
    
    "scrolls": """
    ┌─────────────┐
    │             │
    │   HOLY      │
    │             │
    │   WORD      │
    │             │
    └─────────────┘
      │         │
      │         │
      └─────────┘
"""
}

# Themed ASCII art sets
THEMED_SETS = {
    "simple": ["simple_cross", "small_cross", "alpha_omega"],
    "decorative": ["praying_hands", "cross", "dove", "open_book"],
    "symbolic": ["heart", "lamb", "fish", "star"],
    "liturgical": ["candle", "bible", "crown", "chalice"],
    "nature": ["wheat", "grapes", "olive_branch"],
    "traditional": ["shepherd", "trinity", "anchor", "scrolls"],
}

def get_ascii_art(name: str) -> Optional[str]:
    """Get ASCII art by name."""
    return ASCII_ART.get(name)

def get_random_ascii_art() -> str:
    """Get a random ASCII art."""
    import random
    return random.choice(list(ASCII_ART.values()))

def get_themed_ascii_art(theme: str = "simple") -> str:
    """Get ASCII art from a specific theme."""
    import random
    theme_arts = THEMED_SETS.get(theme, THEMED_SETS["simple"])
    art_name = random.choice(theme_arts)
    return ASCII_ART[art_name]

def display_welcome_screen(console: Console) -> None:
    """Display welcome screen with ASCII art."""
    welcome_art = get_ascii_art("welcome")
    
    # Create a panel with the welcome art
    welcome_panel = Panel(
        Align.center(Text(welcome_art, style="bold cyan")),
        title="[bold yellow]Welcome to Bible CLI[/bold yellow]",
        border_style="bright_blue"
    )
    
    console.print(welcome_panel)
    console.print()

def display_ascii_art(console: Console, name: str, title: Optional[str] = None) -> None:
    """Display ASCII art with optional title."""
    art = get_ascii_art(name)
    if not art:
        return
    
    if title:
        art_panel = Panel(
            Align.center(Text(art, style="bold green")),
            title=f"[bold]{title}[/bold]",
            border_style="green"
        )
    else:
        art_panel = Panel(
            Align.center(Text(art, style="bold green")),
            border_style="green"
        )
    
    console.print(art_panel)

def get_verse_decoration(verse_theme: str = "default") -> str:
    """Get decorative ASCII art for verse display."""
    decorations = {
        "default": "simple_cross",
        "love": "heart",
        "peace": "dove",
        "wisdom": "bible",
        "faith": "cross",
        "hope": "anchor",
        "joy": "star",
        "christmas": "star",
        "easter": "cross",
        "harvest": "wheat",
        "communion": "chalice",
        "baptism": "dove",
        "prayer": "praying_hands",
        "shepherd": "shepherd",
        "trinity": "trinity",
        "nature": "olive_branch",
        "celebration": "crown",
    }
    
    art_name = decorations.get(verse_theme, "simple_cross")
    return ASCII_ART[art_name]

def create_verse_frame(verse_text: str, reference: str, decoration: str = "simple_cross") -> str:
    """Create a framed verse with ASCII art decoration."""
    art = get_ascii_art(decoration)
    if not art:
        art = get_ascii_art("simple_cross")
    
    # Create the frame
    frame_content = f"""
{art}

{reference}

"{verse_text}"
"""
    
    return frame_content

def list_available_art() -> Dict[str, list]:
    """List all available ASCII art by category."""
    return {
        "all": list(ASCII_ART.keys()),
        "themed": THEMED_SETS,
    }

def get_art_preview(name: str) -> str:
    """Get a preview of ASCII art (first few lines)."""
    art = get_ascii_art(name)
    if not art:
        return "Art not found"
    
    lines = art.strip().split('\n')
    preview_lines = lines[:5]  # Show first 5 lines
    preview = '\n'.join(preview_lines)
    
    if len(lines) > 5:
        preview += "\n... (truncated)"
    
    return preview