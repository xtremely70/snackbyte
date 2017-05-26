import sys
from snackbyte import MyWindow
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("mainwindow.ui")[0]


class MyWindow4Test(MyWindow):

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow4Test()
    myWindow.show()

    app.exec_()