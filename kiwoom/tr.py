from functools import wraps

from kiwoom.constant import ReturnCode
from util import strutil
from kiwoom.tr_post import PostFn
from kiwoom import constant
from datetime import datetime
import pdb
from collections import deque
from collections import OrderedDict
import time
import ast


class TrManager():
    def __init__(self, kw):
        self.kw = kw
        self.tr_ret_data = None
        self.tr_next = 0
        self.tr_continue = None
        self.tr_post = PostFn(self)

    def init_tr_ret_data(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            args[0].tr_ret_data = []
            ret = f(*args, **kwargs)
            return ret
        return wrapper

    @init_tr_ret_data
    def opt10026(self, rqname, per, screen_no):
        self.kw._set_input_value("PER구분", per)
        self.kw._comm_rq_data(rqname, "opt10026", "0", screen_no)  # lock event loop
        return self.tr_ret_data  # data set when post_tr_function

    @init_tr_ret_data
    def opt10080(self, rqname, code, tick, screen_no, begin_date, end_date):
        """
        특정 주식종목의 분봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param tick: str - 분단위(1, 3, 5, 10, 15, 30, 45, 60)
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:
        """
        def tr_process(rqname, code, tick, screen_no, next):
            self.kw.code = code
            self.kw._set_input_values([("종목코드", code), ("틱범위", tick), ("수정주가구분", "0")])
            ret_code = self.kw._comm_rq_data(rqname, "opt10080", next, screen_no)  # lock event loop
            if ReturnCode.OP_ERR_NONE != ret_code:
                raise Exception("[KiWoom Error][opt10080] %s" % ReturnCode.CAUSE[ret_code])
        try:
            tr_process(rqname, code, tick, screen_no, 0)
            # data(self.tr_ret_data) is set when post_tr_function
            if self.tr_next == '0':
                return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

            if bool(begin_date) and begin_date >= self.tr_ret_data[-1]['date']:
                return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

            while self.tr_next == '2' and begin_date < self.tr_ret_data[-1]['date']:
                tr_process(rqname, code, tick, screen_no, 2)

            return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]
        except Exception as e:
            print(e)

        return []

    def post_opt10080(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '주식분봉차트조회')
        f = ["현재가", "거래량", "체결시간", "시가", "고가", "저가", "수정주가구분", "수정비욜",
             "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "체결시간": 0, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
                    if "체결시간" == field:  # YYYYMMDDHHMMSS
                        stock_data['date'] = stock_data['체결시간']
                        del stock_data['체결시간']
                    stock_data['code'] = self.kw.code
            self.tr_ret_data.append(stock_data)
        self.tr_next = next

    @init_tr_ret_data
    def opt10081(self, rqname, code, screen_no, begin_date, end_date):
        """
        특정 주식종목의 일봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:

        end_date_str: str - newest date. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        """
        end_date_str = end_date.strftime("%Y%m%d")

        def tr_process(rqname, code, screen_no, end_date_str, next):
            self.kw.code = code
            self.kw._set_input_values([("종목코드", code), ("기준일자", end_date_str), ("수정주가구분", "0")])
            self.kw._comm_rq_data(rqname, "opt10081", next, screen_no)  # lock event loop

        tr_process(rqname, code, screen_no, end_date_str, 0)
        # data(self.tr_ret_data) is set when post_tr_function
        if self.tr_next == '0' or not bool(end_date):
            return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

        while end_date < self.tr_ret_data[-1]['date'] and self.tr_next == '2':
            tr_process(rqname, code, screen_no, end_date_str, 2)

        return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

    def post_opt10081(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '주식일봉차트조회')
        f = ["종목코드", "현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비욜", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "거래대금": 0, "일자": 0, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
                    if "일자" == field:
                        stock_data['date'] = stock_data['일자']
                        del stock_data['일자']
                    stock_data['code'] = self.kw.code
            self.tr_ret_data.append(stock_data)
        self.tr_next = next

    @init_tr_ret_data
    def opt10082(self, rqname, code, screen_no, begin_date, end_date):
        """
        특정 주식종목의 주봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:

        begin_date_str: str - oldest date. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        end_date_str: str - newest date. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        """
        begin_date_str = begin_date.strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")

        def tr_process(rqname, code, screen_no, begin_date_str, end_date_str, next):
            self.kw.code = code
            self.kw._set_input_values([("종목코드", code), ("기준일자", end_date_str), ("끝일자", begin_date_str), ("수정주가구분", "0")])
            self.kw._comm_rq_data(rqname, "opt10082", next, screen_no)  # lock event loop

        tr_process(rqname, code, screen_no, begin_date_str, end_date_str, 0)
        # data set when post_tr_function
        if self.tr_next == '0' or not bool(end_date_str):
            return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

        while end_date < self.tr_ret_data[-1]['date'] and self.tr_next == '2':
            tr_process(rqname, code, screen_no, begin_date_str, end_date_str, 2)

        return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

    def post_opt10082(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '주식주봉차트조회')
        f = ["현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비욜", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "거래대금": 0, "일자": 0, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
                    if "일자" == field:
                        stock_data['date'] = stock_data['일자']
                        del stock_data['일자']
                    stock_data['code'] = self.kw.code
            self.tr_ret_data.append(stock_data)
        self.tr_next = next

    @init_tr_ret_data
    def opt10083(self, rqname, code, screen_no, begin_date, end_date):
        """
        특정 주식종목의 주봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:

        begin_date_str: str - oldest date. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        end_date_str: str - newest date. YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        """
        begin_date_str = begin_date.strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")

        def tr_process(rqname, code, screen_no, begin_date_str, end_date_str, next):
            self.kw.code = code
            self.kw._set_input_values([("종목코드", code), ("기준일자", end_date_str), ("끝일자", begin_date_str), ("수정주가구분", "0")])
            self.kw._comm_rq_data(rqname, "opt10083", next, screen_no)  # lock event loop

        tr_process(rqname, code, screen_no, begin_date_str, end_date_str, 0)
        # data set when post_tr_function
        if self.tr_next == '0' or not bool(end_date_str):
            return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

        while end_date < self.tr_ret_data[-1]['date'] and self.tr_next == '2':
            tr_process(rqname, code, screen_no, begin_date_str, end_date_str, 2)

        return [d for d in self.tr_ret_data if begin_date <= d['date'] <= end_date]

    def post_opt10083(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '주식월봉차트조회')
        f = ["현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비욜", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

        for d in data:
            stock_data = {"현재가": 0, "거래량": 0, "거래대금": 0, "일자": 0, "시가": 0, "고가": 0, "저가": 0}
            for field, val in zip(f, [_.strip() for _ in d]):
                if field in stock_data:
                    stock_data[field] = strutil.convert_data(field, val)
                    if "일자" == field:
                        stock_data['date'] = stock_data['일자']
                        del stock_data['일자']
                    stock_data['code'] = self.kw.code
            self.tr_ret_data.append(stock_data)
        self.tr_next = next

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
        print("(!)[Callback] _on_receive_tr_data")
        try:
            pdb.set_trace()
            post_fn = eval('self.post_' + trcode.lower())
            # post_fn = self.tr_post.fn_table[rqname]
            post_fn(trcode, rqname, next)
        except AttributeError as e:
            print(e)
        except Exception as e:
            print(e)

        self.kw.evt_loop.exit()  # release event loop

    def post_opt10026(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '고저PER')
        # data[0] = ['027410', 'BGF', '0.14', '-10750', '5', '-50', '-0.46', '478761', '-10750'], ...

        f = ["종목코드", "종목명", "PER", "현재가", "전일대비기호", "전일대비", "등락률", "현재거래량", "매도호가"]
        # 전일대비기호 : 2(상승), 3(변동없음), 5(하락)

        for d in data:
            d[2] = float(d[2])
            d[3] = abs(int(d[3]))
            d[5] = int(d[5])
            d[6] = float(d[6])
            d[7] = int(d[7])
            d[8] = abs(int(d[8]))
            self.tr_ret_data.append(dict(zip(f, d)))

    @init_tr_ret_data
    def optkwfid(self, rqname, code_list, screen_no, type_flag, next):
        """
        관심종목을 조회한다.
        :param rqname: str - 사용자 요청
        :param code_list: str - 종목리스트 (ex. code1;code2;...)
        :param screen_no: str - 화면번호
        :param type_flag: int - 조회구분 (0:주식관심종목정보, 3:선물옵션관심종목정보)
        :param next: int - 연속조회요청
        :return: list - 주식정보를 list형태로 반환
        """
        ret = self.kw._comm_kw_rq_data(rqname, code_list, screen_no, type_flag, next)  # lock event loop
        return self.tr_ret_data

    def post_optkwfid(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '관심종목정보')

        f = ["종목코드", "종목명", "현재가", "기준가", "전일대비", "전일대비기호", "등락율", "거래량", "거래대금", "체결량",
             "체결강도", "전일거래량대비", "매도호가", "매수호가", "매도1차호가", "매도2차호가", "매도3차호가", "매도4차호가",
             "매도5차호가", "매수1차호가", "매수2차호가", "매수3차호가", "매수4차호가", "매수5차호가", "상한가", "하한가",
             "시가", "고가", "저가", "종가", "체결시간", "예상체결가", "예상체결량", "자본금", "액면가", "시가총액", "주식수",
             "호가시간", "일자", "우선매도잔량", "우선매수잔량", "우선매도건수", "우선매수건수", "총매도잔량", "총매수잔량",
             "총매도건수", "총매수건수", "패리티", "기어링", "손익분기", "자본지지", "ELW행사가", "전환비율", "ELW만기일",
             "미결제약정", "미결제전일대비", "이론가", "내재변동성", "델타", "감마", "쎄타", "베가", "로"]

        for d in data:
            stock_data = OrderedDict([(k, v) for k, v in zip(f, [_.strip() for _ in d])])
            stock_data["체결시간"] = stock_data["일자"] + stock_data["체결시간"]
            stock_data["호가시간"] = stock_data["일자"] + stock_data["호가시간"]
            stock_data = OrderedDict([(k, strutil.convert_data(k, v)) for k, v in stock_data.items()])
            if "일자" in stock_data:
                stock_data['date'] = stock_data['일자']
                del stock_data['일자']
            self.tr_ret_data.append(stock_data)


class TrController(object):
    def __init__(self):
        self.queue = deque(maxlen=5)

    def prevent_excessive_request(self):
        # pdb.set_trace()
        self.queue.append(datetime.now())
        if len(self.queue) < 5:
            return

        duration = (self.queue[-1] - self.queue[0]).seconds

        if duration < 3:
            t_delay = 3 - duration
            print("[TrController] Delay {}s for avoiding excessive request status".format(t_delay))
            time.sleep(t_delay)
