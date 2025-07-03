import sys
import time
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QComboBox, QPushButton, 
                             QLabel, QSystemTrayIcon, QMenu, QAction, QMessageBox,
                             QSplitter, QGroupBox, QCheckBox, QSpinBox, QFrame,
                             QGridLayout, QTabWidget)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor

from config import ConfigManager
from directories import MacroDirectoryManager
from lua_manager import LuaScriptManager
from keyboard_scanner import KeyboardScanner
from keyboard_monitor import KeyboardMonitorThread
from models import KeyboardDevice


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()


        self.config_manager = ConfigManager()
        self.dir_manager = MacroDirectoryManager()
        self.config_dir, self.keys_dir = self.dir_manager.setup_directories()
        self.script_manager = LuaScriptManager(self.keys_dir, self.config_manager.get_script_timeout())
        self.keyboard_scanner = KeyboardScanner()
        self.monitor_thread = None
        
        # Start minimized if enabled
        if self.config_manager.should_start_minimized():
            QTimer.singleShot(0, self.hide)

        self.init_ui()
        self.init_tray()
        self.load_keyboards()
        
        # Auto-select last keyboard if enabled
        if self.config_manager.should_auto_select():
            self.auto_select_keyboard()
        
        # Auto-start monitoring if enabled
        if self.config_manager.should_auto_start_monitoring():
            QTimer.singleShot(1000, self.try_auto_start_monitoring)


    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("MacroTinyKeyB - Keyboard Macro System")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Keyboard Selection Section
        keyboard_group = QGroupBox("Keyboard Selection")
        keyboard_layout = QGridLayout(keyboard_group)
        
        keyboard_layout.addWidget(QLabel("Select Keyboard:"), 0, 0)
        self.keyboard_combo = QComboBox()
        self.keyboard_combo.setMinimumWidth(400)
        keyboard_layout.addWidget(self.keyboard_combo, 0, 1, 1, 2)
        
        self.refresh_btn = QPushButton("Refresh List")
        self.refresh_btn.clicked.connect(self.load_keyboards)
        keyboard_layout.addWidget(self.refresh_btn, 0, 3)
        
        keyboard_layout.setColumnStretch(1, 1)
        main_layout.addWidget(keyboard_group)
        
        # Settings Section
        settings_group = QGroupBox("Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Row 1
        self.auto_select_cb = QCheckBox("Auto-select last keyboard")
        self.auto_select_cb.setChecked(self.config_manager.should_auto_select())
        self.auto_select_cb.toggled.connect(self.config_manager.set_auto_select)
        settings_layout.addWidget(self.auto_select_cb, 0, 0)
        
        self.auto_start_cb = QCheckBox("Auto-start monitoring")
        self.auto_start_cb.setChecked(self.config_manager.should_auto_start_monitoring())
        self.auto_start_cb.toggled.connect(self.config_manager.set_auto_start_monitoring)
        settings_layout.addWidget(self.auto_start_cb, 0, 1)

        self.start_minimized_cb = QCheckBox("Start minimized")
        self.start_minimized_cb.setChecked(self.config_manager.should_start_minimized())
        self.start_minimized_cb.toggled.connect(self.config_manager.set_start_minimized)
        settings_layout.addWidget(self.start_minimized_cb, 0, 2)
        
        # Row 2
        self.minimize_tray_cb = QCheckBox("Minimize to tray")
        self.minimize_tray_cb.setChecked(self.config_manager.should_minimize_to_tray())
        self.minimize_tray_cb.toggled.connect(self.config_manager.set_minimize_to_tray)
        settings_layout.addWidget(self.minimize_tray_cb, 1, 0)
        
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Script timeout (seconds):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(self.config_manager.get_script_timeout())
        self.timeout_spin.valueChanged.connect(self.on_timeout_changed)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        
        timeout_widget = QWidget()
        timeout_widget.setLayout(timeout_layout)
        settings_layout.addWidget(timeout_widget, 1, 1)
        
        settings_layout.setColumnStretch(0, 1)
        settings_layout.setColumnStretch(1, 1)
        main_layout.addWidget(settings_group)
        
        # Control Section
        control_group = QGroupBox("Control")
        control_layout = QHBoxLayout(control_group)
        
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)
        self.start_btn.setMinimumHeight(35)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(35)
        control_layout.addWidget(self.stop_btn)
        
        control_layout.addStretch()
        
        self.open_scripts_btn = QPushButton("Open Scripts Folder")
        self.open_scripts_btn.clicked.connect(self.open_scripts_folder)
        self.open_scripts_btn.setMinimumHeight(35)
        control_layout.addWidget(self.open_scripts_btn)
        
        self.open_config_btn = QPushButton("Open Config Folder")
        self.open_config_btn.clicked.connect(self.open_config_folder)
        self.open_config_btn.setMinimumHeight(35)
        control_layout.addWidget(self.open_config_btn)
        
        main_layout.addWidget(control_group)
        
        # Logs Section using Tabs
        logs_tabs = QTabWidget()
        
        # Key Press Log Tab
        key_log_widget = QWidget()
        key_log_layout = QVBoxLayout(key_log_widget)
        key_log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.key_log = QTextEdit()
        self.key_log.setFont(QFont("Courier", 9))
        key_log_layout.addWidget(self.key_log)
        
        logs_tabs.addTab(key_log_widget, "Key Presses")
        
        # System Log Tab
        system_log_widget = QWidget()
        system_log_layout = QVBoxLayout(system_log_widget)
        system_log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.system_log = QTextEdit()
        self.system_log.setFont(QFont("Courier", 9))
        system_log_layout.addWidget(self.system_log)
        
        logs_tabs.addTab(system_log_widget, "System Messages")
        
        main_layout.addWidget(logs_tabs)
        
        # Status Bar
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready - Select a keyboard and click 'Start Monitoring'")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        main_layout.addWidget(status_frame)
    
    def init_tray(self):
        """Initialize system tray."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self, "System Tray", "System tray is not available on this system.")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(64, 128, 255))
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "M")
        painter.end()
        
        self.tray_icon.setIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("MacroTinyKeyB")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        
        # Alternative: Set context menu to appear on left click too
        # This forces the context menu to show on any click
        self.tray_icon.setContextMenu(tray_menu)
        
        self.tray_icon.show()
    
    def load_keyboards(self):
        """Load available keyboards into combo box."""
        keyboards = self.keyboard_scanner.find_keyboards()
        self.keyboard_combo.clear()
        
        if not keyboards:
            self.keyboard_combo.addItem("No keyboards found")
            self.log_system_message("No keyboards found. Check permissions.", "warning")
            return
        
        for keyboard in keyboards:
            self.keyboard_combo.addItem(f"{keyboard.name} ({keyboard.path})", keyboard)
        
        self.log_system_message(f"Found {len(keyboards)} keyboard(s)", "info")
    
    def auto_select_keyboard(self):
        """Auto-select the last used keyboard if available."""
        last_keyboard = self.config_manager.get_last_keyboard()
        if not last_keyboard:
            return
        
        if not self.keyboard_scanner.is_keyboard_available(last_keyboard):
            self.log_system_message("Last used keyboard is no longer available", "warning")
            return
        
        # Find and select the keyboard in combo box
        for i in range(self.keyboard_combo.count()):
            keyboard = self.keyboard_combo.itemData(i)
            if keyboard and keyboard.path == last_keyboard.path:
                self.keyboard_combo.setCurrentIndex(i)
                self.log_system_message(f"Auto-selected: {last_keyboard.name}", "info")
                break
    
    def try_auto_start_monitoring(self):
        """Try to auto-start monitoring if a keyboard is selected."""
        if self.keyboard_combo.currentData() is not None:
            self.start_monitoring()
            self.log_system_message("Auto-started monitoring", "info")
    
    def start_monitoring(self):
        """Start keyboard monitoring."""
        if self.keyboard_combo.currentData() is None:
            QMessageBox.warning(self, "No Keyboard", "Please select a keyboard first.")
            return
        
        keyboard = self.keyboard_combo.currentData()
        self.config_manager.set_last_keyboard(keyboard)
        
        # Update script manager timeout
        self.script_manager.timeout = self.config_manager.get_script_timeout()
        
        self.monitor_thread = KeyboardMonitorThread(keyboard.path, self.script_manager)
        self.monitor_thread.key_pressed.connect(self.on_key_pressed)
        self.monitor_thread.device_disconnected.connect(self.on_device_disconnected)
        self.monitor_thread.log_message.connect(self.log_system_message)
        self.monitor_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.keyboard_combo.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.status_label.setText(f"Monitoring: {keyboard.name}")
        
        self.log_system_message(f"Started monitoring: {keyboard.name}", "info")
    
    def stop_monitoring(self):
        """Stop keyboard monitoring."""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait(2000)  # Wait up to 2 seconds
            self.monitor_thread = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.keyboard_combo.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.status_label.setText("Monitoring stopped")
        
        self.log_system_message("Monitoring stopped", "info")
    
    def on_key_pressed(self, keycode: str, filename: str, success: bool, output: str):
        """Handle key press events."""
        status = "SUCCESS" if success else "FAILED"
        self.key_log.append(f"[{status}] {keycode} -> {filename}.lua")
        
        if output.strip():
            self.system_log.append(f"[{filename}] {output}")
        
        # Auto-scroll
        self.key_log.moveCursor(self.key_log.textCursor().End)
        self.system_log.moveCursor(self.system_log.textCursor().End)
    
    def on_device_disconnected(self):
        """Handle device disconnection."""
        self.stop_monitoring()
        QMessageBox.warning(self, "Device Disconnected", "The keyboard was disconnected!")
        self.log_system_message("Keyboard disconnected", "error")
    
    def on_timeout_changed(self, value: int):
        """Handle timeout setting change."""
        self.config_manager.set_script_timeout(value)
        if hasattr(self, 'script_manager'):
            self.script_manager.timeout = value
    
    def open_scripts_folder(self):
        """Open the scripts folder in file manager."""
        subprocess.run(['xdg-open', str(self.keys_dir)])
    
    def open_config_folder(self):
        """Open the config folder in file manager."""
        subprocess.run(['xdg-open', str(self.config_dir)])
    
    def log_system_message(self, message: str, level: str = "info"):
        """Log a system message."""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {"info": "INFO", "warning": "WARNING", "error": "ERROR"}.get(level, "INFO")
        self.system_log.append(f"[{timestamp}] {prefix}: {message}")
        self.system_log.moveCursor(self.system_log.textCursor().End)
    
    def show_window(self):
        """Show the main window."""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
        elif reason == QSystemTrayIcon.Trigger:  # Left click
            # Alternative: Show window on left click, menu on right click
            self.show_window()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.config_manager.should_minimize_to_tray() and self.tray_icon.isVisible():
            QMessageBox.information(
                self, "MacroTinyKeyB",
                "The application will keep running in the system tray. "
                "To terminate the program, choose 'Quit' from the context menu."
            )
            self.hide()
            event.ignore()
        else:
            self.quit_application()
    
    def quit_application(self):
        """Quit the application."""
        self.stop_monitoring()
        QApplication.quit()