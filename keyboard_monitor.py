import evdev
from select import select
from PyQt6.QtCore import QThread, pyqtSignal
from lua_manager import LuaScriptManager
from key_mapping import KeyMapper
import os  # Import os for opening files


class KeyboardMonitorThread(QThread):
    """Thread for monitoring keyboard events."""
    
    key_pressed = pyqtSignal(str, str, bool, str)  # keycode, filename, success, output
    device_disconnected = pyqtSignal()
    log_message = pyqtSignal(str, str)  # message, level (info, warning, error)
    
    def __init__(self, device_path: str, script_manager: LuaScriptManager):
        super().__init__()
        self.device_path = device_path
        self.script_manager = script_manager
        self.device = None
        self.running = False
        self.pressed_keys = set()  # To keep track of currently pressed keys
    
    def run(self):
        """Main monitoring loop."""
        try:
            self.device = evdev.InputDevice(self.device_path)
            try:
                self.device.grab()
                self.log_message.emit("Keyboard successfully grabbed", "info")
            except OSError:
                self.log_message.emit("Could not grab keyboard - other programs may still receive events", "warning")
            
            self.running = True
            
            while self.running:
                r, w, x = select([self.device], [], [], 0.1)
                if r:
                    try:
                        events = self.device.read()
                        for event in events:
                            if event.type == evdev.ecodes.EV_KEY:
                                key_event = evdev.categorize(event)
                                if key_event.keystate == evdev.KeyEvent.key_down:
                                    self.pressed_keys.add(key_event.keycode)
                                    self._process_key(key_event.keycode)
                                elif key_event.keystate == evdev.KeyEvent.key_up:
                                    self.pressed_keys.discard(key_event.keycode)
                    except OSError:
                        self.device_disconnected.emit()
                        break
                        
        except Exception as e:
            self.log_message.emit(f"Error in keyboard monitoring: {e}", "error")
    
    def _process_key(self, keycode: str):
        """Process a single key press."""
        
        # If only RCTRL is pressed, do nothing.
        if keycode == 'KEY_RIGHTCTRL' and len(self.pressed_keys) == 1:
            return
        filename = KeyMapper.keycode_to_filename(keycode)
        script_path = self.script_manager.keys_dir / f"{filename}.lua"
        
        # Check for rctrl + other key combination
        if 'KEY_RIGHTCTRL' in self.pressed_keys and keycode != 'KEY_RIGHTCTRL':
            self.log_message.emit(f"Right Control + {filename} pressed. Opening {filename}.lua for editing.", "info")
            self.script_manager.open_lua_file_in_editor(script_path)
            return  # Do not execute the script, just open the file
        
        if not script_path.exists():
            self.script_manager.create_default_script(filename, script_path)
            self.log_message.emit(f"Created new script: {filename}.lua", "info")
        
        success, output = self.script_manager.execute_script(script_path, filename)
        self.key_pressed.emit(keycode, filename, success, output)
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.device:
            try:
                self.device.ungrab()
            except:
                pass
