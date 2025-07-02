from pathlib import Path
from typing import Tuple

class MacroDirectoryManager:
    """Manages the creation and setup of macro directories."""
    
    def __init__(self, base_name: str = "MacroTinyKeyB"):
        self.base_name = base_name
        self.config_dir = Path.home() / ".config" / base_name
        self.keys_dir = self.config_dir / "scripts"
    
    def setup_directories(self) -> Tuple[Path, Path]:
        """Create necessary directories for the macro system."""
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        return self.config_dir, self.keys_dir
