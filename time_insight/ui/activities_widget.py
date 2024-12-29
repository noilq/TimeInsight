from datetime import datetime
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QScrollArea, QLabel
)
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import ApplicationActivity
from time_insight.log import log_to_console

class ActivitiesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: white;")
        
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
                for activity in activities:
                    activity_info = f"Activity id: {activity.id}, " \
                                    f"Application id: {activity.application_id}, " \
                                    f"Window name: {activity.window_name}, " \
                                    f"Add info: {activity.additional_info}, " \
                                    f"Start time: {activity.session_start}, " \
                                    f"End Time: {activity.session_end}, " \
                                    f"Duration: {activity.duration}"
                    label = QLabel(activity_info, self)
                    self.layout.addWidget(label)
            else:
                no_data_label = QLabel("No application activities found.", self)
                self.layout.addWidget(no_data_label)

        except RuntimeError as e:
            error_label = QLabel(f"Error loading data: {str(e)}", self)
            self.layout.addWidget(error_label)

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