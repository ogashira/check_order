import csv
import pandas as pd

class ConvertUnit:

    def __init__(self, df_hinban:pd.DataFrame) -> None:
        self.__df_hinban = df_hinban


    def convert_unit(self, df_row: pd.Series) -> pd.Series:
        qnt  = df_row['受注数量']
        unit = df_row['受注単位']
        order_hinban = df_row['品番']
        
        if unit == 'CN':
            # .iloc[0] を使って単一の値を取得する
            tnju_series = (self.__df_hinban[self.__df_hinban['品番'] 
                                                       == order_hinban]['単重'])
            if not tnju_series.empty:
                tnju = tnju_series.iloc[0]
                convert_qnt =  qnt * (tnju / 1000)
                return pd.Series([convert_qnt, 'KG'], 
                                                 index=['変換数量', '変換単位'])
            else:
                return pd.Series([0, '単重なし'], 
                                                 index=['変換数量', '変換単位'])

        if unit == 'KG':
            # .iloc[0] を使って単一の値を取得する
            hurikae_hinban_series = (self.__df_hinban[self.__df_hinban['品番'] 
                                              == order_hinban]['振り替え品番'])
            if not hurikae_hinban_series.empty:
                hurikae_hinban = hurikae_hinban_series.iloc[0]
                tnju_series = (self.__df_hinban[self.__df_hinban['品番'] 
                                                    == hurikae_hinban]['単重'])
                if not tnju_series.empty:
                    tnju = tnju_series.iloc[0]
                    if tnju > 0:
                        convert_qnt = qnt / (tnju / 1000)
                        return pd.Series([convert_qnt, 'CN'], 
                                                 index=['変換数量', '変換単位'])
                    else:
                        return pd.Series([0, '単重ゼロ'], 
                                                 index=['変換数量', '変換単位'])
                else:
                    return pd.Series([0, '単重なし'], 
                                                 index=['変換数量', '変換単位'])
            else:
                return pd.Series([0, '振替品番なし'], 
                                                 index=['変換数量', '変換単位'])


        return pd.Series([0, '単位不明'], index=['変換数量', '変換単位'])

