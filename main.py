#!/usr/bin/env python3
"""
MacroTinyKeyB - Keyboard Macro System with System Tray

A PyQt5-based system that intercepts keyboard input and executes corresponding Lua scripts
for each key press. Features a GUI that can minimize to system tray.

Features:
- GUI interface with system tray support
- Blocks selected keyboard from other applications
- Auto-creates Lua scripts for each key press
- Executes custom macros immediately
- Real-time log display
- Configuration management

Author: Enhanced with PyQt5 GUI
License: MIT
"""

import sys
import subprocess # Added this import
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon

from gui import MainWindow
import os

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    
    # Check if user is in 'input' group
    if os.name == 'posix': # Only relevant for Unix-like systems
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
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
