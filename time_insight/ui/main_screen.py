from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel
)
from time_insight.log import log_to_console

from time_insight.ui.activities_widget import ActivitiesWidget
from time_insight.ui.applications_widget import ApplicationsWidget
from time_insight.ui.header_widget import HeaderWidget
from time_insight.ui.chronological_widget import ChronologicalGraphWidget

class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        #timer for updating widgets data
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(30000)    #30 every seconds
        self.update_timer.timeout.connect(self.update_widgets)
        self.update_timer.start()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header_widget = self.create_header()
        layout.addWidget(header_widget)

        self.timeline_widget = ChronologicalGraphWidget()
        layout.addWidget(self.timeline_widget)

        splitter = self.create_splitter()
        
        layout.addWidget(splitter)

        layout.setStretch(0, 1)
        layout.setStretch(1, 5)
        layout.setStretch(2, 5)

        self.setLayout(layout)
        self.connect_signals()

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        self.header_left = HeaderWidget()
        self.header_center = QLabel("Header cent")
        self.header_right = QLabel("Header right")

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
        self.applications_widget.update_applications(selected_date)

    def update_widgets(self):
        #check if window is active and visible
        log_to_console(self.header_left.get_selected_date())
        if self.isActiveWindow() and self.isVisible():
            selected_date = self.header_left.get_selected_date()    #get selected date
            self.activities_widget.update_activities(selected_date)   #update activities widget
            self.applications_widget.update_applications(selected_date)  #update applications widget