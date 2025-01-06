from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QVBoxLayout, QSlider, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush, QWheelEvent, QPainter, QPen
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from time_insight.log import log_to_console

from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity, UserSession, UserSessionType
from datetime import datetime

import random

class ChronologicalGraphWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: none;")

        self.layout = QVBoxLayout(self)

        self.web_view = QWebEngineView()
        self.draw_timeline_graph(QDate.currentDate())

        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

    def draw_timeline_graph(self, target_date):

        df_activities = pd.DataFrame(self.get_programs_data(target_date, target_date, 50))
        df_user_sessions = pd.DataFrame(self.get_computer_usage_data(target_date, target_date))

        
        #activities
        df_activities["Start Time"] = pd.to_datetime(df_activities["Start Time"])
        df_activities["End Time"] = pd.to_datetime(df_activities["End Time"])

        df_activities["Tooltip"] = (
            "Program Name: " + df_activities["Name"] + "<br>" +
            "Window Name: " + df_activities["Window Name"] + "<br>" +
            "Time interval: " + df_activities["Start Time"].dt.strftime("%H:%M:%S") + " - " + df_activities["End Time"].dt.strftime("%H:%M:%S") + "<br>" +
            "Duration: " + df_activities["Duration"].astype(str)
        )

        #set color
        df_activities["Color"] = df_activities["Enrollment Date"].apply(self.get_color)
        df_activities["Category"] = "Activities"

        #user sessions
        df_user_sessions["Start Time"] = pd.to_datetime(df_user_sessions["Start Time"])
        df_user_sessions["End Time"] = pd.to_datetime(df_user_sessions["End Time"])

        #remove all sleep sessions
        df_user_sessions = df_user_sessions[df_user_sessions["Session type name"] != "Sleep"]
        #set color
        df_user_sessions["Color"] = "rgb(144, 238, 144)"
        df_user_sessions["Category"] = "User Sessions"

        df_user_sessions["Tooltip"] = (
            "Active session" + "<br>" +
            "Time interval: " + df_activities["Start Time"].dt.strftime("%H:%M:%S") + " - " + df_activities["End Time"].dt.strftime("%H:%M:%S") + "<br>" +
            "Duration: " + df_user_sessions["Duration"].astype(str)
        )

        #combine both dataframes
        df_combined = pd.concat([df_activities, df_user_sessions])

        fig = px.timeline(
            df_combined, 
            x_start="Start Time", 
            x_end="End Time", 
            y="Category",
            color="Color",
            hover_data={"Tooltip": True, "Category": False, "Start Time": False, "End Time": False, "Color": False}
        )
        
        fig.update_layout(showlegend=False)
        fig.update_yaxes(autorange="reversed")

        html = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html)

    def get_color(self, enrollment_date):
        enrollment_number = int(enrollment_date.timestamp())

        random.seed(enrollment_number)
        
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        return f"rgb({r}, {g}, {b})"

        

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
                            "Start Time": session.session_start,
                            "End Time": session.session_end,
                            "Duration": session.duration
                        }
                        user_sessions_data.append(session_data)
                else:
                    log_to_console("No user sessions found.")

            return user_sessions_data
        except Exception as e:
            log_to_console(f"Error accessing database: {str(e)}")