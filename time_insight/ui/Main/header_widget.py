from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtWidgets import (
            QWidget, QHBoxLayout, QLabel, QLabel, QPushButton, QCalendarWidget, QDateEdit
)

from time_insight.logging.logger import logger

from time_insight.ui.language_manager import language_manager 
from time_insight.translations import t

class HeaderWidget(QWidget):
    date_changed_signal = pyqtSignal(QDate)

    def __init__(self):
        super().__init__()
        #self.setStyleSheet("background-color: none;")
        
        self.selected_date = QDate.currentDate()

        main_layout = QHBoxLayout()

        #create date label
        self.date_label = QLabel(self.selected_date.toString("yyyy-MM-dd"), self)
        self.date_label.setAlignment(Qt.AlignLeft)
        self.date_label.hide()
        #main_layout.addWidget(self.date_label)

        #create calendar button
        """
        self.toggle_calendar_button = QPushButton("📅", self)
        self.toggle_calendar_button.setFixedSize(30, 30)
        self.toggle_calendar_button.clicked.connect(self.toggle_calendar)
        main_layout.addWidget(self.toggle_calendar_button)"""
        self.toggle_calendar_button = QDateEdit()
        self.toggle_calendar_button.setDisplayFormat("dddd, d MMMM yyyy")
        self.toggle_calendar_button.setCalendarPopup(True)
        self.toggle_calendar_button.setDate(QDate.currentDate())
        self.toggle_calendar_button.dateChanged.connect(self.date_changed)
        main_layout.addWidget(self.toggle_calendar_button)

        #create navigation buttons (previous, next, today)
        self.prev_button = QPushButton("⟨", self)
        #self.prev_button.setFixedSize(30, 30)
        self.prev_button.clicked.connect(self.go_to_previous_day)
        main_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("⟩", self)
        #self.next_button.setFixedSize(30, 30)
        self.next_button.clicked.connect(self.go_to_next_day)
        main_layout.addWidget(self.next_button)

        self.today_button = QPushButton("Today", self)
        self.today_button.clicked.connect(self.go_to_today)
        main_layout.addWidget(self.today_button)

        #create calendar widget
        self.calendar = QCalendarWidget(self)
        self.calendar.setSelectedDate(self.selected_date)
        self.calendar.setWindowFlags(Qt.Popup)
        self.calendar.hide()
        self.calendar.selectionChanged.connect(lambda: self.date_changed(self.calendar.selectedDate()))

        self.setLayout(main_layout)

    def retranslate_ui(self):
        self.today_button.setText(t("today_button_text"))

    def update_date_label(self):
        """
        Update date label with selected date
        """
        self.date_label.setText(self.selected_date.toString("yyyy-MM-dd"))

    def go_to_previous_day(self):
        self.selected_date = self.selected_date.addDays(-1)
        self.calendar.setSelectedDate(self.selected_date)
        self.toggle_calendar_button.setDate(self.selected_date)
        self.update_date_label()

    def go_to_next_day(self):
        self.selected_date = self.selected_date.addDays(1)
        self.calendar.setSelectedDate(self.selected_date)
        self.toggle_calendar_button.setDate(self.selected_date)
        self.update_date_label()

    def go_to_today(self):
        self.selected_date = QDate.currentDate()
        self.calendar.setSelectedDate(self.selected_date)
        self.toggle_calendar_button.setDate(self.selected_date)
        self.update_date_label()

    def toggle_calendar(self):
        if self.calendar.isVisible():
            self.calendar.hide()
        else:
            button_pos = self.toggle_calendar_button.mapToGlobal(self.toggle_calendar_button.rect().bottomLeft())
            self.calendar.move(button_pos)
            self.calendar.show()

    def date_changed(self, date: QDate):
        #update selected date and hide calendar
        #self.selected_date = self.toggle_calendar_button.date()
        #self.update_date_label()
        #self.calendar.hide()
        #emit signal
        #self.date_changed_signal.emit(self.selected_date)

        self.selected_date = date
        self.toggle_calendar_button.setDate(self.selected_date)
        self.update_date_label()
        self.date_changed_signal.emit(self.selected_date)

    def get_selected_date(self):
        return self.selected_date