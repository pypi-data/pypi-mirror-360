import os
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QStackedWidget,
)
from PySide6.QtCore import QSize

ICON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons')
)
class Status(QWidget):

    IconSize = QSize(16, 16)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setFixedSize(35, 40)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.qstack = QStackedWidget()
        layout.addWidget(self.qstack)


        wait_icon = QPixmap(os.path.join(ICON_PATH, 'wait.svg'))
        wait_icon = wait_icon.scaled(self.IconSize)
        ok_icon = QPixmap(os.path.join(ICON_PATH, 'ok.svg'))
        ok_icon = ok_icon.scaled(self.IconSize)
        nok_icon = QPixmap(os.path.join(ICON_PATH, 'nok.svg'))
        nok_icon = nok_icon.scaled(self.IconSize)

        wait_label = QLabel()
        wait_label.setPixmap(wait_icon)
        wait_widget = QWidget(self)
        wait_layout = QHBoxLayout(wait_widget)
        wait_layout.addWidget(wait_label)


        ok_label = QLabel()
        ok_label.setPixmap(ok_icon)
        ok_widget = QWidget(self)
        ok_layout = QHBoxLayout(ok_widget)
        ok_layout.addWidget(ok_label)

        nok_label = QLabel()
        nok_label.setPixmap(nok_icon)
        nok_widget = QWidget(self)
        nok_layout = QHBoxLayout(nok_widget)
        nok_layout.addWidget(nok_label)

        self.qstack.addWidget(wait_widget)
        self.qstack.addWidget(ok_widget)
        self.qstack.addWidget(nok_widget)

        self.qstack.setCurrentIndex(0)

    def set_error(self):
        self.qstack.setCurrentIndex(2)

    def set_valid(self):
        self.qstack.setCurrentIndex(1)