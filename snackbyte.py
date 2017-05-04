from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from SbCore import SbCore

form_class = uic.loadUiType("mainwindow.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.sbcore = SbCore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()