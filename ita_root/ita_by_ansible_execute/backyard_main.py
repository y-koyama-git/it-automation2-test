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
from common_libs.common.dbconnect import DBConnectWs
from common_libs.common.exception import AppException
from common_libs.common.util import get_timestamp, arrange_stacktrace_format

from common_libs.ansible_driver.classes import AnsrConstClass

from libs.controll_ansible_agent import DockerMode, KubernetesMode
from libs import common_functions as cm


import os
import traceback
import subprocess


# ansible共通の定数をロード
ans_const = AnsrConstClass.AnscConst()


def backyard_main(organization_id, workspace_id):
    '''
    ita_by_ansible_execute main logic
    called 実行君
    '''
    g.applogger.debug("ita_by_ansible_execute 開始")  # ITAWDCH-STD-50001

    # container software
    container_base = os.getenv('CONTAINER_BASE')
    if container_base == 'docker':
        ansibleAg = DockerMode(organization_id, workspace_id)
    elif container_base == 'kubernetes':
        ansibleAg = KubernetesMode(organization_id, workspace_id)
    else:
        raise Exception('Not support container base.')

    # db instance
    wsDb = DBConnectWs(g.get('WORKSPACE_ID'))  # noqa: F405

    # 実行中のコンテナの状態確認
    if child_process_exist_check(wsDb, ansibleAg) is False:
        g.applogger.error("作業インスタンスの実行プロセスの起動確認が失敗しました。(作業No.:{})")  # ITAANSIBLEH-ERR-50074

    # 実行中の作業の数を取得
    num_of_run_instance = len(get_running_process(wsDb))

    # 未実行（実行待ち）の作業を実行
    try:
        run_unexecuted(wsDb, num_of_run_instance)
    except Exception as e:
        exception(e)
        pass

    # 終了　全体でエラーがあったら、ITAWDCH-ERR-50002をだして、終了したい
    g.applogger.debug("ITAWDCH-STD-50002")


def child_process_exist_check(wsDb, ansibleAg):
    # 実行中のコンテナの状態確認
    retBool = True

    records = get_running_process(wsDb)
    for rec in records:
        # driver_id = rec["DRIVER_ID"]
        driver_name = rec["DRIVER_NAME"]
        execution_no = rec["EXECUTION_NO"]

        if ansibleAg.is_container_running(execution_no) is False:
            g.applogger.error("作業インスタンスの状態が処理中/実行中でプロセスが存在していない？(作業No.:{}, driver_name:{})".format(execution_no, driver_name))  # ITAANSIBLEH-ERR-50071  # noqaa E501

            # 想定外エラーにする
            try:
                wsDb.db_transaction_start()

                time_stamp = get_timestamp()  # noqa F405
                data = {
                    "EXECUTION_NO": execution_no,
                    "STATUS_ID": ans_const.EXCEPTION,
                    "TIME_END": time_stamp,
                    "LAST_UPDATE_USER": os.environ.get("LAST_UPDATE_USER_ID")
                }
                if rec["TIME_START"] is None:
                    data["TIME_START"] = time_stamp
                wsDb.table_update('T_ANSR_EXEC_STS_INST', [data], 'EXECUTION_NO')
                
                wsDb.db_commit()
                g.applogger.debug("ステータスを想定外エラーに設定しました。(作業No.:{})".format(execution_no))  # ITAANSIBLEH-ERR-50075
            except Exception:
                wsDb.db_rollback()
                g.applogger.error("ステータスを想定外エラーに設定出来ませんでした。(作業No.:{})".format(execution_no))  # ITAANSIBLEH-ERR-50072
                retBool = False

    return retBool


def get_running_process(wsDb):
    # 実行中の作業データを取得
    status_id_list = [ans_const.PREPARE, ans_const.PROCESSING, ans_const.PROCESS_DELAYED]
    prepared_list = list(map(lambda a: "%s", status_id_list))

    condition = 'WHERE `DISUSE_FLAG`=0 AND `STATUS_ID` in ({})'.format(','.join(prepared_list))
    records = wsDb.table_select('V_ANSC_EXEC_STS_INST', condition, status_id_list)

    g.applogger.debug("called get_run_instance")
    return records


def run_unexecuted(wsDb, ansibleAg, num_of_run_instance):
    # 未実行（実行待ち）の作業を実行
    condition = """WHERE `DISUSE_FLAG`=0 AND (
        ( `TIME_BOOK` IS NULL AND `STATUS_ID` = %s ) OR
        ( `TIME_BOOK` <= NOW(6) AND `STATUS_ID` = %s )
    ) ORDER BY TIME_REGISTER ASC"""
    records = wsDb.table_select('V_ANSC_EXEC_STS_INST', condition, [ans_const.NOT_YET, ans_const.RESERVE])

    if len(records) == 0:
        return False, "ITAANSIBLEH-STD-51003"

    # 実行順リストを作成する
    execution_info_datalist = {}
    execution_order_list = []
    
    for rec in records:
        # print(rec)
        execution_no = rec["EXECUTION_NO"]

        # 予約時間or最終更新日+ソート用カラム+作業番号（判別用）でリスト生成
        id = str(rec["LAST_UPDATE_TIMESTAMP"]) + "-" + str(rec["TIME_REGISTER"]) + "-" + execution_no
        if rec["TIME_BOOK"] is not None:
            if rec["LAST_UPDATE_TIMESTAMP"] < rec["TIME_BOOK"]:
                id = str(rec["TIME_BOOK"]) + "-" + str(rec["TIME_REGISTER"]) + "-" + execution_no
        execution_order_list.append(id)
        execution_info_datalist[id] = rec
    # ソート
    # print(execution_order_list)
    execution_order_list.sort()
    # print(execution_order_list)

    # ANSIBLEインタフェース情報
    retBool, result = cm.get_ansible_interface_info(wsDb)
    if retBool is False:
        return False, result
    ansible_interface_info = result
    # 並列実行数
    lv_num_of_parallel_exec = ansible_interface_info['ANSIBLE_NUM_PARALLEL_EXEC']

    # 処理実行順に対象作業インスタンスを実行
    for execution_order in execution_order_list:
        # 並列実行数判定
        if num_of_run_instance >= lv_num_of_parallel_exec:
            break

        num_of_run_instance = num_of_run_instance + 1

        # データを取り出す
        execute_data = execution_info_datalist[execution_order]
        retBool, errCode = instance_prepare(wsDb, ansibleAg, execute_data)
        if retBool is False:
            return False, errCode


def instance_prepare(wsDb, execute_data):
    # 作業を準備

    # driver_id = execute_data["DRIVER_ID"]
    driver_name = execute_data["DRIVER_NAME"]
    execution_no = execute_data["EXECUTION_NO"]
    # conductor_instance_id = execute_data["CONDUCTOR_INSTANCE_NO"]

    # 処理対象の作業インスタンス情報取得(再取得)
    retBool, result = cm.get_execution_process_info(wsDb, execution_no)
    if retBool is False:
        return False, result
    execute_data = result

    # 未実行状態で緊急停止出来るようにしているので
    # 未実行状態かを判定
    if execute_data["STATUS_ID"] != ans_const.NOT_YET or execute_data["STATUS_ID"] != ans_const.RESERVE:
        return False, "Emergency stop in unexecuted state.(execution_no: $tgt_execution_no)"

    wsDb.db_transaction_start()

    # 処理対象の作業インスタンスのステータスを準備中に設定
    data = {
        "EXECUTION_NO": execution_no,
        "STATUS_ID": ans_const.PREPARE,
        "LAST_UPDATE_USER": os.environ.get("LAST_UPDATE_USER_ID")
    }
    wsDb.table_update('T_ANSR_EXEC_STS_INST', [data], 'EXECUTION_NO')

    wsDb.db_commit()

    # 子プロセスにして、実行
    g.applogger.debug("ITAANSIBLEH-STD-50077 (作業No.:{}, driver_name:{})".format(driver_name, execution_no))

    command = ["python3", "child_process.py", execution_no, driver_name]
    child_process = subprocess.run(command, capture_output=True)
    # check result
    print("return_code: %s" % child_process.returncode)
    print("stdout:\n%s" % child_process.stdout.decode('utf-8'))
    print("stderr:\n%s" % child_process.stderr.decode('utf-8'))
    child_process.check_returncode()

    g.applogger.debug("ITAANSIBLEH-STD-50078 (作業No.:{}, driver_name:{})".format(driver_name, execution_no))

    return True, ""


def app_exception(e):
    '''
    called when AppException occured
    
    Argument:
        e: AppException
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            args = args[0].args
        elif isinstance(args[0], Exception):
            return exception(args[0])
        else:
            is_arg = True

    # catch - raise AppException("xxx-xxxxx", log_format), and get message
    result_code, log_msg_args, api_msg_args = args
    log_msg = g.appmsg.get_log_message(result_code, log_msg_args)
    g.applogger.error("[error]{}".format(log_msg))


def exception(e):
    '''
    called when Exception occured
    
    Argument:
        e: Exception
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            return app_exception(args[0])
        elif isinstance(args[0], Exception):
            args = args[0].args
        else:
            is_arg = True

    # catch - other all error
    t = traceback.format_exc()
    # g.applogger.exception("[error]")
    g.applogger.error("[error] {}".format(arrange_stacktrace_format(t)))
