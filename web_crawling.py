import re
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pdb

'''
get_date_str(s) - 문자열 s 에서 "YYYY/MM" 문자열 추출
'''
def get_date_str(s):
    date_str = ''
    r = re.search("\d{4}/\d{2}", s)
    if r:
        date_str = r.group()
        date_str = date_str.replace('/', '-')

    return date_str

'''
* code: 종목코드
* fin_type = '0': 재무제표 종류 (0: 주재무제표, 1: GAAP개별, 2: GAAP연결, 3: IFRS별도, 4:IFRS연결)
* freq_type = 'Y': 기간 (Y:년, Q:분기)
'''
def get_finstate_naver(code, fin_type='0', freq_type='Y'):
    # url_tmpl = 'http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?' \
    #                'cmp_cd=%s&fin_typ=%s&freq_typ=%s'
    # url = url_tmpl % (code, fin_type, freq_type)
    url = "http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd=%s&fin_typ=0&freq_typ=Y" % (code)

    #print(url)


    # dfs = pd.read_html(url, encoding="utf-8")
    html = requests.get(url).text
    pdb.set_trace()
    dfs = pd.read_html(html, index_col='주요재무정보')
    df = dfs[0]
    if df.ix[0,0].find('해당 데이터가 존재하지 않습니다') >= 0:
        return None

    df.rename(columns={'주요재무정보':'date'}, inplace=True)
    df.set_index('date', inplace=True)

    cols = list(df.columns)
    if '연간' in cols: cols.remove('연간')
    if '분기' in cols: cols.remove('분기')
    cols = [get_date_str(x) for x in cols]
    df = df.ix[:, :-1]
    df.columns = cols
    dft = df.T
    dft.index = pd.to_datetime(dft.index)

    # remove if index is NaT
    dft = dft[pd.notnull(dft.index)]
    return dft

def main():
    get_finstate_naver("066570", '4')

if __name__ == "__main__":
    main()