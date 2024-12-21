from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QScrollArea,  QLabel
)
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import Application
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

        self.load_applications() 

    def load_applications(self):
        try:
            with Session(engine) as session:
                applications = session.query(Application).all()
                
                if applications:
                    for application in applications:
                        application_info = f"Application id: {application.id}, " \
                                        f"Application name: {application.name}, " \
                                        f"Add info: {application.desc}, " \
                                        f"Path: {application.path}, " \
                                        f"Enrollment date: {application.enrollment_date}, "
                        label = QLabel(application_info, self)
                        self.layout.addWidget(label)
                else:
                    no_data_label = QLabel("No application activities found.", self)
                    self.layout.addWidget(no_data_label)

        except Exception as e:
            error_label = QLabel(f"Error loading data: {str(e)}", self)
            self.layout.addWidget(error_label)