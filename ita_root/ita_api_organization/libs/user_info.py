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
from common_libs.common import *  # noqa: F403
from flask import session


def collect_menus(objdbca):
    """
        ユーザがアクセス可能なメニューグループ・メニューの一覧を取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            menus_data
    """
    # テーブル名
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_group = 'T_COMN_MENU_GROUP'
    
    # 変数定義
    user_id = session.get("USER_ID")
    lang = session.get("LANGUAGE")
    
    # ####メモ：現状ユーザIDとロールと取得可能メニューについての結びつけを行う機能が未実装のため、すべてのメニューグループ・メニューをリターンする処理とする。
    #     　　：最終的には対象のユーザが取得可能なメニューグループ・メニューのみに絞る処理の実装が必要。
    
    # 『メニューグループ管理』テーブルからメニューグループの一覧を取得
    ret = objdbca.table_select(t_common_menu_group, 'WHERE DISUSE_FLAG = %s ORDER BY DISP_SEQ ASC', [0])
    # ####メモ：操作可能なメニューグループが0件の場合もあるため、空の場合のエラー処理は必要なし。
    # if not ret:
    #     log_msg_args = [""]
    #     api_msg_args = [""]
    #     raise AppException("200-0000X", log_msg_args, api_msg_args)  # noqa: F405
    
    menu_group_list = []
    for recode in ret:
        add_menu_group = {}
        add_menu_group['id'] = recode.get('MENU_GROUP_ID')
        add_menu_group['menu_group_name'] = recode.get('MENU_GROUP_NAME_' + lang.upper())
        add_menu_group['disp_seq'] = recode.get('DISP_SEQ')
        menu_group_list.append(add_menu_group)
    
    # 『メニュー管理』テーブルからメニューの一覧を取得
    ret = objdbca.table_select(t_common_menu, 'WHERE DISUSE_FLAG = %s ORDER BY MENU_GROUP_ID ASC, DISP_SEQ ASC', [0])
    # ####メモ：操作可能なメニューが0件の場合もあるため、空の場合のエラー処理は必要なし。
    # if not ret:
    #     log_msg_args = [""]
    #     api_msg_args = [""]
    #     raise AppException("200-0000X", log_msg_args, api_msg_args)  # noqa: F405
    
    menus = {}
    for recode in ret:
        menu_group_id = recode.get('MENU_GROUP_ID')
        if menu_group_id not in menus:
            menus[menu_group_id] = []
        
        add_menu = {}
        add_menu['id'] = recode.get('MENU_ID')
        add_menu['menu_name'] = recode.get('MENU_NAME_' + lang.upper())
        add_menu['menu_name_rest'] = recode.get('MENU_NAME_REST')
        add_menu['disp_seq'] = recode.get('DISP_SEQ')
        menus[menu_group_id].append(add_menu)
    
    menus_data = {
        "menu_groups": menu_group_list,
        "menus": menus
    }
    
    return menus_data
