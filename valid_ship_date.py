import sys
import platform
import os
module_path = r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\ﾏｽﾀ\sql_python_module'
if platform.system() == 'Linux':
    module_path = r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'

sys.path.append(os.path.abspath(module_path))

import csv
import datetime
from re import I
from typing import List, Tuple
from select_data import ISelectData, SelectCalenderUnsouya, SelectCalenderToyo

from pandas.core.reshape.merge import _items_overlap_with_suffix

class ValidShipDateCheck:

    def __init__(self, orderDate:str)-> None:

        minYM, maxYM = self._create_minYM_maxYM(orderDate)
        calenToyo:SelectCalenderToyo = SelectCalenderToyo(minYM, maxYM)
        calenUnso:SelectCalenderUnsouya = SelectCalenderUnsouya(minYM, maxYM)

        calenToyo_col, calenToyo_data = calenToyo.select_data()
        calenUnso_col, calenUnso_data = calenUnso.select_data()
        '''
        ['YYYY/MM/DD', '曜日', '東洋休日', '運送屋休日']
        [['2026/1/1', '木', '休', '休'], ['2026/1/2', '金', '休', '休'],...]
        の形にする。
        '''
        try:
            self._holiday_mtx = \
                  self._create_holiday_mtx(calenToyo_data, calenUnso_data)
        except Exception as e:
            print(e)
            print('処理を中止します')
            sys.exit(1)

        ''' self._holiday_mtx = 
        [['2026/1/1', '木', '休', '休'], ['2026/1/2', '金', '休', '休'], ['2026/1/3', '土', '休', '休'], ['2026/1/4', '日', '休', '休'], ['2026/1/5', '月', '', ''], ['2026/1/6', '火', '', ''], ['2026/1/7', '水', '', ''], ['2026/1/8', '木', '', ''],
        '''

    def _create_holiday_mtx(self, toyo:List[List[str]], 
                            unso:List[List[str]])-> List[List[str]]:

        '''toyo, unso = ['202607','03','金',' '], ['202607','04','土','1']...]
        '''

        if len(toyo) != len(unso):
            raise Exception("東洋休日と運送屋休日のデータ数が合いません")
        
        holidays: List[List[str]] = []
        for i in range(len(toyo)): 
            YYYY_MM_DD = f'{toyo[i][0][:4]}/{toyo[i][0][4:]}/{toyo[i][1]}'
            youbi = toyo[i][2]
            toyo_holiday = ''
            if toyo[i][3] == '1':
                toyo_holiday = '休'
            unso_holiday = ''
            if unso[i][3] == '1':
                unso_holiday = '休'

            inner: List[str] = [YYYY_MM_DD, youbi, toyo_holiday, unso_holiday]

            holidays.append(inner)

        return holidays


    def _create_minYM_maxYM(self, orderDate: str)-> Tuple:
        '''
        minM: 出荷日の月の前月
        maxM: 出荷日の月の翌月
        '''
        orderY = orderDate[:4]
        orderM = orderDate[4:6]
        if orderM == "12":
            minM = str(int(orderM) - 1)
            minY = orderY
            maxM = "01"
            maxY = str(int(orderY) + 1)
        elif orderM == "01":
            minM = "12"
            minY = str(int(orderY) - 1)
            maxM = str(int(orderM) + 1)
            maxY = orderY
        else:
            minM = str(int(orderM) - 1)
            minY = orderY
            maxM = str(int(orderM) + 1)
            maxY = orderY

        if len(maxM) == 1:
            maxM = "0" + maxM
        if len(minM) == 1:
            minM = "0" + minM

        maxYM = "'" + maxY + maxM + "'"
        minYM = "'" + minY + minM + "'"

        return minYM, maxYM


    def date_isExist(self, s_date: str) -> bool:
        '''
        休日表に日にちが存在するか？
        '''
        d_date = datetime.datetime.strptime(s_date, '%Y/%m/%d')
        isExist: bool = False

        for line in self._holiday_mtx:
            if d_date == datetime.datetime.strptime(line[0], '%Y/%m/%d'):
                isExist = True
                return isExist

        return isExist


    def is_Saturday(self, s_date: str)-> bool:
        isSaturday: bool = False
        try:
            d_date = datetime.datetime.strptime(s_date, '%Y/%m/%d')
        except ValueError:
            return isSaturday

        if d_date.weekday() == 5: # 月:0, 火:1, 水:2, 木:3, 金:4, 土:5, 日:0
            isSaturday = True

        return isSaturday



    def is_haulerHoliday(self, s_date: str) -> bool:
        '''
        運送屋が休日か？
        '''
        d_date = datetime.datetime.strptime(s_date, '%Y/%m/%d')
        isHaulerHoliday: bool = False
        
        for line in self._holiday_mtx:
            if d_date == datetime.datetime.strptime(line[0], '%Y/%m/%d'):
                if line[3] == '休':
                    isHaulerHoliday = True
                    return isHaulerHoliday
                return isHaulerHoliday

        return isHaulerHoliday


    def is_toyoHoliday(self, s_date: str) -> bool:
        '''
        東洋工業塗料が休日か？
        '''
        d_date = datetime.datetime.strptime(s_date, '%Y/%m/%d')
        isToyoHoliday: bool = False
        
        for line in self._holiday_mtx:
            if d_date == datetime.datetime.strptime(line[0], '%Y/%m/%d'):
                if line[2] == '休':
                    isToyoHoliday = True
                    return isToyoHoliday
                return isToyoHoliday

        return isToyoHoliday



    def calc_valid_ship_date(self, df_row)-> str:
        '''
        納期から正しい出荷日を求める
        '''

        def to_yyyy_mm_dd(s_date: str) -> str:
            '''
            日付文字列を'2025/09/03'の形にする
            '''

            try:
                d_date = datetime.datetime.strptime(s_date, '%Y/%m/%d')
                result = d_date.strftime('%Y/%m/%d')
            except ValueError: 
                return s_date

            return result
            


        deli_date: str = df_row['納期']
        try:
            lead_time: int  = int(df_row['所要日数'])
        except ValueError:
            return '所要日数データ無し'


        d_deli_date = datetime.datetime.strptime(deli_date, '%Y/%m/%d')
        valid_ship_date: str = 'hoge/hoge/hoge'
        
        ship_row: int = 0 
        i: int = 0
        for i in range(len(self._holiday_mtx)):
            if d_deli_date == datetime.datetime.strptime(
                                 self._holiday_mtx[i][0], '%Y/%m/%d'):
                ship_row = i


        if ship_row == 0 and i > 0:
            return valid_ship_date # 'hoge/hoge/hoge'

        '''
        lead_time = 0の場合、当社の配達
        当社の休日のみ考慮し、運送屋の休日は考慮しない
        '''
        if lead_time == 0:
            while self._holiday_mtx[ship_row][2] == '休':
                ship_row -= 1
            if ship_row < 0:
                return valid_ship_date # 'hoge/hoge/hoge'
            valid_ship_date = self._holiday_mtx[ship_row][0]
            return to_yyyy_mm_dd(valid_ship_date)

        '''
        lead_time > 0 の場合、運送日数分(lead_time)だけ出荷日を早めるが、
        運送屋の休日はカウントしない
        '''
        while lead_time > 0:
            if self._holiday_mtx[ship_row][3] == '休':
                ship_row -= 1
                continue
            ship_row -= 1
            lead_time -= 1
        

        # ship_rowが東洋または運送屋の休日だったら更にデクリメントする
        while (self._holiday_mtx[ship_row][2] == '休' or 
                             self._holiday_mtx[ship_row][3] == '休'):
            ship_row -= 1

        if ship_row < 0 :
            return valid_ship_date # 'hoge/hoge/hoge'

        valid_ship_date = self._holiday_mtx[ship_row][0]
        return to_yyyy_mm_dd(valid_ship_date)

