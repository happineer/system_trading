import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import pandas as pd
import pdb
import random
import logging
import logging.config
from pprint import pprint
from kiwoom import custom_error
from kiwoom.tr import TrManager
from collections import deque


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.tr_mgr = TrManager(self)
        self.evt_loop = QEventLoop()  # lock/release loop
        self.ret_data = None
        self.req_queue = deque(maxlen=10)

        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._on_event_connect)  # 로긴 이벤트
        self.OnReceiveTrData.connect(self.tr_mgr._on_receive_tr_data)  # tr 수신 이벤트
        self.OnReceiveRealData.connect(self._on_receive_real_data)  # 실시간 시세 이벤트
        self.OnReceiveRealCondition.connect(self._on_receive_real_condition)  # 조건검색 실시간 편입, 이탈종목 이벤트
        self.OnReceiveTrCondition.connect(self._on_receive_tr_condition)  # 조건검색 조회응답 이벤트
        self.OnReceiveConditionVer.connect(self._on_receive_condition_ver)  # 로컬에 사용자조건식 저장 성공여부 응답 이벤트
        self.OnReceiveChejanData.connect(self._on_receive_chejan_data)  # 주문 접수/확인 수신시 이벤트
        self.OnReceiveMsg.connect(self._on_receive_msg)  # 수신 메시지 이벤트

    # Kiwoom callback function
    def _on_event_connect(self, err_code):
        """
        Kiwoom Login Callback, 서버 접속 관련 이벤트
        :param err_code: int - 0:로그인 성공, 음수:로그인 실패
        :return:
        """
        self.ret_data = err_code
        self.evt_loop.exit()  # release event loop

    def _on_receive_real_data(self, code, real_type, real_data):
        """
        Kiwoom Receive Realtime Data Callback, 실시간데이터를 받은 시점을 알려준다.
        setRealReg() 메서드로 등록한 실시간 데이터도 이 이벤트 메서드에 전달됩니다.
        getCommRealData() 메서드를 이용해서 실시간 데이터를 얻을 수 있습니다.
        :param code: string - 종목코드
        :param real_type: string - 실시간 타입(KOA의 실시간 목록 참조)
        :param realData: string - 실시간 데이터 전문
        """
        pass

    def _on_receive_real_condition(self, code, update_type, condi_name, condi_index):
        """
        Kiwoom Receive Realtime Condition Result(stock list) Callback, 조건검색 실시간 편입, 이탈 종목을 받을 시점을 알려준다.
        condi_name(조건식)으로 부터 검출된 종목이 실시간으로 들어옴.
        update_type으로 편입된 종목인지, 이탈된 종목인지 구분한다.
        * 조건식 검증할때, 어떤 종목이 검출된 시간을 본 함수내에서 구현해야 함
        :param code: string - 종목코드
        :param update_type: string - 편입("I"), 이탈("D")
        :param condi_name: string - 조건식명
        :param condi_index: string - 조건식명 인덱스
        :return: 없음
        """
        pass

    def _on_receive_tr_condition(self, screen_no, code_list, condi_name, condi_index, next):
        """
        Kiwoom Receive TR Condition Callback, 조건검색 조회응답으로 종목리스트를 구분자(';')로 붙어서 받는 시점.
        :param screen_no: 화면번호 ---> 종목코드라고 설명되어 있음???
        :param code_list: string - 종목리스트 (; 으로 구분)
        :param condi_name: string - 조건식명
        :param condi_index: int - 조건식명 index
        :param next: int - 연속조회유무 (0: 연속조회 없음, 2: 연속 조회)
        :return:
        """
        pass

    def _on_receive_condition_ver(self, ret_code, condition_text):
        """
        Kiwoom Receive Condition Data Callback
        로컬에 사용자 조건식 저장 성공 여부를 확인하는 시점
        :param ret_code: int - 사용자 조건식 저장 성공여부 (1:성공, 나머지:실패)
        :param condition_text: string - 사용자 조건식 문자열(100^조건명1;101^조건명2; ...)
        :return: 없음
        """
        pass

    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """
        Kiwoom Receive Chejan Data Callback, 체결데이터를 받은 시점을 알려준다.
        :param gubun: string - 체결 구분 (0:주문체결통보, 1:잔고통보, 3:특이신호)
        :param item_cnt: int - 아이템 갯수
        :param fid_list: string - 데이터리스트 (데이터 구분은 ';')
        :return:
        """
        pass

    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """
        Kiwoom Receive Msg Callback, 서버통신 후 메시지를 받은 시점을 알려준다.
        :param screen_no: string - 화면번호
        :param rqname: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param trcode: string - TRansaction name
        :param msg: string - 서버 메시지
        :return:
        """
        pass

    def _comm_connect(self):
        """
        키움 서버에 로그인을 시도합니다. (dynamicCall)
        dynamicCall 수행후 이벤트 lock
        :return: int - 0:로그인 성공, 음수:로그인 실패
        """
        self.dynamicCall("CommConnect()")
        self.evt_loop.exec_()  # lock event
        return self.ret_data

    # public kiwoom api
    def login(self):
        """
        키움 서버에 로그인을 시도합니다.
        :return: int - 0:로그인 성공, 음수:로그인 실패
        """
        return self._comm_connect()

    def get_connect_state(self):
        """
        현재 로그인 상태를 알려줍니다.
        :return: Int - 리턴값 1:연결, 0:연결안됨
        """
        return self.dynamicCall("GetConnectState()")

    def get_server_gubun(self):
        """
        현재 모의투자인지, 실투인지 알려준다.
        :return:
        """
        return self.dynamicCall("GetLoginInfo(QString)", ["GetServerGubun"])

    def get_master_stock_name(self, code):
        """
        종목코드에 해당하는 종목명을 return 한다.
        :param code: string - 종목코드
        :return: code_name: string - 종목명
        """
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_theme_group_list(self, n_type):
        """
        키움증권에서 제공하는 주식테마 정보를 알려준다.
        :param n_type: int - 정렬순서 (0:코드순, 1:테마순)
        :return: theme_info_list: list - [[테마코드1, 테마명1], [theme_code2, theme_name2], ... [theme_codeN, theme_nameN]]
        # 테마코드1|테마명1;테마코드2|테마명2
        # ex) 100|태양광_폴리실리콘;152|합성섬유
        """
        theme_group_list = self.dynamicCall("GetThemeGroupList(int)", n_type)
        theme_info_list = [theme.split("|") for theme in theme_group_list.split(";")]
        return theme_info_list

    def get_theme_group_code_list(self, theme_code):
        """
        특정 테마코드에 해당하는 종목리스트를 반환한다.
        :param theme_code: string 테마코드
        :return: code_list: list - [str, str, ..., str] stock_code 리스트
        # 종목코드1;종목코드2
        # A000660;A005930
        """
        theme_group_code = self.dynamicCall("GetThemeGroupCode(QString)", theme_code)
        code_list = theme_group_code.split(";")
        return code_list

    def get_code_list_by_market(self, market):
        """
        kospi, kosdaq 시장별 주식종목 리스트를 반환한다.
        :param market: String  0:kospi, 10:kosdaq
        :return: code_list: list - [code_name1:str, code_name2:str, ..., code_nameN:str]
        """
        if isinstance(market, int):
            market = str(market)
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.strip(';').split(';')
        return code_list

    def get_condition_load(self):
        """
        사용자 조건검색 목록을 서버에 요청합니다.
        조건검색 목록을 모두 수신하면 OnReceiveConditionVer()이벤트 함수가 호출됩니다.
        :return: 1:성공, others:실패
        """
        pdb.set_trace()
        ret = self.dynamicCall("GetConditionLoad()")
        if ret != 1:
            return False

        self.condition_loop = QEventLoop()
        self.condition_loop.exec_()
        return self.condition

    def req_condition_search(self, screen_no, condi_name, condi_index, search_type):
        """
        사용자 조건검색식을 이용하여 검색을 하고, 검색된 종목을 return 한다.
        이 메서드로 얻고자 하는 것은 해당 조건에 맞는 종목코드이다.
        해당 종목에 대한 상세정보는 setRealReg() 메서드로 요청할 수 있다.
        요청이 실패하는 경우는, 해당 조건식이 없거나, 조건명과 인덱스가 맞지 않거나, 조회 횟수를 초과하는 경우 발생한다.
        조건검색에 대한 결과는
        1회성 조회의 경우, receiveTrCondition() 이벤트로 결과값이 전달되며
        실시간 조회의 경우, receiveTrCondition()과 receiveRealCondition() 이벤트로 결과값이 전달된다.

        :param screen_no: string - 화면번호
        :param condi_name: string - 조건식이름
        :param condi_index: int - 조건식명 인덱스
        :param search_type: int - 조회구분(0:조건검색, 1:실시간 조건검색)
        :return: condition_search_resul: list - 종목코드 리스트
        """
        # 화면번호, 조건식이름, 조건명인덱스, 조회구분(0:조건검색, 1:실시간 조건검색)
        print("Start to Condition(%s) Search !" % condi_name)
        ret = self.dynamicCall("SendCondition(QString, QString, int, int)",
                               screen_no, condi_name, condi_index, search_type)
        if not ret:
            raise custom_error.KiwoomProcessingError("sendCondition(): 조건검색 요청 실패")
        self.condition_loop = QEventLoop()
        self.condition_loop.exec_()

        return self.condition_search_result

    def req_condition_search_stop(self, screen_no, condi_name, condi_index):
        """
        실시간 조건검색을 중지한다.
        :param screen_no: string - 화면번호
        :param condi_name: string - 조건식이름
        :param condi_index: int - 조건식명 인덱스
        :return: ret: int - 맞나 ??
        """
        print("Stop to Real Condition(%s) Search !" % condi_name)
        ret = self.dynamicCall("SendConditionStop(QString, QString, int)",
                               screen_no, condi_name, condi_index)
        return ret

    def stock_min_data(self, code, tick='1', limit=0):
        """
        특정 주식종목의 분봉 데이터를 요청하는 함수.
        :param code: string - 주식코드
        :param tick: string - 분단위(1, 3, 5, 10, 15, 30, 45, 60)
        :param limit: int - 반복 request 제한 횟수
        :return:
        """
        self.ret_data = self.tr_mgr.opt10080('주식분봉', code, tick, '1111', limit)
        return self.ret_data

    def stock_day_data(self, code, date, limit=0):
        """
        특정 주식종목의 일봉 데이터를 요청하는 함수.
        :param code: string - 주식코드
        :param date: string - YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param limit: int - 반복 request 제한 횟수
        :return:
        """
        self.ret_data = self.tr_mgr.opt10081('주식일봉', code, date, '1111', limit)
        return self.ret_data

    def stock_week_data(self, code, s_date, e_date, limit=0):
        """
        특정 주식종목의 주봉 데이터를 요청하는 함수.
        :param code: string - 주식코드
        :param s_date: string - YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param e_date: string - YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param limit: int - 반복 request 제한 횟수
        :return:
        """
        self.ret_data = self.tr_mgr.opt10082('주식주봉', code, s_date, e_date, '1111', limit)
        return self.ret_data

    def stock_month_data(self, code, s_date, e_date, limit=0):
        """
        특정 주식종목의 월봉 데이터를 요청하는 함수.
        :param code: string - 주식코드
        :param s_date: string - YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param e_date: string - YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        :param limit: int - 반복 request 제한 횟수
        :return:
        """
        self.ret_data = self.tr_mgr.opt10083('주식월봉', code, s_date, e_date, '1111', limit)
        return self.ret_data

    def _get_comm_data_ex(self, trcode, output_name):
        """
        GetCommData 로 하나씩 받아오지 않고, 여러개의 값을 한번에 배열로 읽어옴.
        KOA의 TR목록에 OUTPUT에 보이는 멀티데이터 이름을 output_name에 적으면 됨.
        _on_receive_tr_data() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.
        :param trcode: string - TRansaction name
        :param output_name:
        :return:
        """
        ret = self.dynamicCall("GetCommDataEx(QString, QString)", trcode, output_name)
        return ret

    def _set_input_value(self, id, value):
        """
        Tran 입력 값을 서버통신 전에 입력한다
        :param id: string - 아이템 명
        :param value: string - 입력값
        :return: None
        """
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def _comm_rq_data(self, rqname, trcode, next, screen_no):
        """
        Tran을 서버로 송신한다.
        :param rqname: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param trcode: string - TRansaction name
        :param next: int -
        :param screen_no: string - 화면번호
        :return:
        """
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, int(next), screen_no)
        # when receive data, invoke self._on_receive_tr_data
        self.evt_loop.exec_()  # lock event loop

    def _get_repeat_cnt(self, trcode, rqname):
        """
        레코드 반복횟수를 반환한다.
        :param trcode: string - TRansaction name
        :param rqname: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :return:
        """
        return self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)

    def _get_comm_data(self, trcode, field_name, index, item_name):
        """

        :param trcode: string - TRansaction name
        :param field_name: string -
        :param index: int -
        :param item_name: string -
        :return:
        """
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, field_name, index, item_name)
        return ret.strip()
