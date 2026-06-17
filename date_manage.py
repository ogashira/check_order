import pandas as pd

class DateManage:

    def change_to_date(self, df:pd.DataFrame)-> pd.DataFrame:

        def change_to_date_series(seri)-> pd.Series:
            seri = seri.map(lambda x: x[:4] + '/'+ x[4:6] + 
                            '/' + x[6:] if int(x) > 20200000 else x) 
            return seri

        df['受注日'] = change_to_date_series(df['受注日'])
        df['出荷予定日'] = change_to_date_series(df['出荷予定日'])
        df['納期'] = change_to_date_series(df['納期'])

        return df


    def lead_time_test(self) -> pd.DataFrame:
        df = pd.DataFrame({'得意先コード': ['T1210','T1210','T1210','T3333','T3335'],
                     '納入先コード': ['AIR01','GZK02',' ',' ',' '],
                     '所要日数':['1', '2', '3', '3', '3']})
        return df
