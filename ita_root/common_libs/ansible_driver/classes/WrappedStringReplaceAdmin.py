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

"""
  指定文字列からの変数抜出及び変数具体値置き換モジュール
"""


class WrappedStringReplaceAdmin:
    """
      指定文字列からの変数抜出及び変数具体値置き換えクラス
    """
    def __init__(self):
        self.strReplacedString = ''

    def stringReplace(self, strSourceString, aryReplaceSource):
        """
          変数を具体値に置き換え
          Arguments:
            strSourceString:(in)   置き換え対象の文字列
            aryReplaceSource:(in)  置換えする変数と具体値の辞書リスト
                                    [{変数名:具体値} , ...]
          Returns:
            True(bool)
        """
        boolRet = True

        strHeadPattern = "{{ "
        strTailPattern = " }}"
        self.strReplacedString = ""

        # 入力データを行単位に分解
        arry_list = strSourceString.split("\n")
        for lineString in arry_list:
            lineString = lineString + "\n"
            if lineString.find("#") == 0:
                self.strReplacedString += lineString
            else:
                # エスケープコード付きの#を一時的に改行に置換
                wstr = lineString
                rpstr = wstr.replace("\\\#", "\n\n")
                # コメント( #)マーク以降の文字列を削除した文字列で変数の具体値置換
                # #の前の文字がスペースの場合にコメントとして扱う
                splitList = rpstr.split(' #')
                lineString = splitList[0]
                splitList.pop(0)
                # 各変数を具体値に置換
                for dectReplace in aryReplaceSource:
                    for strVar, strVal in dectReplace.items():
                        # 変数を具体値に置換
                        strVarName = strHeadPattern + strVar + strTailPattern
                        strReplace = lineString.replace(strVarName, strVal)
                        lineString = strReplace
                # コメント(#)以降の文字列を元に戻す。
                for strLine in splitList:
                    lineString += " #" + strLine
                # エスケープコード付きの#を元に戻す。
                rpstr = lineString.replace("\n\n", "\#")
                self.strReplacedString += rpstr
        return boolRet

    def getReplacedString(self):
        """
          stringReplaceで変数を具体値に置き換えた結果取得
          Arguments:
            None
          Returns:
            変数を具体値に置き換えた結果文字列
        """
        return self.strReplacedString

    def SimpleFillterVerSearch(self, var_heder_id, strSourceString, mt_varsLineArray, mt_varsArray, arrylocalvars, FillterVars=False):
        """
          指定された文字列から指定された変数を抜出す。
          Arguments:
            var_heder_id:(in)            変数名の先頭文字列　TPF_, ""
            in_strSourceString:(in)      変数を抜出す文字列
            mt_varsLineArray:(out)       抜出した変数リスト       呼出元で空リストで初期化必須
                                         [{行番号:変数名}, ...]
            mt_varsarray:(out)           抜出した変数リスト       呼出元で空リストで初期化必須
                                         [変数名, .....]
            FillterVars:(in)             Fillter設定されている変数抜出有無(bool)
          Returns:
            True(bool)
        """
        # Fillter定義されている変数も抜出すか判定
        if FillterVars == 1:
            tailmarke = "([\s]}}|[\s]+\|)"
            reptailmarke = " }} |"
        else:
            tailmarke = "[\s]}}"
            reptailmarke = " }}"

        # 入力データを行単位に分解
        arry_list = strSourceString.split("\n")
        line = 0
        for lineString in arry_list:
            # 行番号
            line += 1
    
            lineString += "\n"
            # コメント行は読み飛ばす
            if lineString.find("#") == 0:
                continue

            # エスケープコード付きの#を一時的に改行に置換
            wstr = lineString
            # コメント( #)マーク以降の文字列を削除する。
            # #の前の文字がスペースの場合にコメントとして扱う
            splitList = wstr.split(' #')
            strRemainString = splitList[0]
            if len(str.strip(strRemainString)) == 0:
                # 空行は読み飛ばす
                continue
            # 変数名　{{ ???_[a-zA-Z0-9_] | Fillter function }} または{{ ???_[a-zA-Z0-9_] }}　を取出す
            keyFilter = "{{[\s]" + var_heder_id + "[a-zA-Z0-9_]*" + tailmarke
            match = re.findall(keyFilter, strRemainString)
            if len(match) != 0:
                # 重複値を除外
                unique_set = set(match)
            else:
                unique_set = []
            for var_name_match in unique_set:
                # 変数名を抜出す
                var_name_match = var_name_match.replace("{{ ", "")
                var_name_match = var_name_match.replace(reptailmarke, "")

                # 変数位置退避
                var_dict = {}
                var_dict[line] = var_name_match
                mt_varsLineArray.append(var_dict)

                # 変数名の重複チェック
                if mt_varsArray.count(var_name_match) == 0:
                    mt_varsArray.append(var_name_match)

            # --- 予約変数　{{ 予約変数 | Fillter function }}　の抜き出し
            for localvarname in arrylocalvars:
                keyFilter = "{{[\s]" + localvarname + tailmarke
                match = re.findall(keyFilter, strRemainString)
                if len(match) != 0:
                    # 重複値を除外
                    unique_set = set(match)
                else:
                    unique_set = []
                for var_name_match in unique_set:
                    # 変数名を抜出す
                    var_name_match = var_name_match.replace("{{ ", "")
                    var_name_match = var_name_match.replace(reptailmarke, "")

                    # 変数位置退避
                    var_dict = {}
                    var_dict[line] = var_name_match
                    mt_varsLineArray.append(var_dict)

                    # 変数名の重複チェック
                    if mt_varsArray.count(var_name_match) == 0:
                        mt_varsArray.append(var_name_match)
            # 予約変数　{{ 予約変数 | Fillter function }}　の抜き出し ---
        return True, mt_varsLineArray
