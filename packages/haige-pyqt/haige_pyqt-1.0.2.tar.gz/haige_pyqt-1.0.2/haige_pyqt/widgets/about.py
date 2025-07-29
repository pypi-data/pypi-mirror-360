from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from haige_pyqt.resources import get_about_pixmap
from haige_pyqt.uis.about import Ui_aboutFrm


class AboutFrom(QWidget, Ui_aboutFrm):
    def __init__(self, parent=None):
        super(AboutFrom, self).__init__(parent=parent)
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.lb_picture.setPixmap(get_about_pixmap())
