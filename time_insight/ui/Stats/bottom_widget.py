from datetime import datetime

import plotly.express as px

from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtWidgets import (
            QVBoxLayout, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget
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

        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)

        #create web view widget (chart)
        self.web_view_widget = QFrame(self)
        self.web_view_layout = QVBoxLayout(self.web_view_widget)
        self.web_view = QWebEngineView(self.web_view_widget)
        self.web_view_layout.addWidget(self.web_view)
        self.stacked_widget.addWidget(self.web_view_widget)

        #create table widget
        self.table_widget = QTableWidget(self)
        self.stacked_widget.addWidget(self.table_widget)

        self.setLayout(self.layout)

    def draw_chart(self, data):
        """Draw chart with data."""
        #create plotly chart
        fig = px.bar(data.reset_index(), x='Start Time', y='Duration')
        fig.update_layout(xaxis_title="Date", yaxis_title="Duration (hours)")
        
        #convert plotly chart to html
        html = fig.to_html(include_plotlyjs='cdn')
        #display html in web view
        self.web_view.setHtml(html)

        #display web view
        self.stacked_widget.setCurrentWidget(self.web_view_widget)

    def draw_table(self, data, order="DESC"):
        """Draw table with data."""

        #create table
        self.table_widget.clear()
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data.columns))
        self.table_widget.setHorizontalHeaderLabels(data.columns)

        #fill table with data
        for row_idx, row in enumerate(data.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row_idx, col_idx, item)

        #auto resize columns
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #hide counter column
        self.table_widget.verticalHeader().setVisible(False)

        #add table to layout
        self.stacked_widget.setCurrentWidget(self.table_widget)