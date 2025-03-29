from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWebEngineWidgets import QWebEngineView     #type: ignore
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)

from time_insight.ui.Stats.bottom_widget import BottomWidget
from time_insight.ui.Stats.top_widget import TopWidget

import plotly.express as px      #type: ignore
import pandas as pd             #type: ignore
import random

from time_insight.data.get_data import get_activity_data, get_computer_usage_data, get_programs_data
from time_insight.time_converter import datetime_from_utc_to_local

from time_insight.settings import get_setting
from time_insight.logging.logger import logger

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        logger.info("Initializing reports screen UI.")

        self.layout = QVBoxLayout(self)

        self.web_view = QWebEngineView()

        self.report_type_combo_box = QComboBox()
        self.report_type_combo_box.addItems(["Daily", "Weekly", "Monthly"])
        self.report_type_combo_box.currentIndexChanged.connect(self.handle_dropdown_change)

        self.layout.addWidget(self.web_view)
        self.layout.addWidget(self.report_type_combo_box)

        self.setLayout(self.layout)




        
        data = get_programs_data(QDate(2025, 1, 1), QDate(2025, 3, 26), 50)
        
        if not data:
            logger.warning("Programs data is empty.")
            return
        
        #convert data to df
        df = pd.DataFrame(data)
        #group by program and sum duration
        df = df.groupby(["Name", "Description", "Path", "Enrollment Date"], as_index=False)["Duration"].sum()

        #convert to local time
        df["Enrollment Date"] = df["Enrollment Date"].apply(datetime_from_utc_to_local)

        #sort by duration before formating to string
        df = df.sort_values(by="Duration", ascending=False)
        #format duration to HH:MM:SS
        df["Total Hours"] = df["Duration"].apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")
        df["Duration in hours"] = df["Duration"] / 3600
        #apply color to each program
        df["Color"] = df["Enrollment Date"].apply(self.get_color)

        #shorten program name
        df["Name"] = df["Name"].str.slice(0, 20)
        
        df = df.sort_values(by="Duration", ascending=True)
        #rename columns
        df = df.rename(columns={"Name": "Program Name", "Description": "Program Description", "Path": "Program Path"})







        self.draw_programs_chart(df)
    
    def handle_dropdown_change(self):
        #get selected values
        report_type = self.report_type_combo_box.currentText()

        match report_type:
            case "Daily": 
                data = get_programs_data(start_date, end_date, 50)

                if not data:
                    logger.warning("Programs data is empty.")
                    return
                
                #convert data to df
                df = pd.DataFrame(data)
                #group by program and sum duration
                df = df.groupby(["Name", "Description", "Path", "Enrollment Date"], as_index=False)["Duration"].sum()

                #convert to local time
                df["Enrollment Date"] = df["Enrollment Date"].apply(datetime_from_utc_to_local)

                #sort by duration before formating to string
                df = df.sort_values(by="Duration", ascending=False)
                #format duration to HH:MM:SS
                df["Total Hours"] = df["Duration"].apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")
                df["Duration in hours"] = df["Duration"] / 3600
                #apply color to each program
                df["Color"] = df["Enrollment Date"].apply(self.get_color)

                #shorten program name
                df["Name"] = df["Name"].str.slice(0, 20)
                
                df = df.sort_values(by="Duration", ascending=True)
                #rename columns
                df = df.rename(columns={"Name": "Program Name", "Description": "Program Description", "Path": "Program Path"})

                self.bottom_widget.draw_programs_chart(df)

            case "Weekly":
                data = get_activity_data(start_date, end_date, 50)

                if not data:
                    logger.warning("Activity data is empty.")
                    return

                #convert data to df
                df = pd.DataFrame(data)
                #group by activity and sum duration
                df = df.groupby(
                ["Window Name", "Program Name", "Enrollment Date", "Program Path", "Start Time", "End Time"],as_index=False).agg({"Duration": "sum"})
                
                #convert to local time
                df["Enrollment Date"] = df["Enrollment Date"].apply(datetime_from_utc_to_local)
                df["Start Time"] = df["Start Time"].apply(datetime_from_utc_to_local)
                df["End Time"] = df["End Time"].apply(datetime_from_utc_to_local)

                #format duration to HH:MM:SS
                df["Duration"] = df["Duration"].apply(lambda x: f"{int(x//3600):02}:{int((x%3600)//60):02}:{int(x%60):02}")
                #sort by start time
                df = df.sort_values(by="Start Time", ascending=False)

                self.bottom_widget.draw_table(df)

            case "Monthly":
                data = get_computer_usage_data(start_date, end_date)

                if not data:
                    logger.warning("Computer usage data is empty.")
                    return
                
                #convert data to df
                df = pd.DataFrame(data)
                df["Start Time"] = pd.to_datetime(df["Start Time"])
                #filter only active sessions
                #group by date (day) and sum duration in hours
                df = df[df["Session type name"]=="Active"].groupby(df["Start Time"].dt.floor('d'))["Duration"].sum() / 3600
                #df.index = df.index.strftime("%d %b %Y")

                #self.bottom_widget.draw_table(data, "ASC")
                if not df.empty:
                    self.bottom_widget.draw_chart(df)
                else:
                    logger.warning("No computer usage data to plot.")
            case _:
                logger.warning("Unknown dropdown selected.")

    def draw_programs_chart(self, data):
        """Draw chart with data."""
        #create plotly chart
        if (get_setting("graphs") == "Bar"):
            fig = px.bar(
                data.reset_index(), 
                x="Program Name", 
                y="Duration in hours", 
                color="Color",
                color_discrete_map="identity",
                hover_data={"Program Name": True, "Total Hours": True, "Color": False}
                #log_y=True
            )
        elif (get_setting("graphs") == "Line"):
            fig = px.line(
                data.reset_index(), 
                x="Program Name", 
                y="Duration in hours", 
                hover_data={"Program Name": True, "Total Hours": True}
                #log_y=True
            )
        
        fig.update_layout(
            xaxis_title="Date", 
            yaxis_title="Duration (hours)",
            plot_bgcolor=get_setting("theme_secondary_color"),
            paper_bgcolor=get_setting("theme_main_color"),
            font=dict(color=get_setting("theme_text_color")),
            xaxis=dict(autorange="reversed")
        )
        
        #convert plotly chart to html
        html = fig.to_html(include_plotlyjs='cdn')
        #display html in web view
        self.web_view.setHtml(html)

        #display web view
        self.layout.addWidget(self.web_view)

    def get_color(self, enrollment_date):
        enrollment_number = int(enrollment_date.timestamp())

        random.seed(enrollment_number)
        
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)

        return f"rgb({r}, {g}, {b})"