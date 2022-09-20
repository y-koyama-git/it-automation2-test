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


from common_libs.conductor.classes.util import ConductorCommonLibs  # noqa: F401
from common_libs.conductor.classes.exec_util import *  # noqa: F403

import uuid  # noqa: F401


def conductor_maintenance(objdbca, menu, conductor_data, target_uuid=''):
    """
        Conductorの登録/更新
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            conductor_data:Conductor設定  {}
            target_uuid: 対象レコードID UUID
        RETRUN:
            data
    """
    msg = ''

    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    try:
        # conductor_data load_table用パラメータ加工
        conductor_class_id = conductor_data.get('conductor').get('id')
        conductor_name = conductor_data.get('conductor').get('conductor_name')
        last_update_date_time = conductor_data.get('conductor').get('last_update_date_time')
        note = conductor_data.get('conductor').get('note')
        if target_uuid == '':
            conductor_class_id = str(uuid.uuid4())
            if 'conductor' in conductor_data:
                conductor_data['conductor']['id'] = conductor_class_id
                conductor_data['conductor']['last_update_date_time'] = None
            
            tmp_parameter = {}
            tmp_parameter.setdefault('conductor_class_id', conductor_class_id)
            tmp_parameter.setdefault('conductor_name', conductor_name)
            tmp_parameter.setdefault('setting', conductor_data)
            tmp_parameter.setdefault('remarks', note)

            parameter = {}
            parameter.setdefault('file', {})
            parameter.setdefault('parameter', tmp_parameter)
            parameter.setdefault('type', 'Register')
            target_uuid = conductor_class_id
        else:
            if 'conductor' in conductor_data:
                conductor_data['conductor']['id'] = target_uuid
                conductor_data['conductor']['last_update_date_time'] = None
            tmp_parameter = {}
            tmp_parameter.setdefault('conductor_class_id', target_uuid)
            tmp_parameter.setdefault('conductor_name', conductor_name)
            tmp_parameter.setdefault('setting', conductor_data)
            tmp_parameter.setdefault('remarks', note)
            tmp_parameter.setdefault('last_update_date_time', last_update_date_time)

            parameter = {}
            parameter.setdefault('file', {})
            parameter.setdefault('parameter', tmp_parameter)
            parameter.setdefault('type', 'Update')

    except Exception:
        # 499-00801
        status_code = "499-00801"
        log_msg_args = []
        api_msg_args = []
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    try:
        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list,movement_list)
        cc_menu = 'conductor_class_edit'
        m_menu = 'movement_list'
        objmovement = load_table.loadTable(objdbca, m_menu)  # noqa: F405
        objcclass = load_table.loadTable(objdbca, cc_menu)  # noqa: F405

        if (objmovement.get_objtable() is False or
                objcclass.get_objtable() is False):
            raise Exception()
        
        objmenus = {
            "objmovement": objmovement,
            "objcclass": objcclass
        }
    except Exception:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    try:
        objCexec = ConductorExecuteLibs(objdbca, menu, objmenus)  # noqa: F405
        # トランザクション開始
        objdbca.db_transaction_start()

        # conductor classテーブルへのレコード追加
        tmp_result = objCexec.conductor_class_exec_maintenance(parameter, target_uuid)
        if tmp_result[0] is not True:
            # 集約エラーメッセージ(JSON化)
            status_code, msg = objcclass.get_error_message_str()
            msg = objCexec.maintenance_error_message_format(msg)
            raise Exception()

        objdbca.db_transaction_end(True)

    except Exception:
        # ロールバック トランザクション終了
        objdbca.db_transaction_end(False)
        # status_code = '499-00201'
        log_msg_args = [msg]
        api_msg_args = [msg]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    result = {
        "conductor_class_id": conductor_class_id
    }

    return result


def get_conductor_data(objdbca, menu, conductor_class_id):
    """
        Conductorクラスの取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            conductor_class_id:ConductorクラスID string
        RETRUN:
            data
    """

    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    try:
        mode = "nomal"
        filter_parameter = {"conductor_class_id": {"LIST": [conductor_class_id]}}
        status_code, tmp_result, msg = objmenu.rest_filter(filter_parameter, mode)

        if len(tmp_result) == 1:
            tmp_data = tmp_result[0].get('parameter')
            tmp_conductor_class_id = tmp_data.get('conductor_class_id')
            tmp_remarks = tmp_data.get('remarks')
            tmp_last_update_date_time = tmp_data.get('last_update_date_time')

            result = tmp_data.get('setting')
            result['conductor']['id'] = tmp_conductor_class_id
            result['conductor']['note'] = tmp_remarks
            result['conductor']['last_update_date_time'] = tmp_last_update_date_time

        elif len(tmp_result) == 0:
            raise Exception()

    except Exception:
        status_code = "499-00802"
        log_msg_args = [conductor_class_id]
        api_msg_args = [conductor_class_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def get_conductor_data_execute(objdbca, menu, conductor_class_id):
    """
        Conductorクラスの取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            conductor_class_id:ConductorクラスID string
        RETRUN:
            data
    """

    menu = 'conductor_class_edit'
    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    try:
        mode = "nomal"
        filter_parameter = {"conductor_class_id": {"LIST": [conductor_class_id]}}
        status_code, tmp_result, msg = objmenu.rest_filter(filter_parameter, mode)

        if len(tmp_result) == 1:
            tmp_data = tmp_result[0].get('parameter')
            tmp_conductor_class_id = tmp_data.get('conductor_class_id')
            tmp_remarks = tmp_data.get('remarks')
            tmp_last_update_date_time = tmp_data.get('last_update_date_time')

            result = tmp_data.get('setting')
            result['conductor']['id'] = tmp_conductor_class_id
            result['conductor']['note'] = tmp_remarks
            result['conductor']['last_update_date_time'] = tmp_last_update_date_time

        elif len(tmp_result) == 0:
            raise Exception()

    except Exception:
        status_code = "499-00802"
        log_msg_args = [conductor_class_id]
        api_msg_args = [conductor_class_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def get_conductor_execute_class_info(objdbca, menu):
    """
        Conductor基本情報
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
        RETRUN:
            statusCode, {}, msg
    """

    menu = 'conductor_class_edit'
    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    
    try:
        result = get_conductor_class_info_data(objdbca)
    except Exception:
        status_code = "499-00803"
        log_msg_args = []
        api_msg_args = []
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def get_conductor_class_info(objdbca, menu):
    """
        Conductor基本情報
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
        RETRUN:
            statusCode, {}, msg
    """

    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    
    try:
        result = get_conductor_class_info_data(objdbca)
    except Exception:
        status_code = "499-00803"
        log_msg_args = []
        api_msg_args = []
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def get_conductor_class_info_data(objdbca, mode=""):
    """
        Conductor基本情報の取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
        RETRUN:
            statusCode, {}, msg
    """
    try:
        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list,movement_list)
        c_menu = 'conductor_instance_list'
        cc_menu = 'conductor_class_edit'
        n_menu = 'conductor_node_instance_list'
        m_menu = 'movement_list'
        objconductor = load_table.loadTable(objdbca, c_menu)  # noqa: F405
        objnode = load_table.loadTable(objdbca, n_menu)  # noqa: F405
        objmovement = load_table.loadTable(objdbca, m_menu)  # noqa: F405
        objcclass = load_table.loadTable(objdbca, cc_menu)  # noqa: F405

        if (objconductor.get_objtable() is False or
                objnode.get_objtable() is False or
                objmovement.get_objtable() is False or
                objcclass.get_objtable() is False):
            raise Exception()

        objmenus = {
            "objconductor": objconductor,
            "objnode": objnode,
            "objmovement": objmovement,
            "objcclass": objcclass
        }

        objCexec = ConductorExecuteLibs(objdbca, '', objmenus)  # noqa: F405
        result = objCexec.get_class_info_data(mode)
    
    except Exception:
        status_code = "499-00803"
        log_msg_args = []
        api_msg_args = []
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def conductor_execute(objdbca, menu, parameter):
    """
        Conductor実行
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            parameter:パラメータ  {}
        RETRUN:
            data
    """

    # 実行準備:loadtable読込
    try:
        conductor_class_name = parameter.get('conductor_class_name')
        operation_name = parameter.get('operation_name')
        schedule_date = parameter.get('schedule_date')

        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list,movement_list)
        c_menu = 'conductor_instance_list'
        cc_menu = 'conductor_class_edit'
        n_menu = 'conductor_node_instance_list'
        m_menu = 'movement_list'
        objconductor = load_table.loadTable(objdbca, c_menu)  # noqa: F405
        objnode = load_table.loadTable(objdbca, n_menu)  # noqa: F405
        objmovement = load_table.loadTable(objdbca, m_menu)  # noqa: F405
        objcclass = load_table.loadTable(objdbca, cc_menu)  # noqa: F405

        if (objconductor.get_objtable() is False or
                objnode.get_objtable() is False or
                objmovement.get_objtable() is False or
                objcclass.get_objtable() is False):
            raise Exception()
        
        objmenus = {
            "objconductor": objconductor,
            "objnode": objnode,
            "objmovement": objmovement,
            "objcclass": objcclass
        }
    except Exception:
        status_code = "499-00804"
        log_msg_args = [conductor_class_name, operation_name, schedule_date]
        api_msg_args = [conductor_class_name, operation_name, schedule_date]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    # 実行:パラメータチェック
    try:
        # 入力パラメータ フォーマットチェック
        objCexec = ConductorExecuteLibs(objdbca, menu, objmenus)  # noqa: F405
        chk_parameter = objCexec.chk_execute_parameter_format(parameter)
        if chk_parameter[0] is not True:
            status_code = '499-00814'
            log_msg_args = chk_parameter[1]
            api_msg_args = chk_parameter[1]
            raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    except Exception as e:
        raise AppException(e)  # noqa: F405

    parameter = chk_parameter[2]

    # 実行:パラメータ生成
    try:
        # Conductor実行　パラメータ生成
        create_parameter = objCexec.create_execute_register_parameter(parameter)
        if create_parameter[0] != '000-00000':
            raise Exception()
    except Exception:
        status_code = "499-00804"
        log_msg_args = [conductor_class_name, operation_name, schedule_date]
        api_msg_args = [conductor_class_name, operation_name, schedule_date]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    
    # 実行:Instance登録 maintenance
    try:
        # conducror_instance_id発番、load_table用パラメータ
        conductor_parameter = create_parameter[1].get('conductor')
        node_parameters = create_parameter[1].get('node')
        conductor_instance_id = create_parameter[1].get('conductor_instance_id')
        
        status_code = "000-00000"
        
        # トランザクション開始
        objdbca.db_transaction_start()

        # 対象メニューのテーブルと「ロック対象テーブル」を昇順でロック
        locktable_list = [objconductor.get_table_name(), objnode.get_table_name()]
        if locktable_list is not None:
            tmp_result = objdbca.table_lock(locktable_list)
        else:
            tmp_result = objdbca.table_lock([objconductor.get_table_name(), objnode.get_table_name()])  # noqa: F841

        # conductor instanceテーブルへのレコード追加
        iem_result = objCexec.conductor_instance_exec_maintenance(conductor_parameter)
        if iem_result[0] is not True:
            raise Exception()
        # node instanceテーブルへのレコード追加
        iem_result = objCexec.node_instance_exec_maintenance(node_parameters)
        if iem_result[0] is not True:
            raise Exception()

        objdbca.db_transaction_end(True)

    except Exception:
        # ロールバック トランザクション終了
        objdbca.db_transaction_end(False)
        status_code = "499-00804"
        log_msg_args = [conductor_class_name, operation_name, schedule_date]
        api_msg_args = [conductor_class_name, operation_name, schedule_date]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
        
    result = {
        "conductor_instance_id": conductor_instance_id
    }

    return result


def get_conductor_info(objdbca, menu, conductor_instance_id):
    """
        Conductor基本情報の取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
        RETRUN:
            statusCode, {}, msg
    """

    objmenu = load_table.loadTable(objdbca, menu)  # noqa: F405
    if objmenu.get_objtable() is False:
        status_code = "401-00003"
        log_msg_args = [menu]
        api_msg_args = [menu]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    
    try:
        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list,movement_list)
        c_menu = 'conductor_instance_list'
        cc_menu = 'conductor_class_edit'
        n_menu = 'conductor_node_instance_list'
        m_menu = 'movement_list'
        objconductor = load_table.loadTable(objdbca, c_menu)  # noqa: F405
        objnode = load_table.loadTable(objdbca, n_menu)  # noqa: F405
        objmovement = load_table.loadTable(objdbca, m_menu)  # noqa: F405
        objcclass = load_table.loadTable(objdbca, cc_menu)  # noqa: F405

        if (objconductor.get_objtable() is False or
                objnode.get_objtable() is False or
                objmovement.get_objtable() is False or
                objcclass.get_objtable() is False):
            raise Exception()

        objmenus = {
            "objconductor": objconductor,
            "objnode": objnode,
            "objmovement": objmovement,
            "objcclass": objcclass
        }

        objCexec = ConductorExecuteLibs(objdbca, '', objmenus)  # noqa: F405
        result = objCexec.get_instance_info_data(conductor_instance_id)

    except Exception:
        status_code = "499-00805"
        log_msg_args = [conductor_instance_id]
        api_msg_args = [conductor_instance_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def get_conductor_instance_data(objdbca, menu, conductor_instance_id):
    """
        Conductorクラスの取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            conductor_class_id:ConductorクラスID string
        RETRUN:
            data
    """

    try:
        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list,movement_list)
        c_menu = 'conductor_instance_list'
        cc_menu = 'conductor_class_edit'
        n_menu = 'conductor_node_instance_list'
        m_menu = 'movement_list'
        objconductor = load_table.loadTable(objdbca, c_menu)  # noqa: F405
        objnode = load_table.loadTable(objdbca, n_menu)  # noqa: F405
        objmovement = load_table.loadTable(objdbca, m_menu)  # noqa: F405
        objcclass = load_table.loadTable(objdbca, cc_menu)  # noqa: F405

        if (objconductor.get_objtable() is False or
                objnode.get_objtable() is False or
                objmovement.get_objtable() is False or
                objcclass.get_objtable() is False):
            raise Exception()

        objmenus = {
            "objconductor": objconductor,
            "objnode": objnode,
            "objmovement": objmovement,
            "objcclass": objcclass
        }

        objCexec = ConductorExecuteLibs(objdbca, '', objmenus)  # noqa: F405
        result = objCexec.get_instance_data(conductor_instance_id)
    
    except Exception:
        status_code = "499-00806"
        log_msg_args = [conductor_instance_id]
        api_msg_args = [conductor_instance_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result


def conductor_execute_action(objdbca, menu, mode='', conductor_instance_id='', node_instance_id=''):
    """
        Conductor作業に対する個別処理(cancel,scram,relese)
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            mode: 処理種別 cancel,scram,relese
            conductor_instance_id:
        RETRUN:
            data
    """
    msg = ''

    try:
        if mode == '' or mode is None:
            raise Exception()

        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list)
        c_menu = 'conductor_instance_list'
        n_menu = 'conductor_node_instance_list'
        objconductor = load_table.loadTable(objdbca, c_menu)  # noqa: F405
        objnode = load_table.loadTable(objdbca, n_menu)  # noqa: F405

        if (objconductor.get_objtable() is False or
                objnode.get_objtable() is False):
            raise Exception()
        
        objmenus = {
            "objconductor": objconductor,
            "objnode": objnode
        }
        objCexec = ConductorExecuteLibs(objdbca, '', objmenus, 'Update', conductor_instance_id)  # noqa: F405
    except Exception:
        status_code = "499-00807"
        log_msg_args = [mode, conductor_instance_id, node_instance_id]
        api_msg_args = [mode, conductor_instance_id, node_instance_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405
    
    try:
        status_code = "000-00000"
        msg_args = []
        # トランザクション開始
        objdbca.db_transaction_start()

        # 対象メニューのテーブルと「ロック対象テーブル」を昇順でロック
        locktable_list = objconductor.get_locktable()
        if locktable_list is not None:
            tmp_result = objdbca.table_lock([locktable_list])
        else:
            tmp_result = objdbca.table_lock([objconductor.get_table_name(), objnode.get_table_name()])  # noqa: F841

        # conductor instanceテーブルへのレコード追加
        action_result = objCexec.execute_action(mode, conductor_instance_id, node_instance_id)
        if action_result[0] is not True:
            status_code = action_result[1]
            msg_args = action_result[2]
            raise Exception()

        objdbca.db_transaction_end(True)
        
        if mode == 'cancel':
            msg_code = 'MSG-40001'
        elif mode == 'scram':
            msg_code = 'MSG-40002'
        elif mode == 'relese':
            msg_code = 'MSG-40003'
        msg = g.appmsg.get_api_message(msg_code, [conductor_instance_id, node_instance_id])

    except Exception:
        # ロールバック トランザクション終了
        objdbca.db_transaction_end(False)
        log_msg_args = msg_args
        api_msg_args = msg_args
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    result = msg

    return result


def create_movement_zip(objdbca, menu, data_type, conductor_instance_id):
    """
        Conductorで実行したMovementのファイルをZIP、base64出力
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            data_type: input/result
            conductor_instance_id:
        RETRUN:
            data
    """
    result = {}

    try:
        if data_type == '' or data_type is None:
            raise Exception()
        if conductor_instance_id == '' or conductor_instance_id is None:
            raise Exception()
        
        # 対象メニューのload_table生成(conductor_instance_list,conductor_node_instance_list,movement_list)
        c_menu = 'conductor_instance_list'
        n_menu = 'conductor_node_instance_list'
        objconductor = load_table.loadTable(objdbca, c_menu)  # noqa: F405
        objnode = load_table.loadTable(objdbca, n_menu)  # noqa: F405

        if (objconductor.get_objtable() is False or
                objnode.get_objtable() is False):
            raise Exception()

        objmenus = {
            "objconductor": objconductor,
            "objnode": objnode,
        }
        ###
        from random import randint
        if randint(1, 3) == 2:
            raise Exception()
        ### dummy data
        if data_type == 'input':
            result = {
                "file_data": "UEsDBBQAAAAIAEQ6LlUosGx6YwYAADwNAAAPAAAASW5wdXREYXRhXzEuemlwC/BmZuFiAAEHF81QBiQgwCDDkJyRmZMSX5CTWJmUn59drB8awsnA/LxaKhmESyu4GRhZQErBRADQJBEgzQE2aYXjdpUJQN4HINbHYpIBDBjr5iZmp8YXlySWlBbHp2XmpOpV5ubgs8i1by9fswFPS7nKvYdHDh25ossfrL1oWa8Lk9cde8b3cTGLyzafL7+/0/nTRFkubt5903cdyi/bxXBzubeg/vdHF3S4/SL23xLZmOsbezW03GGeJcfhPbNknR9NaDP41PjKuPpmb76e2pm4PDfVrsvNyuqKzBOeffFLsX11/fK8+cbT71b+OR5ed7Yg4/xazVvch//NNz/BHoAzCPmBHi9JzQX6uiQV7DXCIYjdIG5QCOYXVFJkCC/QkNKCnPzEFIqM4QIak5FfXBJfllhESoqozS5b+pCRgcGYlYFBDMWMzJJE3eJEYDClGhjiM29r0Pn8WwYi+76vT7i0brbs7UImW8NOz6kac1m+ZFUmKER1KN++oPi2//73OdteLW33uqJxrPL974/3insy/+576XeRNVlt8YPaXYbOa7Yb2v3csPTHi9M3590y+VVufOiXVazO+7oz6c8Kd81bn9f9/ujbkm0iS89Fam6ZkhzpoZg9Jyvy1MZloRmtEtdV326a9EmykyfAidtFa493LBOniYRTWLMG57QfE5dM4apm3HDocOrKhY1zrin9P9wXfeNKi0ogR6YEs9umhFWOUw47LzSaelkrfOlDPw/WhV1/MuUFDgT4p75L5ome+LlFdd+JRQqLhbJYHnKlH81d5/hU8QLDAYdYUxXuBV5Wh3vclha5p05bnthgHBKVzHf+e9EHw9JvL17EzUrZ71r9Jvo495PC2PqytfW3zH6azfydncw1Lzd3k9qOa3E+PnY39iZv6z77/trM3IxzehuuvX377NCuEz9Or5phrzptf0/s5V0cfyssv7Hfj7W7m/F499tM5tZ+i72T4pa68ure350Q/Nj6EbeexWNW4ZojP1uKg33k6mYerbJj37SdsdhXz8W5zPrG7rriXrbZfXsD67NT11kcKtdJknv9fNsU3XuGe+vK9fPc68vcr6tm3CyROrTXtz078p69zbl36d1TI9ctW/310p89s8/n/WPGneh4gAkmviCxKDE3tSSViGSH3RRJNFOQEx6ZRgqiGgnOWWQaJYfNKJKciMhszCo21hbAzLaCiYGBFZrZivFpLw047XfYQGDPZ9HuI1NPfbs1293f9RXjykdBD6JmCk30Wrjy0RRh+fNruitk3pw4V2W72Xh3ocQt7UW19RJxy9+tMAy0X/YzV+r88pKd8Ub24osOy+QH19jzzt24P3JRhU/79IW3l155P+XSJFPu2yE3uNOXNNgsz8vKlDq+k8Hi6JSoRa/7K+TSfv1p/rU/L4z/9u/dZ6u+76m6ZaP39pBe+Ou13EEpG4SftelarxO8KrNDMDbMpsitaV6MYb3yR6Ypwu0+rdbeDEIZBjLhqYqinD9C2m4+3qLxYCMvu2Psns4df9pZhRVjtYNaA2IS2AymMl2e3sqzp6LkgfHR9O9M009904hb6W+rz5Gw5fuE37kJR5+WH9W6L9oaINBXytEQ1rG38+bq88xXHi7k+nN9wkYH1t5Eh+Nvip8rer9SOKhZHpK8Lh412OMmvL9XBeTNgSZZWH1HqEoz7d4IqtJcyvcdSvKPXhldd8zo4AQO9nALHo6P72csNL+7dzf3hKuzXBUm8iU8XtVbaH5P6ctzzo5FxZHyDRzXr/7OWDbN1m/KvMer+tj8oiwPHbxWmZPS7WrOwHhqVor8Xp+dJzrsFyYHxL75+/O1tJZuz7UVb9uCBetkQ3dJoyZHyU/3e5mBbBAWBbrfMa84Mykn1bUiNdm/oCQzP0+vpKIEn0d0yxQCvBmZ5JhxtSkk4Kz/jiAas4XBCjEcI3mDTMXVvoCYCkzvDEsavbCYSrC1gc9SXHU7slecgXZj1PSkG8qNYmgP0FCUWp90A3lRDLwINBCtBUC6kVwoRkoACxjk1gBxsYfaFkCOvRgU81BbBqS7lQfFrb1A9aiVCOkmSqKYeBnNRLTSmnTjBVGMV2NlwFa5kG6sHIqxhdiMJcHpuKoZ5Hg8ycoAq3SIMwq16EQ2yoGdAa0gJS4AUAszZBOBVuIq2nAZzcoGovmA8ApQJIgDxAMAUEsBAhQDFAAAAAgARDouVSiwbHpjBgAAPA0AAA8AAAAAAAAAAAAAAKSBAAAAAElucHV0RGF0YV8xLnppcFBLBQYAAAAAAQABAD0AAACQBgAAAAA=",
                "file_name": "InputData_Conductor_{}.zip".format(conductor_instance_id)
            }
            return result
        elif data_type == 'result':
            result = {
                "file_data": "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",
                "file_name": "ResultData_Conductor_{}.zip".format(conductor_instance_id)
            }
            return result

        objCexec = ConductorExecuteBkyLibs(objdbca)  # noqa: F405

        tmp_result = objCexec.is_conductor_instance_id(conductor_instance_id)
        if tmp_result is False:
            raise Exception()

        tmp_result = objCexec.create_movement_zip(conductor_instance_id, data_type)
        result = tmp_result[1]
    except Exception:
        status_code = "499-00815"
        log_msg_args = [conductor_instance_id]
        api_msg_args = [conductor_instance_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    if len(result) == 0:
        status_code = "499-00815"
        log_msg_args = [conductor_instance_id]
        api_msg_args = [conductor_instance_id]
        raise AppException(status_code, log_msg_args, api_msg_args)  # noqa: F405

    return result
