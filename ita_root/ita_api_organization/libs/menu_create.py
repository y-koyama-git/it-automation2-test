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

import json
from common_libs.common import *  # noqa: F403
from common_libs.loadtable import *  # noqa: F403
from flask import g
from libs.organization_common import check_auth_menu  # noqa: F401
from libs.menu_info import add_tmp_column_group, collect_column_group_sort_order, collect_parent_sord_order
from common_libs.api import check_request_body_key


def collect_menu_create_data(objdbca):
    """
        メニュー定義・作成(新規)用の情報取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            create_data
    """
    # 共通部分を取得
    create_data = _collect_common_menu_create_data(objdbca)

    return create_data


def collect_exist_menu_create_data(objdbca, menu_create):  # noqa: C901
    """
        メニュー定義・作成(既存)用の情報取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            create_data
    """
    # テーブル/ビュー名
    t_menu_define = 'T_MENU_DEFINE'
    t_menu_column = 'T_MENU_COLUMN'
    t_menu_column_group = 'T_MENU_COLUMN_GROUP'
    t_menu_unique_constraint = 'T_MENU_UNIQUE_CONSTRAINT'
    t_menu_role = ('T_MENU_ROLE')
    
    # 変数定義
    lang = g.get('LANGUAGE')
    menu_info = {}
    
    # 共通部分を取得
    create_data = _collect_common_menu_create_data(objdbca)
    
    # 対象メニューグループのデータを形成
    format_target_menu_group_list = {}
    for target in create_data['target_menu_group_list']:
        format_target_menu_group_list[target.get('menu_group_id')] = target.get('menu_group_name')
    
    # シートタイプのデータを形成
    format_sheet_type_list = {}
    for target in create_data['sheet_type_list']:
        format_sheet_type_list[target.get('sheet_type_id')] = target.get('sheet_type_name')
        
    # カラムクラスのデータを形成
    format_column_class_list = {}
    for target in create_data['column_class_list']:
        format_column_class_list[target.get('column_class_id')] = {'column_class_name': target.get('column_class_name'), 'column_class_disp_name': target.get('column_class_disp_name')}  # noqa: E501
    
    # 「メニュー定義一覧」から対象のメニューのレコードを取得
    ret = objdbca.table_select(t_menu_define, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu_create, 0])
    if not ret:
        log_msg_args = [menu_create]
        api_msg_args = [menu_create]
        # ####メモ：「対象のメニューがメニュー定義一覧にありません」的なメッセージ
        raise AppException("999-00001", log_msg_args, api_msg_args)  # noqa: F405
    
    # 対象のuuidを取得
    menu_create_id = ret[0].get('MENU_CREATE_ID')
    
    # 対象メニューグループについて、名称を取得
    menu_group_for_input_id = ret[0].get('MENU_GROUP_ID_INPUT')
    menu_group_for_subst_id = ret[0].get('MENU_GROUP_ID_SUBST')
    menu_group_for_ref_id = ret[0].get('MENU_GROUP_ID_REF')
    menu_group_for_input = format_target_menu_group_list.get(menu_group_for_input_id)
    menu_group_for_subst = format_target_menu_group_list.get(menu_group_for_subst_id)
    menu_group_for_ref = format_target_menu_group_list.get(menu_group_for_ref_id)
    
    # シートタイプについて、名称を取得
    sheet_type_id = ret[0].get('SHEET_TYPE')
    sheet_type_name = format_sheet_type_list.get(sheet_type_id)
    
    # 最終更新日時のフォーマット
    last_update_timestamp = ret[0].get('LAST_UPDATE_TIMESTAMP')
    last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
    
    # 縦メニュー利用の有無を取得
    vertical = ret[0].get('VERTICAL')
    
    # 「メニュー-ロール作成情報」から対象のレコードを取得
    selected_role_list = []
    ret_role_list = objdbca.table_select(t_menu_role, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
    if ret_role_list:
        for recode in ret_role_list:
            role_id = recode.get('ROLE_ID')
            if role_id:
                selected_role_list.append(role_id)
    
    # メニューデータを格納
    menu = {
        "menu_create_id": menu_create_id,
        "menu_name": ret[0].get('MENU_NAME_' + lang.upper()),
        "menu_name_rest": ret[0].get('MENU_NAME_REST'),
        "sheet_type_id": sheet_type_id,
        "sheet_type_name": sheet_type_name,
        "disp_seq": ret[0].get('DISP_SEQ'),
        "vertical": vertical,
        "menu_group_for_input_id": menu_group_for_input_id,
        "menu_group_for_subst_id": menu_group_for_subst_id,
        "menu_group_for_ref_id": menu_group_for_ref_id,
        "menu_group_for_input": menu_group_for_input,
        "menu_group_for_subst": menu_group_for_subst,
        "menu_group_for_ref": menu_group_for_ref,
        "selected_role_id": selected_role_list,
        "description": ret[0].get('DESCRIPTION_' + lang.upper()),
        "remarks": ret[0].get('NOTE'),
        "menu_create_done_status_id": ret[0].get('MENU_CREATE_DONE_STATUS'),
        "last_update_date_time": last_update_date_time
    }
    
    # 「一意制約(複数項目)作成情報」から対象のレコードを取得
    menu['unique_constraint_current'] = None
    ret = objdbca.table_select(t_menu_unique_constraint, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
    if ret:
        str_unique_constraint = json.dumps(ret[0].get('UNIQUE_CONSTRAINT_ITEM'))
        unique_constraint_current = json.loads(str_unique_constraint)
        menu['unique_constraint_current'] = unique_constraint_current
    
    # メニュー情報を格納
    menu_info['menu'] = menu
    
    # 「カラムグループ作成情報」からレコードをすべて取得
    column_group_list = {}
    ret = objdbca.table_select(t_menu_column_group, 'WHERE DISUSE_FLAG = %s', [0])
    col_group_recode_count = len(ret)  # 「カラムグループ作成情報」のレコード数を格納
    for recode in ret:
        add_data = {
            "column_group_id": recode.get('CREATE_COL_GROUP_ID'),
            "column_group_name": recode.get('COL_GROUP_NAME_' + lang.upper()),
            "full_column_group_name": recode.get('FULL_COL_GROUP_NAME_' + lang.upper()),
            "parent_column_group_id": recode.get('PA_COL_GROUP_ID')
        }
        column_group_list[recode.get('CREATE_COL_GROUP_ID')] = add_data
    
    # 「メニュー項目作成情報」から対象のメニューのレコードを取得
    column_info_data = {}
    column_group_info_data = {}
    tmp_column_group = {}
    column_group_parent_of_child = {}  # カラムグループの親子関係があるとき、子の一番大きい親を結びつける
    ret = objdbca.table_select(t_menu_column, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s ORDER BY DISP_SEQ ASC', [menu_create_id, 0])
    if ret:
        for count, recode in enumerate(ret, 1):
            # 最終更新日時のフォーマット
            last_update_timestamp = recode.get('LAST_UPDATE_TIMESTAMP')
            last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
            
            # カラムデータを格納
            col_detail = {
                "create_column_id": recode.get('CREATE_COLUMN_ID'),
                "item_name": recode.get('COLUMN_NAME_' + lang.upper()),
                "item_name_rest": recode.get('COLUMN_NAME_REST'),
                "display_order": recode.get('DISP_SEQ'),
                "required": recode.get('REQUIRED'),
                "uniqued": recode.get('UNIQUED'),
                "column_class_id": "",
                "column_class_name": "",
                "description": recode.get('DESCRIPTION_' + lang.upper()),
                "remarks": recode.get(''),
                "last_update_date_time": last_update_date_time
            }
            
            # フルカラムグループ名を格納
            column_group_id = recode.get('CREATE_COL_GROUP_ID')
            col_detail['column_group_id'] = column_group_id
            col_detail['column_group_name'] = None
            if column_group_id:
                target_data = column_group_list.get(column_group_id)
                if target_data:
                    col_detail['column_group_name'] = target_data.get('full_column_group_name')
                
            # カラムクラス情報を格納
            column_class_id = recode.get('COLUMN_CLASS')
            column_class_name = format_column_class_list.get(column_class_id).get('column_class_name')
            column_class_disp_name = format_column_class_list.get(column_class_id).get('column_class_disp_name')
            col_detail['column_class_id'] = column_class_id
            col_detail['column_class_name'] = column_class_name
            col_detail['column_class_disp_name'] = column_class_disp_name
            
            # カラムクラスに応じて必要な値を格納
            # カラムクラス「文字列(単一行)」用のパラメータを追加
            if column_class_name == "SingleTextColumn":
                col_detail["string_maximum_bytes"] = recode.get('SINGLE_MAX_LENGTH')  # 文字列(単一行) 最大バイト数
                col_detail["string_regular_expression"] = recode.get('SINGLE_REGULAR_EXPRESSION')  # 文字列(単一行) 正規表現
                col_detail["string_default_value"] = recode.get('SINGLE_DEFAULT_VALUE')  # 文字列(単一行) 初期値
            
            # カラムクラス「文字列(複数行)」用のパラメータを追加
            if column_class_name == "MultiTextColumn":
                col_detail["multi_string_maximum_bytes"] = recode.get('MULTI_MAX_LENGTH')  # 文字列(複数行) 最大バイト数
                col_detail["multi_string_regular_expression"] = recode.get('MULTI_REGULAR_EXPRESSION')  # 文字列(複数行) 正規表現
                col_detail["multi_string_default_value"] = recode.get('MULTI_DEFAULT_VALUE')  # 文字列(複数行) 初期値
            
            # カラムクラス「整数」用のパラメータを追加
            if column_class_name == "NumColumn":
                col_detail["integer_maximum_value"] = recode.get('NUM_MAX')  # 整数 最大値
                col_detail["integer_minimum_value"] = recode.get('NUM_MIN')  # 整数 最小値
                col_detail["integer_default_value"] = recode.get('NUM_DEFAULT_VALUE')  # 整数 初期値
            
            # カラムクラス「小数」用のパラメータを追加
            if column_class_name == "FloatColumn":
                col_detail["decimal_maximum_value"] = recode.get('FLOAT_MAX')  # 小数 最大値
                col_detail["decimal_minimum_value"] = recode.get('FLOAT_MIN')  # 小数 最小値
                col_detail["decimal_digit"] = recode.get('decimal_digit')  # 小数 桁数
                col_detail["decimal_default_value"] = recode.get('FLOAT_DEFAULT_VALUE')  # 小数 初期値
            
            # カラムクラス「日時」用のパラメータを追加
            if column_class_name == "DateTimeColumn":
                col_detail["detetime_default_value"] = recode.get('DATETIME_DEFAULT_VALUE')  # 日時 初期値
            
            # カラムクラス「日付」用のパラメータを追加
            if column_class_name == "DateColumn":
                col_detail["dete_default_value"] = recode.get('DATE_DEFAULT_VALUE')  # 日付 初期値
            
            # カラムクラス「プルダウン選択」用のパラメータを追加
            if column_class_name == "IDColumn":
                col_detail["pulldown_selection"] = recode.get('OTHER_MENU_LINK_ID')  # プルダウン選択 メニューグループ:メニュー:項目
                col_detail["pulldown_selection_default_value"] = recode.get('OTHER_MENU_LINK_DEFAULT_VALUE')  # プルダウン選択 初期値
                col_detail["reference_item"] = recode.get('REFERENCE_ITEM')  # プルダウン選択 参照項目
            
            # カラムクラス「パスワード」用のパラメータを追加
            if column_class_name == "PasswordColumn":
                col_detail["password_maximum_bytes"] = recode.get('PASSWORD_MAX_LENGTH')  # パスワード 最大バイト数
            
            # カラムクラス「ファイルアップロード」用のパラメータを追加
            if column_class_name == "FileUploadColumn":
                col_detail["file_upload_maximum_bytes"] = recode.get('FILE_UPLOAD_MAX_SIZE')  # ファイルアップロード 最大バイト数
            
            # カラムクラス「リンク」用のパラメータを追加
            if column_class_name == "HostInsideLinkTextColumn":
                col_detail["link_maximum_bytes"] = recode.get('LINK_MAX_LENGTH')  # リンク 最大バイト数
                col_detail["link_default_value"] = recode.get('LINK_DEFAULT_VALUE')  # リンク 初期値
            
            # カラムクラス「パラメータシート参照」用のパラメータを追加 (未実装)
            # if column_class_name == "LinkIDColumn":
            #     col_detail["parameter_sheet_reference"] = recode.get('PARAM_SHEET_LINK_ID')  # パラメータシート参照
            
            col_num = 'c{}'.format(count)
            column_info_data[col_num] = col_detail
            
            # カラムグループ利用があれば、カラムグループ管理用配列に追加
            if column_group_id:
                tmp_column_group, column_group_parent_of_child = add_tmp_column_group(column_group_list, col_group_recode_count, column_group_id, col_num, tmp_column_group, column_group_parent_of_child)  # noqa: E501
        
        # カラムグループ管理用配列について、カラムグループIDをg1,g2,g3...に変換し、idやnameを格納する。
        column_group_info_data, key_to_id = collect_column_group_sort_order(column_group_list, tmp_column_group, column_group_info_data)
        
        # 大元のカラムの並び順を作成し格納
        menu_info['menu']['columns'] = collect_parent_sord_order(column_info_data, column_group_parent_of_child, key_to_id)
    
    # カラム情報およびカラムグループ情報の個数を取得し、menu_info['menu']に格納
    menu_info['menu']['number_item'] = len(column_info_data)
    menu_info['menu']['number_group'] = len(column_group_info_data)
    
    # カラム情報を格納
    menu_info['column'] = column_info_data
    
    # カラムグループ情報を格納
    menu_info['group'] = column_group_info_data
    
    # 情報を返却値に格納
    create_data['menu_info'] = menu_info
    
    return create_data


def _collect_common_menu_create_data(objdbca):
    """
        【内部呼び出し用】メニュー定義・作成用情報の共通部分取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            common_data
    """
    # テーブル/ビュー名
    # t_common_column_class = 'T_COMN_COLUMN_CLASS'
    v_menu_column_class = 'V_MENU_COLUMN_CLASS'
    v_menu_sheet_type = 'V_MENU_SHEET_TYPE'
    v_menu_target_menu_group = 'V_MENU_TARGET_MENU_GROUP'
    v_menu_other_link = 'V_MENU_OTHER_LINK'

    # 変数定義
    lang = g.get('LANGUAGE')

    # カラムクラスの選択肢一覧
    column_class_list = []
    ret = objdbca.table_select(v_menu_column_class, 'ORDER BY DISP_SEQ ASC')
    for recode in ret:
        column_class_id = recode.get('COLUMN_CLASS_ID')
        column_class_name = recode.get('COLUMN_CLASS_NAME')
        column_class_disp_name = recode.get('COLUMN_CLASS_DISP_NAME_' + lang.upper())
        column_class_list.append({'column_class_id': column_class_id, 'column_class_name': column_class_name, 'column_class_disp_name': column_class_disp_name})  # noqa: E501

    # 対象メニューグループの選択肢一覧
    target_menu_group_list = []
    ret = objdbca.table_select(v_menu_target_menu_group, 'ORDER BY DISP_SEQ ASC')
    for recode in ret:
        menu_group_id = recode.get('MENU_GROUP_ID')
        menu_group_name = recode.get('MENU_GROUP_NAME_' + lang.upper())
        full_menu_group_name = recode.get('FULL_MENU_GROUP_NAME_' + lang.upper())
        target_menu_group_list.append({'menu_group_id': menu_group_id, 'menu_group_name': menu_group_name, 'full_menu_group_name': full_menu_group_name})  # noqa: E501

    # シートタイプの選択肢一覧
    sheet_type_list = []
    ret = objdbca.table_select(v_menu_sheet_type, 'ORDER BY DISP_SEQ ASC')
    for recode in ret:
        sheet_type_id = recode.get('SHEET_TYPE_NAME_ID')
        sheet_type_name = recode.get('SHEET_TYPE_NAME_' + lang.upper())
        sheet_type_list.append({'sheet_type_id': sheet_type_id, 'sheet_type_name': sheet_type_name})

    # カラムクラス「プルダウン選択」の選択項目一覧
    pulldown_item_list = []
    ret = objdbca.table_select(v_menu_other_link, 'ORDER BY MENU_GROUP_ID ASC')
    for recode in ret:
        link_id = recode.get('LINK_ID')
        menu_id = recode.get('MENU_ID')
        link_pulldown = recode.get('LINK_PULLDOWN_' + lang.upper())
        pulldown_item_list.append({'link_id': link_id, 'menu_id': menu_id, 'link_pulldown': link_pulldown})
    
    # ロールの選択肢一覧
    role_list = util.get_workspace_roles()  # noqa: F405
    
    common_data = {
        "column_class_list": column_class_list,
        "target_menu_group_list": target_menu_group_list,
        "sheet_type_list": sheet_type_list,
        "pulldown_item_list": pulldown_item_list,
        "role_list": role_list
    }
    
    return common_data


def menu_create_execute(objdbca, exec_target):
    """
        メニュー作成の実行
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            exec_target: メニュー作成の実行対象
        RETRUN:
            result_data
    """
    
    return {"aaa": "bbb"}


def menu_create_define(objdbca, create_param):
    """
        メニュー定義および作成の実行
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            create_param: メニュー定義用パラメータ
        RETRUN:
            result_data
    """
    # typeから「新規作成」「初期化」「編集」のいずれかを判断
    type = create_param.get('type')
    if type == 'create_new':  # 「新規作成」
        print('タイプは：' + str(type))
        result = _create_new_execute(objdbca, create_param)
        
        history_id = result.get('history_id')
        message = result.get('message')
        # if not status:
        #     # ####メモ：関数で失敗した際にメッセージを受け取ってそれを入れる。
        #     # ####まだここの動き全然考えてないので、あとでやる。
        #     raise AppException('999-00001')  # noqa: F405
        
    elif type == 'initialize':  # 「初期化」
        print('タイプは：' + str(type))
        result = _initialize_execute(objdbca, create_param)
        
        history_id = result.get('history_id')
        message = result.get('message')
        # if not status:
        #     # ####メモ：関数で失敗した際にメッセージを受け取ってそれを入れる。
        #     # ####まだここの動き全然考えてないので、あとでやる。
        #     raise AppException('999-00001')  # noqa: F405
        
    elif type == 'edit':  # 「編集」
        print('タイプは：' + str(type))
        result = _edit_execute(objdbca, create_param)
        
        history_id = result.get('history_id')
        message = result.get('message')
        # if not status:
        #     # ####メモ：関数で失敗した際にメッセージを受け取ってそれを入れる。
        #     # ####まだここの動き全然考えてないので、あとでやる。
        #     raise AppException('999-00001')  # noqa: F405
        
    else:
        # ####メモ：typeが指定された値ではない場合のエラー。あとでちゃんと作る。
        msg = 'type:' + str(type)
        log_msg_args = [msg]
        api_msg_args = [msg]
        raise AppException('499-00212', log_msg_args, api_msg_args)  # noqa: F405
    
    result_data = {'history_id': history_id, 'message': message}
    return result_data


def _create_new_execute(objdbca, create_param):  # noqa: C901
    """
        【内部呼び出し用】「新規作成」時のメニュー作成用メニューに対するレコードをの登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            create_param: メニュー定義用パラメータ
        RETRUN:
            result_data
    """
    # 変数定義
    user_id = g.get('USER_ID')
    
    # 登録するためのデータを抽出
    menu_data = check_request_body_key(create_param, 'menu')  # ####メモ： "menu" keyが無かったら400-00002エラー
    column_data_list = create_param.get('column')
    group_data_list = create_param.get('group')
    
    try:
        # トランザクション開始
        objdbca.db_transaction_start()
        
        # 登録前バリデーションチェック
        retbool, msg = _check_before_registar_validate(objdbca, menu_data, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 「メニュー定義一覧」にレコードを登録
        retbool, menu_create_id, msg = _insert_t_menu_define(objdbca, menu_data)
        if not retbool:
            raise Exception(msg)
        
        # カラムグループ用データがある場合、「カラムグループ作成情報」にレコードを登録
        if group_data_list:
            retbool, msg = _insert_t_menu_column_group(objdbca, group_data_list)
            if not retbool:
                raise Exception(msg)
        
        # 「メニュー項目作成情報」にレコードを登録
        retbool, msg = _insert_t_menu_column(objdbca, menu_data, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 「一意制約(複数項目)作成情報」にレコードを登録
        retbool, msg = _insert_t_menu_unique_constraint(objdbca, menu_data)
        if not retbool:
            raise Exception(msg)
        
        # 「メニュー-ロール作成情報」にレコードを登録
        menu_name = menu_data.get('menu_name')
        role_list = menu_data.get('role_list')
        if role_list:
            retbool, msg = _insert_t_menu_role(objdbca, menu_name, role_list)
            if not retbool:
                raise Exception(msg)
        
        # 「メニュー作成履歴」にレコードを登録
        status_id = "1"  # (1:未実行)
        create_type = "1"  # (1:新規作成)
        retbool, history_id, msg = _insert_t_menu_create_history(objdbca, menu_create_id, status_id, create_type, user_id)
        if not retbool:
            raise Exception(msg)
        
        # コミット/トランザクション終了
        objdbca.db_transaction_end(True)
        
        message = ''
        
    except Exception as e:
        # ####メモ：失敗時のメッセージはちゃんと取り出したいので、作りこみ予定。
        # ロールバック トランザクション終了
        print("エラー発生のためロールバック")
        objdbca.db_transaction_end(False)
        print(e)
        if len(e.args) == 2:
            status_code = '{}'.format(e.args[0])
            msg_args = '{}'.format(e.args[1])
            msg = g.appmsg.get_api_message(status_code, [msg_args])
        else:
            status_code = '999-99999'
            msg_args = '{}'.format(*e.args)
            msg = g.appmsg.get_api_message(status_code, [msg_args])
        
        message = msg
        history_id = None

    result_data = {
        'history_id': history_id,
        'message': message
    }
    
    return result_data


def _initialize_execute(objdbca, create_param):  # noqa: C901
    """
        【内部呼び出し用】「初期化」時のメニュー作成用メニューに対するレコードの登録/更新/廃止
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            create_param: メニュー定義用パラメータ
        RETRUN:
            result_data
    """
    # テーブル名
    t_menu_define = 'T_MENU_DEFINE'
    t_menu_column = 'T_MENU_COLUMN'
    t_menu_unique_constraint = 'T_MENU_UNIQUE_CONSTRAINT'
    t_menu_role = 'T_MENU_ROLE'
    
    # 変数定義
    user_id = g.get('USER_ID')
    
    # データを抽出
    menu_data = check_request_body_key(create_param, 'menu')  # "menu" keyが無かったら400-00002エラー
    column_data_list = check_request_body_key(create_param, 'column')  # "column" keyが無かったら400-00002エラー
    group_data_list = create_param.get('group')
    
    try:
        # トランザクション開始
        objdbca.db_transaction_start()
        
        # 登録前バリデーションチェック
        retbool, msg = _check_before_registar_validate(objdbca, menu_data, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 対象の「メニュー定義一覧」のuuidおよびメニュー名を取得
        menu_create_id = menu_data.get('menu_create_id')
        menu_name = menu_data.get('menu_name')
        
        # 現在の「メニュー定義一覧」のレコードを取得
        current_t_menu_define = objdbca.table_select(t_menu_define, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
        if not current_t_menu_define:
            raise Exception("「メニュー定義一覧」に対象のメニューが存在しません。")
        current_t_menu_define = current_t_menu_define[0]
        
        # 「メニュー定義一覧」のレコードを更新
        retbool, msg = _update_t_menu_define(objdbca, current_t_menu_define, menu_data, 'initialize')
        if not retbool:
            raise Exception(msg)
        
        # カラムグループ用データがある場合、「カラムグループ作成情報」にレコードを登録
        if group_data_list:
            retbool, msg = _insert_t_menu_column_group(objdbca, group_data_list)
            if not retbool:
                raise Exception(msg)
        
        # 現在の「メニュー項目作成情報」のレコードを取得
        current_t_menu_column_list = objdbca.table_select(t_menu_column, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
        
        # 「メニュー項目作成情報」から未使用となる項目のレコードを廃止
        retbool, msg = _disuse_t_menu_column(objdbca, current_t_menu_column_list, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 「メニュー項目作成情報」から更新対象のレコードを更新
        retbool, msg = _update_t_menu_column(objdbca, current_t_menu_column_list, column_data_list, 'initialize')
        if not retbool:
            raise Exception(msg)
        
        # 「メニュー項目作成情報」に新規追加項目用レコードを登録
        retbool, msg = _insert_t_menu_column(objdbca, menu_data, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 現在の「一意制約(複数項目)作成情報」のレコードを取得
        current_t_menu_unique_constraint = objdbca.table_select(t_menu_unique_constraint, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])  # noqa: E501
        
        # 「一意制約(複数項目)」の値があり、かつ「一意制約(複数項目)作成情報」にレコードが存在する場合、レコードを更新
        unique_constraint = menu_data.get('unique_constraint')
        if current_t_menu_unique_constraint and unique_constraint:
            target_recode = current_t_menu_unique_constraint[0]
            retbool, msg = _update_t_menu_unique_constraint(objdbca, menu_data, target_recode)
        
        # 「一意制約(複数項目)」の値がない、かつ「一意制約(複数項目)作成情報」にレコードが存在する場合、レコードを廃止
        elif current_t_menu_unique_constraint and not unique_constraint:
            target_recode = current_t_menu_unique_constraint[0]
            retbool, msg = _disuse_t_menu_unique_constraint(objdbca, target_recode)
        
        # 「一意制約(複数項目)」の値があり、かつ「一意制約(複数項目)作成情報」にレコードが存在しない場合、レコードを登録
        elif not current_t_menu_unique_constraint and unique_constraint:
            retbool, msg = _insert_t_menu_unique_constraint(objdbca, menu_data)
            if not retbool:
                raise Exception(msg)
        
        # 「ロール選択」の値を取得
        role_list = menu_data.get('role_list')
        if not role_list:
            role_list = []
        
        # 現在の「メニュー-ロール作成情報」のレコードを取得
        current_t_menu_role = objdbca.table_select(t_menu_role, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
        current_role_list = []
        current_role_dict = {}
        if current_t_menu_role:
            for recode in current_t_menu_role:
                menu_role_id = recode.get('MENU_ROLE_ID')
                role = recode.get('ROLE_ID')
                last_update_timestamp = recode.get('LAST_UPDATE_TIMESTAMP')
                last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
                current_role_list.append(role)
                current_role_dict[role] = {"menu_role_id": menu_role_id, 'last_update_date_time': last_update_date_time}
        
        # 新規に登録するロールの対象一覧を取得し、レコードを追加
        add_role_list = set(role_list) - set(current_role_list)
        if list(add_role_list):
            retbool, msg = _insert_t_menu_role(objdbca, menu_name, list(add_role_list))
            if not retbool:
                raise Exception(msg)
        
        # 廃止するロールの対象一覧を取得し、レコードを廃止
        disuse_role_list = set(current_role_list) - set(role_list)
        if list(disuse_role_list):
            retbool, msg = _disuse_t_menu_role(objdbca, list(disuse_role_list), current_role_dict)
            if not retbool:
                raise Exception(msg)
        
        # 「メニュー作成履歴」にレコードを登録
        status_id = "1"  # (1:未実行)
        create_type = "2"  # (2:初期化)
        retbool, history_id, msg = _insert_t_menu_create_history(objdbca, menu_create_id, status_id, create_type, user_id)
        if not retbool:
            raise Exception(msg)
        
        # コミット/トランザクション終了
        objdbca.db_transaction_end(True)
        
        message = ''

    except Exception as e:
        # ####メモ：失敗時のメッセージはちゃんと取り出したいので、作りこみ予定。
        # ロールバック トランザクション終了
        print("エラー発生のためロールバック")
        objdbca.db_transaction_end(False)
        print(e)
        if len(e.args) == 2:
            status_code = '{}'.format(e.args[0])
            msg_args = '{}'.format(e.args[1])
            msg = g.appmsg.get_api_message(status_code, [msg_args])
        else:
            status_code = '999-99999'
            msg_args = '{}'.format(*e.args)
            msg = g.appmsg.get_api_message(status_code, [msg_args])

        message = msg
        history_id = None

    result_data = {
        'history_id': history_id,
        'message': message
    }
    
    return result_data


def _edit_execute(objdbca, create_param):  # noqa: C901
    """
        【内部呼び出し用】「編集」時のメニュー作成用メニューに対するレコードの登録/更新/廃止
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            create_param: メニュー定義用パラメータ
        RETRUN:
            result_data
    """
    # テーブル名
    t_menu_define = 'T_MENU_DEFINE'
    t_menu_column = 'T_MENU_COLUMN'
    t_menu_unique_constraint = 'T_MENU_UNIQUE_CONSTRAINT'
    t_menu_role = 'T_MENU_ROLE'
    
    # 変数定義
    user_id = g.get('USER_ID')
    
    # データを抽出
    menu_data = check_request_body_key(create_param, 'menu')  # "menu" keyが無かったら400-00002エラー
    column_data_list = check_request_body_key(create_param, 'column')  # "column" keyが無かったら400-00002エラー
    group_data_list = create_param.get('group')
    
    try:
        # トランザクション開始
        objdbca.db_transaction_start()
        
        # 登録前バリデーションチェック
        retbool, msg = _check_before_registar_validate(objdbca, menu_data, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 対象の「メニュー定義一覧」のuuidおよびメニュー名を取得
        menu_create_id = menu_data.get('menu_create_id')
        menu_name = menu_data.get('menu_name')
        
        # 現在の「メニュー定義一覧」のレコードを取得
        current_t_menu_define = objdbca.table_select(t_menu_define, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
        if not current_t_menu_define:
            raise Exception("「メニュー定義一覧」に対象のメニューが存在しません。")
        current_t_menu_define = current_t_menu_define[0]
        
        # 「メニュー定義一覧」のレコードを更新
        retbool, msg = _update_t_menu_define(objdbca, current_t_menu_define, menu_data, 'edit')
        if not retbool:
            raise Exception(msg)
        
        # カラムグループ用データがある場合、「カラムグループ作成情報」にレコードを登録
        if group_data_list:
            retbool, msg = _insert_t_menu_column_group(objdbca, group_data_list)
            if not retbool:
                raise Exception(msg)
        
        # 現在の「メニュー項目作成情報」のレコードを取得
        current_t_menu_column_list = objdbca.table_select(t_menu_column, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
        
        # 「メニュー項目作成情報」から未使用となる項目のレコードを廃止
        retbool, msg = _disuse_t_menu_column(objdbca, current_t_menu_column_list, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 「メニュー項目作成情報」から更新対象のレコードを更新
        retbool, msg = _update_t_menu_column(objdbca, current_t_menu_column_list, column_data_list, 'edit')
        if not retbool:
            raise Exception(msg)
        
        # 「メニュー項目作成情報」に新規追加項目用レコードを登録
        retbool, msg = _insert_t_menu_column(objdbca, menu_data, column_data_list)
        if not retbool:
            raise Exception(msg)
        
        # 現在の「一意制約(複数項目)作成情報」のレコードを取得
        current_t_menu_unique_constraint = objdbca.table_select(t_menu_unique_constraint, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])  # noqa: E501
        
        # 「一意制約(複数項目)」の値があり、かつ「一意制約(複数項目)作成情報」にレコードが存在する場合、レコードを更新
        unique_constraint = menu_data.get('unique_constraint')
        if current_t_menu_unique_constraint and unique_constraint:
            target_recode = current_t_menu_unique_constraint[0]
            retbool, msg = _update_t_menu_unique_constraint(objdbca, menu_data, target_recode)
        
        # 「一意制約(複数項目)」の値がない、かつ「一意制約(複数項目)作成情報」にレコードが存在する場合、レコードを廃止
        elif current_t_menu_unique_constraint and not unique_constraint:
            target_recode = current_t_menu_unique_constraint[0]
            retbool, msg = _disuse_t_menu_unique_constraint(objdbca, target_recode)
        
        # 「一意制約(複数項目)」の値があり、かつ「一意制約(複数項目)作成情報」にレコードが存在しない場合、レコードを登録
        elif not current_t_menu_unique_constraint and unique_constraint:
            retbool, msg = _insert_t_menu_unique_constraint(objdbca, menu_data)
            if not retbool:
                raise Exception(msg)
        
        # 「ロール選択」の値を取得
        role_list = menu_data.get('role_list')
        if not role_list:
            role_list = []
        
        # 現在の「メニュー-ロール作成情報」のレコードを取得
        current_t_menu_role = objdbca.table_select(t_menu_role, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
        current_role_list = []
        current_role_dict = {}
        if current_t_menu_role:
            for recode in current_t_menu_role:
                menu_role_id = recode.get('MENU_ROLE_ID')
                role = recode.get('ROLE_ID')
                last_update_timestamp = recode.get('LAST_UPDATE_TIMESTAMP')
                last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
                current_role_list.append(role)
                current_role_dict[role] = {"menu_role_id": menu_role_id, 'last_update_date_time': last_update_date_time}
        
        # 新規に登録するロールの対象一覧を取得し、レコードを追加
        add_role_list = set(role_list) - set(current_role_list)
        if list(add_role_list):
            retbool, msg = _insert_t_menu_role(objdbca, menu_name, list(add_role_list))
            if not retbool:
                raise Exception(msg)
        
        # 廃止するロールの対象一覧を取得し、レコードを廃止
        disuse_role_list = set(current_role_list) - set(role_list)
        if list(disuse_role_list):
            retbool, msg = _disuse_t_menu_role(objdbca, list(disuse_role_list), current_role_dict)
            if not retbool:
                raise Exception(msg)
        
        # 「メニュー作成履歴」にレコードを登録
        status_id = "1"  # (1:未実行)
        create_type = "3"  # (3:編集)
        retbool, history_id, msg = _insert_t_menu_create_history(objdbca, menu_create_id, status_id, create_type, user_id)
        if not retbool:
            raise Exception(msg)
        
        # コミット/トランザクション終了
        objdbca.db_transaction_end(True)
        
        message = ''

    except Exception as e:
        # ####メモ：失敗時のメッセージはちゃんと取り出したいので、作りこみ予定。
        # ロールバック トランザクション終了
        print("エラー発生のためロールバック")
        objdbca.db_transaction_end(False)
        print(e)
        if len(e.args) == 2:
            status_code = '{}'.format(e.args[0])
            msg_args = '{}'.format(e.args[1])
            msg = g.appmsg.get_api_message(status_code, [msg_args])
        else:
            status_code = '999-99999'
            msg_args = '{}'.format(*e.args)
            msg = g.appmsg.get_api_message(status_code, [msg_args])

        message = msg
        history_id = None

    result_data = {
        'history_id': history_id,
        'message': message
    }
    
    return result_data


def _insert_t_menu_define(objdbca, menu_data):
    """
        【内部呼び出し用】「メニュー定義一覧」にレコードを登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_data: 登録対象のメニュー情報
        RETRUN:
            boolean, menu_create_id, msg
    """
    try:
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'menu_definition_list')  # noqa: F405
        
        # 登録用パラメータを作成
        parameters = {
            "parameter": {
                "menu_name_ja": menu_data.get('menu_name'),  # メニュー名称(ja)
                "menu_name_en": menu_data.get('menu_name'),  # メニュー名称(en)
                "menu_name_rest": menu_data.get('menu_name_rest'),  # メニュー名称(rest)
                "sheet_type": menu_data.get('sheet_type'),  # シートタイプ名
                "display_order": menu_data.get('display_order'),  # 表示順序
                "description_ja": menu_data.get('description'),  # 説明(ja)
                "description_en": menu_data.get('description'),  # 説明(en)
                "remarks": menu_data.get('remarks'),  # 備考
                "vertical": menu_data.get('vertical'),  # 縦メニュー利用有無
                "menu_group_for_input": menu_data.get('menu_group_for_input'),  # 入力用メニューグループ名
                "menu_group_for_subst": menu_data.get('menu_group_for_subst'),  # 代入値自動登録用メニューグループ名
                "menu_group_for_ref": menu_data.get('menu_group_for_ref')  # 参照用メニューグループ名
            },
            "type": "Register"
        }

        # 登録を実行
        exec_result = objmenu.exec_maintenance(parameters)  # noqa: F405
        if not exec_result[0]:
            print("「メニュー定義一覧」にレコードを登録する際にエラーが起きた。")
            raise Exception(exec_result[2])
        
        # 登録されたレコードのUUIDを保管
        menu_create_id = exec_result[1].get('uuid')
            
    except Exception as msg:
        return False, None, msg
    
    return True, menu_create_id, None


def _update_t_menu_define(objdbca, current_t_menu_define, menu_data, create_type):
    """
        【内部呼び出し用】「メニュー定義一覧」にレコードを登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            current_t_menu_define: 「メニュー定義一覧」の更新対象のレコード
            menu_data: 登録対象のメニュー情報
            create_type: 初期化(initialize), 編集(edit)のいずれか
        RETRUN:
            boolean, msg
    """
    # テーブル/ビュー名
    v_menu_sheet_type = 'V_MENU_SHEET_TYPE'
    
    # 変数定義
    lang = g.get('LANGUAGE')
    
    try:
        # 更新対象レコードの「メニュー作成状態」が「2:作成済み」ではない場合「初期化」「編集」はできないのでエラー判定
        menu_create_done_status = str(current_t_menu_define.get('MENU_CREATE_DONE_STATUS'))
        if not menu_create_done_status == "2":
            msg = "「メニュー定義一覧」の更新対象のレコードの「メニュー作成状態」が「作成済み」では無い場合、「初期化」および「編集」は実行できません。"
            raise Exception(msg)
        
        # 「メニュー名(ja)」「メニュー名(en)」「メニュー名(rest)」に変更がある場合はエラー判定
        currrent_menu_name_ja = current_t_menu_define.get('MENU_NAME_JA')
        current_menu_name_en = current_t_menu_define.get('MENU_NAME_EN')
        current_menu_name_rest = current_t_menu_define.get('MENU_NAME_REST')
        menu_name_ja = menu_data.get('menu_name')
        menu_name_en = menu_data.get('menu_name')
        menu_name_rest = menu_data.get('menu_name_rest')
        if not currrent_menu_name_ja == menu_name_ja or not current_menu_name_en == menu_name_en:
            msg = "「初期化」および「編集」の際はメニュー名は変更できません。"
            raise Exception(msg)
        
        if not current_menu_name_rest == menu_name_rest:
            msg = "「初期化」および「編集」の際はメニュー名(rest)は変更できません。"
            raise Exception(msg)
        
        # 「シートタイプ」「縦メニュー利用」を取得
        sheet_type = str(menu_data.get('sheet_type'))
        vertical = str(menu_data.get('vertical'))
        
        # 「編集」の場合のみチェックするバリデーション
        if create_type == 'edit':
            current_sheet_type = str(current_t_menu_define.get('SHEET_TYPE'))
            current_vertical = str(current_t_menu_define.get('VERTICAL'))
            
            # シートタイプのIDと名称の紐付け取得
            sheet_type_list = objdbca.table_select(v_menu_sheet_type, 'ORDER BY DISP_SEQ ASC')
            sheet_type_dict = {}
            for recode in sheet_type_list:
                sheet_type_name_id = recode.get('SHEET_TYPE_NAME_ID')
                sheet_type_dict[sheet_type_name_id] = recode.get('SHEET_TYPE_NAME_' + lang.upper())
            
            current_sheet_type_name = sheet_type_dict[current_sheet_type]  # シートタイプ名称
            if not current_sheet_type_name == sheet_type:
                msg = "「編集」の際はシートタイプを変更できません。"
                raise Exception(msg)
            
            vertical_id = "1" if vertical == "True" else "0"
            if not current_vertical == vertical_id:
                msg = "「編集」の際は縦メニュー利用を変更できません。"
                raise Exception(msg)
        
        # 対象のuuidを取得
        menu_create_id = menu_data.get('menu_create_id')
        
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'menu_definition_list')  # noqa: F405
        
        # 更新用パラメータを作成
        parameters = {
            "parameter": {
                "menu_name_ja": menu_name_ja,  # メニュー名称(ja)
                "menu_name_en": menu_name_en,  # メニュー名称(en)
                "menu_name_rest": menu_name_rest,  # メニュー名称(rest)
                "sheet_type": sheet_type,  # シートタイプ名
                "display_order": menu_data.get('display_order'),  # 表示順序
                "description_ja": menu_data.get('description'),  # 説明(ja)
                "description_en": menu_data.get('description'),  # 説明(en)
                "remarks": menu_data.get('remarks'),  # 備考
                "vertical": vertical,  # 縦メニュー利用有無
                "menu_group_for_input": menu_data.get('menu_group_for_input'),  # 入力用メニューグループ名
                "menu_group_for_subst": menu_data.get('menu_group_for_subst'),  # 代入値自動登録用メニューグループ名
                "menu_group_for_ref": menu_data.get('menu_group_for_ref'),  # 参照用メニューグループ名
                "last_update_date_time": menu_data.get('last_update_date_time')  # 最終更新日時
            },
            "type": "Update"
        }
        
        # 「メニュー定義一覧」のレコードを更新
        exec_result = objmenu.exec_maintenance(parameters, menu_create_id)  # noqa: F405
        if not exec_result[0]:
            print("「メニュー定義一覧」にレコードを更新する際にエラーが起きた。")
            raise Exception(exec_result[2])

    except Exception as msg:
        return False, msg
    
    return True, None


def _insert_t_menu_column_group(objdbca, group_data_list):
    """
        【内部呼び出し用】「カラムグループ作成情報」にレコードを登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            group_data_list: 登録対象のカラムグループ一覧
        RETRUN:
            boolean, msg
    """
    # テーブル名
    t_menu_column_group = 'T_MENU_COLUMN_GROUP'
    
    # 変数定義
    lang = g.get('LANGUAGE')
    
    try:
        # 現在登録されている「カラムグループ作成情報」のレコード一覧を取得
        column_group_list = objdbca.table_select(t_menu_column_group, 'WHERE DISUSE_FLAG = %s', [0])
        
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'column_group_creation_info')  # noqa: F405
        
        # 「カラムグループ作成情報」登録処理のループスタート
        for num, group_data in group_data_list.items():
            # 登録用パラメータを作成
            col_group_name_ja = group_data.get('col_group_name')
            col_group_name_en = group_data.get('col_group_name')
            parent_full_col_group_name = group_data.get('parent_full_col_group_name')
            
            # 親カラムグループがあれば、対象の「フルカラムグループ名」を取得
            parent_column_group = None
            if parent_full_col_group_name:
                if lang.lower() == 'ja':
                    target_parent = objdbca.table_select(t_menu_column_group, 'WHERE FULL_COL_GROUP_NAME_JA = %s AND DISUSE_FLAG = %s', [parent_full_col_group_name, 0])  # noqa: E501
                elif lang.lower() == 'en':
                    target_parent = objdbca.table_select(t_menu_column_group, 'WHERE FULL_COL_GROUP_NAME_EN = %s AND DISUSE_FLAG = %s', [parent_full_col_group_name, 0])  # noqa: E501
                
                if not target_parent:
                    raise Exception("「カラムグループ作成情報」にレコードを登録する際に、存在しない親IDを指定しようとした。")
                
                # ####メモ：本来は「カラムグループ作成情報」に対する「before_function」にてフルカラムグループ名を作成する処理を実行する。
                # 最終で気にここでフルカラムグループ名を作成する処理は書かない想定。
                # 『親フルカラムグループ/カラムグループ名』の命名規則でフルカラムグループ名を作成。
                parent_full_name_ja = target_parent[0].get('FULL_COL_GROUP_NAME_JA')
                parent_full_name_en = target_parent[0].get('FULL_COL_GROUP_NAME_EN')
                full_column_group_name_ja = parent_full_name_ja + '/' + col_group_name_ja
                full_column_group_name_en = parent_full_name_en + '/' + col_group_name_en
                
                parent_full_name = target_parent[0].get('FULL_COL_GROUP_NAME_' + lang.upper())
                parent_column_group = parent_full_name
                
            else:
                full_column_group_name_ja = col_group_name_ja
                full_column_group_name_en = col_group_name_en
            
            # 『「フルカラムグループ(ja)」』か『「フルカラムグループ(en)」』ですでに同じレコードがあれば処理をスキップ
            skip_flag = False
            for recode in column_group_list:
                if full_column_group_name_ja == recode.get('FULL_COL_GROUP_NAME_JA') or full_column_group_name_en == recode.get('FULL_COL_GROUP_NAME_EN'):  # noqa: E501
                    skip_flag = True
            
            if skip_flag:
                continue
            
            # 登録用パラメータを作成
            parameters = {
                "parameter": {
                    "parent_column_group": parent_column_group,
                    "column_group_name_ja": col_group_name_ja,
                    "column_group_name_en": col_group_name_en,
                    "full_column_group_name_ja": full_column_group_name_ja,
                    "full_column_group_name_en": full_column_group_name_en
                },
                "type": "Register"
            }
            
            # 登録を実行
            exec_result = objmenu.exec_maintenance(parameters)  # noqa: F405
            if not exec_result[0]:
                print("「カラムグループ作成情報」にレコードを登録する際にエラーが起きた。")
                raise Exception(exec_result[2])
            
            # 現在登録されている「カラムグループ作成情報」のレコード一覧を更新
            column_group_list = objdbca.table_select(t_menu_column_group, 'WHERE DISUSE_FLAG = %s', [0])
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _insert_t_menu_column(objdbca, menu_data, column_data_list):
    """
        【内部呼び出し用】「メニュー項目作成情報」にレコードを登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_data: 登録対象のメニュー情報
            column_data_list: 登録対象のカラム情報一覧
        RETRUN:
            boolean, msg
    """
    try:
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'menu_item_creation_info')  # noqa: F405
        
        # menu_dataから登録用のメニュー名を取得
        menu_name = menu_data.get('menu_name')
        
        # 「メニュー項目作成情報」登録処理のループスタート
        for column_data in column_data_list.values():
            # create_column_idが空(null)のもののみ対象とする
            create_column_id = column_data.get('create_column_id')
            if not create_column_id:
                # 登録用パラメータを作成
                column_class = column_data.get('column_class')
                parameter = {
                    "menu_name": menu_name,  # メニュー名(「メニュー定義一覧」のメニュー名)
                    "item_name_ja": column_data.get('item_name'),  # 項目名(ja)
                    "item_name_en": column_data.get('item_name'),  # 項目名(en)
                    "item_name_rest": column_data.get('item_name_rest'),  # 項目名(rest)
                    "description_ja": column_data.get('description'),  # 説明(ja)
                    "description_en": column_data.get('description'),  # 説明(en)
                    "column_class": column_class,  # カラムクラス
                    "display_order": column_data.get('display_order'),  # 表示順序
                    "required": column_data.get('required'),  # 必須
                    "uniqued": column_data.get('uniqued'),  # 一意制約
                    "remarks": column_data.get('remarks'),  # 備考
                }
                
                # カラムグループがある場合
                column_group = column_data.get('column_group')
                if column_group:
                    parameter["column_group"] = column_group  # カラムグループ(「カラムグループ作成情報」のフルカラムグループ名)
                
                # カラムクラス「文字列(単一行)」用のパラメータを追加
                if column_class == "SingleTextColumn":
                    parameter["string_maximum_bytes"] = column_data.get('single_maximum_bytes')  # 文字列(単一行) 最大バイト数
                    parameter["string_regular_expression"] = column_data.get('string_regular_expression')  # 文字列(単一行) 正規表現
                    parameter["string_default_value"] = column_data.get('single_default_value')  # 文字列(単一行) 初期値
                
                # カラムクラス「文字列(複数行)」用のパラメータを追加
                if column_class == "MultiTextColumn":
                    parameter["multi_string_maximum_bytes"] = column_data.get('multi_string_maximum_bytes')  # 文字列(複数行) 最大バイト数
                    parameter["multi_string_regular_expression"] = column_data.get('multi_string_regular_expression')  # 文字列(複数行) 正規表現
                    parameter["multi_string_default_value"] = column_data.get('multi_string_default_value')  # 文字列(複数行) 初期値
                
                # カラムクラス「整数」用のパラメータを追加
                if column_class == "NumColumn":
                    parameter["integer_maximum_value"] = column_data.get('integer_maximum_value')  # 整数 最大値
                    parameter["integer_minimum_value"] = column_data.get('integer_minimum_value')  # 整数 最小値
                    parameter["integer_default_value"] = column_data.get('integer_default_value')  # 整数 初期値
                
                # カラムクラス「小数」用のパラメータを追加
                if column_class == "FloatColumn":
                    parameter["decimal_maximum_value"] = column_data.get('decimal_maximum_value')  # 小数 最大値
                    parameter["decimal_minimum_value"] = column_data.get('decimal_minimum_value')  # 小数 最小値
                    parameter["decimal_digit"] = column_data.get('decimal_digit')  # 小数 桁数
                    parameter["decimal_default_value"] = column_data.get('decimal_default_value')  # 小数 初期値
                
                # カラムクラス「日時」用のパラメータを追加
                if column_class == "DateTimeColumn":
                    parameter["detetime_default_value"] = column_data.get('detetime_default_value')  # 日時 初期値
                
                # カラムクラス「日付」用のパラメータを追加
                if column_class == "DateColumn":
                    parameter["dete_default_value"] = column_data.get('dete_default_value')  # 日付 初期値
                
                # カラムクラス「プルダウン選択」用のパラメータを追加
                if column_class == "IDColumn":
                    parameter["pulldown_selection"] = column_data.get('pulldown_selection')  # プルダウン選択 メニューグループ:メニュー:項目
                    parameter["pulldown_selection_default_value"] = column_data.get('pulldown_selection_default_value')  # プルダウン選択 初期値
                    parameter["reference_item"] = column_data.get('reference_item')  # プルダウン選択 参照項目
                
                # カラムクラス「パスワード」用のパラメータを追加
                if column_class == "PasswordColumn":
                    parameter["password_maximum_bytes"] = column_data.get('password_maximum_bytes')  # パスワード 最大バイト数
                
                # カラムクラス「ファイルアップロード」用のパラメータを追加
                if column_class == "FileUploadColumn":
                    parameter["file_upload_maximum_bytes"] = column_data.get('file_upload_maximum_bytes')  # ファイルアップロード 最大バイト数
                
                # カラムクラス「リンク」用のパラメータを追加
                if column_class == "HostInsideLinkTextColumn":
                    parameter["link_maximum_bytes"] = column_data.get('link_maximum_bytes')  # リンク 最大バイト数
                    parameter["link_default_value"] = column_data.get('link_default_value')  # リンク 初期値
                
                # カラムクラス「パラメータシート参照」用のパラメータを追加 (未実装)
                # if column_class == "LinkIDColumn":
                #     parameter["parameter_sheet_reference"] = column_data.get('parameter_sheet_reference')  # パラメータシート参照
                
                parameters = {
                    "parameter": parameter,
                    "type": "Register"
                }
                
                # 登録を実行
                exec_result = objmenu.exec_maintenance(parameters)  # noqa: F405
                if not exec_result[0]:
                    print("「メニュー項目作成情報」にレコードを登録する際にエラーが起きた。")
                    raise Exception(exec_result[2])
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _update_t_menu_column(objdbca, current_t_menu_column_list, column_data_list, create_type):  # noqa: C901
    """
        【内部呼び出し用】「メニュー項目作成情報」のレコードを更新する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            current_t_menu_column_list: 「メニュー項目作成情報」の現在登録されているレコード（対象メニューのMENU_CREATE_IDと紐づいているもの）
            column_data_list: 登録対象のカラム情報一覧
            create_type: 初期化(initialize), 編集(edit)のいずれか
        RETRUN:
            boolean, msg
    """
    # テーブル/ビュー名
    v_menu_column_class = 'V_MENU_COLUMN_CLASS'
    
    try:
        # current_t_menu_column_listのレコードについて、create_column_idをkeyにしたdict型に変換
        current_t_menu_column_dict = {}
        for recode in current_t_menu_column_list:
            create_column_id = recode.get('CREATE_COLUMN_ID')
            current_t_menu_column_dict[create_column_id] = recode
        
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'menu_item_creation_info')  # noqa: F405
        
        # 「メニュー項目作成情報」更新処理のループスタート
        for column_data in column_data_list.values():
            # 更新対象のuuidを取得
            create_column_id = column_data.get('create_column_id')
            
            # 更新対象の最終更新日時を取得
            last_update_date_time = column_data.get('last_update_date_time')
            
            if create_column_id:
                # 対象のカラムクラスを取得
                column_class = column_data.get('column_class')
                
                # 「編集」の場合、登録済みレコードとの差分によるバリデーションチェックを行う
                if create_type == 'edit':
                    # カラムクラスのIDと名称の紐付け取得
                    column_class_list = objdbca.table_select(v_menu_column_class, 'ORDER BY DISP_SEQ ASC')
                    column_class_dict = {}
                    for recode in column_class_list:
                        column_class_id = recode.get('COLUMN_CLASS_ID')
                        column_class_dict[column_class_id] = recode.get('COLUMN_CLASS_NAME')
                    
                    # 更新対象の現在のレコードを取得
                    target_recode = current_t_menu_column_dict.get(create_column_id)
                    
                    # 「カラムクラス」が変更されている場合エラー判定
                    current_column_class_id = target_recode.get('COLUMN_CLASS')
                    current_column_class_name = column_class_dict.get(current_column_class_id)
                    if not column_class == current_column_class_name:
                        msg = "「編集」の際は既存項目の「カラムクラス」を変更できません。"
                        raise Exception(msg)
                    
                    # 「必須」が変更されている場合エラー判定
                    current_required_id = str(target_recode.get('REQUIRED'))
                    update_required_id = "1" if column_data.get('required') == "True" else "0"
                    if not current_required_id == update_required_id:
                        msg = "「編集」の際は既存項目の「必須」を変更できません。"
                        raise Exception(msg)
                    
                    # 「一意制約」が変更されている場合エラー判定
                    current_uniqued_id = str(target_recode.get('REQUIRED'))
                    update_uniqued_id = "1" if column_data.get('uniqued') == "True" else "0"
                    if not current_uniqued_id == update_uniqued_id:
                        msg = "「編集」の際は既存項目の「一意制約」を変更できません。"
                        raise Exception(msg)
                    
                    # カラムクラス「文字列(単一行)」の場合のバリデーションチェック
                    if column_class == "SingleTextColumn":
                        # 最大バイト数が既存の値よりも下回っている場合エラー判定
                        current_string_maximum_bytes = int(target_recode.get('SINGLE_MAX_LENGTH'))
                        update_string_maximum_bytes = int(column_data.get('single_maximum_bytes'))
                        if current_string_maximum_bytes > update_string_maximum_bytes:
                            msg = "「編集」の際は既存項目の「最大バイト数」が下回る変更はできません。"
                            raise Exception(msg)
                    
                    # カラムクラス「文字列(複数行)」の場合のバリデーションチェック
                    if column_class == "MultiTextColumn":
                        # 最大バイト数が既存の値よりも下回っている場合エラー判定
                        current_multi_string_maximum_bytes = int(target_recode.get('MULTI_MAX_LENGTH'))
                        update_multi_string_maximum_bytes = int(column_data.get('multi_string_maximum_bytes'))
                        if current_multi_string_maximum_bytes > update_multi_string_maximum_bytes:
                            msg = "「編集」の際は既存項目の「最大バイト数」が下回る変更はできません。"
                            raise Exception(msg)
                    
                    # カラムクラス「整数」の場合のバリデーションチェック
                    if column_class == "NumColumn":
                        current_integer_minimum_value = int(target_recode.get('NUM_MIN'))
                        update_integer_minimum_value = int(column_data.get('integer_minimum_value'))
                        # 最小値が既存の値よりも上回っている場合エラー判定
                        if current_integer_minimum_value < update_integer_minimum_value:
                            msg = "「編集」の際は既存項目の「最小値」が上回る変更はできません。"
                            raise Exception(msg)
                        
                        current_integer_maximum_value = int(target_recode.get('NUM_MAX'))
                        update_integer_maximum_value = int(column_data.get('integer_maximum_value'))
                        # 最大値が既存の値よりも下回っている場合エラー判定
                        if current_integer_maximum_value > update_integer_maximum_value:
                            msg = "「編集」の際は既存項目の「最大値」が下回る変更はできません。"
                            raise Exception(msg)
                    
                    # カラムクラス「小数」の場合のバリデーションチェック
                    if column_class == "FloatColumn":
                        current_decimal_minimum_value = int(target_recode.get('FLOAT_MIN'))
                        update_decimal_minimum_value = int(column_data.get('decimal_minimum_value'))
                        # 最小値が既存の値よりも上回っている場合エラー判定
                        if current_decimal_minimum_value < update_decimal_minimum_value:
                            msg = "「編集」の際は既存項目の「最小値」が上回る変更はできません。"
                            raise Exception(msg)
                        
                        current_decimal_maximum_value = int(target_recode.get('FLOAT_MAX'))
                        update_decimal_maximum_value = int(column_data.get('decimal_maximum_value'))
                        # 最大値が既存の値よりも下回っている場合エラー判定
                        if current_decimal_maximum_value > update_decimal_maximum_value:
                            msg = "「編集」の際は既存項目の「最大値」が下回る変更はできません。"
                            raise Exception(msg)
                        
                        current_decimal_digit = int(target_recode.get('FLOAT_DIGIT'))
                        update_decimal_digit = int(column_data.get('decimal_digit'))
                        # 桁数が既存の値よりも下回っている場合エラー判定
                        if current_decimal_digit > update_decimal_digit:
                            msg = "「編集」の際は既存項目の「桁数」が下回る変更はできません。"
                            raise Exception(msg)
                    
                    # カラムクラス「プルダウン選択」の場合のバリデーションチェック
                    # ####メモ：未実装
                    # if column_class == "IDColumn":
                        # ####メモ：選択項目および参照項目に差異がある場合はエラー判定。
                    
                    # カラムクラス「パスワード」の場合のバリデーションチェック
                    if column_class == "PasswordColumn":
                        # 最大バイト数が既存の値よりも下回っている場合エラー判定
                        current_password_maximum_bytes = int(target_recode.get('PASSWORD_MAX_LENGTH'))
                        update_password_maximum_bytes = int(column_data.get('password_maximum_bytes'))
                        if current_password_maximum_bytes > update_password_maximum_bytes:
                            msg = "「編集」の際は既存項目の「最大バイト数」が下回る変更はできません。"
                            raise Exception(msg)
                    
                    # カラムクラス「ファイルアップロード」の場合のバリデーションチェック
                    if column_class == "FileUploadColumn":
                        # 最大バイト数が既存の値よりも下回っている場合エラー判定
                        current_file_upload_maximum_bytes = int(target_recode.get('FILE_UPLOAD_MAX_SIZE'))
                        update_file_upload_maximum_bytes = int(column_data.get('file_upload_maximum_bytes'))
                        if current_file_upload_maximum_bytes > update_file_upload_maximum_bytes:
                            msg = "「編集」の際は既存項目の「最大バイト数」が下回る変更はできません。"
                            raise Exception(msg)
                    
                    # カラムクラス「リンク」の場合のバリデーションチェック
                    if column_class == "HostInsideLinkTextColumn":
                        # 最大バイト数が既存の値よりも下回っている場合エラー判定
                        current_link_maximum_bytes = int(target_recode.get('LINK_MAX_LENGTH'))
                        update_link_maximum_bytes = int(column_data.get('link_maximum_bytes'))
                        if current_link_maximum_bytes > update_link_maximum_bytes:
                            msg = "「編集」の際は既存項目の「最大バイト数」が下回る変更はできません。"
                            raise Exception(msg)
                    
                # 更新用パラメータを作成
                parameter = {
                    "item_name_ja": column_data.get('item_name'),  # 項目名(ja)
                    "item_name_en": column_data.get('item_name'),  # 項目名(en)
                    "item_name_rest": column_data.get('item_name_rest'),  # 項目名(rest)
                    "description_ja": column_data.get('description'),  # 説明(ja)
                    "description_en": column_data.get('description'),  # 説明(en)
                    "column_class": column_class,  # カラムクラス
                    "display_order": column_data.get('display_order'),  # 表示順序
                    "required": column_data.get('required'),  # 必須
                    "uniqued": column_data.get('uniqued'),  # 一意制約
                    "remarks": column_data.get('remarks'),  # 備考
                    "last_update_date_time": last_update_date_time  # 最終更新日時
                }
                
                # カラムグループがある場合
                column_group = column_data.get('column_group')
                if column_group:
                    parameter["column_group"] = column_group  # カラムグループ(「カラムグループ作成情報」のフルカラムグループ名)
                
                # 各カラムクラスに対応するparameterにNoneを挿入
                parameter["string_maximum_bytes"] = None  # 文字列(単一行) 最大バイト数
                parameter["string_regular_expression"] = None  # 文字列(単一行) 正規表現
                parameter["string_default_value"] = None  # 文字列(単一行) 初期値
                parameter["multi_string_maximum_bytes"] = None  # 文字列(複数行) 最大バイト数
                parameter["multi_string_regular_expression"] = None  # 文字列(複数行) 正規表現
                parameter["multi_string_default_value"] = None  # 文字列(複数行) 初期値
                parameter["integer_maximum_value"] = None  # 整数 最大値
                parameter["integer_minimum_value"] = None  # 整数 最小値
                parameter["integer_default_value"] = None  # 整数 初期値
                parameter["decimal_maximum_value"] = None  # 小数 最大値
                parameter["decimal_minimum_value"] = None  # 小数 最小値
                parameter["decimal_digit"] = None  # 小数 桁数
                parameter["decimal_default_value"] = None  # 小数 初期値
                parameter["detetime_default_value"] = None  # 日時 初期値
                parameter["dete_default_value"] = None  # 日付 初期値
                parameter["pulldown_selection"] = None  # プルダウン選択 メニューグループ:メニュー:項目
                parameter["pulldown_selection_default_value"] = None  # プルダウン選択 初期値
                parameter["reference_item"] = None  # プルダウン選択 参照項目
                parameter["password_maximum_bytes"] = None  # パスワード 最大バイト数
                parameter["file_upload_maximum_bytes"] = None  # ファイルアップロード 最大バイト数
                parameter["link_maximum_bytes"] = None  # リンク 最大バイト数
                parameter["link_default_value"] = None  # リンク 初期値
                
                # カラムクラス「文字列(単一行)」用のパラメータを追加
                if column_class == "SingleTextColumn":
                    parameter["string_maximum_bytes"] = column_data.get('single_maximum_bytes')  # 文字列(単一行) 最大バイト数
                    parameter["string_regular_expression"] = column_data.get('string_regular_expression')  # 文字列(単一行) 正規表現
                    parameter["string_default_value"] = column_data.get('single_default_value')  # 文字列(単一行) 初期値
                
                # カラムクラス「文字列(複数行)」用のパラメータを追加
                if column_class == "MultiTextColumn":
                    parameter["multi_string_maximum_bytes"] = column_data.get('multi_string_maximum_bytes')  # 文字列(複数行) 最大バイト数
                    parameter["multi_string_regular_expression"] = column_data.get('multi_string_regular_expression')  # 文字列(複数行) 正規表現
                    parameter["multi_string_default_value"] = column_data.get('multi_string_default_value')  # 文字列(複数行) 初期値
                
                # カラムクラス「整数」用のパラメータを追加
                if column_class == "NumColumn":
                    parameter["integer_maximum_value"] = column_data.get('integer_maximum_value')  # 整数 最大値
                    parameter["integer_minimum_value"] = column_data.get('integer_minimum_value')  # 整数 最小値
                    parameter["integer_default_value"] = column_data.get('integer_default_value')  # 整数 初期値
                
                # カラムクラス「小数」用のパラメータを追加
                if column_class == "FloatColumn":
                    parameter["decimal_maximum_value"] = column_data.get('decimal_maximum_value')  # 小数 最大値
                    parameter["decimal_minimum_value"] = column_data.get('decimal_minimum_value')  # 小数 最小値
                    parameter["decimal_digit"] = column_data.get('decimal_digit')  # 小数 桁数
                    parameter["decimal_default_value"] = column_data.get('decimal_default_value')  # 小数 初期値
                
                # カラムクラス「日時」用のパラメータを追加
                if column_class == "DateTimeColumn":
                    parameter["detetime_default_value"] = column_data.get('detetime_default_value')  # 日時 初期値
                
                # カラムクラス「日付」用のパラメータを追加
                if column_class == "DateColumn":
                    parameter["dete_default_value"] = column_data.get('dete_default_value')  # 日付 初期値
                
                # カラムクラス「プルダウン選択」用のパラメータを追加
                if column_class == "IDColumn":
                    parameter["pulldown_selection"] = column_data.get('pulldown_selection')  # プルダウン選択 メニューグループ:メニュー:項目
                    parameter["pulldown_selection_default_value"] = column_data.get('pulldown_selection_default_value')  # プルダウン選択 初期値
                    parameter["reference_item"] = column_data.get('reference_item')  # プルダウン選択 参照項目
                
                # カラムクラス「パスワード」用のパラメータを追加
                if column_class == "PasswordColumn":
                    parameter["password_maximum_bytes"] = column_data.get('password_maximum_bytes')  # パスワード 最大バイト数
                
                # カラムクラス「ファイルアップロード」用のパラメータを追加
                if column_class == "FileUploadColumn":
                    parameter["file_upload_maximum_bytes"] = column_data.get('file_upload_maximum_bytes')  # ファイルアップロード 最大バイト数
                
                # カラムクラス「リンク」用のパラメータを追加
                if column_class == "HostInsideLinkTextColumn":
                    parameter["link_maximum_bytes"] = column_data.get('link_maximum_bytes')  # リンク 最大バイト数
                    parameter["link_default_value"] = column_data.get('link_default_value')  # リンク 初期値
                
                # カラムクラス「パラメータシート参照」用のパラメータを追加 (未実装)
                # if column_class == "LinkIDColumn":
                #     parameter["parameter_sheet_reference"] = column_data.get('parameter_sheet_reference')  # パラメータシート参照
                
                parameters = {
                    "parameter": parameter,
                    "type": "Update"
                }
                
                # 更新を実行
                exec_result = objmenu.exec_maintenance(parameters, create_column_id)  # noqa: F405
                if not exec_result[0]:
                    print("「メニュー項目作成情報」にレコードを登録する際にエラーが起きた。")
                    raise Exception(exec_result[2])

    except Exception as msg:
        return False, msg
    
    return True, None


def _disuse_t_menu_column(objdbca, current_t_menu_column_list, column_data_list):
    """
        【内部呼び出し用】「メニュー項目作成情報」の不要なレコードを調査し廃止する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            current_t_menu_column_list: 「メニュー項目作成情報」の現在登録されているレコード（対象メニューのMENU_CREATE_IDと紐づいているもの）
            column_data_list: 登録対象のカラム情報一覧
        RETRUN:
            boolean, msg
    """
    try:
        # 現在登録されているレコードのIDをlist化
        current_target_create_column_id_list = []
        current_target_id_timestamp = {}
        for recode in current_t_menu_column_list:
            # IDをlistに格納
            create_column_id = recode.get('CREATE_COLUMN_ID')
            current_target_create_column_id_list.append(create_column_id)
            
            # IDと最終更新日時を紐づけたdictを作成
            last_update_timestamp = recode.get('LAST_UPDATE_TIMESTAMP')
            last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
            current_target_id_timestamp[create_column_id] = last_update_date_time
        
        # 更新対象のIDをlist化
        update_target_create_column_id_list = []
        for target_data in column_data_list.values():
            update_target_create_column_id_list.append(target_data.get('create_column_id'))
        
        # 差分を取得
        disuse_target_id_list = set(current_target_create_column_id_list) - set(update_target_create_column_id_list)
        if disuse_target_id_list:
            # loadTableの呼び出し
            objmenu = load_table.loadTable(objdbca, 'menu_item_creation_info')  # noqa: F405
            
            print(current_target_id_timestamp)
            # # 差分の対象のレコードを廃止
            for disuse_target_id in disuse_target_id_list:
                # 廃止用パラメータを作成
                last_update_date_time = current_target_id_timestamp.get(disuse_target_id)
                parameters = {
                    "parameter": {
                        "last_update_date_time": last_update_date_time
                    },
                    "type": "Discard"
                }
                
                # 廃止を実行
                exec_result = objmenu.exec_maintenance(parameters, disuse_target_id)  # noqa: F405
                if not exec_result[0]:
                    print("「カラムグループ作成情報」のレコードを廃止する際にエラーが起きた。")
                    raise Exception(exec_result[2])
        
    except Exception as msg:
        print(msg)
        return False, msg
    
    return True, None


def _insert_t_menu_unique_constraint(objdbca, menu_data):
    """
        【内部呼び出し用】「一意制約(複数項目)作成情報」にレコードを登録する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_data: 登録対象のメニュー情報
        RETRUN:
            boolean, msg
    """
    try:
        # menu_dataから登録用のメニュー名を取得
        menu_name = menu_data.get('menu_name')
        
        # 一意制約(複数項目)用データがある場合、「一意制約(複数項目)作成情報」にレコードを登録
        unique_constraint = menu_data.get('unique_constraint')
        if unique_constraint:
            unique_constraint_dump = json.dumps(unique_constraint)
            # loadTableの呼び出し
            objmenu = load_table.loadTable(objdbca, 'unique_constraint_creation_info')  # noqa: F405
            parameters = {
                "parameter": {
                    "menu_name": menu_name,
                    "unique_constraint_item": str(unique_constraint_dump)
                },
                "type": "Register"
            }
            
            # 登録を実行
            exec_result = objmenu.exec_maintenance(parameters)  # noqa: F405
            if not exec_result[0]:
                print("「一意制約(複数項目)」にレコードを登録する際にエラーが起きた。")
                raise Exception(exec_result[2])
            
        else:
            # データが無い場合、登録せずreturn
            return True, None
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _update_t_menu_unique_constraint(objdbca, menu_data, target_recode):
    """
        【内部呼び出し用】「一意制約(複数項目)作成情報」のレコードを更新する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_data: 登録対象のメニュー情報
            target_recode: 「一意制約(複数項目)作成情報」の更新対象のレコード情報
        RETRUN:
            boolean, msg
    """
    try:
        # 更新対象レコードからuuidと最終更新日時を取得
        unique_constraint_id = target_recode.get('UNIQUE_CONSTRAINT_ID')
        last_update_timestamp = target_recode.get('LAST_UPDATE_TIMESTAMP')
        last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
        
        unique_constraint = menu_data.get('unique_constraint')
        unique_constraint_dump = json.dumps(unique_constraint)
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'unique_constraint_creation_info')  # noqa: F405
        parameters = {
            "parameter": {
                "unique_constraint_item": str(unique_constraint_dump),
                "last_update_date_time": last_update_date_time
            },
            "type": "Update"
        }
        
        # 更新を実行
        exec_result = objmenu.exec_maintenance(parameters, unique_constraint_id)  # noqa: F405
        if not exec_result[0]:
            print("「一意制約(複数項目)」のレコードを更新する際にエラーが起きた。")
            raise Exception(exec_result[2])
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _disuse_t_menu_unique_constraint(objdbca, target_recode):
    """
        【内部呼び出し用】「一意制約(複数項目)作成情報」のレコードを廃止する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_data: 登録対象のメニュー情報
            target_recode: 「一意制約(複数項目)作成情報」の更新対象のレコード情報
        RETRUN:
            boolean, msg
    """
    try:
        # 廃止対象レコードからuuidと最終更新日時を取得
        unique_constraint_id = target_recode.get('UNIQUE_CONSTRAINT_ID')
        last_update_timestamp = target_recode.get('LAST_UPDATE_TIMESTAMP')
        last_update_date_time = last_update_timestamp.strftime('%Y/%m/%d %H:%M:%S.%f')
        
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'unique_constraint_creation_info')  # noqa: F405
        parameters = {
            "parameter": {
                "last_update_date_time": last_update_date_time
            },
            "type": "Discard"
        }
        
        # 廃止を実行
        exec_result = objmenu.exec_maintenance(parameters, unique_constraint_id)  # noqa: F405
        if not exec_result[0]:
            print("「一意制約(複数項目)」のレコードを廃止する際にエラーが起きた。")
            raise Exception(exec_result[2])
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _insert_t_menu_role(objdbca, menu_name, role_list):
    """
        【内部呼び出し用】「メニュー-ロール作成情報」にレコードを登録する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_name: 対象のメニュー名
            role_list: 対象のロール一覧(list)
        RETRUN:
            boolean, msg
    """
    try:
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'menu_role_creation_info')  # noqa: F405
        for role_name in role_list:
            parameters = {
                "parameter": {
                    "menu_name": menu_name,
                    "role_name": role_name
                },
                "type": "Register"
            }
            
            # 登録を実行
            exec_result = objmenu.exec_maintenance(parameters)  # noqa: F405
            if not exec_result[0]:
                print("「メニュー-ロール作成情報」にレコードを登録する際にエラーが起きた。")
                raise Exception(exec_result[2])
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _disuse_t_menu_role(objdbca, role_list, current_role_dict):
    """
        【内部呼び出し用】「メニュー-ロール作成情報」のレコードを廃止する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_name: 対象のメニュー名
            role_list: 廃止対象のロール一覧(list)
            current_role_dict: 廃止対象を指定するためのdict
        RETRUN:
            boolean, msg
    """
    try:
        # loadTableの呼び出し
        objmenu = load_table.loadTable(objdbca, 'menu_role_creation_info')  # noqa: F405
        for role_name in role_list:
            role_data = current_role_dict.get(role_name)
            menu_role_id = role_data.get('menu_role_id')
            last_update_date_time = role_data.get('last_update_date_time')
            parameters = {
                "parameter": {
                    "last_update_date_time": last_update_date_time
                },
                "type": "Discard"
            }
            
            # 廃止を実行
            exec_result = objmenu.exec_maintenance(parameters, menu_role_id)  # noqa: F405
            
            if not exec_result[0]:
                print("「メニュー-ロール作成情報」のレコードを廃止する際にエラーが起きた。")
                raise Exception(exec_result[2])
            
    except Exception as msg:
        return False, msg
    
    return True, None


def _insert_t_menu_create_history(objdbca, menu_create_id, status_id, create_type, user_id):
    """
        【内部呼び出し用】「メニュー作成履歴」にレコードを登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_create_id: 「メニュー定義一覧」の対象レコードのUUID
            status_id: 「メニュー作成履歴」のステータスID
            create_type: 「メニュー作成履歴」の作成タイプ
            user_id: ユーザID
        RETRUN:
            boolean, history_id, msg
    """
    # テーブル名
    t_menu_create_history = 'T_MENU_CREATE_HISTORY'
    
    try:
        data_list = {
            "MENU_CREATE_ID": menu_create_id,
            "STATUS_ID": status_id,
            "CREATE_TYPE": create_type,
            "MENU_MATERIAL": "",
            "DISUSE_FLAG": "0",
            "LAST_UPDATE_USER": user_id
        }
        primary_key_name = 'HISTORY_ID'
        ret = objdbca.table_insert(t_menu_create_history, data_list, primary_key_name)
        if not ret:
            raise Exception("「メニュー作成履歴」にレコードを登録する際にエラーが起きた。")
        
        history_id = ret[0].get('HISTORY_ID')
        
    except Exception as msg:
        return False, None, msg
    
    return True, history_id, None


def _check_before_registar_validate(objdbca, menu_data, column_data_list):
    """
        【内部呼び出し用】レコード登録前バリデーションチェックの実施
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu_data: 登録対象のメニュー情報
            column_data_list: 登録対象のカラム情報一覧
        RETRUN:
            boolean, history_id, msg
    """
    # テーブル/ビュー名
    v_menu_sheet_type = 'V_MENU_SHEET_TYPE'
    
    # 変数定義
    lang = g.get('LANGUAGE')
    sheet_id = None
    
    try:
        # シートタイプのIDを取得
        sheet_type_name = menu_data.get('sheet_type')
        
        # シートタイプ一覧情報を取得
        ret = objdbca.table_select(v_menu_sheet_type, 'WHERE DISUSE_FLAG = %s', [0])
        for recode in ret:
            check_sheet_type_name = recode.get('SHEET_TYPE_NAME_' + lang.upper())
            if sheet_type_name == check_sheet_type_name:
                sheet_id = str(recode.get('SHEET_TYPE_NAME_ID'))
        
        # シートタイプが「2: データシート」かつ、登録する項目が無い場合エラー判定
        if sheet_id == "2" and not column_data_list:
            raise Exception("シートタイプ「データシート」では項目0件のメニューを作成できません。")
        
    except Exception as msg:
        return False, msg
    
    return True, None
