from datetime import datetime, timedelta
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QScrollArea,  QLabel
)
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import ApplicationActivity, Application
from time_insight.log import log_to_console

class ApplicationsWidget(QWidget):
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

        self.load_applications(QDate.currentDate()) 

    def load_applications(self, target_date):
        try:
            activities = self.get_activities_from_database(target_date)

            with Session(engine) as session:
                applications = {app.id: app for app in session.query(Application).all()}

                if activities:
                    total_time = timedelta()

                    app_time_map = {}
                    for activity in activities:
                        duration = activity.session_end - activity.session_start
                        app_time_map[activity.application_id] = app_time_map.get(activity.application_id, timedelta()) + duration
                        total_time += duration

                    sorted_app_time = sorted(app_time_map.items(), key=lambda x: x[1], reverse=True)

                    for app_id, time_spent in sorted_app_time:
                        app = applications.get(app_id)
                        if app:
                            percentage = (time_spent / total_time * 100) if total_time.total_seconds() > 0 else 0
                            app_info = (
                                f"Application name: {app.name}, "
                                f"Time spent: {time_spent}, "
                                f"Percentage: {percentage:.2f}%"
                            )
                            label = QLabel(app_info, self)
                            self.layout.addWidget(label)

                    if not app_time_map:
                        no_data_label = QLabel("No application activities found.", self)
                        self.layout.addWidget(no_data_label)
                else:
                    no_data_label = QLabel("No application activities found.", self)
                    self.layout.addWidget(no_data_label)

        except Exception as e:
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
        
    def update_applications(self, target_date):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.layout.update()
        self.load_applications(target_date)