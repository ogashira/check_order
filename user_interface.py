from typing import Dict, List, Tuple
import socket
import sys


class UserInterface:

    def __init__(self)-> None:
        self.__pcNames:Dict[str, str] = {'toyo-pc04': '000240', 
                                         'toyo-pc05': '000210',
                                         'toyo-pc13': '000440',
                                         'toyo-pc12': '000410',
                                         'TOYO-PC04': '000240', 
                                         'TOYO-PC05': '000210',
                                         'TOYO-PC13': '000440',
                                         'TOYO-PC12': '000410',
                                         }
        

        self.__userId = ''
        pcName: str = socket.gethostname()

        if  pcName in self.__pcNames.keys():
            self.__userId = self.__pcNames[pcName]
        


    def get_orderDate_and_id(self)-> Tuple[str, str]:
        '''
        ユーザーが入力した受注日と、ユーザーIDのﾀプルを返す。
        PCドメイン名からユーザーIDを返すが、ユーザーIDを変更すること
        も可能
        ユーザーIDがself.__pcNamesのvaluesに無いと進まない。
        '''
        ans: Tuple[str, str] 
        order_date: str = ''
        while True:
            print('チェックしたい受注日を入力してください(例 : 20220930) / Returnで中止')
            order_date = input('受注日 : ')
            if not order_date:
                print('ﾌﾟﾛｸﾞﾗﾑを中止します')
                sys.exit()
                
            if (
                len(order_date) == 8 and
                2020 <= int(order_date[:4]) <= 2100 and
                1 <= int(order_date[4:6]) <= 12 and
                1 <= int(order_date[6:]) <= 31
                ):
                    break

            print('正しい年月日を入力してください')


        while True:
            if self.__userId == '':
                print('userIDを入力してください / Rerurnで中止')
                userId: str = input('userId : ')
                if not userId:
                    print('プログラムを中止します')
                    sys.exit()
                if not userId in self.__pcNames.values():
                    print(f'userID : {userId}は未登録です')
                if userId in self.__pcNames.values():
                    return (order_date, userId)

            if self.__userId != '':
                print(f'userIDは{self.__userId}でよろしいですか？ ( y , n ) ')
                isUserId: str = input()
                if not isUserId:
                    print('プログラムを中止します')
                    sys.exit()

                if isUserId == 'y':
                    return (order_date, self.__userId)

                if isUserId == 'n':
                    while True:
                        print('userIDを入力してください / Rerurnで中止')
                        userId: str = input('userId : ')
                        if not userId:
                            print('プログラムを中止します')
                            sys.exit()
                        if userId in self.__pcNames.values():
                            return (order_date, userId)

                        if not userId in self.__pcNames.values(): 
                            print(f'userID : {userId} は未登録です')




