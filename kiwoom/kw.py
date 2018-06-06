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

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._on_event_connect) # 로긴 이벤트
        self.OnReceiveTrData.connect(self._on_receive_tr_data) # tr 수신 이벤트
        self.OnReceiveRealData.connect(self._on_receive_real_data) # 실시간 시세 이벤트
        self.OnReceiveRealCondition.connect(self._on_receive_real_condition) # 조건검색 실시간 편입, 이탈종목 이벤트
        self.OnReceiveTrCondition.connect(self._on_receive_tr_condition) # 조건검색 조회응답 이벤트
        self.OnReceiveConditionVer.connect(self._on_receive_condition_ver) # 로컬에 사용자조건식 저장 성공여부 응답 이벤트
        self.OnReceiveChejanData.connect(self._on_receive_chejan_data) # 주문 접수/확인 수신시 이벤트
        self.OnReceiveMsg.connect(self._on_receive_msg) # 수신 메시지 이벤트

    # Kiwoom callback function
    def _on_event_connect(self, err_code):
        """
        Kiwoom Login Callback, 서버 접속 관련 이벤트
        :param err_code: int - 0:로그인 성공, 음수:로그인 실패
        :return:
        """
        self.login_loop.exit()

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, _1, _2, _3, _4):
        """
        Kiwoom Receive TR Callback, 서버통신 후 데이터를 받은 시점을 알려준다.
        조회요청 응답을 받거나 조회데이터를 수신했을 때 호출됩니다.
        requestName과 trCode는 commRqData()메소드의 매개변수와 매핑되는 값 입니다.
        조회데이터는 이 이벤트 메서드 내부에서 getCommData() 메서드를 이용해서 얻을 수 있습니다.
        :param screen_no: string - 화면번호(4자리)
        :param rqname: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param trcode: string - TRansaction name
        :param record_name: string - Record name
        :param next: string - 연속조회유무 ('0': 남은 데이터 없음, '2': 남은 데이터 있음)
        """
        pass

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
        self.dynamicCall("CommConnect()")
        self.login_loop = QEventLoop()
        self.login_loop.exec_()

    def login(self):
        self._comm_connect()

    def get_connect_state(self):
        """
        현재 로그인 상태를 알려줍니다.
        :return: Int - 리턴값 1:연결, 0:연결안됨
        """
        return self.dynamicCall("GetConnectState()")