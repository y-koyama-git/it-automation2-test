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

import sys
import os
import datetime
import textwrap
import random

from common_libs.column import *


class loadTable():
    """
    load_table

        共通
            get_menu_info: メニューIDから関連情報全取得
        REST
            info:   メニュー情報、項目情報、ID連携リスト情報
            filter:   一覧データ取得、検索条件による絞り込み
            maintenance:   登録、更新、廃止、復活処理
            maintenance_all:   登録、更新、廃止、復活の複合処理

    """

    def __init__(self, objdbca='', menu='', lang=''):
        # コンストラクタ
        # メニューID
        self.menu = menu

        # エラーメッセージ集約用
        self.message = {
            'DEBUG': [],
            'INFO': [],
            'WARNING': [],
            'ERROR': [],
            'CRITICAL': [],
        }

        # DB接続
        self.objdbca = objdbca

        # 環境情報
        self.lang = lang

        # メニュー関連情報
        self.objtable = {}
        if self.menu is not None:
            self.objtable = self.get_menu_info()

        # メニュー内で使用可能なrestkye
        self.restkey_list = self.get_restkey_list()

        # 廃止、最終更新日時、最終更新者
        self.base_cols_val = {
            "discard": 0,
            "last_update_date_time": None,
            "last_updated_user": 1,
        }

    def set_message(self, message, level=''):
        """
            エラーレベルでメッセージを設定
            ARGS:
                self.message
        """
        if level in self.message:
            self.message[level].append(message)
        else:
            self.message['ERROR'].append(message)

    def get_message(self, level=''):
        """
            メッセージを取得
            ARGS:
                level:メッセージレベル
            RETRUN:
                self.message
        """
        if len(level) == 0:
            message = self.message
        elif level in self.message:
            message = self.message[level]
        else:
            message = self.message
        return message

    def get_message_count(self, level=''):
        """
            レベルでメッセージを取得
            ARGS:
                level:メッセージレベル
            RETRUN:
                self.message
        """
        result = False
        if len(level) != 0:
            if level in self.message:
                result = len(self.message[level])
        return result

    # メニューIDから関連情報全取得
    def get_menu_info(self):
        """
            メニュー情報取得
            ARGS:
            RETRUN:
                True / エラーメッセージ
        """

        menu_id = None
        # メニュー情報
        query_str = textwrap.dedent("""
            SELECT * FROM T_COMN_MENU_TABLE_LINK TAB_A
            LEFT JOIN T_COMN_MENU TAB_B ON ( TAB_A.MENU_ID = TAB_B.MENU_ID )
            WHERE TAB_B.MENU_NAME_REST = %s
        """).format(menu=self.menu).strip()

        tmp_menu_info = self.objdbca.sql_execute(query_str, [self.menu])

        for tmp_menu in tmp_menu_info:
            menu_info = tmp_menu
            menu_id = tmp_menu.get('MENU_ID')

        # カラム情報情報
        query_str = textwrap.dedent("""
            SELECT
                TAB_A.*,
                TAB_B.COLUMN_CLASS_NAME AS COLUMN_CLASS_NAME
            FROM T_COMN_MENU_COLUMN_LINK TAB_A
            LEFT JOIN T_COMN_COLUMN_CLASS TAB_B  ON ( TAB_A.COLUMN_CLASS = TAB_B.COLUMN_CLASS_ID )
            WHERE MENU_ID = '{menu_id}'
            """).format(menu_id=menu_id).strip()
        tmp_cols_info = self.objdbca.sql_execute(query_str)
        cols_info = {}
        list_info = {}
        for tmp_col_info in tmp_cols_info:
            rest_name = tmp_col_info.get('COLUMN_NAME_REST')
            cols_info.setdefault(rest_name, tmp_col_info)
            
            # 参照先テーブル情報
            ref_table_name = tmp_col_info.get('REF_TABLE_NAME')
            ref_pkey_name = tmp_col_info.get('REF_PKEY_NAME')
            ref_col_name = tmp_col_info.get('REF_COL_NAME')
            ref_multi_lang = tmp_col_info.get('REF_MULTI_LANG')
            ref_sort_conditions = tmp_col_info.get('REF_SORT_CONDITIONS')

            if ref_table_name is not None:
                if ref_multi_lang == "1":
                    lang_extja = "_JA"
                    lang_exten = "_EN"
                    user_env = self.get_lang()
                    if user_env is not None:
                        if user_env.lower() == 'ja':
                            ref_col_name = "{}{}".format(ref_col_name, lang_extja)
                        elif user_env.lower() == 'en':
                            ref_col_name = "{}{}".format(ref_col_name, lang_exten)
                    else:
                        ref_col_name = "{}{}".format(ref_col_name, lang_extja)
                query_str = textwrap.dedent("""
                    SELECT * FROM {table_name}
                    WHERE DISUSE_FLAG <> 1
                """).format(table_name=ref_table_name).strip()
                tmp_rows = self.objdbca.sql_execute(query_str)

                tmp_list = {}
                for tmp_row in tmp_rows:

                    tmp_id = tmp_row.get(ref_pkey_name)
                    tmp_nm = tmp_row.get(ref_col_name)
                    tmp_list.setdefault(tmp_id, tmp_nm)

                list_info.setdefault(rest_name, tmp_list)

        result = {
            'MENUINFO': menu_info,
            'COLINFO': cols_info,
            'LIST': list_info
        }

        return result

    def get_lang(self):
        """
            言語情報を取得
            RETRUN:
                string
        """
        return self.lang
    
    def get_objtable(self):
        """
            テーブルデータを設定
            RETRUN:
                self.objtable
        """
        return self.objtable

    def get_objcols(self):
        """
            全カラム設定を取得
            RETRUN:
                {}
        """
        return self.objtable.get('COLINFO')

    def get_objcol(self, rest_key):
        """
            単一カラム設定を取得
            RETRUN:
                {}
        """
        return self.get_objcols().get(rest_key)

    def get_table_name(self):
        """
            テーブル名を取得
            RETRUN:
                string
        """
        return self.get_objtable().get('MENUINFO').get('TABLE_NAME')

    def get_sort_key(self):
        """
            ソートキーを取得
            RETRUN:
                {} or [] ?
        """
        return self.get_objtable().get('MENUINFO').get('SORT_KEY')

    def get_col_name(self, rest_key):
        """
            カラム名を取得
            RETRUN:
                self.col_name
        """
        col_name = None
        if self.get_objcol(rest_key) is not None:
            col_name = self.get_objcol(rest_key).get("COL_NAME")
        return col_name

    def get_col_class_name(self, rest_key):
        """
            カラムクラス設定を取得
            RETRUN:
                {}
        """
        col_class_name = None
        get_objcol = self.get_objcol(rest_key)
        if get_objcol is not None:
            col_class_name = get_objcol.get("COLUMN_CLASS_NAME")
        return col_class_name

    def get_columnclass(self, rest_key, cmd_type=''):
        """
            カラムクラス呼び出し
            ARGS:
                rest_key:REST用の項目名
            RETRUN:
                obj
        """
        # objcol = self.get_objcol(rest_key)
        # col_class_name = self.get_col_class_name(rest_key)
        # col_name = self.get_col_name(rest_key)
        #if col_class_name not in sys.modules:
        #    col_class_name = 'TextColumn'
        #eval_class_str = "{}(self.objdbca,self.objtable,rest_key,cmd_type)".format(col_class_name)
        #print(eval_class_str)
        #objcolumn = eval(eval_class_str)
        
        col_class_name = self.get_col_class_name(rest_key)
        try:
            eval_class_str = "{}(self.objdbca,self.objtable,rest_key,cmd_type)".format(col_class_name)
            objcolumn = eval(eval_class_str)
        except:
            col_class_name = 'TextColumn'
            eval_class_str = "{}(self.objdbca,self.objtable,rest_key,cmd_type)".format(col_class_name)
            objcolumn = eval(eval_class_str)
        return objcolumn

    def get_locktable(self):
        """
            テーブルデータを設定
            RETRUN:
                self.objtable
        """
        return self.get_objtable().get('MENUINFO').get('LOCK_TABLE')

    def get_restkey_list(self):
        """
            rest_key list
            RETRUN:
                []
        """
        return list(self.get_objcols().keys())

    def get_rest_key(self, col_name):
        """
            rest_key list
            RETRUN:
                []
        """
        result = ''
        for rest_key, objcol in self.get_objcols().items():
            tmp_col_name = objcol.get('COL_NAME')
            if col_name == tmp_col_name:
                result = rest_key
                break

        return result
    
    # RESTAPI[info]:ALL
    def rest_info(self):
        """
            RESTAPI[info]:ALL
            ARGS:
            RETRUN:
                {} / エラーメッセージ
        """
        result = {}
        # 対象メニュー関連情報全返却
        objcols = self.get_objcols()

        parameter_cols = {}
        file_cols = {}
        for rest_key, colinfo in objcols.items():
            colname_jp = colinfo.get('COLUMN_NAME_JA')
            # colname_en = colinfo.get('COLUMN_NAME_EN')
            colclass = colinfo.get('COLUMN_CLASS_NAME')
            parameter_cols.setdefault(rest_key, colname_jp)
            if colclass == "FileUploadColumn":
                file_cols.setdefault(rest_key, colname_jp)
        result.setdefault('parameter', parameter_cols)
        result.setdefault('file', file_cols)
        return result

    # RESTAPI[info]:メニュー情報のみ
    def rest_info_menuinfo(self):
        """
            RESTAPI[info]:メニュー情報のみ
            ARGS:
                menu_id:メニュー
            RETRUN:
                {} / エラーメッセージ
        """
        result = {}
        # メニュー情報のみ返却

        return result

    # RESTAPI[info]:カラム情報のみ
    def rest_info_columninfo(self):
        """
            RESTAPI[info]:カラム情報のみ
            ARGS:
            RETRUN:
                {} / エラーメッセージ
        """
        result = {}
        # カラム情報のみ返却

        return result

    # [info]:ID連携用のリスト
    def rest_info_list(self):
        """
            RESTAPI[info]:ID連携用のリスト
            ARGS:
            RETRUN:
                {} / エラーメッセージ
        """
        result = {}
        # ID連携用のリスト返却

        return result

    # [filter]:メニューのレコード取得
    def rest_filter(self, parameter, mode=''):
        """
            RESTAPI[filter]:メニューのレコード取得
            ARGS:
                parameter:検索条件
                mode: 本体 / 履歴
            RETRUN:
                {} / エラーメッセージ
        """
        result = {}
        filter_querys = []
        table_name = self.get_table_name()
        if isinstance(parameter, dict):
            for search_key, search_confs in parameter.items():
                if len(search_confs) > 0:
                    for search_mode, search_conf in search_confs.items():
                        if search_key in self.get_restkey_list():
                            objcolumn = self.get_columnclass(search_key)
                            filter_querys.append(objcolumn.get_filter_query(search_mode, search_conf))
                            print(search_key, search_mode, filter_querys)

        #  全件
        where_str = ''
        bind_value_list = []
        conjunction = "where"
        if len(filter_querys) > 0:
            for filter_query in filter_querys:
                if filter_query.get('where') is not None:
                    print(filter_query)
                    if len(where_str) != 0:
                        conjunction = 'and'
                    tmp_where_str = ' {} {}'.format(conjunction, filter_query.get('where'))
                    bindkeys = filter_query.get('bindkey')
                    if isinstance(bindkeys, str):
                        bindkey = bindkeys
                        tmp_where_str = tmp_where_str.replace(bindkey, '%s')
                        bind_value_list.append(filter_query.get('bindvalue').get(bindkey))
                            
                    elif isinstance(bindkeys, list):
                        for bindkey in bindkeys:
                            tmp_where_str = tmp_where_str.replace(bindkey, '%s')
                            bind_value_list.append(filter_query.get('bindvalue').get(bindkey))
                    where_str = where_str + tmp_where_str
        
        sort_key = self.get_sort_key()
        if sort_key is not None:
            str_orderby = ''
            where_str = where_str + str_orderby

        # データ取得
        tmp_result = self.objdbca.table_select(table_name, where_str, bind_value_list)

        # RESTキー変換はSQL OR python
        result = {
            "parameter": [],
            "file": []
        }
        # RESTパラメータへキー変換
        # rownum = 0
        for rows in tmp_result:
            rest_parameter, rest_file = self.convert_colname_restkey(rows)
            # result['parameter'].setdefault(str(rownum), rest_parameter)
            # result['file'].setdefault(str(rownum), rest_file)
            result['parameter'].append(rest_parameter)
            result['file'].append(rest_file)
            # rownum = +1

        return result

    # [maintenance]:メニューのレコード操作
    def rest_maintenance(self, parameters, target_uuid=''):
        """
            RESTAPI[filter]:メニューのレコード操作
            ARGS:
                parameters:パラメータ
                cmd_type: 登録/更新/廃止/復活
            RETRUN:
                {} / エラーメッセージ
        """
        result = {}
        #  登録/更新/廃止/復活 処理

        # if cmd_type is None:
        cmd_type = parameters.get('maintenance_type')

        # トランザクション開始
        self.objdbca.db_transaction_start()

        # 対象メニューのテーブルと「ロック対象テーブル」を昇順でロック
        locktable_list = self.get_locktable()
        if locktable_list is not None:
            result = self.objdbca.table_lock(locktable_list)
        else:
            result = self.objdbca.table_lock(list(self.get_table_name()))
            print(" no table_lock list  self.objdbca.table_lock(list(self.get_table_name()))")
            # return "{}".format(" no table_lock list ")

        # maintenance呼び出し
        result = self.exec_maintenance(parameters, target_uuid, cmd_type)
        # print({"exec_maintenance": result})
        if result[0] is True:
            # コミット  トランザクション終了
            self.objdbca.db_transaction_end(True)
        else:
            # ロールバック トランザクション終了
            self.objdbca.db_transaction_end(False)

        return result,

    # [maintenance]:メニューのレコード登録
    def rest_maintenance_all(self, list_parameters):
        """
            RESTAPI[filter]:メニューのレコード取得
            ARGS:
                parameters:パラメータ
                mode: 登録/更新/廃止/復活
            RETRUN:
                {} / エラーメッセージ
        """
        result = []

        tmp_result = {}
        # トランザクション開始
        self.objdbca.db_transaction_start()

        # 対象メニューのテーブルと「ロック対象テーブル」を昇順でロック
        locktable_list = self.get_locktable()
        if locktable_list is not None:
            tmp_result = self.objdbca.table_lock(locktable_list)
        else:
            tmp_result = self.objdbca.table_lock(list(self.get_table_name()))
            print(" no table_lock list ")
            # return "{}".format(" no table_lock list ")

        for tmp_parameters in list_parameters:
            entry_no = list_parameters.index(tmp_parameters)
            cmd_type = tmp_parameters.get("maintenance_type")
            parameters = tmp_parameters

            # テーブル情報（カラム、PK取得）
            column_list, primary_key_list = self.objdbca.table_columns_get(self.get_table_name())
            target_uuid_key = self.get_rest_key(primary_key_list[0])
            target_uuid = parameters.get('parameter').get(target_uuid_key)
            
            # maintenance呼び出し
            tmp_result = self.exec_maintenance(parameters, target_uuid, cmd_type)
            # result.setdefault(entry_no, tmp_result)
            result.append(tmp_result)

        if self.get_message_count("ERROR") == 0:
            # コミット
            self.objdbca.db_transaction_end(True)
        elif self.get_message_count("ERROR") > 0:
            # ロールバック トランザクション終了
            self.objdbca.db_transaction_end(False)
            retBool = False
            # return retBool, self.get_message("ERROR")

        return retBool, result,

    # [maintenance]:メニューのレコード操作
    def exec_maintenance(self, parameters, target_uuid, cmd_type):
        """
            RESTAPI[filter]:メニューのレコード操作
            ARGS:
                parameters:パラメータ
                cmd_type: 登録/更新/廃止/復活
            RETRUN:
                {} / エラーメッセージ
        """
        retBool = True
        result = {}
        #  登録/更新(廃止/復活) 処理

        # 各カラム単位の基本処理（前）、個別処理（前）を実施
        # REST用キーのパラメータ、ファイル(base64)
        entry_parameter = parameters.get('parameter')
        entry_file = parameters.get('file')

        # 更新系の追い越し判定簡易チェック
        if cmd_type != 'Register':
            if "last_update_date_time" not in entry_parameter:
                print("追い越し判定予定")

        # 更新時
        if cmd_type != 'Register':
            if "discard" in entry_parameter:
                tmp_discard = entry_parameter.get("discard")
                if tmp_discard == "1":
                    cmd_type = 'Discard'
                elif tmp_discard == "0":
                    cmd_type = 'Restore'
                else:
                    cmd_type = 'Update'
        # print([cmd_type,target_uuid])
        # テーブル情報（カラム、PK取得）
        column_list, primary_key_list = self.objdbca.table_columns_get(self.get_table_name())

        if target_uuid != '':
            target_uuid_key = self.get_rest_key(primary_key_list[0])
            entry_parameter[target_uuid_key] = target_uuid
        
        base_cols_val = self.base_cols_val.copy()

        # 入力項目 PK以外除外
        for tmp_keys in list(entry_parameter.keys()):
            objcol = self.get_objcol(tmp_keys)
            if objcol is not None:
                input_item = objcol.get('INPUT_ITEM')
                tmp_col_name = self.get_col_name(tmp_keys)
                if input_item != '1':
                    if tmp_col_name not in column_list:
                        del entry_parameter[tmp_keys]
                if cmd_type == 'Discard':
                    if tmp_col_name not in primary_key_list:
                        del entry_parameter[tmp_keys]
            else:
                del entry_parameter[tmp_keys]
                    
        for rest_key, rest_val in entry_parameter.items():
            if rest_key in self.restkey_list:
                option = {}
                option.setdefault("target_uuid", target_uuid)

                # ファイル有無
                if entry_file is not None:
                    if rest_key in entry_file:
                        option.setdefault("file_data", entry_file.get(rest_key))

                # カラムクラス呼び出し
                objcolumn = self.get_columnclass(rest_key, cmd_type)

                # カラムクラス毎の処理:レコード操作前
                # カラム毎の個別処理:レコード操作前
                exec1 = objcolumn.before_iud_action(rest_val, option)
                if exec1[0] is not True:
                    print({"exec1": exec1[1]})
                    self.set_message(exec1[1], "ERROR")
            else:
                retBool = False
                msg = "不正なキー"
                return retBool, msg
 
        # テーブル単位の個別処理前を実行
            # メニュー共通処理:レコード操作前
            # メニュー個別処理:レコード操作前

        # レコード操作前エラー確認
        if self.get_message_count("ERROR") > 0:
            retBool = False
            return retBool, self.get_message("ERROR")

        # 登録・更新処理
        # SQL生成  INSERT / UPDATE

        # 廃止の設定
        if cmd_type == 'Discard':
            base_cols_val['discard'] = 1
        else:
            base_cols_val['discard'] = 0

        entry_parameter.update(base_cols_val)

        # rest_key → カラム名に変換
        colname_parameter = self.convert_restkey_colname(entry_parameter)

        if cmd_type == 'Register':
            print(" [{}] INSERT XXXXXX / INSERT XXXXXX_JNL ".format(cmd_type))
            result = self.objdbca.table_insert(self.get_table_name(), colname_parameter, primary_key_list[0])
        elif cmd_type == 'Update':
            print(" [{}] UPDATE XXXXXX / INSERT XXXXXX_JNL ".format(cmd_type))
            result = self.objdbca.table_update(self.get_table_name(), colname_parameter, primary_key_list[0])
        elif cmd_type == 'Discard':
            print(" [{}] UPDATE XXXXXX / INSERT XXXXXX_JNL ".format(cmd_type))
            result = self.objdbca.table_update(self.get_table_name(), colname_parameter, primary_key_list[0])
        elif cmd_type == 'Restore':
            print(" [{}] UPDATE XXXXXX / INSERT XXXXXX_JNL ".format(cmd_type))
            result = self.objdbca.table_update(self.get_table_name(), colname_parameter, primary_key_list[0])

        # print(result)
        if result is False:
            self.set_message(result, "ERROR")
        else:
            temp_rows = {primary_key_list[0]: result[0].get(primary_key_list[0])}
            tmp_result = self.convert_colname_restkey(temp_rows)
            result = tmp_result[0]

        # レコード操作後エラー確認
        if self.get_message_count("ERROR"):
            retBool = False
            return retBool, self.get_message("ERROR")

        # 各カラム単位の基本処理（後）、個別処理（後）を実施
        for rest_key, rest_val in entry_parameter.items():
            # カラムクラス呼び出し
            objcolumn = self.get_columnclass(rest_key, cmd_type)
            # カラムクラス毎の処理:レコード操作後
            # カラム毎の個別処理:レコード操作後
            exec2 = objcolumn.after_iud_action(rest_key, option)
            if exec2[0] is not True:
                self.set_message(exec2[1], "ERROR")
        # テーブル単位の個別処理後を実行
            # メニュー共通処理:レコード操作後
            # メニュー個別処理:レコード操作後

        # レコード操作前エラー確認
        if self.get_message_count("ERROR"):
            retBool = False
            return retBool, self.get_message("ERROR")

        return retBool, result

    # [output]:検索結果のファイル出力
    def rest_export(self, data, mode):
        """
            RESTAPI[output]:検索結果のファイル出力
            ARGS:
                data:データ
                mode:出力形式
            RETRUN:
                ファイルbase64? / エラーメッセージ
        """
        result = None

        #  Excel / Json 出力処理
        # base64変換

        return result

    # []:RESTパラメータのキー変換
    def convert_restkey_colname(self, parameter):
        """
            []::RESTパラメータのキー変換
            ARGS:
                parameter:パラメータ
                mode: 登録/更新/廃止/復活
            RETRUN:
                {}
        """
        result = {}
        for restkey, restval in parameter.items():
            colname = self.get_col_name(restkey)
            if colname is not None:
                result.setdefault(colname, restval)
        return result

    def convert_colname_restkey(self, rows, mode=''):
        """
            []::RESTパラメータへキー変換
            ARGS:
                parameter:パラメータ
                mode: 登録/更新/廃止/復活
            RETRUN:
                {}
        """
        rest_parameter = {}
        rest_file = {}
        for col_name, col_val in rows.items():
            rest_key = self.get_rest_key(col_name)

            if len(rest_key) > 0:
                # objcolumn = self.get_columnclass(rest_key)

                if isinstance(col_val, datetime.datetime):
                    col_val = '{}'.format(col_val.strftime('%Y/%m/%d %H:%M:%S.%f'))

                rest_parameter.setdefault(rest_key, col_val)
                if mode == "output":
                    if self.get_col_class_name(rest_key) == 'FileUploadColumn':
                        # ファイル取得＋64変換
                        file_data = '{}のbase64後のSTR'.format(rest_key)
                        rest_file.setdefault(rest_key, file_data)

        # print({"result":result})
        return rest_parameter, rest_file
