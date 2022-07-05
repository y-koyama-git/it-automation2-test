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

from common_libs.ansible import *

"""
  pioneerの実行に必要な定数定義モジュール
"""
class AnspConst(AnscConst):
    """
      pioneerの実行に必要な定数定義クラス
    """
    vg_driver_id                     = AnscConst.DF_PIONEER_DRIVER_ID
    vg_info_table_name               = "T_ANSC_IF_INFO"
    vg_exe_ins_msg_table_name        = "T_ANSP_EXEC_STS_INST"
    vg_ansible_vars_masterDB         = "T_ANSP_VARIABLE"
    vg_ansible_vars_assignDB         = "T_ANSP_VALUE_AUTOREG"
    vg_ansible_pattern_vars_linkDB   = "T_ANSP_MVMT_VAR_LINK"
    vg_ansible_master_fileDB         = "T_ANSP_MATL_COLL"
    vg_ansible_pho_linkDB            = "T_ANSP_TGT_HOST"
    vg_ansible_pattern_linkDB        = "T_ANSP_MVMT_MATL_LINK"
    vg_ansible_role_packageDB        = ""
    vg_ansible_roleDB                = ""
    vg_ansible_role_varsDB           = ""

    # AnsibleTowerのita_executions_prepare_buildで使用している変数
    vg_tower_driver_type             = "pioneer";
    vg_tower_driver_id               = "ns";
    vg_tower_driver_name             = "pioneer";

    vg_parent_playbook_name          = "playbook.yml";
    vg_log_driver_name               = "Pioneer";

    vg_OrchestratorSubId             = "PIONEER_NS"
    vg_OrchestratorSubId_dir         = "ns"
        
    # 利用用途がないはずなので一旦コメントアウト enomoto 最後に消す
    #zip_temp_save_dir               = $root_dir_path . '/temp'
    #vg_exe_ins_input_file_dir       = $root_dir_path . "/uploadfiles/2100020213"
    #vg_exe_ins_result_file_dir      = $root_dir_path . "/uploadfiles/2100020213"
    #vg_ansible_master_file_pkeyITEM = "DIALOG_MATTER_ID"
    #vg_ansible_master_file_nameITEM = "DIALOG_MATTER_FILE"
    #vg_exe_ins_msg_table_jnl_seq    = "C_ANSIBLE_PNS_EXE_INS_MNG_JSQ"
