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

import os
from flask import g

from common_libs.common import *  # noqa: F403
from common_libs.loadtable import *

def rest_maintenance(objdbca, menu, parameter, target_uuid):
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
    role_check = True
    if not role_check:
        # ####メモ：401を意図的に返したいので最終的に自作Exceptionクラスに渡す。引数のルールは別途決める必要あり。
        status_code = '401-00001'
        msg = g.appmsg.get_api_message(status_code, [menu])
        raise Exception(msg, status_code)

    mode = 'nomal'
    objmenu = load_table.loadTable(objdbca, menu)
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)

    status_code, result, msg = objmenu.rest_maintenance(parameter, target_uuid)
    if status_code != '000-00000':
        if status_code is None:
            status_code = '999-99999'
        elif len(status_code) == 0:
            status_code = '999-99999'
        if isinstance(msg,list):
            log_msg_args = msg
            api_msg_args = msg
        else:
            log_msg_args = [msg]
            api_msg_args = [msg] 
        raise AppException(status_code, log_msg_args, api_msg_args)

    return result
