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

from flask import g  # noqa: F401

from common_libs.common import *  # noqa: F403
from common_libs.loadtable import *  # noqa: F403

from libs.organization_common import check_menu_info  # noqa: F401
from libs.organization_common import check_auth_menu  # noqa: F401
from libs.organization_common import check_sheet_type  # noqa: F401


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

    # メニューに対するロール権限をチェック
    privilege = check_auth_menu(menu, objdbca)
    if privilege == '2':
        status_code = "401-00001"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    
    # 『メニュー-テーブル紐付管理』の取得とシートタイプのチェック
    sheet_type_list = ['0', '1', '2', '3', '4']
    menu_table_link_record = check_sheet_type(menu, sheet_type_list, objdbca)  # noqa: F841

    mode = 'nomal'  # noqa: F841
    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    status_code, result, msg = objmenu.rest_maintenance(parameter, target_uuid)
    if status_code != '000-00000':
        if status_code is None:
            status_code = '999-99999'
        elif len(status_code) == 0:
            status_code = '999-99999'
        if isinstance(msg, list):
            log_msg_args = msg
            api_msg_args = msg
        else:
            log_msg_args = [msg]
            api_msg_args = [msg]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result
