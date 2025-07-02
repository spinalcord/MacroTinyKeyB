from typing import Optional
from PyQt5.QtCore import QSettings
from models import KeyboardDevice

class ConfigManager:
    """Manages configuration using QSettings."""
    
    def __init__(self):
        self.settings = QSettings("MacroTinyKeyB", "MacroTinyKeyB")
    
    def get_last_keyboard(self) -> Optional[KeyboardDevice]:
        """Get the last selected keyboard if it exists."""
        path = self.settings.value("last_keyboard_path", None)
        name = self.settings.value("last_keyboard_name", None)
        
        if path and name:
            return KeyboardDevice(path=path, name=name)
        return None
    
    def set_last_keyboard(self, keyboard: KeyboardDevice) -> None:
        """Save the last selected keyboard."""
        self.settings.setValue("last_keyboard_path", keyboard.path)
        self.settings.setValue("last_keyboard_name", keyboard.name)
    
    def should_auto_select(self) -> bool:
        """Check if auto-selection is enabled."""
        return self.settings.value("auto_select_last", True, type=bool)
    
    def set_auto_select(self, enabled: bool) -> None:
        """Set auto-selection preference."""
        self.settings.setValue("auto_select_last", enabled)
    
    def should_auto_start_monitoring(self) -> bool:
        """Check if auto-start monitoring is enabled."""
        return self.settings.value("auto_start_monitoring", False, type=bool)
    
    def set_auto_start_monitoring(self, enabled: bool) -> None:
        """Set auto-start monitoring preference."""
        self.settings.setValue("auto_start_monitoring", enabled)
    
    def get_script_timeout(self) -> int:
        """Get the script execution timeout."""
        return self.settings.value("script_timeout", 5, type=int)
    
    def set_script_timeout(self, timeout: int) -> None:
        """Set script execution timeout."""
        self.settings.setValue("script_timeout", timeout)
    
    def should_minimize_to_tray(self) -> bool:
        """Check if minimize to tray is enabled."""
        return self.settings.value("minimize_to_tray", True, type=bool)
    
    def set_minimize_to_tray(self, enabled: bool) -> None:
        """Set minimize to tray preference."""
        self.settings.setValue("minimize_to_tray", enabled)