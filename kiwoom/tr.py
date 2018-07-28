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
from pprint import pprint as pp
import ast


class TrManager():
    def __init__(self, kw):
        self.kw = kw
        self.logger = self.kw.logger
        self.tr_ret_data = None
        self.tr_next = 0
        self.tr_continue = None
        self.set_fidlist_n_mask()
        self.tr_post = PostFn(self)

    def set_fidlist_n_mask(self):
        # 10003 - 체결정보, 시간(HHMMSS)
        self.OPT10003_FIDLIST = ["시간", "현재가", "전일대비", "대비율", "우선매도호가단위",
                                 "우선매수호가단위", "체결거래량", "sign", "누적거래량", "누적거래대금", "체결강도"]
        self.OPT10003_MASK =    [str, float, float, float, float,
                                 float, float, str, float, float, float]

        self.OPT10004_FIDLIST = ["호가잔량기준시간",
                                 "매도10차선잔량대비", "매도10차선잔량", "매도10차선호가",
                                 "매도9차선잔량대비", "매도9차선잔량", "매도9차선호가",
                                 "매도8차선잔량대비", "매도8차선잔량", "매도8차선호가",
                                 "매도7차선잔량대비", "매도7차선잔량", "매도7차선호가",
                                 "매도6차선잔량대비", "매도6차선잔량", "매도6차선호가",
                                 "매도5차선잔량대비", "매도5차선잔량", "매도5차선호가",
                                 "매도4차선잔량대비", "매도4차선잔량", "매도4차선호가",
                                 "매도3차선잔량대비", "매도3차선잔량", "매도3차선호가",
                                 "매도2차선잔량대비", "매도2차선잔량", "매도2차선호가",
                                 "매도1차선잔량대비", "매도최우선잔량", "매도최우선호가",
                                 "매수최우선호가", "매수최우선잔량", "매수1차선잔량대비",
                                 "매수2차선호가", "매수2차선잔량", "매수2차선잔량대비",
                                 "매수3차선호가", "매수3차선잔량", "매수3차선잔량대비",
                                 "매수4차선호가", "매수4차선잔량", "매수4차선잔량대비",
                                 "매수5차선호가", "매수5차선잔량", "매수5차선잔량대비",
                                 "매수6차선호가", "매수6차선잔량", "매수6차선잔량대비",
                                 "매수7차선호가", "매수7차선잔량", "매수7차선잔량대비",
                                 "매수8차선호가", "매수8차선잔량", "매수8차선잔량대비",
                                 "매수9차선호가", "매수9차선잔량", "매수9차선잔량대비",
                                 "매수10차선호가", "매수10차선잔량", "매수10차선잔량대비",
                                 "총매도잔량직전대비", "총매도잔량", "총매수잔량", "총매수잔량직전대비",
                                 "시간외매도잔량", "시간외매수잔량", "시간외매수잔량대비"]
        self.OPT10004_MASK = [str,
                              float, float, float,  # 10
                              float, float, float,  # 9
                              float, float, float,  # 8
                              float, float, float,  # 7
                              float, float, float,  # 6
                              float, float, float,  # 5
                              float, float, float,  # 4
                              float, float, float,  # 3
                              float, float, float,  # 2
                              float, float, float,  # 1
                              float, float, float,  # 1
                              float, float, float,  # 2
                              float, float, float,  # 3
                              float, float, float,  # 4
                              float, float, float,  # 5
                              float, float, float,  # 6
                              float, float, float,  # 7
                              float, float, float,  # 8
                              float, float, float,  # 9
                              float, float, float,  # 10
                              float, float, float, float,
                              float, float, str]

        # 10019 - 가격급등락
        self.OPT10019_FIDLIST = ["종목코드", "종목분류", "종목명", "전일대비기호", "전일대비",
                                 "등락률", "기준가", "현재가", "기준대비", "거래량", "급등률"]
        self.OPT10019_MASK =    [str, str, str, str, float,
                                 float, float, float, float, float, float]

        # 10023 - 거래량급증
        self.OPT10023_FIDLIST = ["종목코드", "종목명", "현재가", "전일대비기호", "전일대비",
                                  "등락률", "이전거래량", "현재거래량", "급증량", "급증률"]
        self.OPT10023_MASK =    [str, str, float, str, float,
                                 float, float, float, float, float]

        # 10077 - 당일실현손익상세
        self.OPT10077_FIDLIST = ["종목명", "체결명", "매입단가", "체결가", "당일매도손익",
                                 "손익율", "당일매매수수료", "당일매매세금", "종목코드"]
        self.OPT10077_MASK =    [str, str, float, float, float,
                                 float, float, float, str]

        # 10085
        self.OPT10085_FIDLIST = ["일자", "종목코드", "종목명", "현재가", "매입가", "매입금액",
                                 "보유수량", "당일매도손익", "당일매매수수료", "당일매매세금",
                                 "신용구분", "대출일", "결제잔고", "청산가능수량", "신용금액",
                                 "신용이자", "만기일"]
        self.OPT10085_MASK =    [str, str, str, float, float, float,
                                 float, float, str, float,
                                 str, str, float, float, float,
                                 str, str]

        # 20002 - 업종별주가요청
        self.OPT20002_FIDLIST = ["종목코드", "종목명", "현재가", "전일대비기호", "전일대비",
                                 "등락률", "현재거래량", "매도호가", "매수호가", "시가", "고가", "저가"]
        self.OPT20002_MASK =    [str, str, float, str, float,
                                 float, float, float, float, float, float, float]

        # 20003 - 전업종지수
        self.OPT20003_FIDLIST = ["종목코드", "종목명", "현재가", "대비기호", "전일대비",
                                 "등락률", "거래량", "비중", "거래대금", "상한", "상승",
                                 "보합", "하락", "하한", "상장종목수"]
        self.OPT20003_MASK =    [str, str, float, str, float,
                                 float, float, str, float, float, float,
                                 float, float, float, float]

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
    def opt10001(self, rqname, code, screen_no):
        self.kw._set_input_value("종목코드", code)
        self.kw._comm_rq_data(rqname, "opt10001", "0", screen_no)  # lock event loop
        return self.tr_ret_data  # data set when post_tr_function

    def post_opt10001(self, trcode, rqname, next):
        fid_list_s = ["종목코드", "종목명", "결산월", "액면가", "자본금", "상장주식", "신용비율", "연중최고",
                      "연중최저", "시가총액", "시가총액비중", "외인소진률", "대용가", "PER", "EPS", "ROE", "PBR",
                      "EV", "BPS", "매출액", "영업이익", "당기순이익", "250최고", "250최저", "시가", "고가", "상한가",
                      "하한가", "기준가", "예상체결가", "예상체결수량", "250최고가일", "250최고가대비율", "250최저가일",
                      "250최저가대비율", "현재가", "대비기호", "전일대비", "등락율", "거래량", "거래대비", "액면가단위"]

        tmp = {}
        for f in fid_list_s:
            data = self.kw._get_comm_data(trcode, '주식기본정보', 0, f)
            tmp[f] = data
        self.tr_ret_data = tmp
        self.tr_next = next

    @init_tr_ret_data
    def opt10003(self, rqname, code, screen_no):
        self.kw._set_input_value("종목코드", code)
        self.kw._comm_rq_data(rqname, "opt10003", "0", screen_no)  # lock event loop

        # cnt = 0
        # while self.tr_next == "2":
        #     self.logger.debug("opt10003 tr req cnt: {}".format(cnt))
        #     self.kw._comm_rq_data(rqname, "opt10003", "2", screen_no)  # lock event loop
        return self.tr_ret_data  # data set when post_tr_function

    def post_opt10003(self, trcode, rqname, next):
        m_data = self.kw._get_comm_data_ex(trcode, '체결정보')
        for data in m_data:
            tmp = {}
            for fid, mask_f, d in zip(self.OPT10003_FIDLIST, self.OPT10003_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next


    @init_tr_ret_data
    def opt10004(self, rqname, code, screen_no):
        self.kw._set_input_value("종목코드", code)
        self.kw._comm_rq_data(rqname, "opt10004", "0", screen_no)  # lock event loop
        while self.tr_next == "2":
            self.kw._comm_rq_data(rqname, "opt10004", "2", screen_no)  # lock event loop

        return self.tr_ret_data  # data set when post_tr_function

    def post_opt10004(self, trcode, rqname, next):
        m_data = self.kw._get_comm_data_ex(trcode, '주식호가')
        for data in m_data:
            tmp = {}
            for fid, mask_f, d in zip(self.OPT10004_FIDLIST, self.OPT10004_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next

    @init_tr_ret_data
    def opt10019(self, rqname,
                 market, swing_gubun, time_gubun, time, vol_gubun,
                 stock_condi, credit_condi, price_condi, updown_limit,
                 screen_no):
        self.kw._set_input_value("시장구분", market)
        self.kw._set_input_value("등락구분", swing_gubun)
        self.kw._set_input_value("시간구분", time_gubun)
        self.kw._set_input_value("시간", time)
        self.kw._set_input_value("거래량구분", vol_gubun)
        self.kw._set_input_value("종목조건", stock_condi)
        self.kw._set_input_value("신용조건", credit_condi)
        self.kw._set_input_value("가격조건", price_condi)
        self.kw._set_input_value("상하한포함", updown_limit)
        self.kw._comm_rq_data(rqname, "opt10019", "0", screen_no)

        while self.tr_next == "2":
            self.kw._set_input_value("시장구분", market)
            self.kw._set_input_value("등락구분", swing_gubun)
            self.kw._set_input_value("시간구분", time_gubun)
            self.kw._set_input_value("시간", time)
            self.kw._set_input_value("거래량구분", vol_gubun)
            self.kw._set_input_value("종목조건", stock_condi)
            self.kw._set_input_value("신용조건", credit_condi)
            self.kw._set_input_value("가격조건", price_condi)
            self.kw._set_input_value("상하한포함", updown_limit)
            self.kw._comm_rq_data(rqname, "opt10019", "2", screen_no)

        return self.tr_ret_data  # data set when post_tr_function

    def post_opt10019(self, trcode, rqname, next):
        m_data = self.kw._get_comm_data_ex(trcode, '가격급등락')
        for data in m_data:
            tmp = {}
            for fid, mask_f, d in zip(self.OPT10019_FIDLIST, self.OPT10019_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next

    @init_tr_ret_data
    def opt10023(self, rqname,
                 market, sort_gubun, time_gubun, vol_gubun, time,
                 stock_condi, price_gubun,
                 screen_no):
        self.kw._set_input_value("시장구분", market)
        self.kw._set_input_value("정렬구분", sort_gubun)
        self.kw._set_input_value("시간구분", time_gubun)
        self.kw._set_input_value("거래량구분", vol_gubun)
        self.kw._set_input_value("시간", time)
        self.kw._set_input_value("종목조건", stock_condi)
        self.kw._set_input_value("가격구분", price_gubun)
        self.kw._comm_rq_data(rqname, "opt10023", "0", screen_no)

        while self.tr_next == "2":
            self.kw._set_input_value("시장구분", market)
            self.kw._set_input_value("정렬구분", sort_gubun)
            self.kw._set_input_value("시간구분", time_gubun)
            self.kw._set_input_value("거래량구분", vol_gubun)
            self.kw._set_input_value("시간", time)
            self.kw._set_input_value("종목조건", stock_condi)
            self.kw._set_input_value("가격구분", price_gubun)
            self.kw._comm_rq_data(rqname, "opt10023", "2", screen_no)

        return self.tr_ret_data  # data set when post_tr_function

    def post_opt10023(self, trcode, rqname, next):
        m_data = self.kw._get_comm_data_ex(trcode, '거래량급증')
        for data in m_data:
            tmp = {}
            for fid, mask_f, d in zip(self.OPT10023_FIDLIST, self.OPT10023_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next

    @init_tr_ret_data
    def opt10079(self, rqname, code, tick, screen_no, begin_date, end_date):
        """
        특정 주식종목의 틱봉 데이터를 요청하는 함수.
        :param rqname: str - 요청명
        :param code: str - 주식코드
        :param tick: str - 틱단위(1, 3, 5, 10, 30)
        :param screen_no: str - 화면번호
        :param begin_date: datetime - oldest date of user request
        :param end_date: datetime - newest date of user request
        :return:
        """
        def tr_process(rqname, code, tick, screen_no, next):
            self.kw.code = code
            self.kw._set_input_values([("종목코드", code), ("틱범위", tick), ("수정주가구분", "0")])
            ret_code = self.kw._comm_rq_data(rqname, "opt10079", next, screen_no)  # lock event loop
            if ReturnCode.OP_ERR_NONE != ret_code:
                raise Exception("[KiWoom Error][opt10079] %s" % ReturnCode.CAUSE[ret_code])
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
            self.logger.error(e)

        return []

    def post_opt10079(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '주식틱차트조회')
        f = ["현재가", "거래량", "체결시간", "시가", "고가", "저가", "수정주가구분", "수정비율",
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
            self.logger.error(e)

        return []

    def post_opt10080(self, trcode, rqname, next):
        data = self.kw._get_comm_data_ex(trcode, '주식분봉차트조회')
        f = ["현재가", "거래량", "체결시간", "시가", "고가", "저가", "수정주가구분", "수정비율",
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
             "수정주가구분", "수정비율", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

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
             "수정주가구분", "수정비율", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

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
        """

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        data = self.kw._get_comm_data_ex(trcode, '주식월봉차트조회')
        f = ["현재가", "거래량", "거래대금", "일자", "시가", "고가", "저가",
             "수정주가구분", "수정비율", "대업종구분", "소업종구분", "종목정보", "수정주가이벤트", "전일종가"]

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
    def opt20002(self, rqname, market, code, screen_no):
        """업종별주가요청

        :param rqname:
        :param market:
        :param code:
        :param screen_no:
        :return:
        """
        self.kw._set_input_value("시장구분", market)
        self.kw._set_input_value("업종코드", code)
        self.kw._comm_rq_data(rqname, 'opt20002', "0", screen_no)

        while self.tr_next == '2':
            self.kw._set_input_value("시장구분", market)
            self.kw._set_input_value("업종코드", code)
            self.kw._comm_rq_data(rqname, 'opt20002', "2", screen_no)

        return self.tr_ret_data

    def post_opt20002(self, trcode, rqname, next):
        """업종별주가요청

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        m_data = self.kw._get_comm_data_ex(trcode, '업종별주가')
        for data in m_data:
            tmp = {}
            for fid, mask_f, d in zip(self.OPT20002_FIDLIST, self.OPT20002_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next
        self.logger.info("[POST_OPT20002] completed")

    @init_tr_ret_data
    def opt20003(self, rqname, code, screen_no):
        """전업종 지수 요청

        :param str rqname:
        :param str code: 001:종합(KOSPI), 002:대형주, 003:중형주, 004:소형주 101:종합(KOSDAQ), 201:KOSPI200, 302:KOSTAR, 701: KRX100 나머지 ※ 업종코드 참고
        :param str screen_no:
        :return:
        """
        self.kw._set_input_value("업종코드", code)
        self.kw._comm_rq_data(rqname, 'opt20003', "0", screen_no)
        return self.tr_ret_data

    def post_opt20003(self, trcode, rqname, next):
        """전업종 지수 요청

        :param str trcode:
        :param str rqname:
        :param str next:
        :return:
        """
        m_data = self.kw._get_comm_data_ex(trcode, '전업종지수')
        for data in m_data:
            tmp = {}
            for fid, mask_f, d in zip(self.OPT20003_FIDLIST, self.OPT20003_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next
        self.logger.info("[POST_OPT20003] completed")

    @init_tr_ret_data
    def opt10085(self, rqname, account_no, screen_no):
        """계좌수익률 요청

            그동안 매매했던 모든 종목에 대해 현재 상황을 알려줌.

            ex)
           '메디프론': [{'결제잔고': '60',
                     '당일매도손익': '0',
                     '당일매매세금': '0',
                     '당일매매수수료': '',
                     '대출일': '00000000',
                     '만기일': '00000000',
                     '매입가': '7712',
                     '매입금액': '462720',
                     '보유수량': '60',
                     '신용구분': '00',
                     '신용금액': '0',
                     '신용이자': '0',
                     '일자': '20180723',
                     '종목명': '메디프론',
                     '종목코드': '065650',
                     '청산가능수량': '60',
                     '현재가': '-7370'}],
           '비트컴퓨터': [{'결제잔고': '0',
                      '당일매도손익': '0',
                      '당일매매세금': '0',
                      '당일매매수수료': '',
                      '대출일': '00000000',
                      '만기일': '00000000',
                      '매입가': '0',
                      '매입금액': '0',
                      '보유수량': '0',
                      '신용구분': '00',
                      '신용금액': '0',
                      '신용이자': '0',
                      '일자': '20180723',
                      '종목명': '비트컴퓨터',
                      '종목코드': '032850',
                      '청산가능수량': '0',
                      '현재가': '+6930'}],

        :param rqname str: 요청명
        :param account_no str: 계좌번호
        :param screen_no str: 화면번호
        :return:
        """
        self.kw._set_input_value("계좌번호", account_no)
        self.kw._comm_rq_data(rqname, "opt10085", "0", screen_no)  # lock event loop
        return self.tr_ret_data

    def post_opt10085(self, trcode, rqname, next):
        """계좌수익률 요청

        :param str trcode:
        :param str rqname:
        :param str next:
        :return:
        """
        # data = self.kw._get_comm_data_ex(trcode, '계좌수익률')
        n = self.kw._get_repeat_cnt(trcode, rqname)
        for i in range(n):
            tmp = {}
            data = [self.kw._get_comm_data(trcode, '계좌수익률', i, fid) for fid in self.OPT10085_FIDLIST]
            for fid, mask_f, d in zip(self.OPT10085_FIDLIST, self.OPT10085_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next
        self.logger.info("[POST_OPT10085] completed")

    @init_tr_ret_data
    def opt10077(self, rqname, account_no, account_pw, code, screen_no):
        """당일실현손익상세요청 요청 TR

            당일 '실현손익' 관련 매매 이력이 없으면 data가 아무것도 없음.
            매도를 통해 수익을 '실현'한 부분에 대해서 체결단위로 정보를 만들어줌.

        :param account_no str: 계좌번호
        :param account_pw str: 비밀번호
        :param code str: 종목코드
        :param screen_no str: 화면번호
        :return:
        """
        self.kw._set_input_value("계좌번호", account_no)
        self.kw._set_input_value("비밀번호", account_pw)
        self.kw._set_input_value("종목코드", code)
        self.kw._comm_rq_data(rqname, "opt10077", "0", screen_no)  # lock event loop
        return self.tr_ret_data

    def post_opt10077(self, trcode, rqname, next):
        """당일실현손익상세요청

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        m_data = self.kw._get_comm_data_ex(trcode, '당일실현손익상세')
        if not bool(m_data):
            self.tr_ret_data = []
            return

        for data in m_data:
            data = [d.strip() for d in data]
            data[-1] = data[-1][1:]  # A001470 -> 001470 종목코드 변경
            tmp = {}
            for fid, mask_f, d in zip(self.OPT10077_FIDLIST, self.OPT10077_MASK, data):
                tmp[fid] = mask_f(d)
            self.tr_ret_data.append(tmp)
        self.tr_next = next
        # self.kw._get_comm_data(trcode, '당일실현손익', 0, '당일실현손익')
        self.logger.info("[POST_OPT10077] completed")

    @init_tr_ret_data
    def opw00004(self, rqname, account_no, account_pw, gubun, pw_gubun, screen_no):
        """계좌평가현황요청 TR

        :param rqname str: 요청명
        :param account_no str: 계좌번호
        :param account_pw str: 비밀번호
        :param gubun str: 상장폐지조회구분 (0: 전체, 1:상장폐지종목제외)
        :param pw_gubun str: 비밀번호입력매체구분 ("00")
        :param screen_no str: 화면번호
        :return:
        """
        self.kw._set_input_value("계좌번호", account_no)
        self.kw._set_input_value("비밀번호", account_pw)
        self.kw._set_input_value("상장폐지조회구분", gubun)
        self.kw._set_input_value("비밀번호입력매체구분", pw_gubun)
        self.kw._comm_rq_data(rqname, "OPW00004", "0", screen_no)  # lock event loop
        return self.tr_ret_data

    def post_opw00004(self, trcode, rqname, next):
        # data = self.kw._get_comm_data_ex(trcode, '종목별계좌평가현황')
        n = self.kw._get_repeat_cnt(trcode, rqname)
        account_field = ["예수금", "D+2추정예수금", "유가잔고평가액",
                         "예탁자산평가액", "총매입금액", "추정예탁자산"]

        stock_field = ["종목코드", "종목명", "보유수량", "평균단가", "현재가", "평가금액",
                       "손익금액", "손익율", "매입금액",
                       "전일매수수량", "전일매도수량", "금일매수수량", "금일매도수량"]

        self.tr_ret_data = {
            "계좌정보": None,
            "종목정보": []
        }

        tmp = {}
        for f in account_field:
            data = self.kw._get_comm_data(trcode, '계좌평가현황', 0, f)
            tmp[f] = float(data[1:]) if data.startswith("-") else float(data)
        self.tr_ret_data["계좌정보"] = tmp

        for i in range(n):
            tmp = {}
            for f in stock_field:
                data = self.kw._get_comm_data(trcode, '계좌평가현황', i, f)

                try:
                    if f in ["손익금액", "손익율"]:
                        data = float(data)
                    else:
                        data = float(data[1:]) if data.startswith("-") else float(data)
                    tmp[f] = data
                except ValueError as e:
                    tmp[f] = data.strip()
            self.tr_ret_data["종목정보"].append(tmp)
        self.tr_next = next
        self.logger.info("[POST_OPW00004] completed")
        # self.logger.info(self.tr_ret_data)

    @init_tr_ret_data
    def opw00018(self, rqname, account_no, account_pw, pw_gubun, gubun, screen_no):
        """계좌평가현황요청 TR

        {'계좌평가결과': {'조회건수': '0004',
            '총대ㅜ금액': '',
            '총대출금': '000000000000000',
            '총매입금액': '000000001729030',
            '총수익율(%)': '',
            '총융자금액': '000000000000000',
            '총평가금액': '000000001792800',
            '총평가손익금액': '000000000046113',
            '추정예탁자산': '000000000953814'},
 '계좌평가잔고개별합산': {'디딤': {'금일매도수량': '000000000000000',
                       '금일매수수량': '000000000000000',
                       '대출일': '',
                       '매매가능수량': '000000000000210',
                       '매입가': '000000000003022',
                       '매입금액': '000000000634560',
                       '매입수수료': '000000000002220',
                       '보유비중(%)': '000000036.70',
                       '보유수량': '000000000000210',
                       '세금': '000000000002142',
                       '수수료합': '000000000004710',
                       '수익률(%)': '000000011.43',
                       '신용구분': '00',
                       '신용구분명': '',
                       '전일매도수량': '000000000000010',
                       '전일매수수량': '000000000000220',
                       '전일종가': '000000003095',
                       '종목명': '디딤',
                       '평가금액': '000000000714000',
                       '평가손익': '000000000072528',
                       '평가수수료': '000000000002490',
                       '현재가': '000000003400'},
                '메디프론': {'금일매도수량': '000000000000000',
                         '금일매수수량': '000000000000000',
                         '대출일': '',
                         '매매가능수량': '000000000000060',
                         '매입가': '000000000007712',
                         '매입금액': '000000000462720',
                         '매입수수료': '000000000001610',
                         '보유비중(%)': '000000026.76',
                         '보유수량': '000000000000060',
                         '세금': '000000000001357',
                         '수수료합': '000000000003190',
                         '수익률(%)': '-00000003.21',
                         '신용구분': '00',
                         '신용구분명': '',
                         '전일매도수량': '000000000000130',
                         '전일매수수량': '000000000000190',
                         '전일종가': '000000007880',
                         '종목명': '메디프론',
                         '평가금액': '000000000452400',
                         '평가손익': '-00000000014867',
                         '평가수수료': '000000000001580',
                         '현재가': '000000007540'},
                '캐스텍코리아': {'금일매도수량': '000000000000000',
                           '금일매수수량': '000000000000000',
                           '대출일': '',
                           '매매가능수량': '000000000000090',
                           '매입가': '000000000006553',
                           '매입금액': '000000000589800',
                           '매입수수료': '000000000002060',
                           '보유비중(%)': '000000034.11',
                           '보유수량': '000000000000090',
                           '세금': '000000000001752',
                           '수수료합': '000000000004100',
                           '수익률(%)': '-00000001.95',
                           '신용구분': '00',
                           '신용구분명': '',
                           '전일매도수량': '000000000000000',
                           '전일매수수량': '000000000000090',
                           '전일종가': '000000006300',
                           '종목명': '캐스텍코리아',
                           '평가금액': '000000000584100',
                           '평가손익': '-00000000011522',
                           '평가수수료': '000000000002040',
                           '현재가': '000000006490'},
                '팬스타엔터프라이': {'금일매도수량': '000000000000000',
                             '금일매수수량': '000000000000000',
                             '대출일': '',
                             '매매가능수량': '000000000000030',
                             '매입가': '000000000001398',
                             '매입금액': '000000000041950',
                             '매입수수료': '000000000000140',
                             '보유비중(%)': '000000002.43',
                             '보유수량': '000000000000030',
                             '세금': '000000000000126',
                             '수수료합': '000000000000280',
                             '수익률(%)': '-00000000.11',
                             '신용구분': '00',
                             '신용구분명': '',
                             '전일매도수량': '000000000000000',
                             '전일매수수량': '000000000000010',
                             '전일종가': '000000001445',
                             '종목명': '팬스타엔터프라이',
                             '평가금액': '000000000042300',
                             '평가손익': '-00000000000046',
                             '평가수수료': '000000000000140',
                             '현재가': '000000001410'}}}

        :param rqname str: 요청명
        :param account_no str: 계좌번호
        :param account_pw str: 비밀번호
        :param pw_gubun str: 비밀번호입력매체구분 ("00")
        :param gubun str: 조회구분 (1: 합산, 2: 개별)
        :param screen_no str: 화면번호
        :return:
        """
        self.kw._set_input_value("계좌번호", account_no)
        self.kw._set_input_value("비밀번호", account_pw)
        self.kw._set_input_value("비밀번호입력매체구분", pw_gubun)
        self.kw._set_input_value("조회구분", gubun)
        self.kw._comm_rq_data(rqname, "opw00018", "0", screen_no)  # lock event loop
        return self.tr_ret_data

    def post_opw00018(self, trcode, rqname, next):
        # data = self.kw._get_comm_data_ex(trcode, '계좌평가잔고개별합산')

        n = self.kw._get_repeat_cnt(trcode, rqname)
        self.tr_ret_data = {}

        fid_list1 = ["총매입금액", "총평가금액", "총평가손익금액", "총수익율(%)", "추정예탁자산", "총대출금",
                     "총융자금액", "총대주금액", "조회건수"]

        fid_list2 = ["종목명", "평가손익", "수익률(%)", "매입가", "전일종가", "보유수량", "매매가능수량", "현재가", "전일매수수량",
                     "전일매도수량", "금일매수수량", "금일매도수량", "매입금액", "매입수수료", "평가금액", "평가수수료", "세금",
                     "수수료합", "보유비중(%)", "신용구분", "신용구분명", "대출일"]

        n = self.kw._get_repeat_cnt(trcode, rqname)
        result = {
            '계좌평가결과': {},
            '계좌평가잔고개별합산': {}
        }

        tmp1 = {}
        for f in fid_list1:
            data = self.kw._get_comm_data(trcode, '계좌평가결과', 0, f)
            tmp1[f] = data
        result['계좌평가결과'] = tmp1


        for n in range(n):
            tmp2 = {}
            for f in fid_list2:
                data = self.kw._get_comm_data(trcode, '계좌평가잔고개별합산', n, f)
                tmp2[f] = data
            result['계좌평가잔고개별합산'][tmp2['종목명']] = tmp2

        self.tr_ret_data = result
        pdb.set_trace()
        self.tr_next = next
        self.logger.info("[POST_OPW00018] completed")

    def post_koa_normal_buy_kp_ord(self, trcode, rqname, next):
        """kospi stock buy order completed method

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        self.logger.info("kospi stock buy order is completed. (rqname: {})".format(rqname))
        self.tr_ret_data = []

    def post_koa_normal_buy_kq_ord(self, trcode, rqname, next):
        """kosdaq stock buy order completed method

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        self.logger.info("kosdaq stock buy order is completed. (rqname: {})".format(rqname))
        self.tr_ret_data = []

    def post_koa_normal_sell_kp_ord(self, trcode, rqname, next):
        """kospi stock sell order completed method

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        self.logger.info("kospi stock sell order is completed. (rqname: {})".format(rqname))
        self.tr_ret_data = []

    def post_koa_normal_sell_kq_ord(self, trcode, rqname, next):
        """kosdaq stock sell order completed method

        :param trcode:
        :param rqname:
        :param next:
        :return:
        """
        self.logger.info("kosdaq stock sell order is completed. (rqname: {})".format(rqname))
        self.tr_ret_data = []

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
        self.logger.info("(!)[Callback] _on_receive_tr_data")
        self.logger.info("trcode : {}".format(trcode))
        try:
            post_fn_name = 'post_' + trcode.lower()
            print("post_fn_name: {}".format(post_fn_name))
            post_fn = eval("self." + post_fn_name)
            # post_fn = self.tr_post.fn_table[rqname]
            post_fn(trcode, rqname, next)
        except AttributeError as e:
            self.logger.error(e)
        except Exception as e:
            self.logger.error(e)
        self.logger.info("  ========================> [IMPORTANT] EVENT_LOOP -> RELEASE")
        time.sleep(0.5)
        self.kw.evt_loop.exit()  # release event loop

        # callback
        self.logger.info("[OnReceiveTrData] Notify callback method..")
        if (rqname, screen_no) in self.kw.notify_fn["OnReceiveTrData"]:
            self.kw.notify_fn[(rqname, screen_no)]()

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
    LATEST = -1
    REQ_CNT = 0

    def __init__(self, kw):
        self.kw = kw
        self.logger = self.kw.logger
        self.queue_size = 1000
        self.queue = deque(maxlen=self.queue_size)
        self.now = datetime.now()
        # count, time(sec), delay(sec)
        self.req_limit_setting = [
            (5, 2, 1),
            (100, 70, 20),
            (200, 150, 20),
            (700, 600, 30)
        ]
        self.queue += [self.now] * self.queue_size

    def prevent_excessive_request(self):
        self.REQ_CNT += 1
        self.queue.append(datetime.now())
        if self.REQ_CNT >= 999:
            print("=" * 50)
            print(" ---- 1000번 요청했음 ---- 프로그램 종료합니다. ")
            print("=" * 50)
            exit(0)

        tmp = 0
        print("Req Count: %s" % self.REQ_CNT)
        for cnt, dur_cfg, delay in self.req_limit_setting:
            if self.REQ_CNT < cnt:
                continue
            spend = (self.queue[self.LATEST] - self.queue[-cnt]).seconds
            if (tmp+spend) < dur_cfg:
                print("[Delay] %s sec" % delay)
                time.sleep(delay)
                tmp += spend
