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
import re
import os
import datetime
from common_libs.common.exception import AppException
from common_libs.ansible_driver.classes.AnscConstClass import AnscConst
from common_libs.ansible_driver.functions.util import *
from common_libs.ansible_driver.functions.rest_libs import insert_execution_list, execution_scram

def movement_registr_check(objdbca, parameter, Required=False):
    """
        リクエストボディのMovement_id確認
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            parameter: bodyの中身
            Required: リクエストボディのMovement_idが必須か
                      True:必須　False:任意
        RETRUN:
            movement情報
    """
    keyName = "movement_name"
    if keyName in parameter:
        movement_name = parameter[keyName]
    else:
        movement_name = None
    if Required is True:
        if not movement_name:
            # リクエストボディにパラメータなし
            raise AppException("499-00908", [keyName], [keyName])
    if movement_name:
        # Movement情報取得
        sql = "SELECT * FROM T_COMN_MOVEMENT WHERE MOVEMENT_NAME = %s AND DISUSE_FLAG='0'"
        row = objdbca.sql_execute(sql, [movement_name])
        if len(row) != 1:
            # Movement未登録
            raise AppException("499-00901", [movement_name], [movement_name])
        return row[0]


def operation_registr_check(objdbca, parameter, Required=False):
    """
        リクエストボディのoperation_id確認
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            parameter: bodyの中身
            Required: リクエストボディのoperation_idが必須か
                      True:必須　False:任意
        RETRUN:
            オペレーション情報
    """
    keyName = "operation_name"
    if keyName in parameter:
        operation_name = parameter[keyName]
    else:
        operation_name = None
    if Required is True:
        if not operation_name:
            # リクエストボディにパラメータなし
            raise AppException("499-00908", [keyName], [keyName])
    if operation_name:
        # オペレーション情報取得
        sql = "SELECT * FROM T_COMN_OPERATION WHERE OPERATION_NAME = %s AND DISUSE_FLAG='0'"
        row = objdbca.sql_execute(sql, [operation_name])
        if len(row) != 1:
            # オペレーション未登録
            raise AppException("499-00902", [operation_name], [operation_name])
        return row[0]


def scheduled_format_check(parameter, useed=False):
    keyName = "schedule_date"
    if keyName in parameter:
        schedule_date = parameter[keyName]
        schedule_date += ":00"
    else:
        schedule_date = None

    if schedule_date:
        if useed is False:
            # 予約日時は不要
            raise AppException("499-00907", [], [])
        else:
            result = True
            # 予約時間のフォーマット確認
            match = re.findall("^[0-9]{4}/[0-9]{2}/[0-9]{2}[\s][0-9]{2}:[0-9]{2}:[0-9]{2}$", schedule_date)
            if len(match) == 0:
                result = False
            else:
                try:
                    # 予約時間を確認
                    schedule_date = datetime.datetime.strptime(schedule_date, '%Y/%m/%d %H:%M:%S')
                except Exception:
                    result = False
            if result is False:
                # 予約日時不正
                raise AppException("499-00906", [], [])
        return schedule_date

def get_execution_info(objdbca, execution_no):
    """
        作業実行の状態取得
        ARGS:
            execution_no: 作業実行No
        RETRUN:
            data
    """
    
    # 該当の作業実行取得
    where = "WHERE EXECUTION_NO = " + execution_no
    data_list = objdbca.table_select("T_ANSR_EXEC_STS_INST", where)
    
    # 該当する作業実行が存在しない
    if len(data_list) is None or len(data_list) == 0:
        log_msg_args = [execution_no]
        api_msg_args = [execution_no]
        raise AppException("499-00903", log_msg_args, api_msg_args)

    execution_info = {}
    for row in data_list:
        # 実行種別取得
        where = "WHERE ID = " + row['RUN_MODE']
        tmp_data_list = objdbca.table_select("T_ANSC_EXEC_ENGINE", where)
        for tmp_row in tmp_data_list:
            execution_type = tmp_row['NAME']

        # ステータス取得
        where = "WHERE EXEC_STATUS_ID = " + row['STATUS_ID']
        tmp_data_list = objdbca.table_select("T_ANSC_EXEC_STATUS", where)
        for tmp_row in tmp_data_list:
            if g.LANGUAGE == 'ja':
                status = tmp_row['EXEC_STATUS_NAME_JA']
            else:
                status = tmp_row['EXEC_STATUS_NAME_EN']

        # 実行エンジン取得
        where = "WHERE EXEC_MODE_ID  = " + row['EXEC_MODE']
        tmp_data_list = objdbca.table_select("T_ANSC_EXEC_MODE", where)
        for tmp_row in tmp_data_list:
            if g.LANGUAGE == 'ja':
                execution_engine = tmp_row['EXEC_MODE_NAME_JA']
            else:
                execution_engine = tmp_row['EXEC_MODE_NAME_EN']

        # ホスト指定形式
        where = "WHERE HOST_DESIGNATE_TYPE_ID  = " + row['I_ANS_HOST_DESIGNATE_TYPE_ID']
        tmp_data_list = objdbca.table_select("T_COMN_HOST_DESIGNATE_TYPE", where)
        for tmp_row in tmp_data_list:
            if g.LANGUAGE == 'ja':
                host_specify_format = tmp_row['HOST_DESIGNATE_TYPE_NAME_JA']
            else:
                host_specify_format = tmp_row['HOST_DESIGNATE_TYPE_NAME_EN']

        # WinRM接続取得
        where = "WHERE FLAG_ID  = " + row['I_ANS_WINRM_ID']
        tmp_data_list = objdbca.table_select("T_COMN_BOOLEAN_FLAG", where)
        for tmp_row in tmp_data_list:
            win_rm_connect = tmp_row['FLAG_NAME']

        # 投入・結果データエンコード
        file_name = 'InputData_' + execution_no.zfill(10) + '.zip'
        input_data = getLegayRoleExecutPopulatedDataUploadDirPath()
        with open(input_data + '/' + file_name, "rb") as f:
            bytes = f.read()
            encord_input_data = base64.b64encode(bytes)
        file_name = 'ResultData_' + execution_no.zfill(10) + '.zip'
        result_data = getLegayRoleExecutResultDataUploadDirPath()
        with open(result_data + '/' + file_name, "rb") as f:
            bytes = f.read()
            encord_result_data = base64.b64encode(bytes)

        execution_info['target_execution'] = {'execution_no': execution_no,
                                            'execution_type': execution_type,
                                            'status': status,
                                            'execution_engine': execution_engine,
                                            'conductor_caller': row['CONDUCTOR_NAME'],
                                            'execution_user': row['EXECUTION_USER'],
                                            'movement': {},
                                            'operation': {},
                                            'input_data': str(encord_input_data),
                                            'result_data': str(encord_result_data),
                                            'execution_situation': {}}
        execution_info['target_execution']['movement'] = {'id': row['MOVEMENT_ID'],
                                                        'name': row['I_MOVEMENT_NAME'],
                                                        'delay_time': row['I_TIME_LIMIT'],
                                                        'ansible_use_infomation': {},
                                                        'ansible_core_use_infomation': {},
                                                        'ansible_automation_controller_use_infomation': {},
                                                        'ansible_cfg': row['I_ANSIBLE_CONFIG_FILE']}
        execution_info['target_execution']['movement']['ansible_use_infomation'] = {'host_specify_format': host_specify_format,'win_rm_connect': win_rm_connect}
        execution_info['target_execution']['movement']['ansible_core_use_infomation'] = {'virtual_env': row['I_ENGINE_VIRTUALENV_NAME']}
        execution_info['target_execution']['movement']['ansible_automation_controller_use_infomation'] = {'execution_environment': row['I_EXECUTION_ENVIRONMENT_NAME']}
        execution_info['target_execution']['operation'] = {'id': row['OPERATION_ID'], 'name': row['I_OPERATION_NAME']}
        execution_info['target_execution']['execution_situation'] = {'reserve_date': row['TIME_BOOK'],
                                                                    'start_date': row['TIME_START'],
                                                                    'end_date': row['TIME_END']}
        # ログ情報
        execution_info['progress'] = {}
        execution_info['progress']['execution_log'] = {}
        path = getAnsibleExecutDirPath(AnscConst.DF_LEGACY_ROLE_DRIVER_ID, execution_no)
        if row['MULTIPLELOG_MODE'] == '1':
            list_log = row['LOGFILELIST_JSON'].split(',') 
            for log in list_log:
                log_file_path = path + '/out/' + log
                ret = ky_file_encrypt(log_file_path, path + '/tmp')
                if ret == 1:
                    lcstr = Path(path + '/tmp').read_text(encoding="utf-8")
                    execution_info['progress']['execution_log'][log] = lcstr
        else:
            log_file_path = path + '/out/exec_log'
            ret = ky_file_encrypt(log_file_path, path + '/tmp')
            if ret == 1:
                lcstr = Path(path + '/tmp').read_text(encoding="utf-8")
                execution_info['progress']['execution_log']['exec_log'] = lcstr
        
        log_file_path = path + '/out/error_log'
        ret = ky_file_encrypt(log_file_path, path + '/tmp')
        if ret == 1:
            lcstr = Path(path + '/tmp').read_text(encoding="utf-8")
            execution_info['progress']['execution_log']['error_log'] = lcstr
        
        # 状態監視周期・進行状態表示件数
        where = ""
        tmp_data_list = objdbca.table_select("T_ANSC_IF_INFO", where)
        for tmp_row in tmp_data_list:
            execution_info['status_monitoring_cycle'] = tmp_row['ANSIBLE_REFRESH_INTERVAL']
            execution_info['number_of_rows_to_display_progress_status'] = tmp_row['ANSIBLE_TAILLOG_LINES']

    return execution_info
    
def reserve_cancel(objdbca, execution_no):
    """
        予約取消
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            execution_no: 作業実行No
        RETRUN:
            status: SUCCEED
            execution_no: 作業No
    """
    
    # 該当の作業実行のステータス取得
    where = "WHERE EXECUTION_NO = " + execution_no
    objdbca.table_lock(["T_ANSR_EXEC_STS_INST"])
    data_list = objdbca.table_select("T_ANSR_EXEC_STS_INST", where)
    
    # 該当する作業実行が存在しない
    if len(data_list) is None or len(data_list) == 0:
        log_msg_args = [execution_no]
        api_msg_args = [execution_no]
        raise AppException("499-00903", log_msg_args, api_msg_args)
    
    for row in data_list:
        # ステータスが未実行(予約)でない
        if not row['STATUS_ID'] == AnscConst.RESERVE:
            # ステータス取得
            where = "WHERE EXEC_STATUS_ID = " + row['STATUS_ID']
            tmp_data_list = objdbca.table_select("T_ANSC_EXEC_STATUS", where)
            for tmp_row in tmp_data_list:
                if g.LANGUAGE == 'ja':
                    status = tmp_row['EXEC_STATUS_NAME_JA']
                else:
                    status = tmp_row['EXEC_STATUS_NAME_EN']
                
            log_msg_args = [status]
            api_msg_args = [status]
            raise AppException("499-00910", log_msg_args, api_msg_args)
        
        # ステータスを予約取消に変更
        update_list = {'EXECUTION_NO': execution_no, 'STATUS_ID': AnscConst.RESERVE_CANCEL}
        ret = objdbca.table_update('T_ANSR_EXEC_STS_INST', update_list, 'EXECUTION_NO', True)
        objdbca.db_commit()
        
    return {"status": "SUCCEED", "execution_no": execution_no}