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

import os
import sys
from flask import g
from common_libs.common import *  # noqa: F403

# import column_class
from .id_class import IDColumn

"""
カラムクラス個別処理(Id)
"""


class EnvironmentIDColumn(IDColumn):
    """
    テキスト系クラス共通処理
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
        
    def get_values_by_key(self, where_equal=[]):
        """
            Keyを検索条件に値を取得する
            ARGS:
                where_equal:一致検索のリスト
            RETRUN:
                values:検索結果
        """

        values = {}

        environments = util.get_exastro_platform_workspaces()[1]

        # 一致検索
        if len(where_equal) > 0:
            for where_value in where_equal:
                if where_value in environments:
                    values[where_value] = where_value
        else:
            for environment in environments:
                    values[environment] = environment

        return values

    def get_values_by_value(self, where_equal=[], where_like=""):
        """
            valueを検索条件に値を取得する
            ARGS:
                where_equal:一致検索のリスト(list)
                where_like:あいまい検索の値(string)
            RETRUN:
                values:検索結果
        """
        tmp_environments = {}
        values = {}

        environments = util.get_exastro_platform_workspaces()[1]

        # 一致検索
        if len(where_equal) > 0:
            for where_value in where_equal:
                if where_value in environments:
                    tmp_environments[where_value] = where_value
        else:
            for environment in environments:
                tmp_environments[environment] = environment

        # あいまい検索
        if len(where_like) > 0:
            for environment in tmp_environments.values():
                if where_like in environment:
                    values[environment] = environment
        else:
            values = tmp_environments

        return values
