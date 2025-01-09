from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)

from time_insight.ui.Stats.bottom_widget import BottomWidget
from time_insight.ui.Stats.top_widget import TopWidget

from time_insight.logging.logger import logger

class StatsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        logger.info("Initializing main screen UI.")

        #main layout
        main_layout = QVBoxLayout()

        #create top and botton widgets
        bottom_widget = BottomWidget()
        top_widget = TopWidget(bottom_widget)

        #add widgets to the main layout
        main_layout.addWidget(top_widget)
        main_layout.addWidget(bottom_widget, stretch=1)     #more space for bottom widget

        self.setLayout(main_layout)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    stats_screen = StatsScreen()
    stats_screen.show()
    sys.exit(app.exec_())
