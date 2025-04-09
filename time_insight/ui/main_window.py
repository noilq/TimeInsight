import sys
import os
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
            QApplication, QWidget, QDesktopWidget, QMainWindow, QVBoxLayout, QSystemTrayIcon, QMenu, QStackedWidget, 
            QPushButton, QAction, QLabel
)
from PyQt5.QtGui import QIcon, QPalette, QColor

from time_insight.ui.navigation_widget import NavigationWidget

from time_insight.ui.Main.main_screen import MainScreen
from time_insight.ui.Stats.stats_screen import StatsScreen
from time_insight.ui.Reports.reports_screen import ReportsScreen
from time_insight.ui.Settings.settings_screen import SettingsScreen

from apscheduler.schedulers.background import BackgroundScheduler

from time_insight.settings import get_setting
from time_insight.logging.logger import logger

from time_insight.tracker.tracker import stop_tracker_for_minutes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TimeInsight")
        self.setGeometry(*self.GetWindowGeometry())
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        if getattr(sys, 'frozen', False):
            #builded app
            self.icon_path = os.path.join(sys._MEIPASS, 'time_insight', 'ui', 'icon.png')
        else:
            #not builded app
            self.icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')

        self.setWindowIcon(QIcon(self.icon_path))
        
        self.init_tray()
        self.init_styles()
        self.init_ui()
        self.connect_signals()

    def init_tray(self):
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon(self.icon_path))

            self.tray_menu = QMenu()
            open_action = self.tray_menu.addAction("Open")
            open_action.triggered.connect(self.show)
            quit_action = self.tray_menu.addAction("Exit")
            quit_action.triggered.connect(self.close_app)
            self.tray_icon.setContextMenu(self.tray_menu)
            self.tray_icon.show()

            self.tray_icon.activated.connect(self.on_tray_icon_click)

            logger.info("Tray initialization completed successfully.")
        except Exception as e:
            logger.error("Error during tray initialization.")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        self.navigation_widget = NavigationWidget()
        main_layout.addWidget(self.navigation_widget)

        # Stacked widget for screens
        self.stacked_widget = QStackedWidget()

        # Main Screen
        self.main_screen = MainScreen()

        # Stats Screen
        self.stats_screen = StatsScreen()

        # Reports Screen
        self.reports_screen = ReportsScreen()

        # Options Screen
        self.settings_screen = SettingsScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.stats_screen)
        self.stacked_widget.addWidget(self.reports_screen)
        self.stacked_widget.addWidget(self.settings_screen)

        main_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_layout)

        
        #turn off/on tray tracking button
        self.tracker_button = QPushButton(self)
        self.tracker_button.setToolTip("Tracker is currently running.")
        self.tracker_button.setFixedSize(20, 20)
        self.tracker_button.setStyleSheet("border-radius: 10px; background-color: #5CFF5C; color: white;")##ff4444
        self.tracker_button.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.update_tracker_button_position()
        self.tracker_button.clicked.connect(self.on_tracker_button_click)
        self.tracker_button.show()

    def resizeEvent(self, event):
        self.update_tracker_button_position()
        super().resizeEvent(event)

    def update_tracker_button_position(self):
        margin = 10
        x = self.width() - self.tracker_button.width() - margin
        y = self.height() - self.tracker_button.height() - margin - self.menuBar().height()
        self.tracker_button.move(x, y)

    def on_tracker_button_click(self):
        context_menu = QMenu(self)
        
        fakeaction = QAction("Turn off tracker for", self)
        action1 = QAction("30 minutes", self)
        action2 = QAction("1 hour", self)
        action3 = QAction("4 hours", self)
        action4 = QAction("Until next app start", self)

        action1.triggered.connect(lambda: self.turn_off_tracker(0.1))
        action2.triggered.connect(lambda: self.turn_off_tracker(60))
        action3.triggered.connect(lambda: self.turn_off_tracker(240))
        action4.triggered.connect(lambda: self.turn_off_tracker(2147483647))
        
        context_menu.addAction(fakeaction)
        context_menu.addAction(action1)
        context_menu.addAction(action2)
        context_menu.addAction(action3)
        context_menu.addAction(action4)
        
        context_menu.exec_(self.tracker_button.mapToGlobal(self.tracker_button.rect().topLeft()))

    def turn_off_tracker(self, minutes):
        self.tracker_button.setStyleSheet("border-radius: 10px; background-color: #ff4444; color: white;")
        self.tracker_button.setToolTip("Tracker is currently stopped.")
        stop_tracker_for_minutes(minutes)

        QTimer.singleShot(int(minutes * 60 * 1000), self.on_tracker_running)
    
    def on_tracker_running(self):
        self.tracker_button.setStyleSheet("border-radius: 10px; background-color: #5CFF5C; color: white;")
        self.tracker_button.setToolTip("Tracker is currently running.")

    def on_navigation(self, screen_name):
        #navigate to screen
        if screen_name == "main":
            self.stacked_widget.setCurrentIndex(0)
        elif screen_name == "stats":
            self.stacked_widget.setCurrentIndex(1)
        elif screen_name == "settings":
            self.stacked_widget.setCurrentIndex(3)
        elif screen_name == "reports":
            self.stacked_widget.setCurrentIndex(2)

    def on_ui_update(self, update_type):
        if update_type == "theme":
            logger.info("Updating UI.")
            self.init_styles()

    def connect_signals(self):
        """
        Connect signals, change screen on navigation
        """
        self.navigation_widget.navigation_signal.connect(self.on_navigation)
        self.settings_screen.update_signal.connect(self.on_ui_update)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        """
        self.tray_icon.showMessage(
            "",
            "",
            QSystemTrayIcon.Information,
            2000
        )"""

    def on_tray_icon_click(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def close_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def showEvent(self, event):
        #ubrat posle pokaza okna show on hueta
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.showNormal()

    def GetWindowGeometry(self):
        screen_resolution = QDesktopWidget().screenGeometry()

        width = screen_resolution.width()
        height = screen_resolution.height()

        x = round(width / 4.6)
        y = round(height / 9.7)

        width = round(width / 1.9)
        height = round(height/1.4)

        return x, y, width, height

    def init_styles(self):
        main_color = get_setting("theme_main_color")
        secondary_color = get_setting("theme_secondary_color")
        third_color = get_setting("theme_third_color")
        text_color = get_setting("theme_text_color")
        self.color_theme = f"""
            QWidget {{
                background-color: {main_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {secondary_color};
                color: {text_color};
                border: 1px solid {third_color};
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {third_color};
            }}
            QLineEdit {{
                background-color: {main_color};
                color: {text_color};
                border: 1px solid {third_color};
                padding: 5px;
            }}
            QLabel {{
                color: {text_color};
            }}

            QTableWidget {{
                background-color: {main_color};
                border: 1px solid {third_color};
                gridline-color: {third_color};
            }}
            QHeaderView::section {{
                background-color: {secondary_color};
                color: {text_color};
                padding: 4px;
                border: 1px solid {third_color};
            }}

            QCalendarWidget {{
                background-color: {main_color};
                border: 1px solid {third_color};
            }}
            QCalendarWidget QToolButton {{
                background-color: {secondary_color};
                border: none;
                color: {text_color};
                padding: 5px;
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {main_color};
                selection-background-color: {third_color};
            }}

            QDateEdit {{
                background-color: {main_color};
                color: {text_color};
                border: 1px solid {third_color};
                border-radius: 5px;
                padding: 2px;
            }}
        """

        self.setStyleSheet(self.color_theme)
         
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(main_color))
        palette.setColor(QPalette.Button, QColor(secondary_color))
        palette.setColor(QPalette.Highlight, QColor(third_color))
        palette.setColor(QPalette.WindowText, QColor(text_color))
        
        self.setPalette(palette)

    def update_ui(self):
        print("zalupa rock")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)    

    window = MainWindow()
    window.show()

    app.exec()
    
    sys.exit(app.exec_())