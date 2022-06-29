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
import os
import base64

#import column_class
from column_class import Column

"""
カラムクラス個別処理(FileUploadColumn)
"""
class FileUploadColumn(Column):
    """
    ファイル系クラス共通処理
    """
    def __init__(self, objdbca, objtable, rest_key_name, cmd_type):

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
        
        self.cmd_type = cmd_type

    def check_basic_valid(self, val, option={}):
        """
            バリデーション処理
            ARGS:
                val:値
                dict_valid:バリデーション閾値
            RETRUN:
                True / エラーメッセージ
        """
        retBool = True
        min_length = 0
        max_length = 255
        # 閾値(最大値)
        upload_max_size = None
        # ファイル名正規表現　カンマとダブルクォートとタブとスラッシュと改行以外の文字
        preg_match = r"^[^,\"\t\/\r\n]*$"
        # デコード値
        decode_option = base64.b64decode(option["file_data"].encode())
        # 禁止拡張子
        forbidden_extension_arry = self.objdbca.table_select("T_COMN_SYSTEM_CONFIG", "WHERE CONFIG_ID = %s", bind_value_list=['FORBIDDEN_UPLOAD'])
        
        forbidden_extension = forbidden_extension_arry[0]["VALUE"]
        
        # カラムの閾値を取得
        objcols = self.get_objcols()
        if objcols is not None:
            if self.get_rest_key_name() in objcols:
                dict_valid = self.get_dict_valid()
                # 閾値(文字列長)
                upload_max_size = dict_valid.get('upload_max_size')

        # 文字列長
        if max_length is not None:
            check_val = len(str(val).encode('utf-8'))
            if check_val != 0:
                if int(min_length) < check_val < int(max_length):
                    retBool = True
                else:
                    retBool = False
                    msg = "文字長エラー (閾値:{}<値<{}, 値{})[{}]".format(min_length, max_length, check_val, self.rest_key_name)
                    return retBool, msg
        
        # ファイル名のチェック
        if preg_match is not None:
            if len(preg_match) != 0:
                patarn = re.compile(preg_match, re.DOTALL)
                tmp_result = patarn.fullmatch(val)
                if tmp_result is None:
                    retBool = False
                    msg = "正規表現エラー (閾値:{},値{})[{}]".format(patarn, val, self.rest_key_name)
                    return retBool, msg

        # バイト数比較
        if decode_option and upload_max_size is not None:
            if len(decode_option) > upload_max_size:
                retBool = False
                msg = "バイト数超過　(閾値:{},値{})[{}]".format(upload_max_size, len(decode_option), self.rest_key_name)
                return retBool, msg
        else:
            retBool = False
            msg = "バイト数無し (閾値:{},値{})[{}]".format(upload_max_size, len(decode_option), self.rest_key_name)
            return retBool, msg

        # 拡張子だけ取り出す
        if forbidden_extension is not None:
            forbidden_extensions = forbidden_extension.split(';')
            extension_arr = os.path.splitext(val)
            extension_val = extension_arr[1].lower()
            # リストの中身を全て小文字に変更
            forbidden_extensions = list(map(lambda e: e.lower(), forbidden_extensions))
            if extension_val in forbidden_extensions:
                msg = "禁止拡張子(閾値:{},値{})[{}]".format(forbidden_extensions, extension_val, self.rest_key_name)
                retBool = False
                return retBool, msg
            
        return retBool,

    def after_iud_common_action(self, val, option={}):
        """
           カラムクラス毎の個別処理 レコード操作後
            ARGS:
                val:値
                option:オプション
            RETRUN:
                True / エラーメッセージ
        """
        retBool = True
        decode = base64.b64decode(option["file_data"].encode())
        decode_option = decode.decode()
        uuid = option["uuid"]

        # カラムクラス毎の個別処理
        dir_path = "/workspace/ita_root/test/menu_id/" + uuid
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
            
        try:
            with open(os.path.join(dir_path, val), "x") as f:
                f.write(str(decode_option))
        except FileExistsError as msg:
            retBool = False
            return retBool, msg

        return retBool,
