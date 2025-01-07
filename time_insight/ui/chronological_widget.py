from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QVBoxLayout, QSlider, QWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush, QWheelEvent, QPainter, QPen
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from time_insight.data.get_data import get_computer_usage_data, get_programs_data
from time_insight.time_converter import datetime_from_utc_to_local

from time_insight.log import log_to_console

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
        
        df_activities = pd.DataFrame(get_programs_data(target_date, target_date, 50))
        df_user_sessions = pd.DataFrame(get_computer_usage_data(target_date, target_date))

        if df_activities.empty or df_user_sessions.empty:
            self.web_view.setHtml("")  
            return

        #activities
        df_activities["Start Time"] = pd.to_datetime(df_activities["Start Time"])
        df_activities["End Time"] = pd.to_datetime(df_activities["End Time"])
        
        #convert utc time to local
        df_activities["Start Time"] = df_activities["Start Time"].apply(datetime_from_utc_to_local)
        df_activities["End Time"] = df_activities["End Time"].apply(datetime_from_utc_to_local)

        #set color
        df_activities["Color"] = df_activities["Enrollment Date"].apply(self.get_color)
        df_activities["Category"] = "Activities"

        df_activities["Tooltip"] = (
            "Program Name: " + df_activities["Name"] + "<br>" +
            "Window Name: " + df_activities["Window Name"] + "<br>" +
            "Time interval: " + df_activities["Start Time"].dt.strftime("%H:%M:%S") + " - " + df_activities["End Time"].dt.strftime("%H:%M:%S") + "<br>" +
            "Duration: " + df_activities["Duration"].astype(str)
        )

        #user sessions
        df_user_sessions["Start Time"] = pd.to_datetime(df_user_sessions["Start Time"])
        df_user_sessions["End Time"] = pd.to_datetime(df_user_sessions["End Time"])

        #convert utc time to local
        df_user_sessions["Start Time"] = df_user_sessions["Start Time"].apply(datetime_from_utc_to_local)
        df_user_sessions["End Time"] = df_user_sessions["End Time"].apply(datetime_from_utc_to_local)

        #remove all sleep sessions
        df_user_sessions = df_user_sessions[df_user_sessions["Session type name"] == "Active"]

        #set color
        df_user_sessions["Color"] = "#1fd655"
        df_user_sessions["Category"] = "User Sessions"

        df_user_sessions["Tooltip"] = (
            df_user_sessions["Session type name"] + " session" + "<br>" +
            "Time interval: " + df_user_sessions["Start Time"].dt.strftime("%H:%M:%S") + " - " + df_user_sessions["End Time"].dt.strftime("%H:%M:%S") + "<br>" +
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
            color_discrete_map='identity',  #fix user session color
            hover_data={"Tooltip": True, "Category": False, "Start Time": False, "End Time": False, "Color": False}
        )
        
        fig.update_layout(showlegend=False)
        fig.update_yaxes(autorange="reversed")
        fig.update_yaxes(title_text="") #hide "Category" title

        html = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html)

    def get_color(self, enrollment_date):
        enrollment_number = int(enrollment_date.timestamp())

        random.seed(enrollment_number)
        
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        return f"rgb({r}, {g}, {b})"