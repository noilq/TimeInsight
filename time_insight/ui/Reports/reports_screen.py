from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWebEngineWidgets import QWebEngineView     #type: ignore
from PyQt5.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QTextEdit,
            QLabel, QPushButton, QComboBox, QFrame, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)

import plotly.express as px      #type: ignore
import pandas as pd             #type: ignore
import random

from time_insight.data.get_data import get_activity_data, get_computer_usage_data, get_programs_data
from time_insight.time_converter import datetime_from_utc_to_local

from time_insight.settings import get_setting
from time_insight.logging.logger import logger
from datetime import datetime, timedelta
from collections import defaultdict

from time_insight.ui.language_manager import language_manager 
from time_insight.translations import t

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def retranslate_ui(self):
        print()

    def init_ui(self):
        logger.info("Initializing reports screen UI.")

        self.layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        
        self.report_type_combo_box = QComboBox()
        self.report_type_combo_box.addItems(["Daily", "Weekly", "Monthly"])
        self.report_type_combo_box.currentIndexChanged.connect(lambda: self.handle_dropdown_change(1))
        top_layout.addWidget(self.report_type_combo_box)

        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(lambda: self.handle_dropdown_change(1))
        top_layout.addWidget(self.previous_button)
        self.current_button = QPushButton("Current")
        self.current_button.clicked.connect(lambda: self.handle_dropdown_change(0))
        top_layout.addWidget(self.current_button)

        self.info_label = QLabel("smth")
        top_layout.addWidget(self.info_label)

        top_layout.addStretch()

        self.layout.addLayout(top_layout)


        #self.layout.addWidget(self.web_view)
        #self.layout.addWidget(self.report_type_combo_box)


        self.web_view_left = QWebEngineView()
        self.web_view_right = QWebEngineView()

        self.splitter = QSplitter(Qt.Vertical)

        self.splitter.addWidget(self.web_view_left)
        self.splitter.addWidget(self.web_view_right)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        self.layout.addWidget(self.splitter)

        self.setLayout(self.layout)

    def handle_dropdown_change(self, value=1):
        #get selected values
        report_type = self.report_type_combo_box.currentText()

        match report_type:
            case "Daily":
                daily_data = []
                

            case "Weekly":
                weekly_data = defaultdict(float)
                daily_counts = defaultdict(int)
                last_day_data = []
                weekly_totals = []

                for i in range(10):
                    start_date, end_date = self.get_date_range(report_type, offset=i)
                    data = get_computer_usage_data(start_date, end_date)

                    if not data:
                        weekly_totals.append(0)
                        continue

                    df = pd.DataFrame(data)
                    df["Start Time"] = pd.to_datetime(df["Start Time"])
                    df["End Time"] = pd.to_datetime(df["End Time"])
                    df = df[df["Session type name"] == "Active"]

                    week_total = 0
                    for _, row in df.iterrows():
                        start = row["Start Time"]
                        end = row["End Time"]

                        duration = (end - start).total_seconds() / 3600
                        weekday = start.weekday()

                        weekly_data[weekday] += duration
                        daily_counts[weekday] += 1
                        week_total += duration
                    
                    weekly_totals.append(week_total)

                avg_weekly_data = []
                days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                for i in range(7):
                    avg_duration = weekly_data[i] / daily_counts[i] if daily_counts[i] > 0 else 0
                    avg_weekly_data.append({
                        "Day of Week": days_of_week[i],
                        "Average Active Hours": avg_duration
                    })

                avg_df = pd.DataFrame(avg_weekly_data)
                self.draw_weekly_chart(avg_df, "bottom")

                start_date, end_date = self.get_date_range(report_type, offset=value)
                data = get_computer_usage_data(start_date, end_date)

                if not data:
                    return

                df = pd.DataFrame(data)
                df["Start Time"] = pd.to_datetime(df["Start Time"])
                df["End Time"] = pd.to_datetime(df["End Time"])
                df = df[df["Session type name"] == "Active"]

                last_day_data = []
                for i in range(7):
                    day_data = df[df["Start Time"].dt.weekday == i]
                    daily_duration_hours = day_data["Duration"].sum() / 3600

                    last_day_data.append({
                        "Day of Week": days_of_week[i],
                        "Active Hours": daily_duration_hours
                    })

                last_day_df = pd.DataFrame(last_day_data)
                self.draw_weekly_chart(last_day_df, "top")

                curr_week_hours = weekly_totals[value]
                avg_week_hours = sum(weekly_totals[1:]) / max(len(weekly_totals) - 1, 1)

                diff = round(curr_week_hours - avg_week_hours, 1)
                if value == 0:
                    period = "this week"
                elif value == 1:
                    period = "previous week"

                if diff > 0:
                    msg = f"You have spent {period} {diff} h. more than average."
                elif diff < 0:
                    msg = f"You have spent {period} {abs(diff)} h. less than average."
                else:
                    msg = f"You have spent the same amount of time as usual this {period}."

                self.info_label.setText(msg)

                #self.info_label.setText(f"{curr_week_hours}, {avg_week_hours}, {avg_week_hours-curr_week_hours}")

            case "Monthly":
                hourly_data_avg = defaultdict(float)
                daily_counts = defaultdict(int)

                for i in range(1):
                    start_date, end_date = self.get_date_range(report_type, offset=value)

                    data = get_computer_usage_data(start_date, end_date)

                    if not data:
                        continue

                    df = pd.DataFrame(data)
                    df["Start Time"] = pd.to_datetime(df["Start Time"])
                    df = df[df["Session type name"] == "Active"]

                    for day in range(1, 32):
                        if day > df["Start Time"].dt.days_in_month.max():
                            break
                        day_data = df[df["Start Time"].dt.day == day]
                        daily_duration_hours = day_data["Duration"].sum() / 3600

                        hourly_data_avg[day] += daily_duration_hours
                        daily_counts[day] += 1

                avg_monthly_data = []
                for day in range(1, 32):
                    avg_hourly_duration = hourly_data_avg[day] / daily_counts[day] if daily_counts[day] > 0 else 0
                    avg_monthly_data.append({
                        "Day of Month": day,
                        "Active Hours": avg_hourly_duration
                    })
                
                avg_monthly_df = pd.DataFrame(avg_monthly_data)

                self.draw_monthly_chart(avg_monthly_df, "top")

                curr_month_hours = sum(day["Active Hours"] for day in avg_monthly_data)

                past_month_totals = []
                hourly_data_avg = defaultdict(float)
                daily_counts = defaultdict(int)

                for i in range(6):
                    start_date, end_date = self.get_date_range(report_type, offset=i)
                    data = get_computer_usage_data(start_date, end_date)

                    if not data:
                        continue

                    df = pd.DataFrame(data)
                    df["Start Time"] = pd.to_datetime(df["Start Time"])
                    df = df[df["Session type name"] == "Active"]

                    for day in range(1, 32):
                        if day > df["Start Time"].dt.days_in_month.max():
                            break
                        day_data = df[df["Start Time"].dt.day == day]
                        daily_duration_hours = day_data["Duration"].sum() / 3600
                        hourly_data_avg[day] += daily_duration_hours
                        daily_counts[day] += 1

                avg_monthly_data = []
                for day in range(1, 32):
                    avg_hourly_duration = hourly_data_avg[day] / daily_counts[day] if daily_counts[day] > 0 else 0
                    avg_monthly_data.append({
                        "Day of Month": day,
                        "Active Hours": avg_hourly_duration
                    })

                avg_monthly_df = pd.DataFrame(avg_monthly_data)

                self.draw_monthly_chart(avg_monthly_df, "bottom")

                avg_month_hours = sum(past_month_totals) / max(len(past_month_totals), 1)
                diff = round(curr_month_hours - avg_month_hours, 1)

                if value == 0:
                    period = "this month"
                elif value == 1:
                    period = "previous month"

                if diff > 0:
                    msg = f"You have spent {period} {diff} h. more than average."
                elif diff < 0:
                    msg = f"You have spent {period} {abs(diff)} h. less than average."
                else:
                    msg = f"You have spent the same amount of time as usual this {period}."

                self.info_label.setText(msg)
        
            case _:
                logger.warning("Unknown dropdown selected.") 

    def draw_programs_chart(self, data, chart):
        if (get_setting("graphs") == "Bar"):
            fig = px.bar(
                data.reset_index(), 
                x="Date", 
                y="Active Hours", 
                hover_data={"Date": True, "Active Hours": True}
                #log_y=True
            )
        elif (get_setting("graphs") == "Line"):
            fig = px.line(
                data.reset_index(), 
                x="Date", 
                y="Active Hours", 
                hover_data={"Date": True, "Active Hours": True}
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
        
        html = fig.to_html(include_plotlyjs='cdn')

        match chart:
            case "top":
                self.web_view_left.setHtml(html)
                self.layout.addWidget(self.web_view_left)
            case "bottom":
                self.web_view_right.setHtml(html)
                self.layout.addWidget(self.web_view_right)
            case _:
                #nu kapec
                logger.warning("Wrong type of chart at Reports_screen draw chart")

    def draw_weekly_chart(self, data, position):
        if (get_setting("graphs") == "Bar"):
            fig = px.bar(
                data,
                x="Day of Week",
                y="Active Hours" if position == "top" else "Average Active Hours",
                title="Active Hours per day" if position == "top" else "Average Active Hours by Day of Week",
                labels={"Day of Week": "Day", "Active Hours": "Hours", "Average Active Hours": "Hours"},
                hover_data=["Active Hours" if position == "top" else "Average Active Hours"]
            )
        elif (get_setting("graphs") == "Line"):
            fig = px.line(
                data,
                x="Day of Week",
                y="Active Hours" if position == "top" else "Average Active Hours",
                title="Active Hours" if position == "top" else "Average Active Hours by Day of Week",
                labels={"Day of Week": "Day", "Active Hours": "Hours", "Average Active Hours": "Hours"},
                hover_data=["Active Hours" if position == "top" else "Average Active Hours"]
            )

        fig.update_layout(
            plot_bgcolor=get_setting("theme_secondary_color"),
            paper_bgcolor=get_setting("theme_main_color"),
            font=dict(color=get_setting("theme_text_color")),
            margin=dict(l=40, r=40, t=40, b=40),    #make graph bigger
        )

        html = fig.to_html(include_plotlyjs='cdn')

        #fill the gaps it html 
        html = html.replace(
            "<head>",
            f"<head><style>body {{ background-color: {get_setting("theme_main_color")}; margin: 0; padding: 0; }}</style>"
        )

        if position == "top":
            self.web_view_left.setHtml(html)
        elif position == "bottom":
            self.web_view_right.setHtml(html)

    def draw_monthly_chart(self, data, position):
        if (get_setting("graphs") == "Bar"):
            fig = px.bar(
                data,
                x="Day of Month",
                y="Active Hours",
                title="Active Hours per day" if position == "top" else "Average Active Hours by Day of Month",
                labels={"Hour": "Hour of Day", "Active Hours": "Active Hours", "Day of Month": "Day", "Average Active Hours": "Average Active Hours"},
                hover_data=["Active Hours"]
            )
        elif (get_setting("graphs") == "Line"):
            fig = px.line(
                data,
                x="Day of Month",
                y="Active Hours",
                title="Active Hours per day" if position == "top" else "Average Active Hours by Day of Month",
                labels={"Hour": "Hour of Day", "Active Hours": "Active Hours", "Day of Month": "Day", "Average Active Hours": "Average Active Hours"},
                hover_data=["Active Hours"]
            )

        fig.update_layout(
            plot_bgcolor=get_setting("theme_secondary_color"),
            paper_bgcolor=get_setting("theme_main_color"),
            font=dict(color=get_setting("theme_text_color")),
            margin=dict(l=40, r=40, t=40, b=40),    #make graph bigger
        )


        html = fig.to_html(include_plotlyjs='cdn')

        #fill the gaps it html 
        html = html.replace(
            "<head>",
            f"<head><style>body {{ background-color: {get_setting("theme_main_color")}; margin: 0; padding: 0; }}</style>"
        )

        if position == "top":
            self.web_view_left.setHtml(html)
        elif position == "bottom":
            self.web_view_right.setHtml(html)

    def get_color(self, enrollment_date):
        enrollment_number = int(enrollment_date.timestamp())

        random.seed(enrollment_number)
        
        r = random.randint(50, 200)
        g = random.randint(50, 200)
        b = random.randint(50, 200)

        return f"rgb({r}, {g}, {b})"
    
    def get_date_range(self, report_type, offset=0):
        today = QDate.currentDate()

        match report_type:
            case "Daily":
                start_date = today.addDays(-offset)
                end_date = start_date

            case "Weekly":
                base_week = today.addDays(-offset * 7)
                start_date = QDate(base_week.year(), base_week.month(), base_week.day()).addDays(-base_week.dayOfWeek() + 1)
                end_date = start_date.addDays(6)

            case "Monthly":
                base_month = today.addMonths(-offset)
                start_date = QDate(base_month.year(), base_month.month(), 1)
                end_date = start_date.addMonths(1).addDays(-1)

            case _:
                start_date = None
                end_date = None

        return start_date, end_date