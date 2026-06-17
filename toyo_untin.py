from typing import List, Any, Tuple
import pandas as pd


class ToyoUntin:

    def __init__(self, seikyusaki: List[List[Any]],
                       tyuukei_ari: List[List[Any]],
                       tyuukei_nasi: List[List[Any]],
                       seikyusaki_codes: List[Tuple[str, str]])-> None:

        self._seikyusaki = seikyusaki
        self._tyuukei_ari = tyuukei_ari
        self._tyuukei_nasi = tyuukei_nasi
        self._seikyusaki_codes = seikyusaki_codes

        ''' seikyusaki = 
        [ ['T0060', 'H236', '株式会社 サンキャスト', 
        '茨城県下妻市半谷７４８番地', '100', '1'], .....]
        '''


    def get_toyo_untin(self, df_row: pd.Series)-> int:

        toyo_untin:float = 0
        tokui_code = df_row['得意先コード']
        nonyu_code = df_row['納入先コード']
        cans = df_row['ncan']
        qty = df_row['kg']

        tup = (tokui_code, nonyu_code)
        if nonyu_code == ' ':
            nonyu_code = ''
        tup = (tokui_code, nonyu_code)

        # seikyusaki_codesになかったら０円
        if tup not in self._seikyusaki_codes:
            return int(toyo_untin)

        dist: int = 0
        tyukei: int = 0
        untin_mtx: List[List[Any]] = self._tyuukei_nasi

        for line in self._seikyusaki:
            if tokui_code == line[0] and nonyu_code == line[1]:
                dist = int(line[4])
                tyukei = int(line[5])
                break
        
        # 中継が１以上ならば運賃表をariにする
        if tyukei > 0:
            untin_mtx = self._tyuukei_ari

        # 距離のインデックス求める
        idx_dist: int = 0
        # 最後から１まで
        for i in range(len(untin_mtx[0])-1, 0, -1):
            if int(untin_mtx[0][i]) >= dist:
                idx_dist = i
                break

        # 缶数のインデックス求める
        idx_cans: int = 0
        # 最後から１まで
        for i in range(len(untin_mtx)-1, 0, -1):
            if int(untin_mtx[i][0])>= cans:
                idx_cans = i
                break

        tanka:int = int(untin_mtx[idx_cans][idx_dist])


        toyo_untin = tanka * qty

        return int(toyo_untin)
