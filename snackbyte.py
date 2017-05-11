import sys
from datetime import datetime
from time import sleep
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
        self.sbcore.comm_connect()

        # variables
        # self.watchList = ['004720']     # for testing only
        self.watchList = ['004720', '008700', '003490', '090370']     # for testing only

    def get_ohlcv(self):
        """
        해당 종목의 ohlcv 차트값 읽어옴
        :param symbol: 종목 no
        :param interval_tick: 구간, 10 = 10분봉
        :return: 
        """
        print("===========================================")
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        for symbol in self.watchList:
            self.sbcore.set_input_value("종목코드", symbol)
            self.sbcore.set_input_value("틱범위", "10")
            self.sbcore.set_input_value("수정주가구분", 1)

            print("starting comm_rq_data of ", symbol)
            self.sbcore.comm_rq_data("opt10080_req_ma", "opt10080", 0, "0101")
            sleep(0.3)  # 초당 api call 초과하지 않도록

    def automate_job(self):
        # overlapping call 피하기 위해서 singleShot으로 call
        try:
            self.get_ohlcv()
        finally:
            QTimer.singleShot(60000, self.automate_job)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    # myWindow.get_ohlcv()
    myWindow.show()

    myWindow.automate_job()

    app.exec_()