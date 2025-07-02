import evdev
from typing import List
from models import KeyboardDevice

class KeyboardScanner:
    """Scans for available keyboard devices."""
    
    @staticmethod
    def find_keyboards() -> List[KeyboardDevice]:
        """Find all available keyboard devices."""
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        keyboards = []
        
        for device in devices:
            try:
                capabilities = device.capabilities()
                if evdev.ecodes.EV_KEY in capabilities:
                    keys = capabilities[evdev.ecodes.EV_KEY]
                    # Check if standard keys are present
                    if evdev.ecodes.KEY_A in keys and evdev.ecodes.KEY_SPACE in keys:
                        keyboards.append(KeyboardDevice(device.path, device.name))
            except OSError:
                # Device not available - skip
                continue
        
        return keyboards
    
    @staticmethod
    def is_keyboard_available(keyboard: KeyboardDevice) -> bool:
        """Check if a specific keyboard is still available."""
        try:
            device = evdev.InputDevice(keyboard.path)
            capabilities = device.capabilities()
            return evdev.ecodes.EV_KEY in capabilities
        except (OSError, FileNotFoundError):
            return False