import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import os
import pandas as pd
import pdb
import random
import logging
import logging.config
from pprint import pprint
from kiwoom import custom_error
from kiwoom.tr import TrManager
from kiwoom.tr import TrController
from collections import deque
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from kiwoom import constant
from util import common


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.tr_mgr = TrManager(self)
        self.evt_loop = QEventLoop()  # lock/release event loop
        self.ret_data = None
        self.req_queue = deque(maxlen=10)
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.tr_controller = TrController()

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
        :param real_data: string - 실시간 데이터 전문
        """
        print("code:", code, type(code))
        print("real_type:", real_type, type(real_type))
        # print("real_data:", real_data, type(real_data))
        print("real_data:", repr(real_data))

        print("cwd:", os.getcwd())
        with open(real_type + ".txt", "a") as f:
            f.write(real_data + "\n")

        fid_data = {
            '주식시세': {
                10: '현재가',
                11: '전일대비',
                12: '등락율',
                27: '최우선매도호가',
                28: '최우선매수호가',
                13: '누적거래량',
                14: '누적거래대금',
                16: '시가',
                17: '고가',
                18: '저가',
                25: '전일대비기호',
                26: '전일거래량대비',
                29: '거래대금증감',
                30: '거일거래량대비',
                31: '거래회전율',
                32: '거래비용',
                311: '시가총액(억)'
            }
        }
        """
        result = []
        for fid in fid_data[real_type]:
            value = self._get_comm_real_data(code, fid)
            result.append(value)
            print("Value: " + value)
            
        return result
        """

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
        print("_on_receive_tr_condition")
        max_char_cnt = 60
        print("[조건 검색 결과]".center(max_char_cnt, '-'))
        data = [
            ("screen_no", screen_no),
            ("code_list", code_list),
            ("condi_name", condi_name),
            ("condi_index", condi_index),
            ("next", next)
        ]
        max_key_cnt = max(len(d[0]) for d in data)
        for d in data:
            key = ("* " + d[0]).rjust(max_key_cnt)
            print("{0}: {1}".format(key, d[1]))
        print("-" * max_char_cnt)

        if bool(code_list):
            self.condition_search_result = code_list.strip(';').split(";")
        else:
            self.condition_search_result = []

        self.evt_loop.exit()  # lock event

    def _on_receive_condition_ver(self, ret_code, condition_text):
        """
        Kiwoom Receive Condition Data Callback
        로컬에 사용자 조건식 저장 성공 여부를 확인하는 시점
        :param ret_code: int - 사용자 조건식 저장 성공여부 (1:성공, 나머지:실패)
        :param condition_text: string - 사용자 조건식 문자열(100^조건명1;101^조건명2; ...)
        :return: 없음
        """
        if ret_code != 1:
            print("[Error] Fail to load user condition")
            return False

        print("Success to load user condition")
        condi_name_list = self.get_condition_name_list()
        self.condition = {}
        for condition_info in condi_name_list.split(";")[:-1]:
            condi_index, condi_name = condition_info.split("^")
            self.condition[condi_name] = condi_index
        self.evt_loop.exit()

    def _on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        """
        Kiwoom Receive Chejan Data Callback, 체결데이터를 받은 시점을 알려준다.
        :param gubun: string - 체결 구분 (0:주문체결통보, 1:잔고통보, 3:특이신호)
        :param item_cnt: int - 아이템 갯수
        :param fid_list: string - 데이터리스트 (데이터 구분은 ';')
        :return:
        """
        print("(!)[Callback] _on_receive_chejan_data")
        print("gubun(0:주문체결통보, 1:잔고통보, 3:특이신호): ", gubun)
        print("item_cnt: ", item_cnt)
        print("fid_list: ", fid_list)


    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        """
        Kiwoom Receive Msg Callback, 서버통신 후 메시지를 받은 시점을 알려준다.
        :param screen_no: str - 화면번호
        :param rqname: str - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
        :param trcode: str - TRansaction name
        :param msg: str - 서버 메시지
        :return:
        """
        print("(!)[Callback] _on_receive_msg")
        print("screen_no: ", screen_no)
        print("rqname: ", rqname)
        print("trcode(TRansaction name): ", trcode)
        print("msg: ", msg)

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
        :param market: str  0:kospi, 10:kosdaq
        :return: code_list: list - [code_name1:str, code_name2:str, ..., code_nameN:str]
        """
        if isinstance(market, int):
            market = str(market)
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.strip(';').split(';')
        return code_list

    def get_branch_code_name(self):
        """
        회원사 코드와 이름을 반환합니다.
        :return: str - 회원사코드|회원사명;회원사코드|회원사명
        """
        ret = self.dynamicCall("GetBranchCodeName()")
        return dict([tuple(d.split("|")) for d in ret.split(";")])

    def get_condition_load(self):
        """
        서버에 저장된 사용자 조건식을 조회해서 임시로 파일에 저장.
        사용자 조건검색 목록을 서버에 요청합니다.
        조건검색 목록을 모두 수신하면 OnReceiveConditionVer()이벤트 함수가 호출됩니다.
        :return: 1:성공, others:실패
        """
        ret = self.dynamicCall("GetConditionLoad()")
        if ret != 1:
            return False
        self.evt_loop.exec_()
        return self.condition

    def get_condition_name_list(self):
        """
        조건검색 조건명 리스트를 받아온다.
        :return: str - 조건명 리스트(인덱스^조건명)
        """
        ret = self.dynamicCall("GetConditionNameList()")
        return ret

    @common.type_check
    def send_condition(self, screen_no: str, condi_name: str, condi_index: int, search_type: int):
        """
        사용자 조건검색식을 이용하여 검색을 하고, 검색된 종목을 return 한다.
        이 메서드로 얻고자 하는 것은 해당 조건에 맞는 종목코드이다.
        해당 종목에 대한 상세정보는 setRealReg() 메서드로 요청할 수 있다.
        요청이 실패하는 경우는, 해당 조건식이 없거나, 조건명과 인덱스가 맞지 않거나, 조회 횟수를 초과하는 경우 발생한다.
        조건검색에 대한 결과는
        1회성 조회의 경우, receiveTrCondition() 이벤트로 결과값이 전달되며
        실시간 조회의 경우, receiveTrCondition()과 receiveRealCondition() 이벤트로 결과값이 전달된다.

        :param screen_no: str - 화면번호
        :param condi_name: str - 조건식이름
        :param condi_index: int - 조건식명 인덱스
        :param search_type: int - 조회구분(0:조건검색, 1:실시간 조건검색)
        :return: condition_search_result: list - 종목코드 리스트
        """
        # 화면번호, 조건식이름, 조건명인덱스, 조회구분(0:조건검색, 1:실시간 조건검색)
        print("Start to Condition(%s) Search !" % condi_name)
        ret = self.dynamicCall("SendCondition(QString, QString, int, int)",
                               screen_no, condi_name, condi_index, search_type)
        if ret == 0:
            raise constant.KiwoomProcessingError("sendCondition(): 조건검색 요청 실패")
        self.evt_loop.exec_()  # lock event

        return self.condition_search_result

    def send_condition_stop(self, screen_no, condi_name, condi_index):
        """
        실시간 조건검색을 중지한다. (=조건검색 실시간 중지TR을 송신한다)
        :param screen_no: str - 화면번호
        :param condi_name: str - 조건식이름
        :param condi_index: int - 조건식명 인덱스
        :return:
        """
        print("Stop to Real Condition(%s) Search !" % condi_name)
        self.dynamicCall("SendConditionStop(QString, QString, int)",
                         screen_no, condi_name, condi_index)

    def get_per_info(self, per_condi):
        """
        고저PER 종목 100개를 return하는 함수
        :param per_condi: 1:코스피저PER, 2:코스피고PER, 3:코스닥저PER, 4:코스닥고PER
        :return:
        """
        self.ret_data = self.tr_mgr.opt10026('고저PER', per_condi, "1111")
        return self.ret_data

    @common.type_check
    def stock_price_by_min(self, code: str, tick: str, screen_no: str, begin_date: datetime, end_date: datetime):
        """
        특정 주식종목의 분봉 데이터를 요청하는 함수. tr요청시 한번에 최대 600개까지만 return 가능.
        :param code: str - 주식코드
        :param tick: str - 분단위(1, 3, 5, 10, 15, 30, 45, 60)
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:
        """
        self.ret_data = []
        while True:
            # print("Do Transition opt10080")
            curr_result = self.tr_mgr.opt10080('주식분봉', code, tick, screen_no, begin_date, end_date)
            if not bool(curr_result):
                break
            self.ret_data += curr_result
            end_date = self.ret_data[-1]['date'] - timedelta(minutes=int(tick))
            time.sleep(0.2)  # delay
        return self.ret_data

    @common.type_check
    def stock_price_by_day(self, code: str, screen_no: str, begin_date: datetime, end_date: datetime):
        """
        특정 주식종목의 일봉 데이터를 요청하는 함수. tr요청시 한번에 최대 600개까지만 return 가능.
        :param code: string - 주식코드
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:
        """
        self.ret_data = []
        while True:
            # print("Do Transition opt10081")
            curr_result = self.tr_mgr.opt10081('주식일봉', code, screen_no, begin_date, end_date)
            if not bool(curr_result):
                break
            self.ret_data += curr_result
            end_date = self.ret_data[-1]['date'] - timedelta(days=1)
            time.sleep(0.2)  # delay
        return self.ret_data

    @common.type_check
    def stock_price_by_week(self, code: str, screen_no: str, begin_date: datetime, end_date: datetime):
        """
        특정 주식종목의 주봉 데이터를 요청하는 함수. tr요청시 한번에 최대 600개까지만 return 가능.
        :param code: string - 주식코드
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:
        """
        self.ret_data = []
        while True:
            # print("Do Transition opt10082")
            curr_result = self.tr_mgr.opt10082('주식주봉', code, screen_no, begin_date, end_date)
            if not bool(curr_result):
                break
            self.ret_data += curr_result
            end_date = self.ret_data[-1]['date'] - timedelta(weeks=1)
            time.sleep(0.2)  # delay
        return self.ret_data

    @common.type_check
    def stock_price_by_month(self, code: str, screen_no: str, begin_date: datetime, end_date: datetime):
        """
        특정 주식종목의 월봉 데이터를 요청하는 함수. tr요청시 한번에 최대 600개까지만 return 가능.
        :param code: string - 주식코드
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:
        """
        self.ret_data = []
        while True:
            # print("Do Transition opt10083")
            curr_result = self.tr_mgr.opt10083('주식월봉', code, screen_no, begin_date, end_date)
            if not bool(curr_result):
                break
            self.ret_data += curr_result
            end_date = self.ret_data[-1]['date'] - relativedelta(months=1)
            time.sleep(0.2)  # delay
        return self.ret_data

    def get_master_listed_stock_cnt(self, code):
        """
        종목코드의 상장주식수를 반환한다.
        :param code: str - 종목코드
        :return: int - 상장주식수
        """
        ret = self.dynamicCall("GetMasterListedStockCnt(QString)", code)
        return ret

    def get_master_construction(self, code):
        """
        종목코드의 감리구분을 반환한다.
        :param code: str - 종목코드
        :return: str - 감리구분 (정상, 투자주의, 투자경고, 투자위험, 투자주의환기종목)
        """
        ret = self.dynamicCall("GetMasterConstruction(QString)", code)
        return ret

    def get_master_listed_stock_date(self, code):
        """
        종목코드의 상장일을 반환한다.
        :param code: str - 종목코드
        :return: str - 상장일 (YYYYMMDD)
        """
        ret = self.dynamicCall("GetMasterListedStockDate(QString)", code)
        return ret

    def get_master_last_price(self, code):
        """
        종목코드의 전일가를 반환한다.
        :param code: str - 종목코드
        :return: str - 전일가 (ex. '00085000')
        """
        ret = self.dynamicCall("GetMasterLastPrice(QString)", code)
        return ret

    def get_master_stock_state(self, code):
        """
        종목코드의 종목상태를 반환한다.
        :param code: str - 종목코드
        :return: str - 종목상태(정상, 증거금100%, 거래정지, 관리종목, 감리종목, 투자유의종목, 담보대출, 액면분할, 신용가능)
                       ex. LG전자 -> '증거금20%|담보대출|신용가능'
        """
        ret = self.dynamicCall("GetMasterStockState(QString)", code)
        return ret

    def get_login_info(self, tag):
        """
        로그인한 사용자 정보를 반환한다.

        :return: str - 반환값
        BSTR sTag에 들어 갈 수 있는 값은 아래와 같음
        “ACCOUNT_CNT” – 전체 계좌 개수를 반환한다.
        "ACCNO" – 전체 계좌를 반환한다. 계좌별 구분은 ‘;’이다.
        “USER_ID” - 사용자 ID를 반환한다.
        “USER_NAME” – 사용자명을 반환한다.
        “KEY_BSECGB” – 키보드보안 해지여부. 0:정상, 1:해지
        “FIREW_SECGB” – 방화벽 설정 여부. 0:미설정, 1:설정, 2:해지
        Ex) openApi.GetLoginInfo(“ACCOUNT_CNT”);
        """
        ret = self.dynamicCall("GetLoginInfo(QString)", tag)
        return ret

    def set_real_reg(self, screen_no, codes, fids, reg_type):
        """
        실시간 데이터 요청 메서드
        종목코드와 fid 리스트를 이용해서 실시간 데이터를 요청하는 메서드입니다.
        한번에 등록 가능한 종목과 fid 갯수는 100종목, 100개의 fid 입니다.
        실시간등록타입을 0으로 설정하면, 첫 실시간 데이터 요청을 의미하며
        실시간등록타입을 1로 설정하면, 추가등록을 의미합니다.
        실시간 데이터는 실시간 타입 단위로 receiveRealData() 이벤트로 전달되기 때문에,
        이 메서드에서 지정하지 않은 fid 일지라도, 실시간 타입에 포함되어 있다면, 데이터 수신이 가능하다.
        :param screen_no: string - 화면번호
        :param codes: string - 종목코드 리스트(종목코드;종목코드;...)
        :param fids: string - fid 리스트(fid;fid;...)
        :param reg_type: string - 실시간등록타입(0: 첫 등록, 1: 추가 등록)
                                  처음등록할때에는 꼭 real_type이 0이어야 하고, 이후부터 1로 설정가능.
        """
        print("dynamic Call - SetRealReg")
        ret = self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_no, codes, fids, reg_type)
        return ret

    def set_real_remove(self, screen_no, code):
        """
        실시간 데이터 중지 메서드
        setRealReg() 메서드로 등록한 종목만, 이 메서드를 통해 실시간 데이터 받기를 중지 시킬 수 있습니다.
        :param screen_no: str - 화면번호 또는 "ALL" 키워드 사용가능
        :param code: str - 종목코드 또는 "ALL" 키워드 사용가능
        """
        self.dynamicCall("SetRealRemove(QString, QString)", screen_no, code)

    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga_gubun, orig_order_no):
        """
        매도/매수 주문 함수
        주문유형(order_type) (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
        hoga_gubun – 00:지정가,    03:시장가,    05:조건부지정가,   06:최유리지정가, 07:최우선지정가,
                     10:지정가IOC, 13:시장가IOC, 16:최유리IOC,      20:지정가FOK,
                     23:시장가FOK, 26:최유리FOK, 61:장전시간외종가,  62:시간외단일가, 81:장후시간외종가
        ※ 시장가, 최유리지정가, 최우선지정가, 시장가IOC, 최유리IOC, 시장가FOK, 최유리FOK, 장전시간외, 장후시간외 주문시 주문가격을 입력하지 않습니다.
        :param rqname: str -
        :param screen_no: str -
        :param acc_no: str -
        :param order_type: int -
        :param code: str -
        :param quantity: int -
        :param price: int -
        :param hoga_gubun: str -
        :param orig_order_no: str -
        :return:
        """
        ret = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                               [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga_gubun, orig_order_no])
        return ret

    def get_api_module_path(self):
        ret = self.dynamicCall("GetAPIModulePath()")
        return ret

    def _get_comm_real_data(self, code, fid):
        """
        실시간 데이터 획득 메서드
        이 메서드는 반드시 receiveRealData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.
        :param code: str - 종목코드
        :param fid: - 실시간 타입에 포함된 fid
        :return: string - fid에 해당하는 데이터
        """
        ret = self.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return ret

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

    def _set_input_values(self, args):
        """
        다수의 Tran 입력 값을 서버통신 전에 입력한다
        :param args: list [(id, value), ...] -> _set_input_value의 인자
        :return: None
        """
        for i, v in args:
            self._set_input_value(i, v)

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
        self.tr_controller.prevent_excessive_request()
        ret_code = self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, int(next), screen_no)
        # when receive data, invoke self._on_receive_tr_data
        self.evt_loop.exec_()  # lock event loop
        return ret_code

    def _get_repeat_cnt(self, trcode, rqname):
        """
        레코드 반복횟수를 반환한다.
        :param trcode: str - TRansaction name
        :param rqname: str - TR 요청명(commRqData() 메소드 호출시 사용된 requestName)
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
