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


def rest_filter(objdbca, menu, filter_parameter):
    """
        メニューのレコード取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu: メニュー string
            filter_parameter: 検索条件  {}
            lang: 言語情報 ja / en
            mode: 本体 / 履歴
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
        log_msg_args = ["not menu or table"]
        api_msg_args = ["not menu or table"]
        raise AppException("401-00001", log_msg_args, api_msg_args) # noqa: F405

    status_code, result, msg = objmenu.rest_filter(filter_parameter, mode)
    if status_code != '000-00000':
        log_msg_args = [msg]
        api_msg_args = [msg]
        raise AppException(status_code, log_msg_args, api_msg_args)
    
    return result


def rest_filter_journal(objdbca, menu, uuid):
    """
        メニューのレコード取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu: メニュー string
            filter_parameter: 検索条件  {}
            lang: 言語情報 ja / en
            mode: 本体 / 履歴
        RETRUN:
            statusCode, {}, msg
    """
    
    result_data = {}

    # 変数定義
    lang = os.environ['LANGUAGE']
    
    role_check = True
    if not role_check:
        # ####メモ：401を意図的に返したいので最終的に自作Exceptionクラスに渡す。引数のルールは別途決める必要あり。
        status_code = '401-00001'
        msg = g.appmsg.get_api_message(status_code, [menu])
        raise Exception(msg, status_code)

    objmenu = load_table.loadTable(objdbca, menu)
    if objmenu.get_objtable() is False:
        log_msg_args = ["not menu or table"]
        api_msg_args = ["not menu or table"]
        raise AppException("401-00001", log_msg_args, api_msg_args) # noqa: F405

    mode = 'jnl'
    filter_parameter = {}
    filter_parameter.setdefault('JNL', uuid)
    status_code, result, msg = objmenu.rest_filter(filter_parameter, mode)
    if status_code != '000-00000':
        log_msg_args = [msg]
        api_msg_args = [msg]
        raise AppException(status_code, log_msg_args, api_msg_args)

    return result_data
