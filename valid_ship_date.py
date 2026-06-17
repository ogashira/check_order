import platform
import csv
import datetime
from re import I
from typing import List

from pandas.core.reshape.merge import _items_overlap_with_suffix

class ValidShipDateCheck:

    def __init__(self)-> None:
        file: str = './order_holiday.csv'
        if platform.system() == 'Windows':
            file = f'//192.168.1.247/共有/受注check/master/order_holiday.csv'
        if platform.system() == 'Linux':
            file = f'/mnt/public/受注check/master/order_holiday.csv'
        if platform.system() == 'Darwin':
            file = f'/Volumes/共有/受注check/master/order_holiday.csv'

        self.__holiday_mtx: List[List[str]] = []
        with open(file, newline='', encoding='cp932') as f:
            reader = csv.reader(f)
            next(reader) # 1行目をスキップ
            self.__holiday_mtx = [row for row in reader]


    def date_isExist(self, s_date: str) -> bool:
        '''
        休日表に日にちが存在するか？
        '''
        d_date = datetime.datetime.strptime(s_date, '%Y/%m/%d')
        isExist: bool = False

        for line in self.__holiday_mtx:
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
        
        for line in self.__holiday_mtx:
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
        
        for line in self.__holiday_mtx:
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
        for i in range(len(self.__holiday_mtx)):
            if d_deli_date == datetime.datetime.strptime(
                                 self.__holiday_mtx[i][0], '%Y/%m/%d'):
                ship_row = i


        if ship_row == 0 and i > 0:
            return valid_ship_date # 'hoge/hoge/hoge'

        '''
        lead_time = 0の場合、当社の配達
        当社の休日のみ考慮し、運送屋の休日は考慮しない
        '''
        if lead_time == 0:
            while self.__holiday_mtx[ship_row][2] == '休':
                ship_row -= 1
            if ship_row < 0:
                return valid_ship_date # 'hoge/hoge/hoge'
            valid_ship_date = self.__holiday_mtx[ship_row][0]
            return to_yyyy_mm_dd(valid_ship_date)

        '''
        lead_time > 0 の場合、運送日数分(lead_time)だけ出荷日を早めるが、
        運送屋の休日はカウントしない
        '''
        while lead_time > 0:
            if self.__holiday_mtx[ship_row][3] == '休':
                ship_row -= 1
                continue
            ship_row -= 1
            lead_time -= 1
        

        # ship_rowが東洋または運送屋の休日だったら更にデクリメントする
        while (self.__holiday_mtx[ship_row][2] == '休' or 
                             self.__holiday_mtx[ship_row][3] == '休'):
            ship_row -= 1

        if ship_row < 0 :
            return valid_ship_date # 'hoge/hoge/hoge'

        valid_ship_date = self.__holiday_mtx[ship_row][0]
        return to_yyyy_mm_dd(valid_ship_date)

