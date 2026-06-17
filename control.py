import pprint
import sys
import os
import subprocess
import platform
import pandas as pd
import xlsxwriter
import csv
from typing import Tuple, List, Any
from check_result_display import CheckResultDisplay
from convert_unit import ConvertUnit
from date_manage import DateManage
from export_product_check import ExportProductCheck
from user_interface import UserInterface
from select_data import ISelectData, SelectOrder, SelectHinban, SelectMdestn
from valid_ship_date import ValidShipDateCheck
from dataframe_formatter import format_df_as_grid
from toyo_untin import ToyoUntin



class Control:

    def __init__(self)-> None:
        pass


    def start(self)-> None:
        ui: UserInterface = UserInterface()
        orderDate_and_userId: Tuple[str, str] = ui.get_orderDate_and_id()

        select_order: ISelectData = SelectOrder(orderDate_and_userId[0], 
                                                       orderDate_and_userId[1])

        '''テスト用モックデータ'''
        # select_order: ISelectData = SelectOrder_Test()
        

        select_hinban: ISelectData = SelectHinban()

        df_order: pd.DataFrame = select_order.select_data()
        df_hinban: pd.DataFrame = select_hinban.select_data()

        if len(df_order) == 0:
            print(f'受注日:{orderDate_and_userId[0]} /' 
                  f' userID:{orderDate_and_userId[1]} の受注データはありません')
            print('処理を中止します')
            sys.exit()

        # df['受注日'],df['出荷予定日'],df['納期']を2025/10/17の形にする
        date_manage = DateManage()
        df_order = date_manage.change_to_date(df_order)
        
        # df_orderにMDESTN_U2002をmergeする
        selectMdestn: ISelectData = SelectMdestn()
        df_mdestn = selectMdestn.select_data()
        '''
        ミキ情報では文字列のnullはすべて「" "」(半角スペース)と聞いていたのに、
        MDESTN.DesNonyuCDは、「""」(空文字)だった。そこで、空文字だったら半角スペースに
        変換するコードを追加した
        '''
        df_mdestn['納入先コード'] = df_mdestn['納入先コード'].map(
                                               lambda x: ' ' if x=='' else x)
        df_order = pd.merge(df_order, df_mdestn, 
                             on=['得意先コード', '納入先コード'], how='left')


        # カラムを整理しておく
        df_order['納入先'] = ' '
        df_order['変換数量'] = 0
        df_order['変換単位'] = ' '
        df_order['Check'] = ' '


        # pyrightが右辺はDataFrame,Seriesか迷うのでキャストした
        df_order = pd.DataFrame(df_order[['受注No', '担当者名称', '受注日', 
                             '出荷予定日', '得意先コード', '納入先コード', 
                             '納入先', '得意先名称1', '納入先名称1', 
                             '納入先名称2', '品番', '品名', '受注数量', 
                             '受注単位', '変換数量', '変換単位', '備考1', 
                             '納期', '備考2', 'Check', '所要日数']])
        df_order = df_order.rename(columns={'備考2':'運賃n缶分'})

        # valid_ship_date有効な出荷日を求める
        valid_ship_date = ValidShipDateCheck()
        df_order['isExistShipDate'] = df_order['出荷予定日'].map(
                                                  valid_ship_date.date_isExist)
        df_order['isExistDeliDate'] = df_order['納期'].map(
                                                  valid_ship_date.date_isExist)

        df_order['isShipHolidayToyo'] = df_order['出荷予定日'].map(
                                                valid_ship_date.is_toyoHoliday)
        df_order['isDeliHolidayToyo'] = df_order['納期'].map(
                                                valid_ship_date.is_toyoHoliday)
        df_order['isShipHolidayHauler'] = df_order['出荷予定日'].map(
                                              valid_ship_date.is_haulerHoliday)
        df_order['isDeliHolidayHauler'] = df_order['納期'].map(
                                              valid_ship_date.is_haulerHoliday)

        df_order['valid_ship_date'] = df_order.apply(
                                 valid_ship_date.calc_valid_ship_date, axis= 1)

        df_order['isShipSaturday'] = df_order['出荷予定日'].map(
                                                    valid_ship_date.is_Saturday)
        df_order['isValidShipSaturday'] = df_order['valid_ship_date'].map(
                                                    valid_ship_date.is_Saturday)

        # 輸出製品check df_mdestn = MDESTN_U2002のDataFrame
        export_product_check = ExportProductCheck(df_mdestn)
        df_order['isExport'] = df_order.apply(
                                        export_product_check.is_export, axis= 1)
        df_order['destination'] = df_order.apply(
                                 export_product_check.find_destination, axis= 1)
        df_order['isExistExportProduct'] = df_order.apply(
                           export_product_check.is_exist_exportProduct, axis= 1)

        # 20251107 納入先が表示されないバグを修正
        # destinationの中身を '納入先'にコピる
        df_order['納入先'] = df_order['destination']

        # 単位変換CN->KG, KG->CNを求める
        convert_unit = ConvertUnit(df_hinban)
        df_order[['変換数量', '変換単位']] = df_order.apply(
                                            convert_unit.convert_unit, axis = 1)

        # check列に最終警告を記入する
        check_result_display = CheckResultDisplay()
        df_order['Check'] = df_order.apply(
                               check_result_display.check_result_display, axis=1)
        staff: str = df_order['担当者名称'].iloc[0]
        order_date: str = orderDate_and_userId[0]


        df_order2= pd.DataFrame(df_order[["受注No", "出荷予定日", "得意先コード", 
                              "納入先コード", "納入先", "得意先名称1", 
                              "納入先名称1", "納入先名称2", "品名", 
                              "受注数量", "受注単位", "変換数量", 
                              "変換単位", "備考1", "納期", "運賃n缶分", 
                              "Check"]])

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        
        '''
        2026/4/27 東洋運賃計算結果を追加する
        '''
        csv_path: str = ""
        if platform.system() == 'Windows':
            csv_path = r'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/運賃計算関係/toyo_untin/'
        if platform.system() == 'Linux':
            csv_path = r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/運賃計算関係/toyo_untin/'

        with open(csv_path + 'seikyusaki.csv', 'r', encoding='cp932') as f:
            reader = csv.reader(f)
            seikyusaki:List[List[Any]] = [row for row in reader]
       
        # seikyusaki_codes = [('T0410', ''), ('T0060', 'H084'),...]
        seikyusaki_codes: List[Tuple[str, str]] = []
        for line in seikyusaki:
            tup = (line[0], line[1])
            seikyusaki_codes.append(tup)

        with open(csv_path + 'toyo_untin_tyuukei_ari.csv', 'r', encoding='cp932') as f:
            reader = csv.reader(f)
            tyuukei_ari: List[List[Any]] = [row for row in reader]

        with open(csv_path + 'toyo_untin_tyuukei_nasi.csv', 'r', encoding='cp932') as f:
            reader = csv.reader(f)
            tyuukei_nasi: List[List[Any]] = [row for row in reader]

        
        # 得意先コード、納入先コードでソートしておく
        df_order2 = df_order2.sort_values(by=['得意先コード','納入先コード'])


        def get_cans(df_row)->int:
            cans: int = 0
            if df_row['受注単位'] == 'CN':
                cans = df_row['受注数量']

            if df_row['変換単位'] == 'CN':
                cans = df_row['変換数量']

            return cans

        def get_kg(df_row)->float:
            kg: float = 0
            if df_row['受注単位'] == 'KG':
                kg = df_row['受注数量']

            if df_row['変換単位'] == 'KG':
                kg = df_row['変換数量']

            return kg

        # cansカラムに缶数を詰める
        df_order2['cans'] = df_order2.apply(get_cans, axis=1) 
        # kgカラムにkgを詰める
        df_order2['kg'] = df_order2.apply(get_kg, axis=1) 


        def calc_ncan(df_row):
            tokui_code = df_row['得意先コード']
            nonyu_code = df_row['納入先コード']
            tup = (tokui_code, nonyu_code)

            # effitはnullが' ', seikyusakiデータは''
            if nonyu_code == ' ':
                tup = (tokui_code, '') 

            ncan = 0
            if tup in seikyusaki_codes:
                ncan = df_order2.loc[(df_order2['得意先コード']== tokui_code) 
                    & (df_order2['納入先コード']==nonyu_code),'cans'].sum()
            return ncan

        # 運賃ｎ缶分に追加があった場合はncanカラムに正しい缶数を入れる
        df_order2['ncan'] = df_order2.apply(calc_ncan, axis = 1)

        # toyo運賃を求める
        toyoUntin = ToyoUntin(seikyusaki, tyuukei_ari, tyuukei_nasi, seikyusaki_codes)
        df_order2['toyo運賃'] = df_order2.apply(toyoUntin.get_toyo_untin, axis=1)

        df_order2 = df_order2[[
                '受注No', '出荷予定日', '得意先コード',
                '納入先コード', '納入先', '得意先名称1',
                '納入先名称1', '納入先名称2', '品名',
                '受注数量', '受注単位', '変換数量',
                '変換単位', '備考1', '納期',
                '運賃n缶分', 'ncan', 'toyo運賃', 'Check' ]]

        # 受注No順にソートしなおす。
        df_order2 = df_order2.sort_values(by=['受注No'])
        df_order2.reset_index(drop= True, inplace= True)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        

        # excelと同じものをcsvにも出しておく（念のため）
        df_order2.to_csv('./test.csv', encoding='cp932')
        print(df_order2)

        with pd.ExcelWriter('result.xlsx', engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Sheet1')

            # 1. Set up formats and print settings
            worksheet.set_paper(9)  # A4
            worksheet.set_landscape()
            worksheet.fit_to_pages(1, 0)  # Fit all columns on one page
            worksheet.set_margins(left=0.2, right=0.2, top=0.5, bottom=0.5)

            bold_format = workbook.add_format({'bold': True, 'valign': 'top','font_size': 10})
            HEAD_format = workbook.add_format({
                'valign': 'top', 'font_size': 10})
            header_format = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top',
                'fg_color': '#D7E4BC', 'border': 1, 'font_size': 10})
            cell_format = workbook.add_format({
                'border': 1, 'text_wrap': True, 'valign': 'top', 'font_size': 10})

            # Write custom header in row 1
            worksheet.write('A1', '受注日:', bold_format)
            worksheet.write('B1', order_date, HEAD_format)
            worksheet.write('D1', '顧客満足のため 受注チェックを確実に行います。', HEAD_format)
            worksheet.write('A2', '担当者:', bold_format)
            worksheet.write('B2', staff, HEAD_format)

            # 2. Set column and row properties
            col_widths = {
                '受注No': 10, '出荷予定日': 10, '得意先コード': 5,
                '納入先コード': 5, '納入先': 8, '得意先名称1': 16,
                '納入先名称1': 16, '納入先名称2': 6, '品名': 18,
                '受注数量': 4, '受注単位': 4, '変換数量': 4,
                '変換単位': 4, '備考1': 8, '納期': 10,
                '運賃n缶分': 4, 'ncan': 5, 'toyo運賃': 5, 'Check': 24 
            }
            for i, col_name in enumerate(df_order2.columns):
                worksheet.set_column(i, i, col_widths.get(col_name))

            # Set row heights (with offset for new layout)
            worksheet.set_row(0, 18)  # Table header row (starts at A3)
            worksheet.set_row(1, 18)  # Table header row (starts at A3)
            worksheet.set_row(2, 40)  # Table header row (starts at A3)
            for idx, row in df_order2.iterrows():
                check_text = str(row['Check'])
                num_lines = check_text.count('\n') + 1
                row_height = num_lines * 15
                worksheet.set_row(idx + 3, row_height) # Data rows start after A3

            # 3. Write data to worksheet (with offset for new layout)
            # Write table header starting at A3
            for col_num, value in enumerate(df_order2.columns.values):
                worksheet.write(2, col_num, value, header_format)

            # Write data rows starting at A4
            for row_num, list_of_cells in enumerate(df_order2.values.tolist()):
                worksheet.write_row(row_num + 3, 0, list_of_cells, cell_format)        


        formatted_df = format_df_as_grid(df_order2)
        with open('df_order_grid.txt', 'w', encoding='utf-8') as f:
            f.write(formatted_df)

        print('処理が完了しました。')
        file_to_open = 'result.xlsx'
        
        if platform.system() == 'Windows':
            try:
                os.startfile(file_to_open)
                print(f'{file_to_open} を開きました。')
            except OSError as e:
                print(f'エラー: {file_to_open} を自動で開けませんでした: {e}')
                print('お手数ですが、手動でファイルを開いてご確認ください。')
        if platform.system() == 'Darwin':
            try:
                subprocess.run(['open', file_to_open], check=True)
                print(f'{file_to_open} を開きました。')
            except (OSError, subprocess.CalledProcessError) as e:
                print(f'エラー: {file_to_open} を自動で開けませんでした: {e}')
                print('お手数ですが、手動でファイルを開いてご確認ください。')
        if platform.system() == 'Linux': # For Linux
            print(f'{file_to_open} を作成しました。お手数ですが、手動でファイルを開いてご確認ください。')



