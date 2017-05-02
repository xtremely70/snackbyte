import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class SbCore(QAxWidget):
    def __init__(self):
        super().__init__()
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

    def _set_signal_slots(self):
        """
        Initializing pyqt things.
        :return: n/a
        """
        self.OnEventConnect.connect(self._on_connect)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sb = SbCore()
    sb.comm_connect()
