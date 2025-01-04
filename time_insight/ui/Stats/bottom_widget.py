from datetime import datetime

import plotly.express as px

from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtWidgets import (
            QVBoxLayout, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
)
from time_insight.log import log_to_console

from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity, UserSession, UserSessionType

class BottomWidget(QFrame):
    def __init__(self):
        super().__init__()
        
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: none;")

        self.layout = QVBoxLayout(self)

        self.web_view = QWebEngineView(self)  #init web view
        self.layout.addWidget(self.web_view)

        self.setLayout(self.layout)

    def draw_chart(self, data):
        """Draw chart with data."""
        self.clear_widget()
        
        self.web_view = QWebEngineView(self)  #init web view
        self.layout.addWidget(self.web_view)

        #create plotly chart
        fig = px.bar(data.reset_index(), x='Start time', y='Duration')
        fig.update_layout(xaxis_title="Date", yaxis_title="Duration (hours)")
        
        #convert plotly chart to html
        html = fig.to_html(include_plotlyjs='cdn')
        #display html in web view
        self.web_view.setHtml(html)

    def draw_table(self, data, order="DESC"):
        """Draw table with data."""
        self.clear_widget()

        table = QTableWidget()
        table.setRowCount(len(data))
        table.setColumnCount(len(data.columns))
        table.setHorizontalHeaderLabels(data.columns)

        #fill table with data
        for row_idx, row in enumerate(data.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        #auto resize columns
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #add table to layout
        self.layout.addWidget(table)

    def clear_widget(self):
        """Clear all child widgets."""
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
   

    def get_programs_data(self, start_date, end_date, count):
        """
        Get all programs and activities data within specified time range.
        
        :param: start_date: datetime, start date of the range
        :param: end_date: datetime, end date of the range
        :param: count: int, not implemented
        """
        try:
            start_of_day = datetime(start_date.year(), start_date.month(), start_date.day(), 0, 0, 0)
            end_of_day = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)

            with Session(engine) as session:
                programs = session.query(
                    Application.id.label("Application ID"),
                    Application.name.label("Name"),
                    Application.desc.label("Description"),
                    Application.enrollment_date.label("Enrollment Date"),
                    Application.path.label("Path"),
                    ApplicationActivity.id.label("Activity ID"),
                    ApplicationActivity.window_name.label("Window Name"),
                    ApplicationActivity.additional_info.label("Additional Info"),
                    ApplicationActivity.session_start.label("Start Time"),
                    ApplicationActivity.session_end.label("End Time"),
                    ApplicationActivity.duration.label("Duration"),
                ).join(ApplicationActivity, Application.id == ApplicationActivity.application_id) \
                    .filter(
                        ApplicationActivity.session_start >= start_of_day,
                        ApplicationActivity.session_end <= end_of_day
                    ).all()

                programs_data = []
                for program in programs:
                    programs_data.append({
                        "Application ID": program[0],
                        "Name": program[1],
                        "Description": program[2],
                        "Enrollment Date": program[3],
                        "Path": program[4],
                        "Activity ID": program[5],
                        "Window Name": program[6],
                        "Additional Info": program[7],
                        "Start Time": program[8],
                        "End Time": program[9],
                        "Duration": program[10],
                    })

                return programs_data
        except Exception as e:
            log_to_console(f"Error fetching programs data: {str(e)}")

    def get_activity_data(self, start_date, end_date, count):
        """
        Get all activities data within specified time range.
        
        :param: start_date: datetime, start date of the range
        :param: end_date: datetime, end date of the range
        :param: count: int, not implemented
        """
        try:
            start_of_day = datetime(start_date.year(), start_date.month(), start_date.day(), 0, 0, 0)
            end_of_day = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)

            with Session(engine) as session:
                activities = session.query(
                    ApplicationActivity.id.label("Activity ID"),
                    ApplicationActivity.application_id.label("Application ID"),
                    ApplicationActivity.window_name.label("Window Name"),
                    ApplicationActivity.additional_info.label("Additional Info"),
                    ApplicationActivity.session_start.label("Start Time"),
                    ApplicationActivity.session_end.label("End Time"),
                    ApplicationActivity.duration.label("Duration"),
                    Application.name.label("Program Name"),
                    Application.desc.label("Program Description"),
                    Application.enrollment_date.label("Enrollment Date"),
                    Application.path.label("Program Path")
                ).join(
                    Application, Application.id == ApplicationActivity.application_id
                ).filter(
                    ApplicationActivity.session_start >= start_of_day,
                    ApplicationActivity.session_end <= end_of_day
                ).all()

                activity_data = []
                for activity in activities:
                    activity_data.append({
                        "Activity ID": activity[0],
                        "Application ID": activity[1],
                        "Window Name": activity[2],
                        "Additional Info": activity[3],
                        "Start Time": activity[4],
                        "End Time": activity[5],
                        "Duration": activity[6],
                        "Program Name": activity[7],
                        "Program Description": activity[8],
                        "Enrollment Date": activity[9],
                        "Program Path": activity[10]
                    })

                return activity_data
        except Exception as e:
            log_to_console(f"Error fetching activity data: {str(e)}")
    
    def get_computer_usage_data(self, start_date, end_date):
        """
        Get all user sessions data within specified time range.
        
        :param: start_date: datetime, start date of the range
        :param: end_date: datetime, end date of the range
        """
        try:
            start_of_day = datetime(start_date.year(), start_date.month(), start_date.day(), 0, 0, 0)
            end_of_day = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)

            with Session(engine) as session:
                user_sessions = session.query(UserSession, UserSessionType.name).join(
                    UserSessionType, UserSession.user_session_type_id == UserSessionType.id
                ).filter(
                    UserSession.session_start >= start_of_day,
                    UserSession.session_end <= end_of_day
                ).all()

                if user_sessions:
                    user_sessions_data = []
                    for session, session_type_name in user_sessions:
                        session_data = {
                            "Session id": session.id,
                            "Session type name": session_type_name,
                            "Start time": session.session_start,
                            "End time": session.session_end,
                            "Duration": session.duration
                        }
                        user_sessions_data.append(session_data)
                else:
                    log_to_console("No user sessions found.")

            return user_sessions_data
        except Exception as e:
            log_to_console(f"Error accessing database: {str(e)}")