from datetime import datetime
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import ApplicationActivity, Application

from time_insight.time_converter import datetime_from_utc_to_local
from time_insight.logging.logger import logger

from time_insight.ui.language_manager import language_manager 
from time_insight.translations import t

class ActivitiesWidget(QWidget):
    def __init__(self):
        super().__init__()
        #self.setStyleSheet("background-color: none;")
        
        self.layout = QVBoxLayout()

        #create scroll area widget
        scroll_area_widget = QWidget()
        scroll_area_widget.setLayout(self.layout)

        #add scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_area_widget)

        #add scroll area to main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        #load activities and draw table
        self.load_application_activities(QDate.currentDate())

    def retranslate_ui(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QTableWidget):
                widget.setHorizontalHeaderLabels([
                    t("window_name"),
                    t("additional_info"),
                    t("start_time"),
                    t("end_time"),
                    t("duration")
                ])
            elif isinstance(widget, QLabel):
                if "No application activities found." in widget.text():
                    widget.setText(t("no_activities_message"))
                elif "Error loading data:" in widget.text():
                    pass

    def load_application_activities(self, target_date, program_filter=None):
        """
        Load activities from database and draw table.

        :param target_date: QDate object representing the target date.
        """
        try:
            #get activities
            activities = self.get_activities_from_database(target_date, program_filter)
            
            if activities:
                #convert UTC datetimes to local timezone
                for activity in activities:
                    activity.session_start = datetime_from_utc_to_local(activity.session_start)
                    activity.session_end = datetime_from_utc_to_local(activity.session_end)
                
                #draw table
                self.draw_table(activities)
            else:
                #show message if no activities found
                no_data_label = QLabel("No application activities found.", self)
                self.layout.addWidget(no_data_label)

        except RuntimeError as e:
            error_label = QLabel(f"Error loading data: {str(e)}", self)
            self.layout.addWidget(error_label)

    def draw_table(self, activities):
        """Draw table with activities data."""
        #create table
        table = QTableWidget()
        table.setRowCount(len(activities))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            #"Activity ID", "Application ID", 
            "Window Name", "Additional Info", "Start Time", "End Time", "Duration"
        ])

        #hide counter column
        table.verticalHeader().setVisible(False)

        #fill table with data
        for row_idx, activity in enumerate(activities):
            #table.setItem(row_idx, 0, QTableWidgetItem(str(activity.id)))
            #table.setItem(row_idx, 1, QTableWidgetItem(str(activity.application_id)))
            table.setItem(row_idx, 0, QTableWidgetItem(activity.window_name))
            table.setItem(row_idx, 1, QTableWidgetItem(activity.additional_info))
            table.setItem(row_idx, 2, QTableWidgetItem(str(activity.session_start)))
            table.setItem(row_idx, 3, QTableWidgetItem(str(activity.session_end)))
            table.setItem(row_idx, 4, QTableWidgetItem(str(activity.duration)))

        #auto resize columns
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #add table to layout
        self.layout.addWidget(table)

    def get_activities_from_database(self, target_date, program_filter=None):
        #convert QDate to py datetime
        if isinstance(target_date, QDate):
            target_date = target_date.toPyDate()

        #get start and end of the day
        start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

        try:
            with Session(engine) as session:
                activities = session.query(ApplicationActivity).join(Application).filter(
                    ApplicationActivity.session_start >= start_of_day,
                    ApplicationActivity.session_end <= end_of_day
                )
                
                #filter programs
                if program_filter:
                    activities = activities.filter(Application.name.in_(program_filter))

                return activities.all()
        except Exception as e:
            raise RuntimeError(f"Error accessing database: {str(e)}")


    def update_activities(self, target_date, program_filter=None):
        #clear layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.layout.update()
        #load activities
        self.load_application_activities(target_date, program_filter)