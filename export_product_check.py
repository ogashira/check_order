import platform
import csv
from typing import List

class ExportProductCheck:

    def __init__(self)-> None:

        file_nhm: str = './n&h&m_modify.csv'
        file_unsoutaiou: str = './unsoutaiou_toke.csv'
        if platform.system() == 'Windows':
            file_nhm = f'//192.168.1.247/共有/受注check/master/n&h&m_modify.csv'
            file_unsoutaiou = f'//192.168.1.247/共有/経理課ﾌｫﾙﾀﾞ/運賃計算関係/unsoutaiou_toke.csv'
        if platform.system() == 'Linux':
            file_nhm = f'/mnt/public/受注check/master/n&h&m_modify.csv'
            file_unsoutaiou = f'/mnt/public/経理課ﾌｫﾙﾀﾞ/運賃計算関係/unsoutaiou_toke.csv'
        if platform.system() == 'Darwin':
            file_nhm = f'/Volumes/共有/受注check/master/n&h&m_modify.csv'
            file_unsoutaiou = f'/Volumes/共有/経理課ﾌｫﾙﾀﾞ/運賃計算関係/unsoutaiou_toke.csv'

        self.__nhm_mtx: List[List[str]] = []
        with open(file_nhm, newline='', encoding='cp932') as f:
            reader = csv.reader(f)
            next(reader) # 1行目をスキップ
            self.__nhm_mtx = [row for row in reader]

        self.__unsoutaiou_mtx: List[List[str]] = []
        with open(file_unsoutaiou, newline='', encoding='cp932') as f:
            reader = csv.reader(f)
            next(reader) # 1行目をスキップ
            self.__unsoutaiou_mtx = [row for row in reader]


    def is_export(self, df_row)-> bool:
        '''
        effitAからfetchした納入先コードは空白の場合は ' '半角スペース
        unsoutaiou_tokeの場合は''空文字なので ' 'に合わせる
        '''
        tokui_cd: str = df_row['得意先コード']
        nonyu_cd: str = df_row['納入先コード']
        isExport: bool = False
        tmp_nonyu: str = ' '
        for line in self.__unsoutaiou_mtx:
            tmp_nonyu = line[16]
            if line[16] == '':
                tmp_nonyu = ' '
            if tokui_cd == line[15] and nonyu_cd == tmp_nonyu:
                return line[14] == 'y'
        return isExport


    def find_destination(self, df_row)-> str:
        tokui_cd: str = df_row['得意先コード']
        nonyu_cd: str = df_row['納入先コード']
        isExport: bool = df_row['isExport']
        Destination: str = ''

        if not isExport:
            return Destination

        for line in self.__nhm_mtx:
            tmp_nonyu: str = line[1]
            if line[1] == '':
                tmp_nonyu = ' '
            if tokui_cd == line[0] and nonyu_cd == tmp_nonyu:
                return line[4] 

        return 'n&h&mに向先無し'


    def is_exist_exportProduct(self, df_row)-> bool:
        tokui_cd: str = df_row['得意先コード']
        nonyu_cd: str = df_row['納入先コード']
        hinban: str = df_row['品番']
        isExport: bool = df_row['isExport']

        if not isExport:
            return False

        for line in self.__nhm_mtx:
            tmp_nonyu: str = line[1]
            if line[1] == '':
                tmp_nonyu = ' '
            if (tokui_cd == line[0] and nonyu_cd == tmp_nonyu and 
                                                             hinban == line[2]):
                return True 

        return False
