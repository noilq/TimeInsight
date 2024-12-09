import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QSplitter
from PyQt5.QtCore import Qt
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity
from time_insight.log import log_to_console

class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        
        label = QLabel("", self)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)  

class ChronologicalGraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        
        label = QLabel("", self)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)  

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

class ActivitiesWidget(QWidget):
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

        self.load_application_activities()
        
    def load_application_activities(self):
        try:
            with Session(engine) as session:
                activities = session.query(ApplicationActivity).all()
                
                if activities:
                    for activity in activities:
                        activity_info = f"Activity id: {activity.id}, " \
                                        f"Aplication id: {activity.application_id}, " \
                                        f"Window name: {activity.window_name}, " \
                                        f"Add info: {activity.additional_info}, " \
                                        f"Start time: {activity.session_start}, " \
                                        f"End Time: {activity.session_end}, " \
                                        f"Duration: {activity.duration}"
                        label = QLabel(activity_info, self)
                        self.layout.addWidget(label)
                else:
                    no_data_label = QLabel("No application activities found.", self)
                    self.layout.addWidget(no_data_label)

        except Exception as e:
            error_label = QLabel(f"Error loading data: {str(e)}", self)
            self.layout.addWidget(error_label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TimeInsight")
        self.setGeometry(*self.GetWindowGeometry())
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        self.header_widget = HeaderWidget()
        main_layout.addWidget(self.header_widget)

        self.timeline_widget = ChronologicalGraphWidget()
        main_layout.addWidget(self.timeline_widget)

        splitter = QSplitter(Qt.Horizontal)

        self.applications_widget = ApplicationsWidget()
        self.applications_widget.setMinimumSize(300, 100)

        self.activities_widget = ActivitiesWidget()
        self.activities_widget.setMinimumSize(300, 100)
        
        splitter.addWidget(self.applications_widget)
        splitter.addWidget(self.activities_widget)

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        splitter.setSizes([300, 500])  #левый виджет 300, правый виджет 500

        #добавляем разделитель в основной макет
        main_layout.addWidget(splitter)

        #настройка пропорций макета
        main_layout.setStretch(0, 1)  #хеадер
        main_layout.setStretch(1, 5)  #таймлайн
        main_layout.setStretch(2, 5)  #нижний разделитель

        central_widget.setLayout(main_layout)

    def showEvent(self, event):
        #ubrat posle pokaza okna show on hueta
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.showNormal()

    def GetWindowGeometry(self):
        screen_resolution = QDesktopWidget().screenGeometry()

        width = screen_resolution.width()
        height = screen_resolution.height()

        x = round(width / 4.6)
        y = round(height / 9.7)

        width = round(width / 1.9)
        height = round(height/1.4)

        return x, y, width, height

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
    
    sys.exit(app.exec_())