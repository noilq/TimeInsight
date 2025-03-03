from datetime import datetime, timedelta
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QScrollArea,  QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
)
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import ApplicationActivity, Application

from time_insight.settings import get_setting
from time_insight.logging.logger import logger

class ApplicationsWidget(QWidget):
    def __init__(self, chronological_widget, activity_widget):
        super().__init__()
        #self.setStyleSheet("background-color: none;")
        self.chronological_widget = chronological_widget
        self.activity_widget = activity_widget

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
        
        #load activities + apps and draw table
        self.load_applications(QDate.currentDate()) 

        self.date = QDate.currentDate()

    def load_applications(self, target_date):
        """
        Load application activities from database and draw table.

        :param target_date: QDate object representing the target date.
        """
        self.date = target_date

        try:
            #get activities 
            activities = self.get_activities_from_database(target_date)
            
            with Session(engine) as session:
                #get all apps
                applications = {app.id: app for app in session.query(Application).all()}

                if activities:
                    total_time = timedelta() #total time spent on all apps

                    app_time_map = {} #dict to store time spent on each app
                    for activity in activities:
                        #calculate duration of each activity
                        duration = activity.session_end - activity.session_start
                        #add duration to app_time_map
                        app_time_map[activity.application_id] = app_time_map.get(activity.application_id, timedelta()) + duration
                        #add duration to total_time
                        total_time += duration

                    #sort app by time spent in desc order
                    sorted_app_time = sorted(app_time_map.items(), key=lambda x: x[1], reverse=True)

                    #draw table
                    self.draw_table(sorted_app_time, applications, total_time)
                else:
                    #show message if no data found
                    no_data_label = QLabel("No application activities found.", self)
                    self.layout.addWidget(no_data_label)

        except Exception as e:
            error_label = QLabel(f"Error loading data: {str(e)}", self)
            self.layout.addWidget(error_label)

    def draw_table(self, sorted_app_time, applications, total_time):
        """
        Draw a table with application data.

        :param sorted_app_time: List of tuples (app_id, time_spent) sorted by time spent.
        :param applications: Dict of applications.
        :param total_time: Total time spent on all apps (timedelta obj).
        """
        #create table
        table = QTableWidget()
        table.setRowCount(len(sorted_app_time))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Select", "Application Name", "Time Spent", "Percentage"])

        #hide counter column
        table.verticalHeader().setVisible(False)

        #fill table with data
        for row_idx, (app_id, time_spent) in enumerate(sorted_app_time):
            app = applications.get(app_id)
            if app:
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.on_checkbox_state_changed)
                table.setCellWidget(row_idx, 0, checkbox)

                #calculate percentage of time spent
                percentage = (time_spent / total_time * 100) if total_time.total_seconds() > 0 else 0
                #assign data to table
                table.setItem(row_idx, 1, QTableWidgetItem(app.name))
                table.setItem(row_idx, 2, QTableWidgetItem(str(time_spent)))
                table.setItem(row_idx, 3, QTableWidgetItem(f"{percentage:.2f}%"))

        #auto resize columns
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #add table to layout
        self.layout.addWidget(table)

    def get_activities_from_database(self, target_date):
        """
        Get application activities from database for the given date.

        :param target_date: QDate object representing the target date.
        :return: List of ApplicationActivity objects.
        """
        #convert QDate to py datetime
        if isinstance(target_date, QDate):
            target_date = target_date.toPyDate()

        #get start and end of the day
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
        """
        Clears the layout and reloads the applications data for the given date.

        :param target_date: QDate object representing the target date.
        """
        #clear layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.layout.update()
        #load activities and draw table
        self.load_applications(target_date)

    def on_checkbox_state_changed(self, state):
        selected_apps = self.get_selected_applications()
        print("Selected applications:", selected_apps)  

        self.chronological_widget.draw_timeline_graph(self.date, selected_apps)
        self.activity_widget.update_activities(self.date, selected_apps)

    def get_selected_applications(self):
        selected_apps = []
        table = self.layout.itemAt(0).widget()
        if isinstance(table, QTableWidget):
            for row in range(table.rowCount()):
                checkbox = table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    app_name = table.item(row, 1).text()
                    selected_apps.append(app_name)
        return selected_apps