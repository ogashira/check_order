import warnings
import pandas as pd
from typing import List
from abc import ABC, abstractmethod
from sql_server import SqlServer as SqlServer
from sql_server_test import SqlServer as TestSqlServer


warnings.filterwarnings('ignore', category=UserWarning)

class ISelectData(ABC):
    @abstractmethod
    def select_data(self)-> pd.DataFrame:
        pass


class SelectOrder(ISelectData):

    def __init__(self, order_date: str, staff_no: str) -> None:
        self.__order_date = order_date
        self.__staff_no = staff_no


    def select_data(self)-> pd.DataFrame:
        ss: SqlServer = SqlServer()
        cnxn = ss.get_cnxn()


        # cursor = cnxn.cursor()

        sqlQuery = ("SELECT RJYUCD.RjcJCNo, MTANTO.TanManNam, RJYUCD.RjcJcDay," 
                    " RJYUCD.RjcSKDay, RJYUCD.RjcTokCD, RJYUCD.RjcNonyuCD, RJYUCH.RjcTokNam1," 
                    " RJYUCH.RjcNonyuNam1, RJYUCH.RjcNonyuNam2,"
                    " RJYUCD.RjcHinCD, RJYUCD.RjcHinNam, RJYUCD.RjcJcSu," 
                    " RJYUCD.RjcTniCD, RJYUCD.RjcCMNo, RJYUCD.RjcMBiko," 
                    " RJYUCH.RjcHBiko, RJYUCD.RjcNODay"
                    " From dbo.RJYUCD"
                    " JOIN dbo.RJYUCH"
                    " ON RJYUCD.RjcJCNo = RJYUCH.RjcJCNo"
                    " JOIN dbo.MTANTO"
                    " ON RJYUCH.RjcOpeManNo = MTANTO.TanManNo"
                    " WHERE RJYUCD.RjcJcDay =" + self.__order_date + 
                    " AND RJYUCH.RjcOpeManNo =" + self.__staff_no + 
                    " ORDER BY RJYUCD.RjcJCNo")
        df: pd.DataFrame = pd.read_sql(sqlQuery, cnxn)
        df = df.rename(columns={'RjcJCNo':'受注No', 'TanManNam': '担当者名称', 
                     'RjcJcDay': '受注日', 'RjcSKDay': '出荷予定日', 'RjcTokCD': '得意先コード',
                     'RjcNonyuCD': '納入先コード', 'RjcTokNam1': '得意先名称1', 
                     'RjcNonyuNam1': '納入先名称1', 
                     'RjcNonyuNam2': '納入先名称2', 'RjcHinCD': '品番', 
                     'RjcHinNam': '品名', 'RjcJcSu': '受注数量', 
                     'RjcTniCD': '受注単位', 'RjcCMNo': '得意先注文No', 
                     'RjcMBiko': '備考1', 'RjcHBiko': '備考2', 
                     'RjcNODay': '納期'})
        #df = df.sort_values(['得意先コード','納入先コード'])
        #df = df.reset_index(drop = True)

        ss.close()

        return df


class SelectOrder_Test(ISelectData):
    '''
    テスト用モック
    '''
    def __init__(self) -> None:
        pass


    def select_data(self)-> pd.DataFrame:



        df = pd.DataFrame({'受注No': ['aa', 'bb', 'cc', 'dd', 'ee'], 
                           '担当者名称': ['oga', 'oga', 'oga', 'oga', 'oga'], 
                     '受注日': ['20251203','20251203','20251203','20251203','20251203'],
                     '出荷予定日': ['20251217', '20251219', '20251217', '20251217', '20251217'],
                     '得意先コード': ['T1210','T1210','T1210','T3333','T3334'],
                     '納入先コード': ['THK06','THK06',' ',' ',' '],
                     '得意先名称1': ['hoge株', 'hoge株', 'hoge株', 'hoge株', 'hoge株'],
                     '納入先名称1': ['hoge事業所','hoge事業所','hoge事業所','hoge事業所','hoge事業所'],
                     '納入先名称2': [' ',' ',' ',' ',' '],
                           '品番': ['S3-N404-U-R-EX','S3-N404K2-U-R-EX','S6-UV542-U','S6-UV542-U','S6-UV542-U'],
                     '品名': ['ＵＶ－５４２ｱﾝﾀﾞｰ','ＵＶ－５４２ｱﾝﾀﾞｰ','ＵＶ－５４２ｱﾝﾀﾞｰ','ＵＶ－５４２ｱﾝﾀﾞｰ','ＵＶ－５４２ｱﾝﾀﾞｰ'],
                     '受注数量': [1.0, 2.0, 3.0, 4.0, 5.0],
                     '受注単位': ['CN','CN','CN','CN','CN'],
                     '得意先注文No': [' ',' ',' ',' ',' '],
                     '備考1': ['hoge', ' ', 'hoge', ' ',' '],
                     '備考2': [' ',' ',' ',' ',' '],
                     '納期':['20251219', '20251223', '20251218', '20251217', '20280104']})


        return df


class SelectHinban(ISelectData):

    def __init__(self) -> None:
        pass


    def select_data(self)-> pd.DataFrame:
        ss: SqlServer = SqlServer()
        cnxn = ss.get_cnxn()

        # cursor = cnxn.cursor()

        sqlQuery = ("SELECT HinHinCD, HinNam, HinTniCD, HinTju," 
                    " HinFree10, HinFree11" 
                    " From dbo.MHINCD"
                    " ORDER BY HinHinCD")
        df: pd.DataFrame = pd.read_sql(sqlQuery, cnxn)
        df = df.rename(columns={'HinHinCD':'品番', 'HinNam': '品名', 
                     'HinTniCD': '単位コード', 'HinTju': '単重', 
                     'HinFree10': '自由入力欄10', 'HinFree11': '振り替え品番'})

        ss.close()

        return df


class SelectMdestn(ISelectData):

    def __init__(self) -> None:
        pass


    def select_data(self)-> pd.DataFrame:
        ss: SqlServer = SqlServer()
        cnxn = ss.get_cnxn()

        # cursor = cnxn.cursor()

        sqlQuery = ("SELECT DesTokCD AS '得意先コード'," 
                    " DesNonyuCD AS '納入先コード',"
                    " DesLeadTime AS '所要日数',"
                    " DesIsExport AS 'isExport'"
                    " From dbo.MDESTN_U2002"
                    " ORDER BY DesTokCD, DesNonyuCD")
        df: pd.DataFrame = pd.read_sql(sqlQuery, cnxn)


        ss.close()

        return df
