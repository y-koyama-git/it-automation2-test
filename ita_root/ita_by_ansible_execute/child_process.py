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
from common_libs.common.util import arrange_stacktrace_format

from common_libs.ansible_driver.classes.ansible_common_libs import AnsibleCommonLibs
from common_libs.ansible_driver.classes import AnsrConstClass
from common_libs.driver.functions import operation_LAST_EXECUTE_TIMESTAMP_update

from libs.controll_ansible_agent import DockerMode, KubernetesMode
from libs import common_functions as cm

import os
import traceback
import sys


# ansible共通の定数をロード
ans_const = AnsrConstClass.AnscConst()


def main():
    # v1子プロの開始　[50052] = "[処理]プロシージャ開始 (作業No.:{})";
    g.applogger.debug("instance_execution 開始")  # "ITAANSIBLEH-STD-50052"

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

    # コマンドラインから引数を受け取る["モジュール名", "関数名", "organization_id"]
    myfile_name, execution_no, driver_name = sys.argv
    print("OK")
    print(execution_no)
    print(driver_name)

    # 処理対象の作業インスタンス情報取得(再取得)
    retBool, result = cm.get_execution_process_info(wsDb, execution_no)
    if retBool is False:
        return False, result
    execute_data = result

    instance_execution(wsDb, ansibleAg, execute_data)


def instance_execution(wsDb, ansibleAg, execute_data):
    driver_id = execute_data["DRIVER_ID"]
    # driver_name = execute_data["DRIVER_NAME"]
    execution_no = execute_data["EXECUTION_NO"]
    conductor_instance_id = execute_data["CONDUCTOR_INSTANCE_NO"]

    # ディレクトリを生成
    if driver_id == ans_const.DF_LEGACY_ROLE_DRIVER_ID:
        driver_path = "{}/{}/driver/ansible/legacy_role/{}".format(g.get('ORGANIZATION_ID'), g.get('WORKSPACE_ID'), execution_no)
        container_driver_path = os.environ.get('STORAGEPATH') + driver_path

    work_dir = container_driver_path + "/in"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    work_dir = container_driver_path + "/out"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)
    work_dir = container_driver_path + "/.tmp"
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)

    if not conductor_instance_id:
        conductor_instance_id = "dummy"
    conductor_path = "{}/{}/driver/conducotr/{}".format(g.get('ORGANIZATION_ID'), g.get('WORKSPACE_ID'), conductor_instance_id)
    container_conductor_path = os.environ.get('STORAGEPATH') + conductor_path
    if not os.path.isdir(container_conductor_path):
        os.makedirs(container_conductor_path)

    # 対話ファイルに埋め込まれるリモートログインのパスワード用変数の名前
    vg_dialog_passwd_var_name = "__loginpassword__"
    # 子playbookに埋め込まれるリモートログインのユーザー用変数の名前
    vg_playbook_user_var_name = "__loginuser__"

    # ANSIBLEインタフェース情報
    retBool, result = cm.get_ansible_interface_info(wsDb)
    if retBool is False:
        return False, result
    ansible_interface_info = result

    # Conductorインタフェース情報を取得
    retBool, result = cm.get_conductor_interface_info(wsDb)
    if retBool is False:
        return False, result
    conductor_interface_info = result

    wsDb.db_transaction_start()
    try:
        # 投入オペレーションの最終実施日を更新する
        operation_LAST_EXECUTE_TIMESTAMP_update(execute_data["OPERATION_NO_UAPK"])
        wsDb.db_commit()
    except AppException as e:
        wsDb.db_rollback()

    ansibleAg.container_start_up(execution_no, conductor_instance_id, driver_path, conductor_path)


if __name__ == '__main__':
    main()
