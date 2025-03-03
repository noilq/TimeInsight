from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel
)

from time_insight.ui.Main.activities_widget import ActivitiesWidget
from time_insight.ui.Main.applications_widget import ApplicationsWidget
from time_insight.ui.Main.header_widget import HeaderWidget
from time_insight.ui.Main.chronological_widget import ChronologicalGraphWidget

from time_insight.logging.logger import logger

class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        #timer for updating widgets data
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(100000)    #100 every seconds
        self.update_timer.timeout.connect(self.update_widgets)
        self.update_timer.start()

    def init_ui(self):
        """
        Initialize UI of main screen
        """

        #create layout
        layout = QVBoxLayout(self)

        #create header widget
        header_widget = self.create_header()
        layout.addWidget(header_widget)

        #create timeline widget
        self.timeline_widget = ChronologicalGraphWidget()
        layout.addWidget(self.timeline_widget)

        #create splitter
        splitter = self.create_splitter()
        
        #add splitter to layout
        layout.addWidget(splitter)

        #set stretch
        layout.setStretch(0, 1) #header
        layout.setStretch(1, 5) #timeline
        layout.setStretch(2, 5) #splitter

        #set layout
        self.setLayout(layout)

        #connect signals
        self.connect_signals()  #update widgets on date change

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        self.header_left = HeaderWidget()   #date selection widget
        self.header_center = QLabel("Header cent")
        self.header_right = QLabel("Header right")

        header_layout.addWidget(self.header_left, 1)
        header_layout.addWidget(self.header_center, 2)
        header_layout.addWidget(self.header_right, 1)

        return header_widget
    
    def create_splitter(self):
        #create splitter
        splitter = QSplitter(Qt.Horizontal)

        #create widgets
        self.activities_widget = ActivitiesWidget()
        self.activities_widget.setMinimumSize(300, 100)

        self.applications_widget = ApplicationsWidget(self.timeline_widget, self.activities_widget)
        self.applications_widget.setMinimumSize(300, 100)

        #add widgets to splitter
        splitter.addWidget(self.applications_widget)
        splitter.addWidget(self.activities_widget)

        #turn off collapsible
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([300, 500])

        return splitter
    
    def connect_signals(self):
        """
        Connect signals to header widget for date change event
        """
        self.header_left.date_changed_signal.connect(self.on_date_changed)

    def on_date_changed(self, selected_date):
        """
        Update widgets data when date is changed
        """
        self.activities_widget.update_activities(selected_date)
        self.applications_widget.update_applications(selected_date)
        self.timeline_widget.draw_timeline_graph(selected_date)

    def update_widgets(self):
        """
        Update widgets data
        """
        #check if window is active and visible
        if self.isActiveWindow() and self.isVisible():
            selected_date = self.header_left.get_selected_date()    #get selected date
            self.activities_widget.update_activities(selected_date)   #update activities widget
            self.applications_widget.update_applications(selected_date)  #update applications widget
            #self.timeline_widget.draw_timeline_graph(selected_date) do not #update timeline widget