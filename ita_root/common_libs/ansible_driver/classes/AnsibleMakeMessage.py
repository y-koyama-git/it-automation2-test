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

"""
Ansibleメッセージ作成module
"""

from flask import g


class AnsibleMakeMessage():
    
    def AnsibleMakeMessage(chkmode, msgcode, paramAry=[]):
    
        # 定数定義
        LC_RUN_MODE_STD = "0"
        LC_RUN_MODE_VARFILE = "1"
        
        # 変数定義の解析に失敗しました。{}
        msgtblary = ['MSG-10301']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10577', LC_RUN_MODE_VARFILE: 'MSG-10578'}
        # 変数定義が想定外なので解析に失敗しました。{}
        msgtblary = ['MSG-10302']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10312', LC_RUN_MODE_VARFILE: 'MSG-10313'}
        # 繰返階層の変数定義が一致していません。{}
        msgtblary = ['MSG-10303']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10577', LC_RUN_MODE_VARFILE: 'MSG-10578'}
        # 代入順序が複数必要な変数定義になっています。{}
        msgtblary = ['MSG-10304']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10577', LC_RUN_MODE_VARFILE: 'MSG-10578'}
        # 繰返構造の繰返数が99999999を超えてた定義です。{}
        msgtblary = ['MSG-10444']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10577', LC_RUN_MODE_VARFILE: 'MSG-10578'}
        # 変数が二重定義されています。{}
        msgtblary = ['MSG-10568']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10577', LC_RUN_MODE_VARFILE: 'MSG-10578'}
        # ファイル埋込変数がファイル管理に登録されていません。{}
        msgtblary = ['MSG-10408']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10583', LC_RUN_MODE_VARFILE: 'MSG-10584'}
        # ファイル埋込変数に紐づくファイルがファイル管理に登録されていません。 {}
        msgtblary = ['MSG-10409']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10583', LC_RUN_MODE_VARFILE: 'MSG-10584'}
        # テンプレート埋込変数に紐づくファイルがテンプレート管理に登録されていません。{}
        msgtblary = ['MSG-10557']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10585', LC_RUN_MODE_VARFILE: 'MSG-10586'}
        # テンプレート埋込変数がテンプレート管理に登録されていません。{}
        msgtblary = ['MSG-10559']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10585', LC_RUN_MODE_VARFILE: 'MSG-10586'}
        # グローバル変数がグローバル管理に登録されていません。 {})
        msgtblary = ['MSG-10571']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10587', LC_RUN_MODE_VARFILE: 'MSG-10588'}
        # 変数名が不正です。{}
        msgtblary = ['MSG-10306']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10307', LC_RUN_MODE_VARFILE: 'MSG-10308'}
        # メンバー変数名が不正です。メンバー変数名に 「 ．(ドット)  [  ] 」の3記号は使用できません。{}
        msgtblary = ['MSG-10309']['msgcode'] = {LC_RUN_MODE_STD: 'MSG-10310', LC_RUN_MODE_VARFILE: 'MSG-10311'}
        
        msgtblary = ['MSG-10301']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3'}
        msgtblary = ['MSG-10302']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0'}
        msgtblary = ['MSG-10303']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3'}
        msgtblary = ['MSG-10304']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3'}
        msgtblary = ['MSG-10444']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3'}
        msgtblary = ['MSG-10568']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3'}
        msgtblary = ['MSG-10408']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '2,3'}
        msgtblary = ['MSG-10409']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '2,3'}
        msgtblary = ['MSG-10557']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '2,3'}
        msgtblary = ['MSG-10559']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '2,3'}
        msgtblary = ['MSG-10571']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '2,3'}
        msgtblary = ['MSG-10306']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3'}
        msgtblary = ['MSG-10309']['paramlist'] = {LC_RUN_MODE_STD: 'all', LC_RUN_MODE_VARFILE: '0,3,4'}
        
        if not msgtblary[msgcode]:
            result_msg = g.appmsg.get_api_message(msgcode, paramAry)
        else:
            for code, mode in msgtblary[msgcode]['msgcode']:
                if chkmode == mode:
                    pram_code = code
                    break
            for plist, mode in msgtblary[msgcode]['paramlist']:
                if chkmode == mode:
                    param_list = plist
                    break
            if pram_code != "":
                if param_list == 'all':
                    parm_msg = g.appmsg.get_api_message(pram_code, paramAry)
                    result_msg = g.appmsg.get_api_message(msgcode, list[parm_msg])
                else:
                    param_msg = []
                    for param_no in param_list.split(','):
                        param_msg.append(paramAry[param_no])
                        
                    parm_msg = g.appmsg.get_api_message(pram_code, param_msg)
                    result_msg = g.appmsg.get_api_message(msgcode, list[parm_msg])
        
        return result_msg
