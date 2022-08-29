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
from flask import g
from common_libs.common import *  # noqa: F403
from .multi_text_class import MultiTextColumn


class LastUpdateUserColumn(MultiTextColumn):
    """
    カラムクラス個別処理(LastUpdateUserColumn)
    """
    # def __init__(self, objdbca, objtable, rest_key_name, cmd_type):

    #     # カラムクラス名
    #     self.class_name = self.__class__.__name__
    #     # メッセージ
    #     self.message = ''
    #     # バリデーション閾値
    #     self.dict_valid = {}
    #     # テーブル情報
    #     self.objtable = objtable

    #     # テーブル名
    #     table_name = ''
    #     objmenu = objtable.get('MENUINFO')
    #     if objmenu is not None:
    #         table_name = objmenu.get('TABLE_NAME')
    #     self.table_name = table_name

    #     # カラム名
    #     col_name = ''
    #     objcols = objtable.get('COLINFO')
    #     if objcols is not None:
    #         objcol = objcols.get(rest_key_name)
    #         if objcol is not None:
    #             col_name = objcol.get('COL_NAME')

    #     self.col_name = col_name
        
    #     # rest用項目名
    #     self.rest_key_name = rest_key_name

    #     self.db_qm = "'"

    #     self.objdbca = objdbca
        
    #     self.cmd_type = cmd_type

    def convert_value_input(self, val=''):
        """
            値を暗号化
            ARGS:
                val:値
            RETRUN:
                retBool, msg, val
        """
        retBool = True
        msg = ''
        user_env = g.LANGUAGE.upper()
        table_name = "T_COMN_BACKYARD_USER"
        where_str = "WHERE USER_NAME_{} = %s".format(user_env)
        bind_value_list = [val]
        return_values = self.objdbca.table_select(table_name, where_str, bind_value_list)
        ret = len(return_values)
        if ret == 1:
            val = return_values[0]["USER_ID"]
        # return_valuesの結果が1ならUSER_IDを返す　それ以外は共通基盤に問い合わせる処理

        return retBool, msg, val

    # [load_table] 出力用の値へ変換
    def convert_value_output(self, val=''):
        """
            出力用の値へ変換
            ARGS:
                val:値
            RETRUN:
                retBool, msg, val
        """
        retBool = True
        msg = ''
        user_env = g.LANGUAGE.upper()
        table_name = "T_COMN_BACKYARD_USER"
        where_str = "WHERE USER_ID = %s AND DISUSE_FLAG='0'"
        bind_value_list = [val]

        return_values = self.objdbca.table_select(table_name, where_str, bind_value_list)
        # return_valuesの結果が1ならUSER_NAMEを返す　それ以外は共通基盤に問い合わせる処理
        if len(return_values) == 1:
            try:
                val = return_values[0]["USER_NAME_{}".format(user_env)]
            except Exception as e:
                print(e)
        else:
            users = util.get_exastro_platform_users()

            if val in users:
                val = users[val]
            else:
                status_code = 'MSG-00001'
                val = g.appmsg.get_api_message(status_code, [val])

        return retBool, msg, val,

