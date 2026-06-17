import platform
import csv
from typing import List
import pandas as pd
from get_idx import GetIdx


class ExportProductCheck:

    def __init__(self, df_mdestn: pd.DataFrame)-> None:

        file_nhm: str = './n&h&m_modify.csv'
        if platform.system() == 'Windows':
            file_nhm = f'//192.168.1.247/共有/受注check/master/n&h&m_modify.csv'
        if platform.system() == 'Linux':
            file_nhm = f'/mnt/public/受注check/master/n&h&m_modify.csv'
        if platform.system() == 'Darwin':
            file_nhm = f'/Volumes/共有/受注check/master/n&h&m_modify.csv'

        self.__nhm_mtx: List[List[str]] = []
        with open(file_nhm, newline='', encoding='cp932') as f:
            reader = csv.reader(f)
            next(reader) # 1行目をスキップ
            self.__nhm_mtx = [row for row in reader]

        # df_mdestn = MDESTN_U2002のDataFrame をリストにする
        self.__mdestn_mtx: List[List[str]] = df_mdestn.to_numpy().tolist()
        self.__mdestn_col: List[str] = df_mdestn.columns.tolist()
        self.__getIdx = GetIdx()


    def is_export(self, df_row)-> bool:
        '''
        effitAからfetchした納入先コードは空白の場合は ' '半角スペース
        unsoutaiou_tokeの場合は''空文字なので ' 'に合わせる
        '''
        tokui_cd: str = df_row['得意先コード']
        nonyu_cd: str = df_row['納入先コード']
        isExport: bool = False
        tmp_nonyu: str = ' '

        tokui_idx: int = self.__getIdx.get_idx(self.__mdestn_col, '得意先コード')
        nonyu_idx: int = self.__getIdx.get_idx(self.__mdestn_col, '納入先コード')
        isExp_idx: int = self.__getIdx.get_idx(self.__mdestn_col, 'isExport')
        for line in self.__mdestn_mtx:
            tmp_nonyu = line[nonyu_idx]
            if tmp_nonyu == '':
                tmp_nonyu = ' '
            if tokui_cd == line[tokui_idx] and nonyu_cd == tmp_nonyu:
                return line[isExp_idx] == 1 # MDESTN_U2002では輸出"y"は　1 
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
