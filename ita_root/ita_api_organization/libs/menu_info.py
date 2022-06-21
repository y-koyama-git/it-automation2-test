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


def collect_menu_info(objdbca, menu, lang):
    """
    関数の説明
    """
    try:
        # テーブル名
        t_common_menu = 'T_COMN_MENU'
        t_common_menu_table_link = 'T_COMN_MENU_TABLE_LINK'
        t_common_menu_column_link = 'T_COMN_MENU_COLUMN_LINK'
        t_common_column_class = 'T_COMN_COLUMN_CLASS'
        t_common_column_group = 'T_COMN_COLUMN_GROUP'
        
        # メッセージクラス呼び出し
        objmsg = MessageTemplate('ja')  # noqa: F405
        msg = ''
        
        # ####メモ：ユーザが対象のメニューの情報を取得可能かどうかのロールチェック処理が必要
        role_check = True
        if not role_check:
            # ####メモ：401を意図的に返したいので最終的に自作Exceptionクラスに渡す。引数のルールは別途決める必要あり。
            raise Exception(msg, 'statusCode')
        
        # 『メニュー管理』テーブルから対象のデータを取得
        ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu, 0])
        if not ret:
            msg = objmsg.get_message('MENU_API_ERR_0000001010')  # 『メニュー管理』に対象のメニューが存在しません
            return 'statusCode', {}, msg
        
        menu_id = ret[0].get('MENU_ID')  # 対象メニューを特定するためのUUID
        menu_name = ret[0].get('MENU_NAME_' + lang.upper())
        login_necessity = ret[0].get('LOGIN_NECESSITY')
        auto_filter_flg = ret[0].get('AUTOFILTER_FLG')
        initial_filter_flg = ret[0].get('INITIAL_FILTER_FLG')
        web_print_limit = ret[0].get('WEB_PRINT_LIMIT')
        web_print_confirm = ret[0].get('WEB_PRINT_CONFIRM')
        xls_print_limit = ret[0].get('XLS_PRINT_LIMIT')
        sort_key = ret[0].get('SORT_KEY')
        
        # 『メニュー-テーブル紐付管理』テーブルから対象のデータを取得
        ret = objdbca.table_select(t_common_menu_table_link, 'WHERE MENU_ID = %s AND DISUSE_FLAG = %s', [menu_id, 0])
        if not ret:
            msg = objmsg.get_message('MENU_API_ERR_0000001020')  # 『メニュー-テーブル紐付管理』に対象のメニューが存在しません
            return 'statusCode', {}, msg
        
        menu_info = ret[0].get('MENU_INFO_' + lang.upper())
        sheet_type = ret[0].get('SHEET_TYPE')
        table_name = ret[0].get('TABLE_NAME')
        view_name = ret[0].get('VIEW_NAME')
        inherit = ret[0].get('INHERIT')
        vertical = ret[0].get('VERTICAL')
        
        menu_info_data = {
            'menu_info': menu_info,
            'menu_name': menu_name,
            'sheet_type': sheet_type,
            'table_name': table_name,
            'view_name': view_name,
            'inherit': inherit,
            'vertical': vertical,
            'login_necessity': login_necessity,
            'auto_filter_flg': auto_filter_flg,
            'initial_filter_flg': initial_filter_flg,
            'web_print_limit': web_print_limit,
            'web_print_confirm': web_print_confirm,
            'xls_print_limit': xls_print_limit,
            'sort_key': sort_key
        }
        
        # 『カラムクラスマスタ』テーブルからcolumn_typeの一覧を取得
        ret = objdbca.table_select(t_common_column_class, 'WHERE DISUSE_FLAG = %s', [0])
        if not ret:
            # msg = objmsg.get_message('MENU_API_ERR_0000001030')  # 『カラムクラスマスタ』にデータが存在しません
            msg = "『カラムクラスマスタ』にデータが存在しません"
            return 'statusCode', {}, msg
        
        column_class_master = {}
        for recode in ret:
            column_class_master[recode.get('COLUMN_CLASS_ID')] = recode.get('COLUMN_CLASS_NAME')
        
        # 『カラムグループ管理』テーブルからカラムグループ一覧を取得
        ret = objdbca.table_select(t_common_column_group, 'WHERE DISUSE_FLAG = %s', [0])
        column_group_list = {}
        if ret:
            for recode in ret:
                print(recode)
                col_group_name = 'COL_GROUP_NAME_' + lang.upper()
                column_group_list[recode.get('COL_GROUP_ID')] = recode.get(col_group_name)
            
        # 『メニュー-カラム紐付管理』テーブルから対象のデータを取得
        ret = objdbca.table_select(t_common_menu_column_link, 'WHERE MENU_ID = %s AND DISUSE_FLAG = %s', [menu_id, 0])
        if not ret:
            msg = objmsg.get_message('MENU_API_ERR_0000001030')  # 『メニュー-カラム紐付管理』に対象のメニューが存在しません
            return 'statusCode', {}, msg
        
        # ####メモ：〇〇マスタとかに紐づくもの（例えばcolumn_type）は、とりあえずIDを入れている。最終的にはマスタから参照した文字列を挿入予定。
        column_info_data = {}
        for recode in ret:
            # json形式のレコードは改行を削除
            validate_option = recode.get('VALIDATE_OPTION')
            if type(validate_option) is str:
                validate_option = validate_option.replace('\n', '')
                
            before_validate_register = recode.get('BEFORE_VALIDATE_REGISTER')
            if type(before_validate_register) is str:
                before_validate_register = before_validate_register.replace('\n', '')
                
            after_validate_register = recode.get('AFTER_VALIDATE_REGISTER')
            if type(after_validate_register) is str:
                after_validate_register = after_validate_register.replace('\n', '')
            
            # カラムグループIDがあればカラムグループ名を取得
            column_group_id = recode.get('COL_GROUP_ID')
            column_group_name = ''
            if column_group_id:
                column_group_name = column_group_list.get(column_group_id)
            
            detail = {
                'column_id': recode.get('COLUMN_DEFINITION_ID'),
                'column_name': recode.get('COLUMN_NAME_' + lang.upper()),
                'column_name_rest': recode.get('COLUMN_NAME_REST'),
                'column_group_id': column_group_id,
                'column_group_name': column_group_name,
                'column_type': column_class_master[recode.get('COLUMN_CLASS')],
                'column_disp_seq': recode.get('COLUMN_DISP_SEQ'),
                'description': recode.get('DESCRIPTION_' + lang.upper()),
                'ref_table_name': recode.get('REF_TABLE_NAME'),
                'ref_pkey_name': recode.get('REF_PKEY_NAME'),
                'ref_col_name': recode.get('REF_COL_NAME'),
                'ref_sort_conditions': recode.get('REF_SORT_CONDITIONS'),
                'ref_multi_lang': recode.get('REF_MULTI_LANG'),
                'col_name': recode.get('COL_NAME'),
                'save_type': recode.get('SAVE_TYPE'),
                'auto_input': recode.get('AUTO_INPUT'),
                'input_item': recode.get('INPUT_ITEM'),
                'view_item': recode.get('VIEW_ITEM'),
                'unique_item': recode.get('UNIQUE_ITEM'),
                'required_item': recode.get('REQUIRED_ITEM'),
                'initial_value': recode.get('INITIAL_VALUE'),
                'validate_option': validate_option,
                'before_validate_register': before_validate_register,
                'after_validate_register': after_validate_register,
                'filter_type': {},  # 未実装
                'pulldown_info': {}  # 未実装
            }
            
            column_info_data[recode.get('COLUMN_NAME_REST')] = detail

        result_data = {
            'MENU_INFO': menu_info_data,
            'COLUMN_INFO': column_info_data
        }
        return 'statusCode', result_data, msg
    
    except Exception:
        raise


def collect_menu_column_info(objdbca, menu, lang):
    """
    関数の説明
    """
    try:
        # 変数定義
        t_common_menu = 'T_COMN_MENU'
        t_common_menu_column_link = 'T_COMN_MENU_COLUMN_LINK'
        
        # メッセージクラス呼び出し
        objmsg = MessageTemplate('ja')  # noqa: F405
        msg = ''
        
        # ####メモ：ユーザが対象のメニューの情報を取得可能かどうかのロールチェック処理が必要
        role_check = True
        if not role_check:
            # ####メモ：401を意図的に返したいので最終的に自作Exceptionクラスに渡す。引数のルールは別途決める必要あり。
            raise Exception(msg, 'statusCode')
        
        # 『メニュー管理』テーブルから対象のデータを取得
        ret = objdbca.table_select(t_common_menu, 'WHERE MENU_NAME_REST = %s AND DISUSE_FLAG = %s', [menu, 0])
        if not ret:
            msg = objmsg.get_message('MENU_API_ERR_0000001010')  # 『メニュー管理』に対象のメニューが存在しません
            return 'statusCode', {}, msg
        
        menu_id = ret[0].get('MENU_ID')  # 対象メニューを特定するためのUUID
        
        # 『メニュー-カラム紐付管理』テーブルから対象のデータを取得
        ret = objdbca.table_select(t_common_menu_column_link, 'WHERE MENU_ID = %s order by COLUMN_DISP_SEQ ASC', [menu_id])
        if not ret:
            msg = objmsg.get_message('MENU_API_ERR_0000001030')  # 『メニュー-カラム紐付管理』に対象のメニューが存在しません
            return 'statusCode', {}, msg
        
        column_list = []
        for recode in ret:
            column_list.append(recode.get('COLUMN_NAME_REST'))
        
        result_data = column_list
        return 'statusCode', result_data, msg
    
    except Exception:
        raise
