import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
            QApplication, QWidget, QDesktopWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
            QSplitter, QSystemTrayIcon, QMenu, QLabel, QStackedWidget
)
from PyQt5.QtGui import QIcon
from time_insight.log import log_to_console

from time_insight.ui.activities_widget import ActivitiesWidget
from time_insight.ui.applications_widget import ApplicationsWidget
from time_insight.ui.chronological_widget import ChronologicalGraphWidget
from time_insight.ui.header_widget import HeaderWidget

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

        header_widget = self.create_header()
        main_layout.addWidget(header_widget)

        self.timeline_widget = ChronologicalGraphWidget()
        main_layout.addWidget(self.timeline_widget)

        splitter = self.create_splitter()
        main_layout.addWidget(splitter)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 5)
        main_layout.setStretch(2, 5)

        central_widget.setLayout(main_layout)

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        self.header_left = HeaderWidget()
        self.header_center = QLabel("Header cent")
        self.header_right = QLabel("Header right")

        self.header_left.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        self.header_center.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        self.header_right.setStyleSheet("border: 2px solid black; background-color: lightgray;")

        header_layout.addWidget(self.header_left, 1)
        header_layout.addWidget(self.header_center, 2)
        header_layout.addWidget(self.header_right, 1)

        return header_widget
    
    def create_splitter(self):
        splitter = QSplitter(Qt.Horizontal)

        self.applications_widget = ApplicationsWidget()
        self.applications_widget.setMinimumSize(300, 100)

        self.activities_widget = ActivitiesWidget()
        self.activities_widget.setMinimumSize(300, 100)

        splitter.addWidget(self.applications_widget)
        splitter.addWidget(self.activities_widget)

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([300, 500])

        return splitter

    def connect_signals(self):
        self.header_left.date_changed_signal.connect(self.on_date_changed)



    def on_date_changed(self, selected_date):
        self.activities_widget.update_activities(selected_date)

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