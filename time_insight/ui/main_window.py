import sys
import os
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from PyQt5.QtWidgets import (
            QApplication, QWidget, QDesktopWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
            QSplitter, QSystemTrayIcon, QMenu, QLabel, QStackedWidget, QPushButton
)
from PyQt5.QtGui import QIcon
from time_insight.log import log_to_console

from time_insight.ui.activities_widget import ActivitiesWidget
from time_insight.ui.applications_widget import ApplicationsWidget
from time_insight.ui.chronological_widget import ChronologicalGraphWidget
from time_insight.ui.header_widget import HeaderWidget
from time_insight.ui.navigation_widget import NavigationWidget

from time_insight.ui.main_screen import MainScreen
from time_insight.ui.Stats.stats_screen import StatsScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TimeInsight")
        self.setGeometry(*self.GetWindowGeometry())
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.setWindowIcon(QIcon(self.icon_path))
        
        self.init_tray()
        self.init_ui()
        self.connect_signals()

    def init_tray(self):
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
        self.options_screen = QWidget()
        self.options_screen.setStyleSheet("background-color: white;")

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.stats_screen)
        self.stacked_widget.addWidget(self.options_screen)

        main_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_layout)

    def on_navigation(self, screen_name):
        if screen_name == "main":
            self.stacked_widget.setCurrentIndex(0)
        elif screen_name == "stats":
            self.stacked_widget.setCurrentIndex(1)
        elif screen_name == "options":
            self.stacked_widget.setCurrentIndex(2)

    def connect_signals(self):
        self.navigation_widget.navigation_signal.connect(self.on_navigation)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)    

    window = MainWindow()
    window.show()

    app.exec()
    
    sys.exit(app.exec_())