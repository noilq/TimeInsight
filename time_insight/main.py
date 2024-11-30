import sys
import threading
from PyQt5.QtWidgets import QApplication
from time_insight.ui.main_window import MainWindow
from time_insight.data.database import init_db
from time_insight.tracker.tracker import init_tracker
from time_insight.log import log_to_console

def main():
    init_db()
    log_to_console("Db init.")

    tracker_thread = threading.Thread(target=init_tracker, daemon=True)
    tracker_thread.start()
    log_to_console("Tracker init.")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()