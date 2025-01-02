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

        if order.upper() == "DESC":
            sorted_data = data.sort_index(ascending=False)
        else:
            sorted_data = data.sort_index(ascending=True)

        # Заполняем таблицу данными
        for row_idx, row in enumerate(sorted_data.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        # Автоматическое изменение размера колонок
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Добавляем таблицу в макет
        self.layout.addWidget(table)

    def clear_widget(self):
        """Clear all child widgets."""
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
   

    def get_programs_data(self, start_date, end_date, count):
        #get programs data here
        return []

    def get_activity_data(self, start_date, end_date, count):
        #get activity data here
        return []
    
    def get_computer_usage_data(self, start_date, end_date):
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
            #log_to_console(f"Error accessing database: {str(e)}")
            raise RuntimeError(f"Error accessing database: {str(e)}")