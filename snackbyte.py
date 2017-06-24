import sys
from datetime import datetime
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from SbCore import SbCore

form_class = uic.loadUiType("mainwindow.ui")[0]


class MyWindow(QMainWindow, form_class):

    BASKET_SIZE = 3

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.sbcore = SbCore()
        self.sbcore.comm_connect()

        # get account info
        # self.num_of_accounts = self.sbcore._get_login_info("ACCOUNT_CNT")
        # self.account_no = self.sbcore._get_login_info("ACCNO")

        # init class variables
        self.sbcore.basket_size = self.BASKET_SIZE
        self.watchList = ['008970', '033250', '004720', '008700', '003490', '009270', '001550']     # for testing only

    def automate_job(self):
        # overlapping call 피하기 위해서 singleShot으로 call
        try:
            # 폐장 이후에는 stop
            current_time = datetime.now()
            if (current_time.hour > 14) and (current_time.minute > 30):
                sys.exit(0)

            # OHLCV 값 받아옴
            if current_time.minute % 10 == 0:   # 10분 단위
                self.search_short_signal()
                self.get_ohlcv()

        finally:
            QTimer.singleShot(60000, self.automate_job)

    def get_ohlcv(self):
        """
        해당 종목의 ohlcv 차트값 읽어옴
        :param symbol: 종목 no
        :param interval_tick: 구간, 10 = 10분봉
        :return: 
        """
        print("===========================================",
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        for symbol in self.watchList:
            self.sbcore.set_symbol(symbol)     # Set sbcore's symbol
            self.sbcore.set_input_value("종목코드", symbol)
            self.sbcore.set_input_value("틱범위", "10")
            self.sbcore.set_input_value("수정주가구분", 1)

            # print("starting comm_rq_data of ", symbol)
            self.sbcore.comm_rq_data("opt10080_req_ma", "opt10080", 0, "0101")
            sleep(0.25)  # 초당 api call 초과하지 않도록

    def search_short_signal(self):
        """
        basket에 담긴 종목들의 셀 시그널 검색
        :return:
        """
        print("===========================================",
              "매도신호검색 시작:", self.sbcore.basket,
              datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        for symbol in self.sbcore.basket:
            self.sbcore.set_symbol(symbol)  # Set sbcore's symbol
            self.sbcore.set_input_value("종목코드", symbol)
            self.sbcore.set_input_value("틱범위", "10")
            self.sbcore.set_input_value("수정주가구분", 1)

            self.sbcore.comm_rq_data("매도신호검색", "opt10080", 0, "0101")
            sleep(0.25)  # 초당 api call 초과하지 않도록


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    # myWindow.get_ohlcv()
    myWindow.show()

    myWindow.automate_job()
    # myWindow.sbcore._sendOrder("send_order_req", "0101", myWindow.sbcore.account_no, "1", '009270', 10, 0, "03", "")
    app.exec_()