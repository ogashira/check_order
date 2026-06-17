import valid_ship_date
import datetime


class CheckResultDisplay:

    def __init__(self)-> None:
        pass

    def check_result_display(self, df_row)-> str:
        isExistShipDate      = df_row['isExistShipDate']
        isExistDeliDate      = df_row['isExistDeliDate']
        isShipHolidayToyo    = df_row['isShipHolidayToyo']
        isDeliHolidayToyo    = df_row['isDeliHolidayToyo']
        isShipHolidayHauler  = df_row['isShipHolidayHauler']
        isDeliHolidayHauler  = df_row['isDeliHolidayHauler']
        valid_ship_date      = df_row['valid_ship_date']
        ship_date            = df_row['出荷予定日']
        isShipSaturday       = df_row['isShipSaturday']
        isValidShipSaturday  = df_row['isValidShipSaturday']
        isExport             = df_row['isExport']
        destination          = df_row['destination']
        isExistExportProduct = df_row['isExistExportProduct']
        convert_unit         = df_row['変換単位']

        if not isExistShipDate:
            return '休日表に出荷予定日が無し\n'
        if not isExistDeliDate:
            return '休日表に納入日が無し\n'
        if valid_ship_date == 'hoge/hoge/hoge':
            return '正しい出荷日が休日表に無し\n'
        if valid_ship_date == '所要日数データ無し':
            return '所要日数データ無し\n'

        # --- Refactoring the complex if statement ---

        # Define conditions for clarity
        all_dates_exist = isExistShipDate and isExistDeliDate
        no_holidays = not isShipHolidayToyo and not isShipHolidayHauler and not isDeliHolidayHauler
        is_ship_date_correct = datetime.datetime.strptime(valid_ship_date, '%Y/%m/%d') == datetime.datetime.strptime(ship_date, '%Y/%m/%d')
        is_saturday_ok = not isShipSaturday and not isValidShipSaturday
        is_unit_ok = convert_unit in ['KG', 'CN']

        # Non-export success case
        non_export_success = (
            all_dates_exist and
            no_holidays and
            is_ship_date_correct and
            is_saturday_ok and
            not isExport
        )

        # Export success case
        export_conditions_met = (
            isExport and
            destination != 'n&h&mに向先無し' and
            isExistExportProduct
        )
        export_success = export_conditions_met and is_unit_ok

        errors = []
        if non_export_success or export_success:
            errors.append('レ')
        # --- Build error message if not success ---
        
        if isShipHolidayToyo:
            errors.append('出荷予定日が休日')
        if isShipSaturday:
            errors.append('出荷予定日は土曜日！')
        if isShipHolidayHauler:
            errors.append('出荷予定日運送屋休日')
        if isDeliHolidayHauler:
            errors.append('納入日運送屋休日')

        if isExport:
            if destination == 'n&h&mに向先無し':
                errors.append('n&h&mに向先無し')
            if not isExistExportProduct:
                errors.append('輸出品番無し!')

        ship_date_dt = datetime.datetime.strptime(ship_date, '%Y/%m/%d')
        valid_ship_date_dt = datetime.datetime.strptime(valid_ship_date, '%Y/%m/%d')

        if valid_ship_date_dt < ship_date_dt:
            errors.append('納期遅延!')

        if valid_ship_date_dt != ship_date_dt:
            if isValidShipSaturday:
                errors.append(f'{valid_ship_date}?(土曜日)')
            else:
                errors.append(f'{valid_ship_date}?')

        if not is_unit_ok:
            errors.append(convert_unit)
            
        return '\n'.join(errors)
