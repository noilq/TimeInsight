from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QVBoxLayout, QSlider, QWidget
)
from PyQt5.QtCore import Qt, QRectF, QDateTime, QPointF
from PyQt5.QtGui import QColor, QBrush, QWheelEvent, QPainter, QPen
import random


class ChronologicalGraphWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: none;")