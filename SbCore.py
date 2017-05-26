import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class SbCore(QAxWidget):
    def __init__(self):
        super().__init__()

        # list of variables
        self.basket_size = 3        # default value
        self.budget = 100000        # budget for each item
        self.account_no = '8090377411'
        self.sn = '0000'
        self.login_event_loop = None
        self.tr_event_loop = None
        self.current_symbol = None
        self.basket = list()        # list of symbols

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

    def _get_signal_ma(self):
        """
        ohlcv 기준으로 ma 계산(종가 기준)
        :return: Boolean. True - long position 
        """
        close20 = list()

        # retrieve close price from self.ohlcv
        for i in range(21):
            date, open_price, high, low, close, volume = self.ohlcv[i]
            if i == 0:
                current_price = abs(int(close))     # close는 string
            # print(i, self.ohlcv[i])
            close20.append(abs(int(close)))

        # calculate ma20, ma10, ma5
        ma20 = round(sum(close20[:20])/20)
        ma20_previous = round(sum(close20[1:21])/20)
        ma20_delta = ma20 - ma20_previous

        ma10 = round(sum(close20[:10])/10)
        ma10_previous = round(sum(close20[1:11])/10)
        ma10_delta = ma10 - ma10_previous

        ma5 = round(sum(close20[:5])/5)
        ma5_previous = round(sum(close20[1:6])/5)
        ma5_delta = ma5 - ma5_previous

        print(self.current_symbol, "MA20, MA10, MA5 현재: ", ma20, ma10, ma5,
              "과거: ", ma20_previous, ma10_previous, ma5_previous)
        # print("MA20:", ma20, ma20_previous, ma20_delta, "MA10:", ma10, ma10_previous, "MA5:", ma5, ma5_previous)

        # set position
        if (ma20_delta >= 0) and (ma10_delta >= 0) and (ma5_delta > 0):
            if (ma5_previous < ma10_previous) and (ma5 >= ma10):    # long position
                print("Long signal : ", self.current_symbol)
                print("Budget: ", self.budget, "current price: ", current_price)
                qty = int(self.budget / current_price)
                print("buying price: ", qty)
                self._sendOrder("자동매수주문", "0101", self.account_no, "1", self.current_symbol,
                                qty, 0, "03", "")
                self.basket.append(self.current_symbol)
                print("Current basket: ", self.basket)

    def _on_connect(self, err_code):
        if err_code == 0:   # connected successfully
            print("connected")
        else:
            print("disconnected")
        self.login_event_loop.exit()

    def _on_opt10080(self, rqname, trcode):
        """
        분봉차트 요청(단일 심볼)
        :param rqname: 
        :param trcode: 
        :return: 
        """
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        # print("data_cnt", data_cnt)

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
            # print(date, open_price, high, low, close, volume)

    def _on_send_order(self, rqname, trcode):
        pass

    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        order_no = self.dynamicCall("GetChejanData(int)", 9203)  # 주문번호
        symbol = self.dynamicCall("GetChejanData(int)", 9001)  # 종목코드
        symbol_name = self.dynamicCall("GetChejanData(int)", 302)  # 종목명
        order_quantity = self.dynamicCall("GetChejanData(int)", 900)  # 주문수량
        order_price = self.dynamicCall("GetChejanData(int)", 901)  # 주문가격

        print(gubun, order_no, symbol, symbol_name, order_quantity, "주", order_price, "원")

    def _on_receive_msg(self, screen_no, request_name, tr_code, msg):
        """
        메시지 수신 이벤트
        :param screen_no: string - 화면번호 
        :param request_name: request명(사용자 정의)
        :param tr_code: string 
        :param msg: string - returned from server
        :return: n/a
        """
        self.msg = request_name + ": " + msg
        print(self.msg)

    def _on_receive_tr_data(self, screen_no, request_name, trcode,
                            record_name, next, unused1, unused2, unused3, unused4):
        """
        transaction 수신 이벤트
        :param screen_no: string - 화면번호 
        :param request_name: comm_rq_data()에서 넘어오는 값
        :param trcode: string
        :param record_name: string
        :param next: 다음 데이터('0': 남은 데이터 없음, '2': 남은 데이터 있음)
        :param unused1: 
        :param unused2: 
        :param unused3: 
        :param unused4: 
        :return: 
        """
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        # rqname에 따른 분기
        if request_name == "opt10080_req":    # 분봉 차트 요청
            self._on_opt10080(request_name, trcode)
        elif request_name == "opt10080_req_ma":   # 분봉 + MA 요청
            self._on_opt10080(request_name, trcode)
            self._get_signal_ma()
        elif request_name == "자동매수주문":    # 주문
            print(request_name, "TR data received successfully.")

        # event loop 종료
        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _sendOrder(self, sRQName, sScreenNo, sAccountNo, nOrderType, sItemCode, nQty, nPrice, sBid, sOrgOrderNo):
        ret = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                               [sRQName, sScreenNo, sAccountNo, nOrderType, sItemCode, nQty, nPrice, sBid, sOrgOrderNo])

    def _set_signal_slots(self):
        """
        Initializing pyqt things.
        :return: n/a
        """
        self.OnEventConnect.connect(self._on_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.OnReceiveMsg.connect(self._on_receive_msg)
        self.OnReceiveChejanData.connect(self._on_receive_chejan_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        """
        Send request to server
        :param rqname: string - TR request name
        :param trcode: string
        :param next: int(0: 다음 데이터 없음, 2: 남은 데이터 조회)
        :param screen_no: string - 화면번호
        :return: n/a
        """
        if not self.get_connect_state():
            sys.exit(1)

        return_code = self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         rqname, trcode, next, screen_no)

        # 이벤트 루프 생성. _on_receive_tr_data()에서 종료
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def get_connect_state(self):
        """
        현재 connection state 반환
        :return: int (0: 접속 해제, 1: 연결)
        """
        ret = self.dynamicCall("GetConnectState()")
        return ret

    def set_symbol(self, value):
        """
        
        :param value: 
        :return: nothing.
        """
        self.current_symbol = value

    def set_input_value(self, id, value):
        """
        1. set_input_value
        2. 
        :param id: 
        :param value: 
        :return: 
        """
        self.dynamicCall("SetInputValue(QString, QString)", id, value)


class Stock:

    def __init__(self, symbol, price):

        # variables
        self.symbol = symbol
        self.buy_price = price


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sb = SbCore()
    sb.comm_connect()

    sb.set_input_value("종목코드", "066910")
    sb.set_input_value("틱범위", "10")
    sb.set_input_value("수정주가구분", 1)

    print("starting comm_rq_data...")
    sb.comm_rq_data("opt10080_req", "opt10080", 0, "0101")