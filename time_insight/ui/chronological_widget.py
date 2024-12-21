from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QLabel
)
from time_insight.log import log_to_console

class ChronologicalGraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        
        label = QLabel("", self)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)  