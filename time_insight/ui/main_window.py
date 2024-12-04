import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity
from time_insight.log import log_to_console

class TopWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        
        label = QLabel("", self)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)  

class ApplicationListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: white;")
        
        label = QLabel("", self)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)  

class ApplicationActivityListWidget(QWidget):
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
                                        f"Add info: {activity.additional_info}" \
                                        f"Start time: {activity.session_start}, " \
                                        f"End Time: {activity.session_end}" \
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

        top_widget = TopWidget()
        main_layout.addWidget(top_widget)

        bottom_layout = QHBoxLayout()

        left_widget = ApplicationListWidget()
        right_widget = ApplicationActivityListWidget()

        bottom_layout.addWidget(left_widget)
        bottom_layout.addWidget(right_widget)

        bottom_layout.setStretch(0, 4)
        bottom_layout.setStretch(1, 7)

        main_layout.addLayout(bottom_layout)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

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