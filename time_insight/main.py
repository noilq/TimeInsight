import sys
from PyQt5.QtWidgets import QApplication
from time_insight.ui.main_window import MainWindow
from time_insight.data.database import init_db

def main():
    init_db()
    print("Db init.")

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()