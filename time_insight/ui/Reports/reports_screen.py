from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)

from time_insight.ui.Stats.bottom_widget import BottomWidget
from time_insight.ui.Stats.top_widget import TopWidget

from time_insight.logging.logger import logger

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        logger.info("Initializing reports screen UI.")