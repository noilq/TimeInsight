from PyQt5.QtWidgets import (
    QGraphicsView, QVBoxLayout
)
from PyQt5.QtCore import QDate
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.express as px
import pandas as pd

from time_insight.data.get_data import get_computer_usage_data, get_programs_data
from time_insight.time_converter import datetime_from_utc_to_local

from time_insight.settings import get_setting
from time_insight.logging.logger import logger

import random

from time_insight.ui.language_manager import language_manager 
from time_insight.translations import t

class ChronologicalGraphWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        #self.setStyleSheet("background-color: none;")

        self.layout = QVBoxLayout(self)

        self.web_view = QWebEngineView()
        self.draw_timeline_graph(QDate.currentDate())

        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

    def draw_timeline_graph(self, target_date, program_filter=None):
        
        df_activities = pd.DataFrame(get_programs_data(target_date, target_date, 50))
        df_user_sessions = pd.DataFrame(get_computer_usage_data(target_date, target_date))

        if df_activities.empty or df_user_sessions.empty:
            self.web_view.setHtml("")
            return

        if program_filter:
            df_activities = df_activities[df_activities['Name'].isin(program_filter)]

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
            t("program_name") + ": " + df_activities["Name"] + "<br>" +
            t("window_name") + ": " + df_activities["Window Name"] + "<br>" +
            t("time_interval") + ": " + df_activities["Start Time"].dt.strftime("%H:%M:%S") + " - " + df_activities["End Time"].dt.strftime("%H:%M:%S") + "<br>" +
            t("duration") + ": " + df_activities["Duration"].astype(str)
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
        df_user_sessions["Color"] = "#1fd655"   #light green
        df_user_sessions["Category"] = "User Sessions"

        df_user_sessions["Tooltip"] = (
            df_user_sessions["Session type name"] + " " + t("session") + "<br>" +
            t("time_interval") + ": " + df_user_sessions["Start Time"].dt.strftime("%H:%M:%S") + " - " + df_user_sessions["End Time"].dt.strftime("%H:%M:%S") + "<br>" +
            t("duration") + ": " + df_user_sessions["Duration"].astype(str)
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

        fig.update_layout(
            showlegend=False,
            plot_bgcolor=get_setting("theme_secondary_color"),
            paper_bgcolor=get_setting("theme_main_color"),
            font=dict(color=get_setting("theme_text_color")),
            margin=dict(l=40, r=40, t=40, b=40),    #make graph bigger
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_yaxes(title_text="") #hide "Category" title

        html = fig.to_html(include_plotlyjs='cdn')

        #fill the gaps it html 
        html = html.replace(
            "<head>",
            f"<head><style>body {{ background-color: {get_setting("theme_main_color")}; margin: 0; padding: 0; }}</style>"
        )

        self.web_view.setHtml(html)

    def get_color(self, enrollment_date):
        enrollment_number = int(enrollment_date.timestamp())

        random.seed(enrollment_number)
        
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)

        return f"rgb({r}, {g}, {b})"

class ProgramList:
    def __init__(self):
        self.programs = []

    def add_program(self, program_name):
        if program_name not in self.programs:
            self.programs.append(program_name)

    def remove_program(self, program_name):
        if program_name in self.programs:
            self.programs.remove(program_name)
        else:
            logger.warning(f"Program {program_name} not found in the list.")

    def get_programs(self):
        return self.programs

program_list = ProgramList()