from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)

from time_insight.ui.Stats.bottom_widget import BottomWidget
from time_insight.ui.Stats.top_widget import TopWidget

from time_insight.logging.logger import logger

from time_insight.ui.language_manager import language_manager 
from time_insight.translations import t

class StatsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def retranslate_ui(self):
        self.bottom_widget.retranslate_ui()
        self.top_widget.retranslate_ui()

    def init_ui(self):
        logger.info("Initializing main screen UI.")

        #main layout
        main_layout = QVBoxLayout()

        #create top and botton widgets
        self.bottom_widget = BottomWidget()
        self.top_widget = TopWidget(self.bottom_widget)

        #add widgets to the main layout
        main_layout.addWidget(self.top_widget)
        main_layout.addWidget(self.bottom_widget, stretch=1)     #more space for bottom widget

        self.setLayout(main_layout)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    stats_screen = StatsScreen()
    stats_screen.show()
    sys.exit(app.exec_())
