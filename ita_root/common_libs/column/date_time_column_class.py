# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
from datetime import datetime

#import column_class
from date_column_class import DateColumn 

"""
カラムクラス個別処理(DateTimeColumn)
"""
class DateTimeColumn(DateColumn) :
    """
    テキスト系クラス共通処理
    """
    def __init__(self,objdbca,objtable,rest_key_name):
        # カラムクラス名
        self.class_name = self.__class__.__name__
        # メッセージ
        self.message = ''
        # バリデーション閾値
        self.dict_valid = {}
        # テーブル情報
        self.objtable = objtable

        # テーブル名
        table_name = ''
        objmenu = objtable.get('MENUINFO')
        if objmenu is not None:
            table_name = objmenu.get('TABLE_NAME')
        self.table_name = table_name

        # カラム名
        col_name = ''
        objcols = objtable.get('COLINFO')
        if objcols is not None:
            objcol = objcols.get(rest_key_name)
            if objcol is not None:
                col_name = objcol.get('COL_NAME')

        self.col_name = col_name
        
        # rest用項目名
        self.rest_key_name = rest_key_name

        self.db_qm = "'"

        self.objdbca = objdbca

    def check_basic_valid(self,val,option={}):
        """
            バリデーション処理(カラムクラス毎)
            ARGS:
                val:値
            RETRUN:
                True / エラーメッセージ
        """
        retBool = True
        # 閾値(最小値)
        min_datetime = datetime.strptime('1000/01/01 00:00:00.000000', '%Y/%m/%d %H:%M:%S.%f')
        # 閾値(最大値)
        max_datetime = datetime.strptime('9999/12/31 23:59:59.999999', '%Y/%m/%d %H:%M:%S.%f')  

        if len(val) == 0:
            return retBool,

		# 日付形式に変換
        try:
            dt_val = datetime.strptime(val, '%Y/%m/%d %H:%M:%S.%f')
        except ValueError as msg:
            retBool = False
            return retBool, msg

        #文字列長
        if min_datetime is not None and max_datetime is not None:
            check_val = dt_val.timestamp()
            if check_val < .000000:
                msg = "正常に処理できる範囲外です。(値{})".format(check_val)
                retBool = False
                return retBool, msg
            elif check_val != 0:
                if min_datetime >= dt_val or dt_val >= max_datetime:
                    retBool = False
                    msg = "範囲外({}<={}<={})".format(min_datetime, dt_val, max_datetime)
                    return retBool, msg

        return retBool,
