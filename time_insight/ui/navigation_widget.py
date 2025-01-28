from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
            QWidget, QHBoxLayout, QPushButton
)

from time_insight.logging.logger import logger

class NavigationWidget(QWidget):
    navigation_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.main_button = QPushButton("Main")
        self.stats_button = QPushButton("Stats")
        self.options_button = QPushButton("Settings")

        #emit signal with screen name
        self.main_button.clicked.connect(lambda: self.emit_signal("main"))
        self.stats_button.clicked.connect(lambda: self.emit_signal("stats"))
        self.options_button.clicked.connect(lambda: self.emit_signal("settings"))

        layout.addWidget(self.main_button)
        layout.addWidget(self.stats_button)
        layout.addWidget(self.options_button)

        self.setLayout(layout)

    def emit_signal(self, screen_name):
        self.navigation_signal.emit(screen_name)
        logger.info(f"Sreen changed to: {screen_name}.")