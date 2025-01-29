import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
            QApplication, QWidget, QDesktopWidget, QMainWindow, QVBoxLayout, QSystemTrayIcon, QMenu, QStackedWidget
)
from PyQt5.QtGui import QIcon, QPalette, QColor

from time_insight.ui.navigation_widget import NavigationWidget

from time_insight.ui.Main.main_screen import MainScreen
from time_insight.ui.Stats.stats_screen import StatsScreen
from time_insight.ui.Settings.settings_screen import SettingsScreen

from time_insight.settings import get_setting
from time_insight.logging.logger import logger

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

        # Options Screen
        self.settings_screen = SettingsScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.stats_screen)
        self.stacked_widget.addWidget(self.settings_screen)

        main_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_layout)

    def on_navigation(self, screen_name):
        #navigate to screen
        if screen_name == "main":
            self.stacked_widget.setCurrentIndex(0)
        elif screen_name == "stats":
            self.stacked_widget.setCurrentIndex(1)
        elif screen_name == "settings":
            self.stacked_widget.setCurrentIndex(2)

    def on_ui_update(self):
        print("bla")
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