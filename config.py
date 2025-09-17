from typing import Optional
from PyQt6.QtCore import QSettings
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

    def has_shown_minimize_to_tray_message(self) -> bool:
        """Check if the minimize to tray message has been shown."""
        return self.settings.value("shown_minimize_to_tray_message", False, type=bool)

    def set_shown_minimize_to_tray_message(self, shown: bool) -> None:
        """Set whether the minimize to tray message has been shown."""
        self.settings.setValue("shown_minimize_to_tray_message", shown)

    def should_start_minimized(self) -> bool:
        """Check if the application should start minimized."""
        return self.settings.value("start_minimized", False, type=bool)

    def set_start_minimized(self, enabled: bool) -> None:
        """Set the preference for starting the application minimized."""
        self.settings.setValue("start_minimized", enabled)

    def get_editor_path(self) -> str:
        """Get the configured editor path."""
        return self.settings.value("editor_path", "")

    def set_editor_path(self, editor_path: str) -> None:
        """Set the editor path."""
        self.settings.setValue("editor_path", editor_path)


    # Extension for ConfigManager class - add these methods to your existing ConfigManager

    def get_editor_path(self) -> str:
        """Get the configured text editor path."""
        return self.settings.value("editor_path", "", type=str)

    def set_editor_path(self, path: str):
        """Set the text editor path."""
        self.settings.setValue("editor_path", path)
        self.settings.sync()