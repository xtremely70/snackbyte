import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class SbCore(QAxWidget):
    def __init__(self):
        super().__init__()

        # list of variables
        self.login_event_loop = None
        self.tr_event_loop = None

        self._create_kw_instance()
        self._set_signal_slots()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _create_kw_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _on_connect(self, err_code):
        if err_code == 0:   # connected successfully
            print("connected")
        else:
            print("disconnected")
        self.login_event_loop.exit()

    def _on_opt10080(self, rqname, trcode):
        """
        분봉차트 요청
        :param rqname: 
        :param trcode: 
        :return: 
        """
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        print("data_cnt", data_cnt)

        self.ohlcv = list()

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "체결시간")
            open_price = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")
            self.ohlcv.append(
                (date, open_price, high, low, close, volume)
            )
            print(date, open_price, high, low, close, volume)

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        print("tr_received: ", rqname)

        # rqname에 따른 분기
        if rqname == "opt10080_req":    # 분봉 차트 요청
            self._on_opt10080(rqname, trcode)

        # event loop 종료
        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _set_signal_slots(self):
        """
        Initializing pyqt things.
        :return: n/a
        """
        self.OnEventConnect.connect(self._on_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def set_input_value(self, id, value):
        """
        1. set_input_value
        2. 
        :param id: 
        :param value: 
        :return: 
        """
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sb = SbCore()
    sb.comm_connect()

    sb.set_input_value("종목코드", "066910")
    sb.set_input_value("틱범위", "10")
    sb.set_input_value("수정주가구분", 1)

    print("starting comm_rq_data...")
    sb.comm_rq_data("opt10080_req", "opt10080", 0, "0101")