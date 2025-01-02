import pandas as pd

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from time_insight.log import log_to_console

from time_insight.ui.Stats.bottom_widget import BottomWidget

class TopWidget(QWidget):
    def __init__(self, bottom_widget):
        super().__init__()

        self.bottom_widget = bottom_widget
        self.init_ui()

    def init_ui(self):
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignLeft)   #align all items to the left

        #label "From"
        from_label = QLabel("From")
        top_layout.addWidget(from_label)

        #date pick "From"
        self.from_date = QDateEdit()
        self.from_date.setDisplayFormat("dddd, d MMMM yyyy")
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-7))  #set default to 7 days before today
        self.from_date.dateChanged.connect(self.handle_dropdown_change)
        top_layout.addWidget(self.from_date)

        #label "To"
        to_label = QLabel("To")
        top_layout.addWidget(to_label)

        #date pick "To"
        self.to_date = QDateEdit()
        self.to_date.setDisplayFormat("dddd, d MMMM yyyy")
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())    #set default to today
        self.to_date.dateChanged.connect(self.handle_dropdown_change)
        top_layout.addWidget(self.to_date)

        #go to previous day btn
        self.left_button = QPushButton()
        self.left_button.setText("<")
        self.left_button.pressed.connect(self.handle_dropdown_change)
        top_layout.addWidget(self.left_button)

        #go to next day btn
        self.right_button = QPushButton()
        self.right_button.setText(">")
        self.right_button.pressed.connect(self.handle_dropdown_change)
        top_layout.addWidget(self.right_button)

        #time interval dropdown 
        self.dropdown_time_interval = QComboBox()
        self.dropdown_time_interval.addItems(["All", "Today", "This week", "This month", "This year", "Custom"])
        self.dropdown_time_interval.currentIndexChanged.connect(self.handle_dropdown_change)
        top_layout.addWidget(self.dropdown_time_interval)

        #stats type dropdown
        self.dropdown_stats_type = QComboBox()
        self.dropdown_stats_type.addItems(["Programs", "Activity", "Computer usage"])
        self.dropdown_stats_type.currentIndexChanged.connect(self.handle_dropdown_change)
        top_layout.addWidget(self.dropdown_stats_type)

        self.setLayout(top_layout)

    def handle_dropdown_change(self):
        time_interval = self.dropdown_time_interval.currentText()
        stats_type = self.dropdown_stats_type.currentText()
        
        start_date = None
        end_date = None

        match time_interval:
            case "All":
                log_to_console("All selected")
                start_date = QDate(2000, 1, 1)
                end_date = QDate.currentDate()
            case "Today":
                log_to_console("Today selected")
                start_date = QDate.currentDate()
                end_date = QDate.currentDate()
            case "This week":
                log_to_console("This week selected")
                start_date = QDate.currentDate().addDays(-QDate.currentDate().dayOfWeek())
                end_date = QDate.currentDate()
            case "This month":
                log_to_console("This month selected")
                start_date = QDate(QDate.currentDate().year(), QDate.currentDate().month(), 1)
                end_date = QDate.currentDate()
            case "This year":
                log_to_console("This year selected")
                start_date = QDate(QDate.currentDate().year(), 1, 1)
                end_date = QDate.currentDate()
            case "Custom":
                log_to_console("Custom selected")
                start_date = self.from_date.date()
                end_date = self.to_date.date()

                #check if start date is in the future
                if start_date > QDate.currentDate():
                    start_date = QDate.currentDate()    #set to today

                #check if end date is before start date
                if end_date < start_date:
                    end_date = start_date   #set end date to match start date
            case _:
                log_to_console("Unknown dropdown selected")

        

        match stats_type:
            case "Programs": 
                log_to_console("Programs selected")
            case "Activity":
                log_to_console("Activity selected")
                data = self.bottom_widget.get_computer_usage_data(start_date, end_date)

                df = pd.DataFrame(data)

                self.bottom_widget.draw_table(df)
            case "Computer usage":
                log_to_console("Computer usage selected")
                data = self.bottom_widget.get_computer_usage_data(start_date, end_date)

                df = pd.DataFrame(data)
                df["Start time"] = pd.to_datetime(df["Start time"])
                df = df[df["Session type name"]=="Active"].groupby(df["Start time"].dt.floor('d'))["Duration"].sum() / 3600
                df.index = df.index.strftime("%d %b %Y")

                #self.bottom_widget.draw_table(data, "ASC")
                if not df.empty:
                    self.bottom_widget.draw_chart(df)
                else:
                    log_to_console("No data to plot")
            case _:
                log_to_console("Unknown dropdown selected")