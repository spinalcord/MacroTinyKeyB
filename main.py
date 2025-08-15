#!/usr/bin/env python3
"""
MacroTinyKeyB - Keyboard Macro System with System Tray

A PyQt6-based system that intercepts keyboard input and executes corresponding Lua scripts
for each key press. Features a GUI that can minimize to system tray.

Features:
- GUI interface with system tray support
- Single instance enforcement (prevents multiple launches)
- Blocks selected keyboard from other applications
- Auto-creates Lua scripts for each key press
- Executes custom macros immediately
- Real-time log display
- Configuration management

Author: Enhanced with PyQt6 GUI and Single Instance
License: MIT
"""

import sys
import subprocess
import os
import tempfile
import atexit
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QSystemTrayIcon

from gui import MainWindow

def is_already_running():
    """Check if another instance is already running."""
    lock_file = os.path.join(tempfile.gettempdir(), "MacroTinyKeyB.lock")
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            if os.name == 'posix':
                try:
                    os.kill(pid, 0)  # Check if process exists
                    return True
                except OSError:
                    # Process doesn't exist, remove stale lock file
                    os.remove(lock_file)
            else:
                # Windows - simple check
                import subprocess
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                if str(pid) in result.stdout:
                    return True
                else:
                    os.remove(lock_file)
        except:
            # Invalid lock file, remove it
            if os.path.exists(lock_file):
                os.remove(lock_file)
    
    # Create lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
    
    # Clean up on exit
    def cleanup():
        if os.path.exists(lock_file):
            os.remove(lock_file)
    atexit.register(cleanup)
    
    return False

def main():
    """Main entry point."""
    
    # Check if already running
    if is_already_running():
        # Show message and exit
        temp_app = QApplication(sys.argv)
        QMessageBox.warning(None, "MacroTinyKeyB", 
                           "MacroTinyKeyB is already running!\n\n"
                           "Please check the system tray for the icon.")
        sys.exit(1)
    
    # Create main application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Check if user is in 'input' group
    if os.name == 'posix':
        username = os.getenv('USER')
        if username:
            try:
                groups_output = subprocess.run(['groups', username], capture_output=True, text=True, check=True)
                if 'input' not in groups_output.stdout.split():
                    QMessageBox.critical(None, "Permission Error",
                                        f"User '{username}' is not in the 'input' group. "
                                        "Please run the following command in the terminal and restart the application:\n\n"
                                        f"sudo usermod -a -G input {username}\n\n"
                                        "You might need to log out and log back in for the changes to take effect.")
                    sys.exit(1)
            except FileNotFoundError:
                QMessageBox.warning(None, "Command Not Found",
                                    "The 'groups' command was not found. "
                                    "Cannot check group membership. Please ensure 'coreutils' is installed.")
            except subprocess.CalledProcessError as e:
                QMessageBox.warning(None, "Group Check Error",
                                    f"Error executing 'groups {username}': {e.stderr}")

    # Check for system tray availability
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray",
                            "System tray is not available on this system.")
        sys.exit(1)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
