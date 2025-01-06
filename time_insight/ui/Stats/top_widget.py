import pandas as pd

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from time_insight.ui.Stats.bottom_widget import BottomWidget

from time_insight.time_converter import datetime_from_utc_to_local
from time_insight.log import log_to_console


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

        #simulate the "This month" and "Activity" selection
        self.dropdown_time_interval.setCurrentIndex(self.dropdown_time_interval.findText("This month"))
        self.dropdown_stats_type.setCurrentIndex(self.dropdown_stats_type.findText("Activity"))

    def handle_dropdown_change(self):
        #get selected values
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
                data = self.bottom_widget.get_programs_data(start_date, end_date, 50)

                #convert data to df
                df = pd.DataFrame(data)
                #group by program and sum duration
                df = df.groupby(["Name", "Description", "Path", "Enrollment Date"], as_index=False)["Duration"].sum()

                #convert to local time
                df["Enrollment Date"] = df["Enrollment Date"].apply(datetime_from_utc_to_local)
                #format duration to HH:MM:SS
                df["Duration"] = df["Duration"].apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")

                #sort by duration
                df = df.sort_values(by="Duration", ascending=False)
                #rename columns
                df = df.rename(columns={"Name": "Program Name", "Description": "Program Description", "Path": "Program Path", "Duration": "Total Hours"})

                self.bottom_widget.draw_table(df)

            case "Activity":
                data = self.bottom_widget.get_activity_data(start_date, end_date, 50)

                #convert data to df
                df = pd.DataFrame(data)
                #group by activity and sum duration
                df = df.groupby(
                ["Window Name", "Program Name", "Enrollment Date", "Program Path", "Start Time", "End Time"],as_index=False).agg({"Duration": "sum"})
                
                #convert to local time
                df["Enrollment Date"] = df["Enrollment Date"].apply(datetime_from_utc_to_local)
                df["Start Time"] = df["Start Time"].apply(datetime_from_utc_to_local)
                df["End Time"] = df["End Time"].apply(datetime_from_utc_to_local)

                #format duration to HH:MM:SS
                df["Duration"] = df["Duration"].apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")
                #sort by start time
                df = df.sort_values(by="Start Time", ascending=False)

                self.bottom_widget.draw_table(df)

            case "Computer usage":
                data = self.bottom_widget.get_computer_usage_data(start_date, end_date)

                #convert data to df
                df = pd.DataFrame(data)
                df["Start time"] = pd.to_datetime(df["Start time"])
                #filter only active sessions
                #group by date (day) and sum duration in hours
                df = df[df["Session type name"]=="Active"].groupby(df["Start time"].dt.floor('d'))["Duration"].sum() / 3600
                #df.index = df.index.strftime("%d %b %Y")

                #self.bottom_widget.draw_table(data, "ASC")
                if not df.empty:
                    self.bottom_widget.draw_chart(df)
                else:
                    log_to_console("No data to plot")
            case _:
                log_to_console("Unknown dropdown selected")