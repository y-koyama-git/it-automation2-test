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

from common_libs.common import *  # noqa: F403
from common_libs.loadtable import *

def rest_maintenance_all(objdbca, menu, parameters, lang):
    """
        メニューのレコード登録/更新(更新/廃止/復活)
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            parameter:パラメータ  {}
            target_uuid: 対象レコードID UUID
            lang: 言語情報 ja / en
        RETRUN:
            statusCode, {}, msg
    """
    
    result_data = {}
    
    try:
        
        # メッセージクラス呼び出し
        msg = ''
        
        # ####メモ：ユーザが対象のメニューの情報を取得可能かどうかのロールチェック処理が必要
        # role_check = True
        # if not role_check:
        #    # ####メモ：401を意図的に返したいので最終的に自作Exceptionクラスに渡す。引数のルールは別途決める必要あり。
        #     raise Exception(msg, 'statusCode')

        objmenu = load_table.loadTable(objdbca, menu, lang)
        result_data = objmenu.rest_maintenance_all(parameters)

        return 'statusCode', result_data[1], msg
    
    except Exception:
        raise
