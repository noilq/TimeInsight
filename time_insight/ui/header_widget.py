from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtWidgets import (
            QWidget, QHBoxLayout, QLabel, QLabel, QPushButton, QCalendarWidget
)
from time_insight.log import log_to_console

class HeaderWidget(QWidget):
    date_changed_signal = pyqtSignal(QDate)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 2px solid black; background-color: lightgray;")
        
        self.selected_date = QDate.currentDate()

        main_layout = QHBoxLayout()

        self.date_label = QLabel(self.selected_date.toString("yyyy-MM-dd"), self)
        self.date_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.date_label)

        self.toggle_calendar_button = QPushButton("📅", self)
        self.toggle_calendar_button.setFixedSize(30, 30)
        self.toggle_calendar_button.clicked.connect(self.toggle_calendar)
        main_layout.addWidget(self.toggle_calendar_button)

        self.prev_button = QPushButton("⟨", self)
        self.prev_button.setFixedSize(30, 30)
        self.prev_button.clicked.connect(self.go_to_previous_day)
        main_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("⟩", self)
        self.next_button.setFixedSize(30, 30)
        self.next_button.clicked.connect(self.go_to_next_day)
        main_layout.addWidget(self.next_button)

        self.today_button = QPushButton("Сегодня", self)
        self.today_button.clicked.connect(self.go_to_today)
        main_layout.addWidget(self.today_button)

        self.calendar = QCalendarWidget(self)
        self.calendar.setSelectedDate(self.selected_date)
        self.calendar.setWindowFlags(Qt.Popup)
        self.calendar.hide()
        self.calendar.selectionChanged.connect(self.date_changed)

        self.setLayout(main_layout)

    def create_button(text, callback, size=(30, 30)):
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.clicked.connect(callback)
        return button

    def update_date_label(self):
        self.date_label.setText(self.selected_date.toString("yyyy-MM-dd"))

    def go_to_previous_day(self):
        self.selected_date = self.selected_date.addDays(-1)
        self.calendar.setSelectedDate(self.selected_date)
        self.update_date_label()

    def go_to_next_day(self):
        self.selected_date = self.selected_date.addDays(1)
        self.calendar.setSelectedDate(self.selected_date)
        self.update_date_label()

    def go_to_today(self):
        self.selected_date = QDate.currentDate()
        self.calendar.setSelectedDate(self.selected_date)
        self.update_date_label()

    def toggle_calendar(self):
        if self.calendar.isVisible():
            self.calendar.hide()
        else:
            button_pos = self.toggle_calendar_button.mapToGlobal(self.toggle_calendar_button.rect().bottomLeft())
            self.calendar.move(button_pos)
            self.calendar.show()

    def date_changed(self):
        """Обработчик изменения даты через календарь."""
        self.selected_date = self.calendar.selectedDate()
        self.update_date_label()
        self.calendar.hide()
        self.date_changed_signal.emit(self.selected_date)