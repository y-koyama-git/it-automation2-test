#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re
import binascii
from libs.organization_common import check_auth_menu  # noqa: F401


def menu_column_valid(objdbca, objtable, option):
    retBool = True
    msg = ''
    # menu_name_rest = objtable.get('MENUINFO').get('MENU_NAME_REST')
    entry_parameter = option.get('entry_parameter').get('parameter')    
    column_class = entry_parameter.get("column_class")

    # 文字列(単一行)最大バイト数
    string_maximum_bytes = entry_parameter.get("string_maximum_bytes")
    # 文字列(単一行)正規表現
    string_regular_expression = entry_parameter.get("string_regular_expression")
    # 初期値(文字列(単一行))
    string_default_value = entry_parameter.get("string_default_value")
    # 文字列(複数行)最大バイト数
    multi_string_maximum_bytes = entry_parameter.get("multi_string_maximum_bytes")
    # 文字列(複数行)正規表現
    multi_string_regular_expression = entry_parameter.get("multi_string_regular_expression")
    # 初期値(文字列(複数行))
    multi_string_default_value = entry_parameter.get("multi_string_default_value")
    # 整数最大値
    integer_maximum_value = entry_parameter.get("integer_maximum_value")
    # 整数最小値
    integer_minimum_value = entry_parameter.get("integer_minimum_value")
    # 初期値(整数)
    integer_default_value = entry_parameter.get("integer_default_value")
    # 小数最大値
    decimal_maximum_value = entry_parameter.get("decimal_maximum_value")
    # 小数最小値
    decimal_minimum_value = entry_parameter.get("decimal_minimum_value")
    # 小数桁数
    decimal_digit = entry_parameter.get("decimal_digit")
    # 初期値(小数)
    decimal_default_value = entry_parameter.get("decimal_default_value")
    # 初期値(日時)
    detetime_default_value = entry_parameter.get("detetime_default_value")
    # 初期値(日付)
    dete_default_value = entry_parameter.get("dete_default_value")
    # メニューグループ：メニュー：項目
    pulldown_selection = entry_parameter.get("pulldown_selection")
    # 初期値(プルダウン選択)
    pulldown_selection_default_value = entry_parameter.get("pulldown_selection_default_value")
    # 参照項目
    reference_item = entry_parameter.get("reference_item")
    # パスワード最大バイト数
    password_maximum_bytes = entry_parameter.get("password_maximum_bytes")
    # ファイルアップロード/ファイル最大バイト数
    file_upload_maximum_bytes = entry_parameter.get("file_upload_maximum_bytes")
    # リンク/最大バイト数
    link_maximum_bytes = entry_parameter.get("link_maximum_bytes")
    # 初期値(リンク)
    link_default_value = entry_parameter.get("link_default_value")
    # パラメータシート参照/メニューグループ：メニュー：項目
    parameter_sheet_reference = entry_parameter.get("parameter_sheet_reference")
    
    # メモ 正規表現専用のバリデータクラス　正規表現が不正な文法

    # 入力方式が文字列(単一行)の場合
    if column_class == "1":
        # 文字列(単一行)最大バイト数が設定されていない場合、エラー
        if retBool and string_maximum_bytes is None:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「最大バイト数」は必須です。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「文字列(単一行)」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"
        # 最大バイト数と初期値の条件一致をチェック
        if retBool and string_default_value:
            hex_value = str(string_default_value)
            hex_value = binascii.b2a_hex(hex_value.encode('utf-8'))
            if int(string_maximum_bytes) < int(len(hex_value)) / 2:
                retBool = False
                msg = "「初期値」の値が指定した「最大バイト数」を超えています。"
            # 正規表現と初期値の条件一致をチェック
            if retBool and string_regular_expression:
                patarn = string_regular_expression
                patarn = re.compile(r'{}'.format(patarn), re.DOTALL)
                tmp_result = patarn.fullmatch(string_default_value)
                if tmp_result is None:
                    retBool = False
                    msg = "「初期値」の値が指定した「正規表現」とマッチしません。"

    # 入力方式が文字列(複数行)の場合
    elif column_class == "2":
        # 文字列(複数行)最大バイト数が設定されていない場合、エラー
        if retBool and multi_string_maximum_bytes is None:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「文字列(複数行)最大バイト数」は必須です。"
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"
        # 最大バイト数と初期値の条件一致をチェック
        if retBool and multi_string_default_value:
            # 改行コードを\r\nに置換(改行は2バイトとして計算する)
            multi_value = re.sub("\n|\r", "\r\n", multi_string_default_value)            
            hex_value = str(multi_value)
            hex_value = binascii.b2a_hex(hex_value.encode('utf-8'))
            if int(multi_string_maximum_bytes) < int(len(hex_value)) / 2:
                retBool = False
                msg = "「初期値」の値が指定した「最大バイト数」を超えています。"
            # 正規表現と初期値の条件一致をチェック
            if retBool and multi_string_regular_expression:
                patarn = multi_string_regular_expression
                patarn = re.compile(r'{}'.format(patarn), re.MULTILINE | re.DOTALL)
                tmp_result = patarn.fullmatch(multi_string_default_value)
                if tmp_result is None:
                    retBool = False
                    msg = "「初期値」の値が指定した「正規表現」とマッチしません。"

    # 入力方式が整数の場合
    elif column_class == "3":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「整数」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「整数」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「整数」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「整数」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されていない場合、一時最小値にする
        if retBool and integer_minimum_value is None:
            integer_minimum_value = -2147483648
        # 整数最大値が設定されていない場合、一時最大値にする(最大値>最小値チェックの時エラー出ないため)
        if retBool and integer_maximum_value is None:
            integer_maximum_value = 2147483648
        # 最大値<最小値になっている場合、エラー
        if retBool and int(integer_minimum_value) > int(integer_maximum_value):
            retBool = False
            msg = "「整数」を設定した場合、「最大値」は「最小値」より大きい数値を入力してください。（範囲外です。最小値：{},最大値：{}）".format(integer_minimum_value, integer_maximum_value)
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「整数」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「整数」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「整数」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「整数」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「整数」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「整数」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「整数」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「整数」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「整数」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「整数」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"
        # 初期値(整数) 最大数、最小数をチェック
        if retBool and integer_default_value:
            if int(integer_maximum_value) < int(integer_default_value) or int(integer_default_value) < int(integer_minimum_value):
                retBool = False
                msg = "「初期値」の値が指定した「最小値,最大値」の範囲外です。"

    # 入力方式が小数の場合
    elif column_class == "4":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「小数」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「小数」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「小数」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「小数」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「小数」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「小数」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されていない場合、一時最小値にする
        if retBool and decimal_minimum_value is None:
            decimal_minimum_value = -9999999999999
        # 小数最大値が設定されていない場合、一時最大値にする
        if retBool and decimal_maximum_value is None:
            decimal_maximum_value = 9999999999999
        # 最大値<最小値になっている場合、エラー
        if retBool and float(decimal_minimum_value) > float(decimal_maximum_value):
            retBool = False
            msg = "「小数」を設定した場合、「最大値」は「最小値」より大きい数値を入力してください。（範囲外です。最小値：{},最大値：{}）".format(decimal_minimum_value, decimal_maximum_value)
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「小数」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「小数」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「小数」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「小数」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「小数」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「小数」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「小数」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「文字列(複数行)」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「小数」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「小数」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「小数」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「小数」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「小数」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"
        # 初期値(小数) 最大数、最小数をチェック
        if retBool and decimal_default_value:
            if float(decimal_maximum_value) < float(decimal_default_value) or float(decimal_default_value) < float(decimal_minimum_value):
                retBool = False
                msg = "「初期値」の値が指定した「最小値,最大値」の範囲外です。"
            # 桁数をチェック
            if retBool and decimal_digit:
                srt_val = str(decimal_default_value)
                if "." in srt_val:
                    srt_val = srt_val.rstrip("0")
                vlen = int(len(srt_val))
                if "." in srt_val or "-" in srt_val:
                    vlen -= 1
                if int(decimal_digit) < vlen:
                    retBool = False
                    msg = "初期値」の値が指定した「桁数」を超えています。"

    # 入力方式が日時の場合
    elif column_class == "5":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「日時」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「日時」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「日時」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「日時」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「日時」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「日時」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「日時」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「日時」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「日時」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「日時」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「日時」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「日時」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「日時」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「日時」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「日時」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「日時」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"

    # 入力方式が日付の場合
    elif column_class == "6":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「日付」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「日付」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「日付」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「日付」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「日付」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「日付」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「日付」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「日付」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「日付」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「日付」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「日付」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「日付」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「日付」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「日付」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「日付」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「日付」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"

    # 作成中
    # 入力方式がプルダウンの場合
    # elif column_class == "7":
        # # 文字列(単一行)最大バイト数が設定されている場合、エラー
        # if retBool and string_maximum_bytes:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # # 文字列(単一行)正規表現が設定されている場合、エラー
        # if retBool and string_regular_expression:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # # 文字列(複数行)最大バイト数が設定されている場合、エラー
        # if retBool and multi_string_maximum_bytes:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # # 文字列(複数行)正規表現が設定されている場合、エラー
        # if retBool and multi_string_regular_expression:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # # 整数最小値が設定されている場合、エラー
        # if retBool and integer_minimum_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「整数最小値」は設定できません。"
        # # 整数最大値が設定されている場合、エラー
        # if retBool and integer_maximum_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「整数最大値」は設定できません。"
        # # 小数最小値が設定されている場合、エラー
        # if retBool and decimal_minimum_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「小数最小値」は設定できません。"
        # # 小数最大値が設定されている場合、エラー
        # if retBool and decimal_maximum_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「小数最大値」は設定できません。"
        # # 小数桁数が設定されている場合、エラー
        # if retBool and decimal_digit:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「小数最大値」は設定できません。"
        # # メニューグループ：メニュー：項目が設定されていない場合、エラー
        # if retBool and pulldown_selection is None:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「メニューグループ：メニュー：項目」は必須です。"
        # # パスワード最大バイト数が設定されている場合、エラー
        # if retBool and password_maximum_bytes:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        # if retBool and file_upload_maximum_bytes:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # # リンク/最大バイト数が設定されている場合、エラー
        # if retBool and link_maximum_bytes:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # # 初期値(文字列(単一行))が設定されている場合、エラー
        # if retBool and string_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # # 初期値(文字列(複数行))が設定されている場合、エラー
        # if retBool and multi_string_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # # 初期値(整数)が設定されている場合、エラー
        # if retBool and integer_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(整数)」は設定できません。"
        # # 初期値(小数)が設定されている場合、エラー
        # if retBool and decimal_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(小数)」は設定できません。"
        # # 初期値(日時)が設定されている場合、エラー
        # if retBool and detetime_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(日時)」は設定できません。"
        # # 初期値(日付)が設定されている場合、エラー
        # if retBool and dete_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(日付)」は設定できません。"
        # # 初期値(リンク)が設定されている場合、エラー
        # if retBool and link_default_value:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「初期値(リンク)」は設定できません。"
        # # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        # if retBool and parameter_sheet_reference:
        #     retBool = False
        #     msg = "「プルダウン選択」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"
        # # 参照項目
        # if retBool and reference_item:
        #     # プルダウン選択がない場合、エラー
        #     if not pulldown_selection:
        #         retBool = False
        #         msg = "「メニューグループ：メニュー：項目」が選択されていない場合、「参照項目」は設定できません。"
        #         return retBool, msg, option
        #     # カンマ区切りの数字であることをチェック
        #     arry_reference_item = reference_item.split(',')
        #     for id in arry_reference_item:
        #         if not id.isdigit():
        #             retBool = False
        #             msg = "「参照項目」にはカンマ区切りのIDのみ入力できます。"
        #             return retBool, msg, option
        #     # プルダウン選択のIDから対象のメニューIDを取得
        #     table_name = "V_MENU_OTHER_LINK"
        #     where_str = "DISUSE_FLAG = '0' AND LINK_ID =  %s"
        #     bind_value_list = [pulldown_selection]
        #     return_values = objdbca.table_select(table_name, where_str, bind_value_list)
        #     # メニューIDを取得
        #     menu_id = ""
        #     if len(return_values) > 0:
        #         menu_id = return_values[0]['MENU_ID']
        #     else:
        #         retBool = False
        #         msg = "「プルダウン選択」の対象を特定できませんでした。"
        #         return retBool, msg, option

        #     # 参照項目リストを取得
        #     table_name = "T_MENU_REFERENCE_ITEM"
        #     where_str = "DISUSE_FLAG = '0' AND MENU_ID =  %s"
        #     bind_value_list = [menu_id]
        #     return_values = objdbca.table_select(table_name, where_str, bind_value_list)
        #     # 参照項目リストから、プルダウン選択のメニューの中に参照項目のIDが存在するかをチェック
        #     for id in arry_reference_item:
        #         check_flg = False
        #         for data in return_values:
        #             if data['ORIGINAL_MENU_FLAG'] == 1:
        #                 # 既存メニューの場合、LINK_IDが一致している場合のみ許可
        #                 if data['LINK_ID'] == pulldown_selection:
        #                     if data['ITEM_ID'] == id:
        #                         check_flg = True
        #                         break
        #             else:
        #                 if data['ITEM_ID'] == id:
        #                     check_flg = True
        #                     break
        #         if not check_flg:
        #             retBool = False
        #             msg = "選択できない参照項目のIDが含まれています。"

        # # 初期値(プルダウン選択)
        # if retBool and pulldown_selection_default_value:
        #     # 他メニュー連携から、必要な情報を取得
        #     table_name = "T_MENU_OTHER_LINK"
        #     where_str = "DISUSE_FLAG = '0' AND LINK_ID =  %s"
        #     bind_value_list = [pulldown_selection]
        #     return_values = objdbca.table_select(table_name, where_str, bind_value_list)
        #     if not len(return_values) > 0:
        #         # DBエラー
        #         retBool = False
        #         msg = "バリデーションチェックに必要なデータの取得に失敗しました。"
        #         return retBool, msg, option
        #     else:
        #         # 必要なデータを取得
        #         menu_id = return_values[0]["MENU_ID"]
        #         table_name = return_values[0]["REF_TABLE_NAME"]
        #         pri_name = return_values[0]["REF_PKEY_NAME"]
        #         column_name = return_values[0]["REF_COL_NAME"]
        #     # 対象のテーブルからレコードを取得
        #     where_str = "DISUSE_FLAG = '0'"
        #     bind_value_list = []
        #     return_values = objdbca.table_select(table_name, where_str, bind_value_list)
        #     # アクセス許可チェック
        #     privilege = check_auth_menu(menu_name_rest, objdbca)
        #     if not privilege:
        #         retBool = False
        #         msg = "指定できない初期値です。"
        #         return retBool, msg, option
        #     # 指定した初期値のIDが指定可能なレコードであるかどうかをチェック
        #     for data in return_values:
        #         check_flg = False
        #         if data[pri_name] == pulldown_selection_default_value:
        #             check_flg = True
        #             break
        #     if not check_flg:
        #         retBool = False
        #         msg = "指定できない初期値です。"

    # 入力方式がパスワードの場合
    elif column_class == "8":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「パスワード」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「パスワード」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「パスワード」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「パスワード」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「パスワード」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「パスワード」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されていない場合、エラー
        if retBool and password_maximum_bytes is None:
            retBool = False
            msg = "「パスワード」を設定した場合、「最大バイト数」は必須です。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「パスワード」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「パスワード」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「パスワード」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「パスワード」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「パスワード」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"

    # 入力方式がファイルアップロードの場合
    elif column_class == "9":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されていない場合、エラー
        if retBool and file_upload_maximum_bytes is None:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は必須です。"
        # リンク/最大バイト数が設定されている場合、エラー
        if retBool and link_maximum_bytes:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「リンク/最大バイト数」は設定できません。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(リンク)が設定されている場合、エラー
        if retBool and link_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(リンク)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「ファイルアップロード」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"

    # 入力方式がリンクの場合
    elif column_class == "10":
        # 文字列(単一行)最大バイト数が設定されている場合、エラー
        if retBool and string_maximum_bytes:
            retBool = False
            msg = "「リンク」を設定した場合、「文字列(単一行)最大バイト数」は設定できません。"
        # 文字列(単一行)正規表現が設定されている場合、エラー
        if retBool and string_regular_expression:
            retBool = False
            msg = "「リンク」を設定した場合、「文字列(単一行)正規表現」は設定できません。"
        # 文字列(複数行)最大バイト数が設定されている場合、エラー
        if retBool and multi_string_maximum_bytes:
            retBool = False
            msg = "「リンク」を設定した場合、「文字列(複数行)最大バイト数」は設定できません。"
        # 文字列(複数行)正規表現が設定されている場合、エラー
        if retBool and multi_string_regular_expression:
            retBool = False
            msg = "「リンク」を設定した場合、「文字列(複数行)正規表現」は設定できません。"
        # 整数最小値が設定されている場合、エラー
        if retBool and integer_minimum_value:
            retBool = False
            msg = "「リンク」を設定した場合、「整数最小値」は設定できません。"
        # 整数最大値が設定されている場合、エラー
        if retBool and integer_maximum_value:
            retBool = False
            msg = "「リンク」を設定した場合、「整数最大値」は設定できません。"
        # 小数最小値が設定されている場合、エラー
        if retBool and decimal_minimum_value:
            retBool = False
            msg = "「リンク」を設定した場合、「小数最小値」は設定できません。"
        # 小数最大値が設定されている場合、エラー
        if retBool and decimal_maximum_value:
            retBool = False
            msg = "「リンク」を設定した場合、「小数最大値」は設定できません。"
        # 小数桁数が設定されている場合、エラー
        if retBool and decimal_digit:
            retBool = False
            msg = "「リンク」を設定した場合、「小数最大値」は設定できません。"
        # メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and pulldown_selection:
            retBool = False
            msg = "「リンク」を設定した場合、「メニューグループ：メニュー：項目」は設定できません。"
        # パスワード最大バイト数が設定されている場合、エラー
        if retBool and password_maximum_bytes:
            retBool = False
            msg = "「リンク」を設定した場合、「パスワード最大バイト数」は設定できません。"
        # ファイルアップロード/ファイル最大バイト数が設定されている場合、エラー
        if retBool and file_upload_maximum_bytes:
            retBool = False
            msg = "「リンク」を設定した場合、「ファイルアップロード/ファイル最大バイト数」は設定できません。"
        # リンク/最大バイト数が設定されていない場合、エラー
        if retBool and link_maximum_bytes is None:
            retBool = False
            msg = "「リンク」を設定した場合、「リンク/最大バイト数」は必須です。"
        # 参照項目が設定されている場合、エラー
        if retBool and reference_item:
            retBool = False
            msg = "「リンク」を設定した場合、「参照項目」は設定できません。"
        # 初期値(文字列(単一行))が設定されている場合、エラー
        if retBool and string_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(文字列(単一行))」は設定できません。"
        # 初期値(文字列(複数行))が設定されている場合、エラー
        if retBool and multi_string_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(文字列(複数行))」は設定できません。"
        # 初期値(整数)が設定されている場合、エラー
        if retBool and integer_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(整数)」は設定できません。"
        # 初期値(小数)が設定されている場合、エラー
        if retBool and decimal_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(小数)」は設定できません。"
        # 初期値(日時)が設定されている場合、エラー
        if retBool and detetime_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(日時)」は設定できません。"
        # 初期値(日付)が設定されている場合、エラー
        if retBool and dete_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(日付)」は設定できません。"
        # 初期値(プルダウン選択)が設定されている場合、エラー
        if retBool and pulldown_selection_default_value:
            retBool = False
            msg = "「リンク」を設定した場合、「初期値(プルダウン選択)」は設定できません。"
        # パラメータシート参照/メニューグループ：メニュー：項目が設定されている場合、エラー
        if retBool and parameter_sheet_reference:
            retBool = False
            msg = "「リンク」を設定した場合、「パラメータシート参照/メニューグループ：メニュー：項目」は設定できません。"
        # 最大バイト数と初期値の条件一致をチェック
        if retBool and link_default_value:
            hex_value = str(link_default_value)
            hex_value = binascii.b2a_hex(hex_value.encode('utf-8'))
            if int(link_maximum_bytes) < int(len(hex_value)) / 2:
                retBool = False
                msg = "「初期値」の値が指定した「最大バイト数」を超えています。"

    return retBool, msg, option
