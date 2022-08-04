# 開発用に手っ取り早くパラメータシートを作成するためのpythonファイル。
# 「メニュー定義一覧」と「メニュー紐付管理」にレコードが登録されていること前提で動く。
import sys
import re
import base64
# import pprint
from flask import Flask, g

# sys.path.append("/exastro/")
from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.loadtable import *  # noqa: F403
# from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate


def main():
    flask_app = Flask(__name__)
    with flask_app.app_context():
        args = sys.argv
        g.ORGANIZATION_ID = args[1]
        g.WORKSPACE_ID = args[2]
        g.LANGUAGE = 'ja'
        # roles_org = args[3]
        # roles_decode = base64.b64decode(roles_org.encode()).decode("utf-8")
        # roles = roles_decode.split("\n")
        # g.ROLES = roles
        role_id = args[3]
        create_menu_name_rest = args[4]
        
        # g.applogger = AppLog()
        g.appmsg = MessageTemplate()
        
        # DB接続
        objdbca = DBConnectWs(g.WORKSPACE_ID)  # noqa: F405
        
        # 変数定義
        t_menu_define = 'T_MENU_DEFINE'
        t_menu_column = 'T_MENU_COLUMN'
        t_common_menu = 'T_COMN_MENU'
        
        # 「メニュー定義一覧」から対象データを取得
        ret = objdbca.table_select(t_menu_define, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [create_menu_name_rest, 0])
        if not ret:
            print("「メニュー定義一覧」に指定した名前のレコードが無い。")
            return
        
        create_menu_id = ret[0].get('CREATE_MENU_ID')
        menu_name_ja = ret[0].get('MENU_NAME_JA')
        menu_name_en = ret[0].get('MENU_NAME_EN')
        menu_name_rest = ret[0].get('MENU_NAME_REST')
        sheet_type = ret[0].get('SHEET_TYPE')
        display_order = ret[0].get('DISP_SEQ')
        menu_group_input = ret[0].get('MENU_GROUP_ID_INPUT')
        # menu_group_subst = ret[0].get('MENU_GROUP_ID_SUBST')
        # menu_group_view = ret[0].get('MENU_GROUP_ID_VIEW')
        create_table_name = 'T_CMDB_{}'.format(create_menu_id)
        
        # 「メニュー項目作成情報」から対象のデータを取得
        ret = objdbca.table_select(t_menu_column, 'WHERE CREATE_MENU_ID = %s AND DISUSE_FLAG = %s', [create_menu_id, 0])
        if not ret:
            print("「メニュー項目作成情報」に対象のメニューのレコードが無い。")
            return
        
        create_column_list = ret
        
        # ####ここからメイン処理####
        # ####メモ：これ以降の処理について、（テーブル作成は違うかもだけど）トランザクションで、途中で登録が何かしら失敗したら全部無しにしたい。
        # ####loadTableを使っての複数レコード登録時、トランザクションをどうするか確認したい。
        # 1. パラメータシート用のテーブルを作成する
        with open("./create_cmdb.sql", "r") as f:
            file = f.read()
            file = file.replace('★★★UUID★★★', create_menu_id)
            
            sql_list = file.split(";\n")
            for sql in sql_list:
                if re.fullmatch(r'[\s\n\r]*', sql) is None:
                    objdbca.sql_execute(sql)
        
        # ####メモ：「入力用」「代入値自動登録用」「参照用」のそれぞれ3つメニューが作成されるので、以下を3回ループする。
        
        # 2. 「メニュー管理(T_COMN_MENU)」にレコードを登録する
        target_menu = 'menu_list'
        objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
        parameters = {
            'parameter': {
                'menu_group_name': menu_group_input,
                'menu_name_ja': menu_name_ja,
                'menu_name_en': menu_name_en,
                'menu_name_rest': menu_name_rest,
                'login_necessity': 1,
                'display_order': display_order,
                'autofilter_flg': 0,
                'initial_filter_flg': 0
            },
            'type': 'Register'
        }
        print(parameters)
        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # 「メニュー管理(T_COMN_MENU)」に登録されたレコードのUUIDを取得
        ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu_name_rest, 0])
        menu_id = ret[0].get('MENU_ID')
        
        # 3. 「ロール-メニュー紐付管理(T_COMN_ROLE_MENU_LINK)」にレコードを登録する
        target_menu = 'role_menu_link_list'
        objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
        parameters = {
            'parameter': {
                'menu_name': menu_id,
                'role_name': role_id,
                'associate': 1
            },
            'type': 'Register'
        }
        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        
        # 4. 「メニュー-テーブル紐付管理(T_COMN_MENU_TABLE_LINK)」にレコードを登録する
        target_menu = 'menu_table_link_list'
        objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
        parameters = {
            'parameter': {
                'menu_name': menu_id,
                'table_name': create_table_name,
                'view_name': '',
                'discription_ja': '',
                'discription_en': '',
                'sheet_type': sheet_type,
                'history_table_flag': 1,
                'inheritance_flag': 0,
                'vertical_flag': 0,
                'row_insert_flag': 1,
                'row_update_flag': 1,
                'row_disuse_flag': 1,
                'row_reuse_flag': 1,
                'substitution_value_link_flag': 0
            },
            'type': 'Register'
        }
        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        
        # 5. 「メニュー-カラム紐付管理(T_COMN_COLUMN_LINK)」にレコードを登録する
        # ####メモ：メンテナンスオール使いたいが、とりあえず単発ずつ入れる。
        # メニュー作成で作った項目だけでなく、ROW_IDやHOST_IDやDISUSE_FLAGなどのも作る必要あり。
        target_menu = 'menu_column_link_list'
        objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
        
        # 項番用のレコードを作成
        column_name_ja = '項番'
        column_name_en = 'uuid'
        column_name_rest = 'uuid'
        column_class_group_name = None
        column_class_id = 1  # TextColumn
        display_order = 10
        id_link_table = None
        id_link_key_column_name = None
        id_link_column_name = None
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'ROW_ID'
        db_storage_format = None
        automatic_input_flag = 1
        input_target_flag = 0
        output_target_flag = 1
        required_input_flag = 1
        unique_constraints_flag = 1
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = None
        description_en = None
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # ホスト名用のレコードを作成
        column_name_ja = 'ホスト名'
        column_name_en = 'Host name'
        column_name_rest = 'host_name'
        column_class_group_name = None
        column_class_id = 7  # IDColumn
        display_order = 20
        id_link_table = 'T_DUMMY_HOST_LIST'
        id_link_key_column_name = 'HOST_ID'
        id_link_column_name = 'HOST_NAME'
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'HOST_ID'
        db_storage_format = None
        automatic_input_flag = 0
        input_target_flag = 1
        output_target_flag = 1
        required_input_flag = 1
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = None
        description_en = None
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # オペレーション名用のレコードを作成
        column_name_ja = 'オペレーション名'
        column_name_en = 'Operation name'
        column_name_rest = 'operation_name'
        column_class_group_name = None
        column_class_id = 7  # IDColumn
        display_order = 30
        id_link_table = 'T_COMN_OPERATION'
        id_link_key_column_name = 'OPERATION_ID'
        id_link_column_name = 'OPERATION_NAME'
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'OPERATION_ID'
        db_storage_format = None
        automatic_input_flag = 0
        input_target_flag = 1
        output_target_flag = 1
        required_input_flag = 1
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = None
        description_en = None
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # 代入順序用のレコードを作成
        column_name_ja = '代入順序'
        column_name_en = 'Input order'
        column_name_rest = 'input_order'
        column_class_group_name = None
        column_class_id = 3  # NumColumn
        display_order = 40
        id_link_table = None
        id_link_key_column_name = None
        id_link_column_name = None
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'INPUT_ORDER'
        db_storage_format = None
        automatic_input_flag = 0
        input_target_flag = 1
        output_target_flag = 1
        required_input_flag = 0
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = None
        description_en = None
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # 作成した項目用のレコードを作成
        display_order = 40
        for recode in create_column_list:
            column_name_ja = recode.get('COLUMN_NAME_JA')
            column_name_en = recode.get('COLUMN_NAME_EN')
            column_name_rest = recode.get('COLUMN_NAME_REST')
            column_class_group_name = None
            column_class_id = recode.get('COLUMN_CLASS')
            display_order = int(display_order) + 10
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = 0
            sensitive_coloumn_name = None
            column_name = 'DATA_JSON'
            db_storage_format = 'JSON'
            automatic_input_flag = 0
            input_target_flag = 1
            output_target_flag = 1
            required_input_flag = 0
            unique_constraints_flag = 0
            auto_reg_hide_item = 0
            auto_reg_only_item = 0
            initial_value = None
            validation_value = None  # 未対応
            before_individual_validation = None
            after_individual_validation = None
            description_ja = recode.get('DESCRIPTION_JA')
            description_en = recode.get('DESCRIPTION_EN')
            parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

            target_uuid = ""
            status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
            print(status_code)
            print(result)
            print(msg)
        
        # 備考用のレコードを作成
        column_name_ja = '備考'
        column_name_en = 'Remarks'
        column_name_rest = 'remarks'
        column_class_group_name = None
        column_class_id = 12
        display_order = 80
        id_link_table = None
        id_link_key_column_name = None
        id_link_column_name = None
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'NOTE'
        db_storage_format = None
        automatic_input_flag = 0
        input_target_flag = 1
        output_target_flag = 1
        required_input_flag = 0
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = '自由記述欄。レコードの廃止・復活時にも記載可能。'
        description_en = 'Comments section. Can comment when removing or res...'
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # 廃止フラグ用のレコードを作成
        column_name_ja = '廃止フラグ'
        column_name_en = 'Discard'
        column_name_rest = 'discard'
        column_class_group_name = None
        column_class_id = 1
        display_order = 90
        id_link_table = None
        id_link_key_column_name = None
        id_link_column_name = None
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'DISUSE_FLAG'
        db_storage_format = None
        automatic_input_flag = 1
        input_target_flag = 0
        output_target_flag = 0
        required_input_flag = 1
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = '廃止フラグ。復活以外のオペレーションは不可'
        description_en = 'Discard flag. Cannot do operation other than resto...'
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # 最終更新日時用のレコードを作成
        column_name_ja = '最終更新日時'
        column_name_en = 'Last update date/time'
        column_name_rest = 'last_update_date_time'
        column_class_group_name = None
        column_class_id = 13
        display_order = 100
        id_link_table = None
        id_link_key_column_name = None
        id_link_column_name = None
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'LAST_UPDATE_TIMESTAMP'
        db_storage_format = None
        automatic_input_flag = 1
        input_target_flag = 0
        output_target_flag = 1
        required_input_flag = 1
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = 'レコードの最終更新日。自動登録のため編集不可。'
        description_en = 'Last update date of record. Cannot edit because of...'
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)
        
        # 最終更新者用のレコードを作成
        column_name_ja = '最終更新者'
        column_name_en = 'Last updated by'
        column_name_rest = 'last_updated_user'
        column_class_group_name = None
        column_class_id = 14
        display_order = 110
        id_link_table = None
        id_link_key_column_name = None
        id_link_column_name = None
        id_link_sort_condition = None
        id_link_multilingual_support = 0
        sensitive_coloumn_name = None
        column_name = 'LAST_UPDATE_USER'
        db_storage_format = None
        automatic_input_flag = 1
        input_target_flag = 0
        output_target_flag = 1
        required_input_flag = 1
        unique_constraints_flag = 0
        auto_reg_hide_item = 0
        auto_reg_only_item = 0
        initial_value = None
        validation_value = None
        before_individual_validation = None
        after_individual_validation = None
        description_ja = '更新者。ログインユーザのIDが自動的に登録される。編集不可。'
        description_en = 'Updated by. Login user ID is automatically registe...'
        parameters = get_column_link_param(menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501
        
        target_uuid = ""
        status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
        print(status_code)
        print(result)
        print(msg)


def get_column_link_param(
        menu_id, column_name_ja, column_name_en, column_name_rest, column_class_group_name,
        column_class_id, display_order, id_link_table, id_link_key_column_name, id_link_column_name,
        id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name,
        db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag,
        unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value,
        before_individual_validation, after_individual_validation, description_ja, description_en):
    
    print("ユニーク値は：")
    print(unique_constraints_flag)
    print("必須値は：")
    print(required_input_flag)
    parameters = {
        'parameter': {
            'menu_name': menu_id,
            'column_name_ja': column_name_ja,
            'column_name_en': column_name_en,
            'column_name_rest': column_name_rest,
            'column_class_group_name': column_class_group_name,
            'column_class': column_class_id,
            'display_order': display_order,
            'id_link_table': id_link_table,
            'id_link_key_column_name': id_link_key_column_name,
            'id_link_column_name': id_link_column_name,
            'id_link_sort_condition': id_link_sort_condition,
            'id_link_multilingual_support': id_link_multilingual_support,
            'sensitive_coloumn_name': sensitive_coloumn_name,
            'column_name': column_name,
            'db_storage_format': db_storage_format,
            'automatic_input_flag': automatic_input_flag,
            'input_target_flag': input_target_flag,
            'output_target_flag': output_target_flag,
            'required_input_flag': required_input_flag,
            'unique_constraints_flag': unique_constraints_flag,
            'auto_reg_hide_item': auto_reg_hide_item,
            'auto_reg_only_item': auto_reg_only_item,
            'initial_value': initial_value,
            'validation_value': validation_value,
            'before_individual_validation': before_individual_validation,
            'After_individual_validation': after_individual_validation,
            'description_ja': description_ja,
            'description_en': description_en,
        },
        'type': 'Register'
    }
    
    return parameters


if __name__ == '__main__':
    main()
