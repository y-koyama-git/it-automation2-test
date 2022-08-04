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
        # t_common_menu = 'T_COMN_MENU'
        t_common_menu_group = 'T_COMN_MENU_GROUP'
        t_common_column_class = 'T_COMN_COLUMN_CLASS'
        t_common_sheet_type = 'T_COMN_SHEET_TYPE'
        v_common_operation_privileges = 'T_COMN_OPERATION_PRIVILEGES'
        v_common_menu_group_menu_pulldown = 'V_COMN_MENU_GROUP_MENU_PULLDOWN'
        
        # 「メニュー定義一覧」から対象データを取得
        ret = objdbca.table_select(t_menu_define, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [create_menu_name_rest, 0])
        if not ret:
            print("「メニュー定義一覧」に指定した名前のレコードが無い。")
            return
        
        menu_create_id = ret[0].get('MENU_CREATE_ID')
        menu_name_ja = ret[0].get('MENU_NAME_JA')
        menu_name_en = ret[0].get('MENU_NAME_EN')
        menu_name_rest = ret[0].get('MENU_NAME_REST')
        sheet_type = ret[0].get('SHEET_TYPE')
        display_order = ret[0].get('DISP_SEQ')
        menu_group_input = ret[0].get('MENU_GROUP_ID_INPUT')
        menu_group_subst = ret[0].get('MENU_GROUP_ID_SUBST')
        menu_group_view = ret[0].get('MENU_GROUP_ID_VIEW')
        create_table_name = 'T_CMDB_{}'.format(menu_create_id)
        
        # 「メニュー項目作成情報」から対象のデータを取得
        ret = objdbca.table_select(t_menu_column, 'WHERE MENU_CREATE_ID = %s AND DISUSE_FLAG = %s', [menu_create_id, 0])
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
            file = file.replace('★★★UUID★★★', menu_create_id)
            
            sql_list = file.split(";\n")
            for sql in sql_list:
                if re.fullmatch(r'[\s\n\r]*', sql) is None:
                    objdbca.sql_execute(sql)
        
        # ####メモ：「入力用」「代入値自動登録用」「参照用」のそれぞれ3つメニューが作成されるので、以下を3回ループする。
        target_menu_group_list = []
        if sheet_type == "1":
            print("シートタイプは：パラメータシート(ホスト/オペレーションあり)")
            target_menu_group_list = ['input', 'substitution', 'reference']
        elif sheet_type == "2":
            print("シートタイプは：データシート")
            target_menu_group_list = ['input']
        else:
            print("シートタイプが不正")
            return
        
        # 「シートタイプマスタ(T_COMN_SHEET_TYPE)」より、シートタイプの名称を参照するためのレコード取得
        sheet_type_list = {}
        ret = objdbca.table_select(t_common_sheet_type, 'WHERE DISUSE_FLAG = %s', [0])
        for recode in ret:
            sheet_type_list[recode.get('SHEET_TYPE_NAME_ID')] = recode.get('SHEET_TYPE_NAME_' + g.LANGUAGE.upper())
        print(sheet_type_list)
        
        # 「カラムクラスマスタ(T_COMN_COLUMN_CLASS)」より、カラムクラスの名称を参照するためのレコード取得
        column_class_list = {}
        ret = objdbca.table_select(t_common_column_class, 'WHERE DISUSE_FLAG = %s', [0])
        for recode in ret:
            column_class_list[recode.get('COLUMN_CLASS_ID')] = recode.get('COLUMN_CLASS_NAME')
        print("カラムクラスリストは：")
        print(column_class_list)
        
        # ここから対象メニューグループごとにループスタート
        for target_menu_group in target_menu_group_list:
            print("------------対象メニューグループ毎の作業スタート------------")
            print(target_menu_group)
            
            # メニュー名称(rest)は対象メニューグループ毎に名称を変える必要がある。
            tmp_maneu_name_rest = menu_name_rest
            target_menu_group_id = ""
            if target_menu_group == "input":
                tmp_maneu_name_rest = tmp_maneu_name_rest + '_input'
                target_menu_group_id = menu_group_input
            elif target_menu_group == "substitution":
                tmp_maneu_name_rest = tmp_maneu_name_rest + '_sub'
                target_menu_group_id = menu_group_subst
            elif target_menu_group == "reference":
                tmp_maneu_name_rest = tmp_maneu_name_rest + '_ref'
                target_menu_group_id = menu_group_view
            print("対象のメニュー名称(rest)は：")
            print(tmp_maneu_name_rest)
            
            ret = objdbca.table_select(t_common_menu_group, 'WHERE MENU_GROUP_ID = %s AND DISUSE_FLAG = %s', [target_menu_group_id, 0])
            if not ret:
                print("対象のメニューグループ名がないのでなんかおかしい")
                return
            menu_group_name = ret[0].get('MENU_GROUP_NAME_' + g.LANGUAGE.upper())
            print("メニューグループ名は：")
            print(menu_group_name)
            
            # 2. 「メニュー管理(T_COMN_MENU)」にレコードを登録する
            print("メニュー管理の処理スタート")
            target_menu = 'menu_list'
            objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
            parameters = {
                'parameter': {
                    'menu_group_name': menu_group_name,
                    'menu_name_ja': menu_name_ja,
                    'menu_name_en': menu_name_en,
                    'menu_name_rest': tmp_maneu_name_rest,
                    'login_necessity': 'True',
                    'display_order': display_order,
                    'autofilter_flg': 'False',
                    'initial_filter_flg': 'False'
                },
                'type': 'Register'
            }
            
            target_uuid = ""
            status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
            print(status_code)
            print(result)
            print(msg)
            
            # 「メニューグループ-メニュープルダウン(V_COMN_MENU_GROUP_MENU_PULLDOWN)」にから「メニューグループ名:メニュー名」の値を取得
            ret = objdbca.table_select(v_common_menu_group_menu_pulldown, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [tmp_maneu_name_rest, 0])
            if not ret:
                print("対象のメニューグループ名:メニュー名がないのでなんかおかしい")
                return
            print(ret[0])
            menugroup_menu_name = ret[0].get('MENU_GROUP_NAME_PULLDOWN_' + g.LANGUAGE.upper())
            print("メニューグループ名:メニュー名は：")
            print(menugroup_menu_name)
            
            # 3. 「ロール-メニュー紐付管理(T_COMN_ROLE_MENU_LINK)」にレコードを登録する
            print("ロールメニュー紐付け管理の処理スタート")
            target_menu = 'role_menu_link_list'
            
            ret = objdbca.table_select(v_common_operation_privileges, 'WHERE DISUSE_FLAG = %s', [0])
            for recode in ret:
                if recode.get('PRIVILEGES_ID') == "1":
                    associate = recode.get('PRIVILEGES_NAME_' + g.LANGUAGE.upper())
            
            objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
            parameters = {
                'parameter': {
                    'menu_name': menugroup_menu_name,
                    'role_name': role_id,
                    'associate': associate
                },
                'type': 'Register'
            }
            target_uuid = ""
            status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
            print(status_code)
            print(result)
            print(msg)
            
            # 4. 「メニュー-テーブル紐付管理(T_COMN_MENU_TABLE_LINK)」にレコードを登録する
            print("メニューテーブル紐付管理の処理スタート")
            target_menu = 'menu_table_link_list'
            sheet_type_name = sheet_type_list.get(sheet_type)
            substitution_value_link_flag = "False"
            if target_menu_group == "substitution":
                substitution_value_link_flag = "True"
            objmenu = load_table.loadTable(objdbca, target_menu)  # noqa: F405
            parameters = {
                'parameter': {
                    'menu_name': menugroup_menu_name,
                    'table_name': create_table_name,
                    # 'view_name': '',
                    # 'description_ja': '',
                    # 'description_en': '',
                    'sheet_type': sheet_type_name,
                    'history_table_flag': "True",
                    'inheritance_flag': "False",
                    'vertical_flag': "False",
                    'row_insert_flag': "True",
                    'row_update_flag': "True",
                    'row_disuse_flag': "True",
                    'row_reuse_flag': "True",
                    'substitution_value_link_flag': substitution_value_link_flag
                },
                'type': 'Register'
            }
            target_uuid = ""
            status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
            print(status_code)
            print(result)
            print(msg)
        
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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 10
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'ROW_ID'
            db_storage_format = None
            automatic_input_flag = "True"
            input_target_flag = "False"
            output_target_flag = "True"
            required_input_flag = "True"
            unique_constraints_flag = "True"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = None
            description_en = None
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 20
            id_link_table = 'T_DUMMY_HOST_LIST'
            id_link_key_column_name = 'HOST_ID'
            id_link_column_name = 'HOST_NAME'
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'HOST_ID'
            db_storage_format = None
            automatic_input_flag = "False"
            input_target_flag = "True"
            output_target_flag = "True"
            required_input_flag = "True"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = None
            description_en = None
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 30
            id_link_table = 'T_COMN_OPERATION'
            id_link_key_column_name = 'OPERATION_ID'
            id_link_column_name = 'OPERATION_NAME'
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'OPERATION_ID'
            db_storage_format = None
            automatic_input_flag = "False"
            input_target_flag = "True"
            output_target_flag = "True"
            required_input_flag = "True"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = None
            description_en = None
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 40
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'INPUT_ORDER'
            db_storage_format = None
            automatic_input_flag = "False"
            input_target_flag = "True"
            output_target_flag = "True"
            required_input_flag = "False"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = None
            description_en = None
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
                column_class_name = column_class_list.get(str(column_class_id))
                display_order = int(display_order) + 10
                id_link_table = None
                id_link_key_column_name = None
                id_link_column_name = None
                id_link_sort_condition = None
                id_link_multilingual_support = "False"
                sensitive_coloumn_name = None
                column_name = 'DATA_JSON'
                db_storage_format = 'JSON'
                automatic_input_flag = "False"
                input_target_flag = "True"
                output_target_flag = "True"
                required_input_flag = "False"
                unique_constraints_flag = "False"
                auto_reg_hide_item = "False"
                auto_reg_only_item = "False"
                initial_value = None
                validation_value = None  # 未対応
                before_individual_validation = None
                after_individual_validation = None
                description_ja = recode.get('DESCRIPTION_JA')
                description_en = recode.get('DESCRIPTION_EN')
                parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 80
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'NOTE'
            db_storage_format = None
            automatic_input_flag = "False"
            input_target_flag = "True"
            output_target_flag = "True"
            required_input_flag = "False"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = '自由記述欄。レコードの廃止・復活時にも記載可能。'
            description_en = 'Comments section. Can comment when removing or res...'
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 90
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'DISUSE_FLAG'
            db_storage_format = None
            automatic_input_flag = "True"
            input_target_flag = "False"
            output_target_flag = "False"
            required_input_flag = "True"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = '廃止フラグ。復活以外のオペレーションは不可'
            description_en = 'Discard flag. Cannot do operation other than resto...'
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 100
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'LAST_UPDATE_TIMESTAMP'
            db_storage_format = None
            automatic_input_flag = "True"
            input_target_flag = "False"
            output_target_flag = "True"
            required_input_flag = "True"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = 'レコードの最終更新日。自動登録のため編集不可。'
            description_en = 'Last update date of record. Cannot edit because of...'
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501

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
            column_class_name = column_class_list.get(str(column_class_id))
            display_order = 110
            id_link_table = None
            id_link_key_column_name = None
            id_link_column_name = None
            id_link_sort_condition = None
            id_link_multilingual_support = "False"
            sensitive_coloumn_name = None
            column_name = 'LAST_UPDATE_USER'
            db_storage_format = None
            automatic_input_flag = "True"
            input_target_flag = "False"
            output_target_flag = "True"
            required_input_flag = "True"
            unique_constraints_flag = "False"
            auto_reg_hide_item = "False"
            auto_reg_only_item = "False"
            initial_value = None
            validation_value = None
            before_individual_validation = None
            after_individual_validation = None
            description_ja = '更新者。ログインユーザのIDが自動的に登録される。編集不可。'
            description_en = 'Updated by. Login user ID is automatically registe...'
            parameters = get_column_link_param(menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name, column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name, id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name, db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag, unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value, before_individual_validation, after_individual_validation, description_ja, description_en) # noqa: E501
            
            target_uuid = ""
            status_code, result, msg = objmenu.rest_maintenance(parameters, target_uuid)
            print(status_code)
            print(result)
            print(msg)


def get_column_link_param(
        menugroup_menu_name, column_name_ja, column_name_en, column_name_rest, column_class_group_name,
        column_class_name, display_order, id_link_table, id_link_key_column_name, id_link_column_name,
        id_link_sort_condition, id_link_multilingual_support, sensitive_coloumn_name, column_name,
        db_storage_format, automatic_input_flag, input_target_flag, output_target_flag, required_input_flag,
        unique_constraints_flag, auto_reg_hide_item, auto_reg_only_item, initial_value, validation_value,
        before_individual_validation, after_individual_validation, description_ja, description_en):
    
    print("カラムクラス名は：")
    print(column_class_name)
    parameters = {
        'parameter': {
            'menu_name': menugroup_menu_name,
            'column_name_ja': column_name_ja,
            'column_name_en': column_name_en,
            'column_name_rest': column_name_rest,
            'column_class_group_name': column_class_group_name,
            'column_class': column_class_name,
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
            'after_individual_validation': after_individual_validation,
            'description_ja': description_ja,
            'description_en': description_en,
        },
        'type': 'Register'
    }
    
    return parameters


if __name__ == '__main__':
    main()
