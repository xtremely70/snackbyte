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

    accounts_num = int(myWindow.sbcore._get_login_info("ACCOUNT_CNT"))
    accounts = myWindow.sbcore._get_login_info("ACCNO")
    print(accounts_num, accounts)

    app.exec_()