from datetime import datetime
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import ApplicationActivity
from time_insight.log import log_to_console

class ActivitiesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: none;")
        
        self.layout = QVBoxLayout()

        scroll_area_widget = QWidget()
        scroll_area_widget.setLayout(self.layout)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_area_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.load_application_activities(QDate.currentDate())

    def load_application_activities(self, target_date):
        try:
            activities = self.get_activities_from_database(target_date)
            
            if activities:
                self.draw_table(activities)
            else:
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

    def get_activities_from_database(self, target_date):
        if isinstance(target_date, QDate):
            target_date = target_date.toPyDate()

        start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_of_day = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

        try:
            with Session(engine) as session:
                activities = session.query(ApplicationActivity).filter(
                    ApplicationActivity.session_start >= start_of_day,
                    ApplicationActivity.session_end <= end_of_day
                ).all()
                return activities
        except Exception as e:
            raise RuntimeError(f"Error accessing database: {str(e)}")


    def update_activities(self, target_date):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.layout.update()
        self.load_application_activities(target_date)