import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class SbCore(QAxWidget):
    def __init__(self):
        super().__init__()

        # initialize variables
        self.login_event_loop = None
        self.tr_event_loop = None

        self._create_kw_instance()
        self._set_signal_slots()

    def _create_kw_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _on_connect(self, err_code):
        if err_code == 0:   # connected successfully
            print("connected")
        else:
            print("disconnected")
        self.login_event_loop.exit()

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        # rqname에 따른 분기
        if rqname == "opt10080_req":    # 분봉 차트 요청
            pass

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sb = SbCore()
    sb.comm_connect()
