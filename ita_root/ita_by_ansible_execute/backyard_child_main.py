# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from flask import g
import traceback
import os
import sys
import re
import time
import datetime
import json
import yaml
import glob
import shutil

from common_libs.common.dbconnect import DBConnectWs
from common_libs.common.exception import AppException, ValidationException
from common_libs.common.util import get_timestamp, arrange_stacktrace_format
# from common_libs.ci.util import app_exception, exception, log_err

from common_libs.ansible_driver.classes.AnsrConstClass import AnscConst, AnsrConst
from common_libs.ansible_driver.classes.ansible_execute import AnsibleExecute
from common_libs.ansible_driver.classes.SubValueAutoReg import SubValueAutoReg
from common_libs.ansible_driver.classes.CreateAnsibleExecFiles import CreateAnsibleExecFiles
from common_libs.ansible_driver.functions.util import getAnsibleExecutDirPath
from common_libs.ansible_driver.functions.ansibletowerlibs.AnsibleTowerExecute import AnsibleTowerExecution
from common_libs.driver.functions import operation_LAST_EXECUTE_TIMESTAMP_update

from libs import common_functions as cm


# ansible共通の定数をロード
ansc_const = AnscConst()
ansr_const = AnsrConst()


def backyard_child_main(organization_id, workspace_id):
    # コマンドラインから引数を受け取る["自身のファイル名", "organization_id", "workspace_id", …, …]
    args = sys.argv
    # print(args)
    execution_no = args[3]
    driver_id = args[4]

    # 子プロ用のログモジュール
    g.local_applogger = LocalAppLog(driver_id, execution_no, "debug")

    # v1子プロの開始　[50052] = "[処理]プロシージャ開始 (作業No.:{})";
    g.local_applogger.debug("child_process 開始")  # "ITAANSIBLEH-STD-50052"

    # db instance
    wsDb = DBConnectWs(workspace_id)  # noqa: F405

    # while True:
    #     time.sleep(1)

    try:
        result = main_logic(wsDb, execution_no, driver_id)
        if result[0] is True:
            # 正常終了
            g.local_applogger.debug("ITAANSIBLEH-STD-50053")
        else:
            if len(result) == 2:
                g.local_applogger.error(result[1])
            update_status_error(wsDb, execution_no)
            # 全体でエラーがあったらITAANSIBLEH-STD-50054、警告ならITAANSIBLEH-STD-50055、をだして、終了したい？
            g.local_applogger.debug("ITAANSIBLEH-STD-50054")
    except AppException:
        pass
    except Exception:
        t = traceback.format_exc()
        g.local_applogger.error(arrange_stacktrace_format(t))
        update_status_error(wsDb, execution_no)
        g.local_applogger.debug("ITAANSIBLEH-STD-50054")


def update_status_error(wsDb: DBConnectWs, execution_no):
    # 異常終了としてステータス更新
    timestamp = get_timestamp()
    wsDb.db_transaction_start()
    data = {
        "EXECUTION_NO": execution_no,
        "STATUS_ID": ansc_const.EXCEPTION,
        "TIME_START": timestamp,
        "TIME_END": timestamp,
    }
    result = cm.update_execution_record(wsDb, data)
    if result[0] is True:
        wsDb.db_commit()


def main_logic(wsDb: DBConnectWs, execution_no, driver_id):
    # 処理対象の作業インスタンス情報取得
    retBool, execute_data = cm.get_execution_process_info(wsDb, execution_no)
    if retBool is False:
        return False, execute_data
    execution_no = execute_data["EXECUTION_NO"]
    # conductor_instance_no = execute_data["CONDUCTOR_INSTANCE_NO"]
    run_mode = execute_data['RUN_MODE']

    # ディレクトリを生成
    container_driver_path = getAnsibleExecutDirPath(driver_id, execution_no)

    work_dir = container_driver_path + "/in"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    work_dir = container_driver_path + "/out"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    work_dir = container_driver_path + "/.tmp"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)

    # 	処理区分("1")、パラメータ確認、作業実行、ドライラン
    # 		代入値自動登録とパラメータシートからデータを抜く
    # 		該当のオペレーション、Movementのデータを代入値管理に登録
    sub_value_auto_reg = SubValueAutoReg()
    try:
        sub_value_auto_reg.GetDataFromParameterSheet("1", execute_data["OPERATION_ID"], execute_data["MOVEMENT_ID"], execution_no, wsDb)
    except ValidationException as e:
        result_code, log_msg_args = e.args
        log_msg = g.appmsg.get_log_message(result_code, log_msg_args)
        return False, log_msg

    # 実行モードが「パラメータ確認」の場合は終了
    if run_mode == ansc_const.CHK_PARA:
        wsDb.db_transaction_start()
        data = {
            "EXECUTION_NO": execution_no,
            "STATUS_ID": ansc_const.COMPLETE,
            "TIME_END": get_timestamp(),
        }
        result = cm.update_execution_record(wsDb, data)
        if result[0] is True:
            wsDb.db_commit()
        g.local_applogger.debug("ITAANSIBLEH-STD-50052")
        return True,

    # ANSIBLEインタフェース情報を取得
    retBool, result = cm.get_ansible_interface_info(wsDb)
    if retBool is False:
        return False, result
    ans_if_info = result

    # # Conductorインタフェース情報を取得
    # retBool, result = cm.get_conductor_interface_info(wsDb)
    # if retBool is False:
    #     return False, result
    # conductor_interface_info = result

    # 投入オペレーションの最終実施日を更新する
    wsDb.db_transaction_start()
    result = operation_LAST_EXECUTE_TIMESTAMP_update(wsDb, execute_data["OPERATION_ID"])
    if result[0] is False:
        wsDb.db_commit()

    # ansible実行に必要なファイル群を生成するクラス
    ansdrv = CreateAnsibleExecFiles(driver_id, ans_if_info, execution_no, execute_data['I_ENGINE_VIRTUALENV_NAME'], execute_data['I_ANSIBLE_CONFIG_FILE'], wsDb)  # noqa: E501

    # 処理対象の作業インスタンス実行
    retBool, execute_data, result_data = instance_execution(wsDb, ansdrv, ans_if_info, execute_data, driver_id)

    # 実行結果から、処理対象の作業インスタンスのステータス更新
    if retBool is True:
        wsDb.db_transaction_start()
        result = cm.update_execution_record(wsDb, execute_data)
        if result[0] is True:
            wsDb.db_commit()
    else:
        # 失敗
        return False, result_data
    
    # ステータスが実行中以外は終了
    if execute_data["STATUS_ID"] != ansc_const.PROCESSING:
        return False, "def instance_execution is failed"

    # 実行結果から取得
    tower_host_list = result_data

    g.applogger.debug("ITAANSIBLEH-STD-50069")  # ary[50069] = "[処理]処理対象インスタンス 作業確認開始(作業No.:{})";

    status_update = True
    check_interval = 3
    while True:
        time.sleep(check_interval)
        
        if status_update is True:
            # 処理対象の作業インスタンス情報取得
            retBool, execute_data = cm.get_execution_process_info(wsDb, execution_no)
            if retBool is False:
                return False, execute_data
            # クローン作製
            clone_execute_data = execute_data

        # 実行結果の確認
        retBool, clone_execute_data, db_update_need = instance_checkcondition(wsDb, ansdrv, ans_if_info, clone_execute_data, driver_id, tower_host_list)  # noqa: E501

        status_update = False
        # ステータスが更新されたか判定
        if clone_execute_data['STATUS_ID'] != execute_data['STATUS_ID'] or db_update_need is True:
            # 処理対象の作業インスタンスのステータス更新
            status_update = True

            wsDb.db_transaction_start()
            result = cm.update_execution_record(wsDb, clone_execute_data)
            if result[0] is True:
                wsDb.db_commit()

        if clone_execute_data['STATUS_ID'] in [ansc_const.COMPLETE, ansc_const.FAILURE, ansc_const.EXCEPTION, ansc_const.SCRAM]:
            break

    g.applogger.debug("ITAANSIBLEH-STD-50070")

    return True,


def instance_execution(wsDb: DBConnectWs, ansdrv: CreateAnsibleExecFiles, ans_if_info, execute_data, driver_id):
    g.applogger.debug("ITAANSIBLEH-STD-51070")  # ITAANSIBLEH-STD-51070

    execution_no = execute_data["EXECUTION_NO"]
    pattern_id = execute_data["PATTERN_ID"]
    run_mode = execute_data['RUN_MODE']  # 処理対象のドライランモードのリスト

    # 処理対象の並列実行数のリストを格納 (pioneer)
    tgt_exec_count = execute_data['I_ANS_PARALLEL_EXE']
    if len(tgt_exec_count.strip()) == 0:
        tgt_exec_count = '0'

    file_subdir_zip_input = 'FILE_INPUT'
    zip_temp_save_dir = getAnsibleExecutDirPath(driver_id, execution_no) + '/.tmp'

    # ANSIBLEインタフェース情報をローカル変数に格納
    ansible_exec_options = ans_if_info['ANSIBLE_EXEC_OPTIONS']
    ans_exec_user = ans_if_info['ANSIBLE_EXEC_USER']
    ans_exec_mode = ans_if_info['ANSIBLE_EXEC_MODE']

    if len(str(ans_exec_user).strip()) == 0:
        ans_exec_user = 'root'

    winrm_id = ""
    if driver_id == ansc_const.DF_LEGACY_ROLE_DRIVER_ID:
        winrm_id = execute_data["I_ANS_WINRM_ID"]

    # Ansibleコマンド実行ユーザー設定
    ansdrv.setAnsibleExecuteUser(ans_exec_user)

    # データベースからansibleで実行する情報取得し実行ファイル作成
    result = call_CreateAnsibleExecFiles(ansdrv, execute_data, driver_id, winrm_id)  # noqa: E501

    if result[0] is False:
        return False, execute_data, result[1]

    tmp_array_dirs = ansdrv.getAnsibleWorkingDirectories(ansr_const.vg_OrchestratorSubId_dir, execution_no)
    # print(tmp_array_dirs)
    zip_data_source_dir = tmp_array_dirs[3]

    # ansible-playbookのオプションパラメータを確認
    movement_ansible_exec_option = getMovementAnsibleExecOption(wsDb, pattern_id)

    option_parameter = ansible_exec_options + ' ' + movement_ansible_exec_option
    option_parameter = option_parameter.replace("--verbose", "-v")

    # Tower実行の場合にオプションパラメータをチェックする。
    if ans_exec_mode != ansc_const.DF_EXEC_MODE_ANSIBLE:
        # Pioneerの場合の並列実行数のパラメータ設定
        if driver_id == ansc_const.DF_PIONEER_DRIVER_ID:
            if tgt_exec_count != '0':
                option_parameter = option_parameter + " -f {} ".format(tgt_exec_count)

        # 重複除外用のオプションパラメータ
        result = getAnsiblePlaybookOptionParameter(
            wsDb,
            option_parameter)
        if result[0] is False:
            err_msg_ary = result[1]
            for err_msg in err_msg_ary:
                # LocalLogPrint
                g.local_applogger.error(err_msg)
            return False, execute_data, "getAnsiblePlaybookOptionParameter is failed[{}]".format(",".join(err_msg_ary))
        
        retBool, err_msg_ary, JobTemplatePropertyParameterAry, JobTemplatePropertyNameAry, param_arry_exc = result

    # ansible-playbookコマンド実行時のオプションパラメータを共有ディレクトリのファイルに出力
    with open(zip_data_source_dir + "/AnsibleExecOption.txt", "w") as f:
        f.write(option_parameter)

    # 投入データ用ZIPファイル作成
    vg_exe_ins_input_file_dir = ansdrv.getTowerProjectsScpPath()
    retBool, err_msg, zip_input_file, zip_input_file_dir = fileCreateZIPFile(
        execution_no,
        zip_data_source_dir,
        vg_exe_ins_input_file_dir,
        zip_temp_save_dir,
        file_subdir_zip_input,
        'InputData_')

    # 投入データ用ZIP 履歴ファイル作成
    if retBool is True:
        execute_data["FILE_INPUT"] = zip_input_file

        # 投入データ用ZIP 履歴ファイル作成
        result = fileCreateHistoryZIPFile(
            execution_no,
            zip_input_file,
            zip_input_file_dir)
        if result[0] is False:
            # ZIPファイル作成の作成に失敗しても、ログに出して次に進む
            g.local_applogger.info()
    
    else:
        # ZIPファイル作成の作成に失敗しても、ログに出して次に進む
        g.local_applogger.info()

    # 準備で異常がなければ実行にうつる
    # 実行エンジンを判定
    if ans_exec_mode == ansc_const.DF_EXEC_MODE_ANSIBLE:
        g.local_applogger.debug("ITAANSIBLEH-STD-51066")

        ansible_execute = AnsibleExecute()
        retBool = ansible_execute.execute_construct(driver_id, execution_no, "", "", ans_if_info['ANSIBLE_CORE_PATH'], ans_if_info['ANSIBLE_VAULT_PASSWORD'], run_mode, "")  # noqa: E501

        if retBool is True:
            execute_data["STATUS_ID"] = ansc_const.PROCESSING
            execute_data["TIME_START"] = get_timestamp()
        else:
            err_msg = ansible_execute.getLastError()
            ansdrv.LocalLogPrint()
            return False, execute_data, err_msg
    else:
        g.local_applogger.debug("ITAANSIBLEH-STD-51068")

        uiexec_log_path = ansdrv.getAnsible_out_Dir() + "/exec.log"
        uierror_log_path = ansdrv.getAnsible_out_Dir() + "/error.log"
        multiple_log_mark = ""
        multiple_log_file_json_ary = ""

        Ansible_out_Dir = ansdrv.getAnsible_out_Dir()
        TowerProjectsScpPath = ansdrv.getTowerProjectsScpPath()
        TowerInstanceDirPath = ansdrv.getTowerInstanceDirPath()
        try:
            # execute_dataのSTATUS_ID/TIME_STARTはAnsibleTowerExecution内で設定
            # statusは使わない
            retBool, tower_host_list, execute_data, multiple_log_mark, multiple_log_file_json_ary, status, error_flag, warning_flag = AnsibleTowerExecution(  # noqa: E501
                ansc_const.DF_EXECUTION_FUNCTION,
                ans_if_info,
                [],
                execute_data,
                Ansible_out_Dir, uiexec_log_path,
                uierror_log_path,
                multiple_log_mark, multiple_log_file_json_ary,
                "",
                JobTemplatePropertyParameterAry,
                JobTemplatePropertyNameAry,
                TowerProjectsScpPath,
                TowerInstanceDirPath,
                wsDb)

        except Exception as e:
            AnsibleTowerExecution(
                ansc_const.DF_DELETERESOURCE_FUNCTION, ans_if_info,
                [],
                execute_data,
                Ansible_out_Dir, uiexec_log_path,
                uierror_log_path,
                multiple_log_mark, multiple_log_file_json_ary)
            raise Exception(e)

        # マルチログか判定
        if multiple_log_mark and execute_data['MULTIPLELOG_MODE'] != multiple_log_mark:
            execute_data['MULTIPLELOG_MODE'] = multiple_log_mark

    return True, execute_data, tower_host_list


def instance_checkcondition(wsDb: DBConnectWs, ansdrv: CreateAnsibleExecFiles, ans_if_info, execute_data, driver_id, tower_host_list):
    db_update_need = False
    sql_exec_flag = 0

    execution_no = execute_data["EXECUTION_NO"]

    file_subdir_zip_result = 'FILE_RESULT'
    zip_temp_save_dir = getAnsibleExecutDirPath(driver_id, execution_no) + '/.tmp'

    # ANSIBLEインタフェース情報をローカル変数に格納
    # ans_storage_path_ans = ans_if_info['ANSIBLE_STORAGE_PATH_ANS']
    # ans_protocol = ans_if_info['ANSIBLE_PROTOCOL']
    # ans_hostname = ans_if_info['ANSIBLE_HOSTNAME']
    # ans_port = ans_if_info['ANSIBLE_PORT']
    # ans_access_key_id = ans_if_info['ANSIBLE_ACCESS_KEY_ID']
    # ans_secret_access_key = ky_decrypt(ans_if_info['ANSIBLE_SECRET_ACCESS_KEY'])

    ans_exec_user = ans_if_info['ANSIBLE_EXEC_USER']
    ans_exec_mode = ans_if_info['ANSIBLE_EXEC_MODE']

    # proxySetting = {}
    # proxySetting['address'] = ans_if_info["ANSIBLE_PROXY_ADDRESS"]
    # proxySetting['port'] = ans_if_info["ANSIBLE_PROXY_PORT"]

    if len(str(ans_exec_user).strip()) == 0:
        ans_exec_user = 'root'

    tmp_array_dirs = ansdrv.getAnsibleWorkingDirectories(ansr_const.vg_OrchestratorSubId_dir, execution_no)
    zip_data_source_dir = tmp_array_dirs[4]

    # 実行エンジンを判定
    if ans_exec_mode == ansc_const.DF_EXEC_MODE_ANSIBLE:
        g.local_applogger.debug("ITAANSIBLEH-STD-50071")

        ansible_execute = AnsibleExecute()
        status = ansible_execute.execute_statuscheck(driver_id, execution_no)

        # 想定外エラーはログを出す
        if status == ansc_const.ansc_const.EXCEPTION:
            ansdrv.LocalLogPrint(ansible_execute.getLastError())
            sql_exec_flag = 1
    else:
        g.local_applogger.debug("ITAANSIBLEH-STD-50071")

        uiexec_log_path = ansdrv.getAnsible_out_Dir() + "/exec.log"
        uierror_log_path = ansdrv.getAnsible_out_Dir() + "/error.log"
        multiple_log_mark = ""
        multiple_log_file_json_ary = ""
        Ansible_out_Dir = ansdrv.getAnsible_out_Dir()
        status = 0

        retBool, tower_host_list, execute_data, multiple_log_mark, multiple_log_file_json_ary, status, error_flag, warning_flag = AnsibleTowerExecution(  # noqa: E501
            ansc_const.DF_CHECKCONDITION_FUNCTION,
            ans_if_info,
            tower_host_list,
            execute_data,
            Ansible_out_Dir, uiexec_log_path,
            uierror_log_path,
            multiple_log_mark, multiple_log_file_json_ary,
            status)

        # マルチログか判定
        if multiple_log_mark and execute_data['MULTIPLELOG_MODE'] != multiple_log_mark:
            execute_data['MULTIPLELOG_MODE'] = multiple_log_mark
            db_update_need = True
        # マルチログファイルリスト
        if multiple_log_file_json_ary and execute_data['LOGFILELIST_JSON'] != multiple_log_file_json_ary:
            execute_data['LOGFILELIST_JSON'] = multiple_log_file_json_ary
            db_update_need = True

        # 5:正常終了時
        # 6:完了(異常)
        # 7:想定外エラー
        # 8:緊急停止
        if status in [ansc_const.COMPLETE, ansc_const.FAILURE, ansc_const.EXCEPTION, ansc_const.SCRAM]:
            # SQL(UPDATE)をEXECUTEする
            sql_exec_flag = 1
        else:
            status = -1

    # 状態をログに出力
    g.local_applogger.debug("ExecutionNo:{}  Status:{}".format(execution_no, status))

    # 5:正常終了時
    # 6:完了(異常)
    # 7:想定外エラー
    # 8:緊急停止
    if status in [ansc_const.COMPLETE, ansc_const.FAILURE, ansc_const.EXCEPTION, ansc_const.SCRAM] or error_flag != 0:
        # 実行結果ファイルをTowerから転送
        # 実行エンジンを判定
        if ans_exec_mode != ansc_const.DF_EXEC_MODE_ANSIBLE:
            # 戻り値は確認しない
            multiple_log_mark = ""
            multiple_log_file_json_ary = ""
            AnsibleTowerExecution(
                ansc_const.DF_RESULTFILETRANSFER_FUNCTION,
                ans_if_info,
                tower_host_list,
                execute_data,
                Ansible_out_Dir, uiexec_log_path,
                uierror_log_path,
                multiple_log_mark, multiple_log_file_json_ary,
                status)

        # 結果データ用ZIPファイル作成
        vg_exe_ins_result_file_dir = ansdrv.getTowerInstanceDirPath()
        retBool, err_msg, zip_result_file, zip_result_file_dir = fileCreateZIPFile(
            execution_no,
            zip_data_source_dir,
            vg_exe_ins_result_file_dir,
            zip_temp_save_dir,
            file_subdir_zip_result,
            'ResultData_')

    # statusによって処理を分岐
    if status != -1:
        # SQL(UPDATE)をEXECUTEする
        sql_exec_flag = 1

        execute_data["STATUS_ID"] = status
        execute_data["TIME_END"] = get_timestamp()
    else:
        # 遅延を判定
        # 遅延タイマを取得
        time_limit = int(execute_data['I_TIME_LIMIT']) if execute_data['I_TIME_LIMIT'] else None
        delay_flag = 0

        # ステータスが実行中(3)、かつ制限時間が設定されている場合のみ遅延判定する
        if execute_data["STATUS_ID"] == ansc_const.PROCESSING and time_limit:
            # 開始時刻(「UNIXタイム.マイクロ秒」)を生成
            rec_time_start = execute_data['TIME_START']
            utc_time_start = rec_time_start.astimezone(datetime.timezone.utc)
            starttime_unixtime = utc_time_start.timestamp()
            # 開始時刻(マイクロ秒)＋制限時間(分→秒)＝制限時刻(マイクロ秒)
            limit_unixtime = starttime_unixtime + (time_limit * 60)
            # 現在時刻(「UNIXタイム.マイクロ秒」)を生成
            now_unixtime = time.time()

            # 制限時刻と現在時刻を比較
            if limit_unixtime < now_unixtime:
                delay_flag = 1
                g.local_applogger.debug("ITAANSIBLEH-STD-50030  ExecutionNo:{}".format(execution_no))
            else:
                g.local_applogger.debug("ITAANSIBLEH-STD-50031  ExecutionNo:{}".format(execution_no))

        if delay_flag == 1:
            sql_exec_flag = 1
            # ステータスを「実行中(遅延)」とする
            execute_data["STATUS_ID"] = 4

    # 遅延中以外の場合に結果データ用ZIP 履歴ファイル作成
    if sql_exec_flag == 1 and execute_data["STATUS_ID"] == 4:
        fileCreateHistoryZIPFile(
            execution_no,
            zip_result_file,
            zip_result_file_dir)
        execute_data['FILE_RESULT'] = zip_result_file

    # 実行エンジンを判定
    if ans_exec_mode != ansc_const.DF_EXEC_MODE_ANSIBLE:
        # 5:正常終了時
        # 6:完了(異常)
        # 7:想定外エラー
        # 8:緊急停止
        if status in [ansc_const.COMPLETE, ansc_const.FAILURE, ansc_const.EXCEPTION, ansc_const.SCRAM]:
            g.local_applogger.debug("ITAANSIBLEH-STD-50075  ExecutionNo:{}".format(execution_no))

            # AnsibleTower ゴミ掃除 戻り値は確認しない
            # 戻り値は確認しない
            retBool,
            tower_host_list,
            execute_data,
            multiple_log_mark,
            multiple_log_file_json_ary,
            status, error_flag, warning_flag = AnsibleTowerExecution(
                ansc_const.DF_DELETERESOURCE_FUNCTION,
                ans_if_info,
                tower_host_list,
                execute_data,
                Ansible_out_Dir,
                uiexec_log_path,
                uierror_log_path,
                multiple_log_mark,
                multiple_log_file_json_ary,
                status)

            g.local_applogger.debug("ITAANSIBLEH-STD-50076  ExecutionNo:{}".format(execution_no))

    return True, execute_data, db_update_need


def call_CreateAnsibleExecFiles(ansdrv: CreateAnsibleExecFiles, execute_data, driver_id, winrm_id):
    execution_no = execute_data["EXECUTION_NO"]
    conductor_instance_no = execute_data["CONDUCTOR_INSTANCE_NO"]
    operation_id = execute_data["OPERATION_ID"]
    pattern_id = execute_data["PATTERN_ID"]
    # ホストアドレス指定方式（I_ANS_HOST_DESIGNATE_TYPE_ID）
    # null or 1 がIP方式 2 がホスト名方式
    hostaddres_type = execute_data['I_ANS_HOST_DESIGNATE_TYPE_ID']

    exec_mode = execute_data["EXEC_MODE"]
    exec_playbook_hed_def = execute_data["I_ANS_PLAYBOOK_HED_DEF"]
    exec_option = execute_data["I_ANS_EXEC_OPTIONS"]

    hostlist = {}
    hostostypelist = {}
    hostinfolist = {}  # 機器一覧ホスト情報
    playbooklist = {}
    dialogfilelist = {}

    host_vars = []
    pioneer_template_host_vars = {}
    vault_vars = {}
    vault_host_vars_file_list = {}
    host_child_vars = []
    DB_child_vars_master = []

    # Legacy-Role対応
    rolenamelist = []
    role_rolenamelist = {}
    role_rolevarslist = {}
    role_roleglobalvarslist = {}
    role_rolepackage_id = ""

    MultiArray_vars_list = {}
    All_vars_list = []

    def_vars_list = {}
    def_array_vars_list = {}

    result = ansdrv.CreateAnsibleWorkingDir(ansr_const.vg_OrchestratorSubId_dir, execution_no, operation_id, hostaddres_type,
                                            winrm_id,
                                            pattern_id,
                                            role_rolenamelist,
                                            role_rolevarslist,
                                            role_roleglobalvarslist,
                                            role_rolepackage_id,
                                            def_vars_list,
                                            def_array_vars_list,
                                            conductor_instance_no)

    retBool, role_rolenamelist, role_rolevarslist, role_roleglobalvarslist, role_rolepackage_id, def_vars_list, def_array_vars_list = result
    if retBool is False:
        return False, "ITAANSIBLEH-ERR-50003" "00010004"

    result = ansdrv.AnsibleEnginVirtualenvPathCheck()
    if result is False:
        return False, "AnsibleEnginVirtualenvPathCheck is failed"

    result = ansdrv.getDBHostList(
        execution_no,
        pattern_id,
        operation_id,
        hostlist,
        hostostypelist,
        hostinfolist,
        winrm_id)
    retBool, hostlist, hostostypelist, hostinfolist = result
    if retBool is False:
        return False, "ITAANSIBLEH-ERR-50003" "00010000"

    if driver_id == ansc_const.DF_LEGACY_DRIVER_ID:
        # データベースからPlayBookファイルを取得
        #    playbooklist:     子PlayBookファイル返却配列
        #                     [INCLUDE順序][素材管理Pkey]=>素材ファイル
        result = ansdrv.getDBLegacyPlaybookList(pattern_id, playbooklist)
        retBool, playbooklist = result
        if retBool is False:
            return False, "ITAANSIBLEH-ERR-50003" "00010001"
    elif driver_id == ansc_const.DF_PIONEER_DRIVER_ID:
        # データベースから対話ファイルを取得
        #    dialogfilelist:     子PlayBookファイル返却配列
        #                     [ホスト名(IP)][INCLUDE順番][素材管理Pkey]=対話ファイル
        result = ansdrv.getDBPioneerDialogFileList(pattern_id, operation_id, dialogfilelist, hostostypelist)
        retBool, dialogfilelist = result
        if retBool is False:
            return False, "ITAANSIBLEH-ERR-50003" "00010002"
    elif driver_id == ansc_const.DF_LEGACY_ROLE_DRIVER_ID:
        # データベースからロール名を取得
        #    rolenamelist:     ロール名返却配列
        #                     [実行順序][ロールID(Pkey)]=>ロール名
        result = ansdrv.getDBLegactRoleList(pattern_id, rolenamelist)
        retBool, rolenamelist = result
        if retBool is False:
            return False, "ITAANSIBLEH-ERR-50003" "00010001"

    # Legacy-Role 多次元配列　恒久版対応
    if driver_id == ansc_const.DF_LEGACY_DRIVER_ID or driver_id == ansc_const.DF_PIONEER_DRIVER_ID:
        #  データベースから変数情報を取得する。
        result = ansdrv.getDBVarList(
            pattern_id,
            operation_id,
            host_vars,
            pioneer_template_host_vars,
            vault_vars,
            vault_host_vars_file_list,
            host_child_vars,
            DB_child_vars_master)
        retBool, host_vars, pioneer_template_host_vars, vault_vars, vault_host_vars_file_list, host_child_vars, DB_child_vars_master = result
        if retBool is False:
            return False, "ITAANSIBLEH-ERR-50003" "00010003"
    elif driver_id == ansc_const.DF_LEGACY_ROLE_DRIVER_ID:
        # データベースから変数情報を取得する。
        #   $host_vars:        変数一覧返却配列
        #                      [ホスト名(IP)][ 変数名 ]=>具体値
        result = ansdrv.getDBRoleVarList(execution_no, pattern_id, operation_id, host_vars, MultiArray_vars_list, All_vars_list)
        retBool, host_vars, MultiArray_vars_list, All_vars_list = result
        if retBool is False:
            return False, "ITAANSIBLEH-ERR-50003" "00010003"

    host_vars = ansdrv.addSystemvars(host_vars, hostinfolist)

    # Legacy-Role 多次元配列　恒久版対応
    # ansibleで実行するファイル作成
    result = ansdrv.CreateAnsibleWorkingFiles(
        hostlist,
        host_vars,
        pioneer_template_host_vars,
        vault_vars,
        vault_host_vars_file_list,
        playbooklist,
        dialogfilelist,
        rolenamelist,
        role_rolenamelist,
        role_rolevarslist,
        role_roleglobalvarslist,
        hostinfolist,
        host_child_vars,
        DB_child_vars_master,
        MultiArray_vars_list,
        def_vars_list,
        def_array_vars_list,
        exec_mode,
        exec_playbook_hed_def,
        exec_option)
    if retBool is False:
        return False, "ITAANSIBLEH-ERR-50003" "00010005"

    return True, ""


def getMovementAnsibleExecOption(wsDb, pattern_id):
    condition = 'WHERE `DISUSE_FLAG`=0 AND PATTERN_ID = %s'
    records = wsDb.table_select('V_ANSR_MOVEMENT', condition, [pattern_id])

    return records[0]['ANS_EXEC_OPTIONS']


def getAnsiblePlaybookOptionParameter(wsDb, option_parameter):
    res_retBool = True
    JobTemplatePropertyParameterAry = {}
    JobTemplatePropertyNameAry = {}
    param_arry_exc = {}
    err_msg_arr = []
    verbose_cnt = 0

    # Towerが扱えるオプションパラメータ取得
    job_template_property_info = getJobTemplateProperty(wsDb)

    param = "-__dummy__ " + option_parameter.strip() + ' '
    param_arr = re.split(r'((\s)-)', param)
    # 無効なオプションパラメータが設定されていないか判定
    for param_string in param_arr:
        if param_string.strip() == '-__dummy__':
            continue

        hit = False
        chk_param_string = '-' + param_string + ' '
        for job_template_property_record in job_template_property_info:
            key_string = job_template_property_record['KEY_NAME'].strip()
            if key_string != "":
                if re.match(key_string, chk_param_string):
                    hit = True
                    break
            key_string = job_template_property_record['SHORT_KEY_NAME'].strip()
            if key_string != "":
                if re.match(key_string, chk_param_string):
                    hit = True
                    break
        
        if hit is False:
            err_msg_arr.append(chk_param_string)  # "ITAANSIBLEH-ERR-6000104"

    if len(err_msg_arr) != 0:
        # err_msg
        return False, err_msg_arr

    # 除外された場合のリスト
    param_arry_exc = param_arr

    for job_template_property_record in job_template_property_info:
        #  除外リストの初期化
        excist_list = []
        # KEY SHRT_KEYチェック用配列の初期化
        key_short_chk = []
        # tags skipのvalue用の配列の初期化
        tag_skip_value_key = []
        tag_skip_Value_key_s = {}

        JobTemplatePropertyNameAry[job_template_property_record['PROPERTY_NAME']] = 0

        if job_template_property_record['KEY_NAME']:
            retBool, err_msg_arr, excist_list, tag_skip_value_key, verbose_cnt = makeJobTemplateProperty(
                job_template_property_record['KEY_NAME'],
                job_template_property_record['PROPERTY_TYPE'],
                param_arr,
                err_msg_arr,
                excist_list,
                tag_skip_value_key,
                verbose_cnt)

            # 重複データの場合のみ
            excist_count = len(excist_list)
            i = 0
            if excist_count >= 1:
                for excist_elm in excist_list:
                    # 最後のデータは削除しない
                    if excist_count - 1 == i:
                        # KEYのチェックデータ格納
                        key_short_chk.append(excist_elm)
                        break
                    j = 0
                    for elm_ary in param_arry_exc:
                        # 除外リストと一致した場合
                        if excist_elm == elm_ary:
                            # 要素を削除
                            param_arry_exc.pop(j)
                            break
                        j = j + 1
                    i = i + 1
                    
            if retBool is False:
                res_retBool = False
            
            # 除外リストの初期化
            excist_list = []

        if job_template_property_record['SHORT_KEY_NAME']:
            retBool, err_msg_arr, excist_list, tag_skip_Value_key_s, verbose_cnt = makeJobTemplateProperty(
                job_template_property_record['SHORT_KEY_NAME'],
                job_template_property_record['PROPERTY_TYPE'],
                param_arr,
                err_msg_arr,
                excist_list,
                tag_skip_Value_key_s,
                verbose_cnt)

            # 重複データの場合のみ
            excist_count = len(excist_list)
            i = 0
            if excist_count >= 1:
                for excist_elm in excist_list:
                    # 最後のデータは削除しない
                    if excist_count - 1 == i:
                        # KEYのチェックデータ格納
                        key_short_chk.append(excist_elm)
                        break
                    j = 0
                    for elm_ary in param_arry_exc:
                        # 除外リストと一致した場合
                        if excist_elm == elm_ary:
                            # 要素を削除
                            param_arry_exc.pop(j)
                            break
                        j = j + 1
                    i = i + 1
                    
            if retBool is False:
                res_retBool = False
            
        # KEY SHORTのチェック
        k = 0
        if len(key_short_chk) >= 2:
            # KEY SHORTそれぞれ存在する場合,先頭データを削除
            for param_arry_exc_key_chk in param_arry_exc:
                if param_arry_exc_key_chk == key_short_chk[0]:
                    param_arry_exc.pop(k)
                    break
                if param_arry_exc_key_chk == key_short_chk[1]:
                    param_arry_exc.pop(k)
                k = k + 1

        # tags,skipの場合','区切りに修正する
        if r'--tags=' == job_template_property_record['KEY_NAME'] or r'--skip-tags=' == job_template_property_record['KEY_NAME']:
            # tags,skipの場合、','区切りにしてデータを渡す（文字列整形）
            values_param = ''
            ll = 0
            m = 0
            for param_arr_tmp_tab_skip in param_arr:
                chk_param_string = '-' + param_arr_tmp_tab_skip + ' '
                # KEYのtagsのvalueを取得
                if re.match(r'--tags=', chk_param_string) and r'--tags=' == job_template_property_record['KEY_NAME']:
                    values_param = values_param + tag_skip_value_key[ll] + ','
                    ll = ll + 1
                # KEYのskipのvalueを取得
                if re.match(r'--skip-tags=', chk_param_string) and r'--skip-tags=' == job_template_property_record['KEY_NAME']:
                    values_param = values_param + tag_skip_value_key[ll] + ','
                    ll = ll + 1
                # KEY SHORTのtagsのvalueを取得
                if re.match(r'-t(\s)+', chk_param_string) and r'-t(\s)+' == job_template_property_record['SHORT_KEY_NAME']:
                    values_param = values_param + tag_skip_Value_key_s[m] + ','
                    m = m + 1

            # 末尾の','を削除
            if values_param[-1] == ',':
                values_param = values_param[:-1]

            # リストのデータを書き換え
            n = 0
            for param_arr_tmp_key_chg in param_arry_exc:
                chk_param_string_chg = '-' + param_arr_tmp_key_chg + ' '
                if re.match(r'--tags=', chk_param_string_chg) and r'--tags=' == job_template_property_record['KEY_NAME']:
                    # 要素を書き換え
                    param_arry_exc[n] = '-tags=' + values_param
                    break
                if re.match(r'--skip-tags=', chk_param_string_chg) and r'--skip-tags=' == job_template_property_record['KEY_NAME']:
                    # 要素を書き換え
                    param_arry_exc[n] = '-skip-tags=' + values_param
                    break
                if re.match(r'-t(\s)+', chk_param_string_chg) and r'-t(\s)+' == job_template_property_record['SHORT_KEY_NAME']:
                    # 要素を書き換え
                    param_arry_exc[n] = 't ' + values_param
                    break
                n = n + 1

        # JobTemplatePropertyParameterAryの作成
        if len(job_template_property_record['KEY_NAME'].strip()) != 0:
            retBool, JobTemplatePropertyParameterAry = makeJobTemplatePropertyParameterAry(
                job_template_property_record['KEY_NAME'],
                job_template_property_record['PROPERTY_TYPE'],
                job_template_property_record['PROPERTY_NAME'],
                JobTemplatePropertyParameterAry,
                param_arry_exc,
                verbose_cnt)
        if len(job_template_property_record['SHORT_KEY_NAME'].strip()) != 0:
            retBool, JobTemplatePropertyParameterAry = makeJobTemplatePropertyParameterAry(
                job_template_property_record['SHORT_KEY_NAME'],
                job_template_property_record['PROPERTY_TYPE'],
                job_template_property_record['PROPERTY_NAME'],
                JobTemplatePropertyParameterAry,
                param_arry_exc,
                verbose_cnt)

    return res_retBool, err_msg_arr, JobTemplatePropertyParameterAry, JobTemplatePropertyNameAry, param_arry_exc


def getJobTemplateProperty(wsDb):
    res = []

    condition = 'WHERE `DISUSE_FLAG`=0'
    records = wsDb.table_select('T_ANSC_TWR_JOBTP_PROPERTY', condition)

    for record in records:
        data = {
            'KEY_NAME': record['KEY_NAME'],
            'SHORT_KEY_NAME': record['SHORT_KEY_NAME'],
            'PROPERTY_TYPE': record['PROPERTY_TYPE'],
            'PROPERTY_NAME': record['PROPERTY_NAME'],
            'TOWERONLY': record['TOWERONLY']
        }
        res.append(data)

    return res


def makeJobTemplateProperty(key_string, property_type, param_arr, err_msg_arr, excist_list, tag_skip_value_key, verbose_cnt):
    res_retBool = True
    err_msg_arr = []

    for param_string in param_arr:
        chk_param_string = '-' + param_string + ' '
        if re.match(key_string, chk_param_string):
            property_arr = re.split(r'^{}'.format(key_string), chk_param_string)
            # 6000001 = "値が設定されていないオプションパラメータがあります。(パラメータ: {})"
            # 6000002 = "重複しているオプションパラメータがあります。(パラメータ: {})"
            # 6000003 = "不正なオプションパラメータがあります。(パラメータ: {})"

            # chk_param_stringを除外リストに設定(追加)
            excist_list.append(param_string)

            if property_type == ansc_const.DF_JobTemplateKeyValueProperty:
                if len(property_arr[1].strip()) == 0:
                    err_msg_arr.append()  # "ITAANSIBLEH-ERR-6000001" chk_param_string
                    res_retBool = False
                elif re.search(r'-f', key_string):
                    if str.isdecimal(property_arr[1].strip()):
                        err_msg_arr.append()  # "ITAANSIBLEH-ERR-6000003" chk_param_string
                        res_retBool = False
                # tags skipの対応
                elif key_string == r'--tags=' or key_string == r'-t(\s)+' or key_string == r'--skip-tags=':
                    tag_skip_value_key.append(property_arr[1].strip())

            elif property_type == ansc_const.DF_JobTemplateVerbosityProperty:
                property_arr = re.split(r'^(v)*', param_string)
                if len(property_arr[1].strip()) != 0:
                    err_msg_arr.append()  # "ITAANSIBLEH-ERR-6000003" chk_param_string
                    res_retBool = False
                else:
                    verbose_cnt = verbose_cnt + len(param_string.strip())

            elif property_type == ansc_const.DF_JobTemplatebooleanTrueProperty:
                if len(property_arr[1]).strip() != 0:
                    err_msg_arr.append()  # "ITAANSIBLEH-ERR-6000003" chk_param_string
                    res_retBool = False

            elif property_type == ansc_const.DF_JobTemplateExtraVarsProperty:
                if len(property_arr[1]).strip() == 0:
                    err_msg_arr.append()  # "ITAANSIBLEH-ERR-6000001" chk_param_string
                    res_retBool = False
                else:
                    ext_var_string = property_arr[1].strip()
                    ret = makeExtraVarsParameter(ext_var_string)
                    if ret is False:
                        err_msg_arr.append()  # "ITAANSIBLEH-ERR-6000003" chk_param_string
                        res_retBool = False

    return res_retBool, err_msg_arr, excist_list, tag_skip_value_key, verbose_cnt


def makeJobTemplatePropertyParameterAry(key_string, property_type, property_name, JobTemplatePropertyParameterAry, param_arr, verbose_cnt):
    retBool = True

    for param_string in param_arr:
        chk_param_string = '-' + param_string + ' '
        if not re.fullmatch(r'^{}'.format(key_string), chk_param_string):
            continue

        proper_ary = re.split(r'^{}'.format(key_string), chk_param_string)

        if property_type == ansc_const.DF_JobTemplateKeyValueProperty:
            JobTemplatePropertyParameterAry[property_name] = proper_ary[1].strip()
            break
        elif property_type == ansc_const.DF_JobTemplateVerbosityProperty:
            if verbose_cnt >= 6:
                verbose_cnt = 5
            JobTemplatePropertyParameterAry[property_name] = verbose_cnt
            break
        elif property_type == ansc_const.DF_JobTemplatebooleanTrueProperty:
            JobTemplatePropertyParameterAry[property_name] = True
        elif property_type == ansc_const.DF_JobTemplateExtraVarsProperty:
            ext_var_string = proper_ary[1].strip().strip("\"").strip("\'")
            ext_var_string = ext_var_string.replace("\\n", "\n")
            JobTemplatePropertyParameterAry[property_name] = ext_var_string

    return retBool, JobTemplatePropertyParameterAry


def makeExtraVarsParameter(ext_var_string):
    ext_var_string = ext_var_string.strip("\"").strip("\'")
    ext_var_string = ext_var_string.replace("\\n", "\n")

    # JSON形式のチェック
    try:
        json.loads(ext_var_string)
        return True
    except json.JSONDecodeError:
        pass
    
    # YAML形式のチェック
    try:
        yaml.safe_load(ext_var_string)
        return True
    except Exception:
        pass

    return False


def fileCreateZIPFile(execution_no, zip_data_source_dir, exe_ins_input_file_dir, zip_temp_save_dir, zip_subdir, zip_file_pfx):
    ########################################
    # 処理内容
    #  入力/結果ZIPファイル作成
    # パラメータ
    #  execution_no:               作業実行番号
    #  zip_data_source_dir:     inディレクトリ
    #  exe_ins_input_file_dir:  ZIPファイル格納ホームディレクトリ
    #                               root_dir_path . "/uploadfiles/21000xxxxx";
    #  zip_temp_save_dir:       作業ディレクトリ      = root_dir_path . '/temp';
    #  zip_subdir:              入力/出力ディレクトリ
    #                                 入力:FILE_INPUT   出力:FILE_RESULT
    #  zip_file_pfx:            入力/出力ファイルブラフィックス
    #                                 入力:InputData_   出力:ResultData_
    #
    #  ZIPファイルディレクトリ構成
    #   /uploadfiles/21000xxxxx/FILE_INPUT/作業番号(10桁)/InputData_0000000001.zip
    #   /uploadfiles/21000xxxxx/FILE_INPUT/作業番号(10桁)/old/履歴通番/InputData_0000000001.zip
    #
    # 戻り値
    #   true:正常　false:異常
    #   zip_file_name:           ZIPファイル名返却
    #   utn_file_dir:            ZIPファイル格納ディレクトリ
    #                                  exe_ins_input_file_dir/FILE_INPUT/作業実行番号
    ########################################
    err_msg = ""
    zip_file_name = ""
    utn_file_dir = ""

    if len(glob(zip_data_source_dir + "/*")) > 0:
        # ----ZIPファイルを作成する
        zip_file_name = zip_file_pfx + execution_no + '.zip'

        # OSコマンドでzip圧縮する
        tmp_str_command = "cd " + zip_data_source_dir + "; zip -r " + zip_temp_save_dir + "/" + zip_file_name + " . -x ssh_key_files/* -x winrm_ca_files/*"  # noqa: E501

        os.system(tmp_str_command)

        utn_file_dir = exe_ins_input_file_dir + "/" + zip_subdir + "/" + execution_no
        if not os.path.isdir(utn_file_dir):
            # ここ(UTNのdir)だけは再帰的に作成する
            try:
                os.makedirs(utn_file_dir)
                os.chmod(utn_file_dir, 0o777)
            except Exception as e:
                False, "[fileCreateZIPFile] {}".format(e)

        # zipファイルを正式な置き場に移動
        os.rename(zip_temp_save_dir + "/" + zip_file_name, utn_file_dir + "/" + zip_file_name)

        # zipファイルの存在を確認
        if not os.path.exists(utn_file_dir + "/" + zip_file_name):
            False, "[fileCreateZIPFile] file({}) not exists".format(utn_file_dir + "/" + zip_file_name), zip_file_name, utn_file_dir

    return True, err_msg, zip_file_name, utn_file_dir


def fileCreateHistoryZIPFile(execution_no, zip_file_name, utn_file_dir):
    ########################################
    # 処理内容
    #  履歴用入力/結果ZIPファイル作成
    # パラメータ
    #  execution_no:               作業実行番号
    #  zip_file_name:           ZIPファイル名返却
    #  utn_file_dir:            ZIPファイル格納ディレクトリ
    #                                  exe_ins_input_file_dir/作業実行番号
    #
    #  ZIPファイルディレクトリ構成
    #  　/uploadfiles/21000xxxxx/FILE_RESULT/作業番号(10桁)/ResultData_0000000001.zip
    #  　/uploadfiles/21000xxxxx/FILE_RESULT/作業番号(10桁)/old/履歴通番(10桁)/ResultData_0000000001.zip
    #
    # 戻り値
    #   true:正常　false:異常
    ########################################

    tmp_jnl_file_dir_trunk = utn_file_dir + "/old"
    tmp_jnl_file_dir_focus = tmp_jnl_file_dir_trunk + "/" + ""

    # 履歴フォルダへコピー
    if not os.path.exists(tmp_jnl_file_dir_trunk):
        try:
            os.makedirs(tmp_jnl_file_dir_trunk)
            os.chmod(tmp_jnl_file_dir_trunk, 0o777)
        except Exception:
            False, "ITAANSIBLEH-ERR-59851"

    if not os.path.exists(tmp_jnl_file_dir_focus):
        try:
            os.makedirs(tmp_jnl_file_dir_focus)
            os.chmod(tmp_jnl_file_dir_focus, 0o777)
        except Exception:
            False, "ITAANSIBLEH-ERR-59852"

    try:
        shutil.copy(utn_file_dir + "/" + zip_file_name, tmp_jnl_file_dir_focus + "/" + zip_file_name)
    except Exception:
        False, "ITAANSIBLEH-ERR-59853"

    g.local_applogger.debug("ITAANSIBLEH-STD-59801")
    return True, ""


class LocalAppLog():
    __level = ""
    __available_log_level = ["ERROR", "INFO", "DEBUG"]
    __output_filename = ""

    def __init__(self, driver_id, execution_no, level):
        """
        constructor
        """
        execute_path = getAnsibleExecutDirPath(driver_id, execution_no)
        self.__output_filename = "{}/out/error.log".format(execute_path)

        self.set_level(level)

    def set_level(self, level):
        """
        set log level

        Arguments:
            level: (str) "ERROR" | "INFO" | "DEBUG"
        """
        if level not in self.__available_log_level:
            return

        self.__level = level

    def error(self, message):
        """
        output error log

        Arguments:
            message: message for output
        """
        self.out(message)

    def info(self, message):
        """
        output info log

        Arguments:
            message: message for output
        """
        level_index = self.__available_log_level.index(self.__level)
        if level_index <= 0:
            return
        self.out(message)

    def debug(self, message):
        """
        output debug log

        Arguments:
            message: message for output
        """
        level_index = self.__available_log_level.index(self.__level)
        if level_index <= 1:
            return
        self.out(message)

    def __env_message(self):
        """
        make environ info message

        Arguments:
            msg: (str)
        """
        msg = ""

        if "ORGANIZATION_ID" not in g:
            return msg
        msg += "[ORGANIZATION_ID:{}]".format(g.ORGANIZATION_ID)

        if "WORKSPACE_ID" not in g:
            return msg + " "
        msg += "[WORKSPACE_ID:{}]".format(g.WORKSPACE_ID)

        if "USER_ID" not in g:
            return msg + " "
        msg += "[USER_ID:{}]".format(g.USER_ID)

        return msg + " "

    def out(self, message):
        message = self.__env_message() + str(message)
        with open(self.__output_filename, "a") as fd:
            fd.write(message)
