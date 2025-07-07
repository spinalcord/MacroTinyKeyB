import subprocess
from pathlib import Path
from typing import Tuple
import lupa
import os
import sys # Import sys for platform detection
from clipboard_utils import get_clipboard_content, set_clipboard_content

class LuaScriptManager:
    """Handles creation and execution of Lua scripts."""
    
    def __init__(self, keys_directory: Path, timeout: int = 5):
        self.keys_dir = keys_directory
        self.timeout = timeout
        self.lua_available = self._check_lua_installation()
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.lua_output_buffer = []
        self.lua.execute(f"package.path = package.path .. ';{os.getcwd()}/?.lua'")
        self.lua.globals().get_clipboard = get_clipboard_content
        self.lua.globals().set_clipboard = set_clipboard_content
        self.lua.globals().python_print = self._lua_print_redirect
        self.lua.globals().insert_text = self._lua_insert_text
        self.lua.globals().run_command = self._lua_run_command
        self.lua.globals().run_command_async = self._lua_run_command_async
    
    def _check_lua_installation(self) -> bool:
        """Check if Lua is installed on the system."""
        try:
            result = subprocess.run(['lua', '-v'], capture_output=True, text=True)
            return True
        except FileNotFoundError:
            return False
    
    def create_default_script(self, key_name: str, script_path: Path) -> None:
        """Create a default Lua script template for a key."""
        default_script = f'''-- Macro script for key: {key_name}
-- This script is executed when '{key_name}' is pressed

print("Key {key_name} was pressed!")

-- Insert your macro code here
-- Examples:

-- os.execute("echo 'Hello from {key_name}'")
-- os.execute("notify-send 'Macro' 'Key {key_name} pressed'")
-- os.execute("xdotool type 'Hello World'")
-- os.execute("xdotool key ctrl+alt+t")
-- os.execute("sleep 2")
-- For more complex actions:
-- os.execute("firefox https://google.com")
-- os.execute("code ~/Documents")

-- To run a command asynchronously (non-blocking):
-- run_command_async("konsole")
-- run_command_async("firefox https://google.com")

-- Clipboard operations:
-- To get clipboard content:
-- local clipboard_content = get_clipboard()
-- print("Clipboard content: " .. clipboard_content)

-- To set clipboard content:
-- set_clipboard("Hello from Lua!")
-- print("Clipboard content set to 'Hello from Lua!'")

-- To insert text at cursor position (requires xdotool):
-- insert_text("This text will be typed at the cursor.")

-- To run a shell command and get its output:
-- local output = run_command("echo Hello from Lua!")
-- print("Command output: " .. output)
'''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(default_script)
    
    def _lua_print_redirect(self, *args):
        """Redirects Lua print statements to a Python buffer."""
        self.lua_output_buffer.append(" ".join(str(arg) for arg in args))

    def _lua_insert_text(self, text: str):
        """
        Backs up clipboard, inserts text, triggers paste, and restores clipboard.
        Requires xdotool to be installed for paste command.
        """
        original_clipboard = get_clipboard_content()
        set_clipboard_content(text)
        
        # Trigger paste command (Ctrl+V) using xdotool
        # This assumes xdotool is installed on the system.
        try:
            subprocess.run(['xdotool', 'key', 'control+v'], check=True)
            self.lua_output_buffer.append(f"Inserted text: '{text[:50]}...'")
        except FileNotFoundError:
            self.lua_output_buffer.append("Error: xdotool not found. Cannot trigger paste.")
        except subprocess.CalledProcessError as e:
            self.lua_output_buffer.append(f"Error triggering paste with xdotool: {e}")
        finally:
            # Restore original clipboard content
            set_clipboard_content(original_clipboard)

    def _lua_run_command(self, command_string: str) -> str:
        """
        Executes a shell command and returns its stdout.
        """
        try:
            result = subprocess.run(
                command_string,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.timeout
            )
            self.lua_output_buffer.append(f"Command executed: '{command_string}'")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.lua_output_buffer.append(f"Error executing command '{command_string}': {e.stderr.strip()}")
            return f"Error: {e.stderr.strip()}"
        except subprocess.TimeoutExpired:
            self.lua_output_buffer.append(f"Command '{command_string}' timed out after {self.timeout} seconds.")
            return f"Error: Command timed out."
        except Exception as e:
            self.lua_output_buffer.append(f"Unexpected error running command '{command_string}': {e}")
            return f"Error: {e}"

    def _lua_run_command_async(self, command_string: str):
        """
        Executes a shell command in a non-blocking way.
        """
        try:
            subprocess.Popen(command_string, shell=True)
            self.lua_output_buffer.append(f"Async command launched: '{command_string}'")
        except Exception as e:
            self.lua_output_buffer.append(f"Error launching async command '{command_string}': {e}")

    def execute_script(self, script_path: Path, key_name: str) -> Tuple[bool, str]:
        """Execute a Lua script and return success status and output."""
        if not self.lua_available:
            return False, "Lua not installed"
        
        self.lua_output_buffer = [] # Clear buffer before each execution
        
        try:
            # Override Lua's print function to use our Python redirect
            self.lua.execute("function print(...) python_print(...) end")
            self.lua.execute(script_path.read_text())
            
            output = "\n".join(self.lua_output_buffer)
            return True, f"Script executed successfully via Lupa.\nOutput:\n{output}"
            
        except Exception as e:
            return False, f"Error executing script via Lupa: {e}"

    def open_lua_file_in_editor(self, script_path: Path):
        """Opens the specified Lua file in the default text editor."""
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(script_path)
            elif sys.platform == 'darwin':  # For macOS
                subprocess.Popen(['open', script_path])
            else:  # For Linux and other POSIX systems
                subprocess.Popen(['xdg-open', script_path])
            self.lua_output_buffer.append(f"Opened {script_path} in default editor.")
        except FileNotFoundError:
            self.lua_output_buffer.append(f"Error: Could not find a suitable application to open {script_path}.")
        except Exception as e:
            self.lua_output_buffer.append(f"Error opening {script_path}: {e}")