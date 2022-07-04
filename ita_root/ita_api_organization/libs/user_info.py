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
from flask import g

# ####メモ：あとでutil.pyを使うため不要になる
import base64

def collect_menu_group_panels(objdbca):
    """
        メニューグループの画像を取得する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            panels_data
    """
    
    # ####メモ：必要なものは？
    # メニューグループIDとパネル画像をbase64エンコードかけたもの。
    
    # テーブル名
    t_common_menu_group = 'T_COMN_MENU_GROUP'
    
    # 変数定義
    user_id = g.USER_ID
    # lang = g.LANGUAGE
    
    # ####メモ：現状ユーザIDとロールと取得可能メニューについての結びつけを行う機能が未実装のため、すべてのメニューグループ・メニューをリターンする処理とする。
    #     　　：最終的には対象のユーザが取得可能なメニューグループ・メニューのみに絞る処理の実装が必要。
    
    # 『メニューグループ管理』テーブルからメニューグループの一覧を取得
    ret = objdbca.table_select(t_common_menu_group, 'WHERE DISUSE_FLAG = %s ORDER BY DISP_SEQ ASC', [0])
    # ####メモ：操作可能なメニューグループが0件の場合もあるため、空の場合のエラー処理は必要なし。
    
    panels_data = {}
    for recode in ret:
        menu_group_id = recode.get('MENU_GROUP_ID')
        icon = recode.get('MENU_GROUP_ICON')
        
        # ####メモ：画像データは一時的に以下に格納している。
        # /workspace/ita_root/test/MENU_GROUP_ICON/{menu_group_id}/
        # ####メモ：最終的なデータの格納先は、以下のようなディレクトリに対象のファイルが格納される想定。
        # /strorage/{organization_id}/{workspace_id}/uploadfiles/{menu_id}/{uuid}/{column_rest_name}/
        icon_path = "/workspace/ita_root/test/MENU_GROUP_ICON/"
        target_file = icon_path + menu_group_id + "/" + icon
        print(target_file)
        
        # ####メモ：util.pyのファイル変換関数を使いたい
        with open(target_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode(encoding='utf-8')  # base64エンコードしたものをstring型にしたもの
            print(encoded)
        
        panels_data[menu_group_id] = encoded
    
    return panels_data


def collect_user_auth(objdbca):
    """
        ユーザの権限情報を取得する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            user_auth_data
    """
    
    # ####メモ：必要なものは？
    # 1:ユーザID
    # 2:ユーザ名
    # 3:所属ロール(複数)
    # 4:所属ワークスペース(複数)
    # ロールとワークスペースはそれぞれID/NAMEと持ちたいかも。その場合、[{"id": "xxx", "name": "yyy"}, {"id": "xxx", "name": "yyy"}]というような構造にする？
    
    # 変数定義
    user_id = g.USER_ID
    # lang = g.LANGUAGE
    
    # ユーザ名を取得
    # ####メモ：共通認証基盤側からユーザ名を取得する処理
    user_name = "ユーザ名"
    
    # ロールを取得
    # ####メモ：対象のユーザが所属するロールの一覧を取得する処理
    roles = ["ロール1", "ロール2", "ロール3"]
    
    # Workspaceを取得
    # ####メモ：対象のユーザが所属するワークスペースの一覧を取得する処理
    workspaces = ["ワークスペース1", "ワークスペース2"]
    
    user_auth_data = {
        "user_id": user_id,
        "user_name": user_name,
        "roles": roles,
        "workspaces": workspaces
    }
    
    return user_auth_data


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
    user_id = g.USER_ID
    lang = g.LANGUAGE
    
    # ####メモ：現状ユーザIDとロールと取得可能メニューについての結びつけを行う機能が未実装のため、すべてのメニューグループ・メニューをリターンする処理とする。
    #     　　：最終的には対象のユーザが取得可能なメニューグループ・メニューのみに絞る処理の実装が必要。
    
    # 『メニュー管理』テーブルからメニューの一覧を取得
    ret = objdbca.table_select(t_common_menu, 'WHERE DISUSE_FLAG = %s ORDER BY MENU_GROUP_ID ASC, DISP_SEQ ASC', [0])
    # ####メモ：操作可能なメニューが0件の場合もあるため、空の場合のエラー処理は必要なし。
    # if not ret:
    #     log_msg_args = [""]
    #     api_msg_args = [""]
    #     raise AppException("200-0000X", log_msg_args, api_msg_args)  # noqa: F405
    
    # メニューグループごとのメニュー一覧を作成
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
    
    # 『メニューグループ管理』テーブルからメニューグループの一覧を取得
    ret = objdbca.table_select(t_common_menu_group, 'WHERE DISUSE_FLAG = %s ORDER BY DISP_SEQ ASC', [0])
    # ####メモ：操作可能なメニューグループが0件の場合もあるため、空の場合のエラー処理は必要なし。
    # if not ret:
    #     log_msg_args = [""]
    #     api_msg_args = [""]
    #     raise AppException("200-0000X", log_msg_args, api_msg_args)  # noqa: F405
    
    # メニューグループの一覧を作成し、メニュー一覧も格納する
    menu_group_list = []
    for recode in ret:
        add_menu_group = {}
        menu_group_id = recode.get('MENU_GROUP_ID')
        add_menu_group['id'] = menu_group_id
        add_menu_group['menu_group_name'] = recode.get('MENU_GROUP_NAME_' + lang.upper())
        add_menu_group['disp_seq'] = recode.get('DISP_SEQ')
        add_menu_group['menus'] = menus[menu_group_id]
        menu_group_list.append(add_menu_group)
    
    menus_data = {
        "menu_groups": menu_group_list,
    }
    
    return menus_data
