# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expPress or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re

# import text_column_class
from .text_column_class import TextColumn

"""
カラムクラス個別処理(SingleText)
"""


class SingleTextColumn(TextColumn):
    def check_basic_valid(self, val, option={}):
        """
            バリデーション処理(カラムクラス毎)
            ARGS:
                val:値
                option:オプション
            RETRUN:
                ( True / False , メッセージ )
        """
        retBool = True
        preg_match = r"^[^\t\r\n]*$"

        if val is not None:
            val = str(val)

            # 親クラスのvalidation確認。
            validate_result = super().check_basic_valid(val)
            if validate_result[0] is not True:
                return validate_result
            
            # 正規表現
            pattern = re.compile(preg_match)
            tmp_result = pattern.fullmatch(val)
            if tmp_result is None:
                retBool = False
                msg = "正規表現エラー (閾値:{},値{})[{}]".format(pattern, val, self.rest_key_name)
                return retBool, msg
            
        return retBool,