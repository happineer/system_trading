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
        self.OnEventConnect.connect(self._on_event_connect)
        self.OnReceiveTrData.connect(self._on_receive_tr_data)
        self.OnReceiveRealData.connect(self._on_receive_real_data)
        self.OnReceiveRealCondition.connect(self._on_receive_real_condition)
        self.OnReceiveTrCondition.connect(self._on_receive_tr_condition)
        self.OnReceiveConditionVer.connect(self._on_receive_condition_ver)
        self.OnReceiveChejanData.connect(self._on_receive_chejan_data)
        self.OnReceiveMsg.connect(self._on_receive_msg)

    # Kiwoom callback function
    def _on_event_connect(self, err_code):
        """
        Kiwoom Login Callback
        :param err_code:
        :return:
        """
        self.login_loop.exit()

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, _1, _2, _3, _4):
        """
        Kiwoom Receive TR Callback
        조회요청 응답을 받거나 조회데이터를 수신했을 때 호출됩니다.
        requestName과 trCode는 commRqData()메소드의 매개변수와 매핑되는 값 입니다.
        조회데이터는 이 이벤트 메서드 내부에서 getCommData() 메서드를 이용해서 얻을 수 있습니다.
        :param screenNo: string - 화면번호(4자리)
        :param rqname: string - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param trcode: string
        :param record_name: string
        :param next: string - 조회('0': 남은 데이터 없음, '2': 남은 데이터 있음)
        """
        pass

    def _on_receive_real_data(self, code, real_type, real_data):
        """
        Kiwoom Receive Realtime Data Callback
        실시간 데이터를 수신할 때 마다 호출되며,
        setRealReg() 메서드로 등록한 실시간 데이터도 이 이벤트 메서드에 전달됩니다.
        getCommRealData() 메서드를 이용해서 실시간 데이터를 얻을 수 있습니다.
        :param code: string - 종목코드
        :param real_type: string - 실시간 타입(KOA의 실시간 목록 참조)
        :param realData: string - 실시간 데이터 전문
        """
        pass

    def _on_receive_real_condition(self, code, update_type, condi_name, condi_index):
        """
        Kiwoom Receive Realtime Condition Result(stock list) Callback
        조건검색 실시간 편입, 이탈 종목을 받을 시점을 알려준다.
        condi_name 에 해당하는 종목이 실시간으로 들어옴.
        update_type으로 편입된 종목인지, 이탈된 종목인지 구분한다.
        * 조건식 검증할때, 어떤 종목이 검출된 시간을 본 함수내에서 구현해야 함
        :param code: string - 종목코드
        :param update_type: string - 편입("I"), 이탈("D")
        :param condi_name: string - 조건명
        :param condi_index: string - 조건명 인덱스
        :return: 없음
        """
        pass

    def _on_receive_tr_condition(self, screen_no, code_list, condi_name, condi_index, next):
        """
        Kiwoom Receive TR Condition Callback
        :param screen_no:
        :param code_list:
        :param condi_name:
        :param condi_index:
        :param next:
        :return:
        """
        pass

    def _on_receive_condition_ver(self, ret_code, condition_text):
        """
        Kiwoom Receive Condition Data Callback
        로컬에 사용자 조건식 저장 성공 여부를 확인하는 시점
        :param ret_code: int - 성공(1), 실패(not 1)
        :param condition_text: string - 사용자 조건식 문자열(100^조건명1;101^조건명2; ...)
        :return: 없음
        """
        pass

    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """
        Kiwoom Receive Chejan Data Callback
        :param gubun:
        :param item_cnt:
        :param fid_list:
        :return:
        """
        pass

    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """
        Kiwoom Receive Msg Callback
        :param screen_no:
        :param rqname:
        :param trcode:
        :param msg:
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