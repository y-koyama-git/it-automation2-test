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
"""
Ansible共通module
"""

import json
import os
import subprocess
import inspect
import hashlib
import re
from tkinter import W

from flask import g
from pathlib import Path
from pprint import pprint

from common_libs.common import *
from common_libs.loadtable import *
from common_libs.common.exception import *
from .AnsibleMakeMessage import AnsibleMakeMessage
from .AnscConstClass import AnscConst
from .WrappedStringReplaceAdmin import WrappedStringReplaceAdmin


class AnsibleCommonLibs():
    """
    Ansible共通class
    F0001  set_run_mode
    F0002  GetRunMode
    F0003  getCPFVarsMaster
    F0004  chkCPFVarsMasterReg
    F0005  getTPFVarsMaster
    F0006  chkTPFVarsMasterReg
    F0007  getGBLVarsMaster
    F0008  chkGBLVarsMasterReg
    F0009  CommonVarssAanalys
    F0010  selectDBRecodes
    """
    
    # 定数定義
    LV_RUN_MODE = ""
    
    # ローカル変数(全体)宣言
    lv_val_assign_tbl = 'T_ANSR_VALUE_AUTOREG'
    lv_pattern_link_tbl = 'T_ANSR_MVMT_MATL_LINK'
    lv_ptn_vars_link_tbl = 'T_ANSR_MVMT_VAR_LINK'
    lv_member_col_comb_tbl = 'T_ANSR_NESTVAR_MEMBER_COL_COMB'
    lv_array_member_tbl = 'T_ANSR_NESTVAR_MEMBER'
    strCurTableVarsAss = 'T_ANSR_VALUE'
    strJnlTableVarsAss = strCurTableVarsAss + "_JNL"
    strSeqOfCurTableVarsAss = strCurTableVarsAss + "_RIC"
    strSeqOfJnlTableVarsAss = strCurTableVarsAss + "_JSQ"
    vg_FileUPloadColumnBackupFilePath = ""
    db_update_flg = False
    g_null_data_handling_def = ""
    warning_flag = 0
    error_flag = 0
    

    def __init__(self, run_mode=AnscConst.LC_RUN_MODE_STD):
        global LV_RUN_MODE
        LV_RUN_MODE = run_mode

    def set_run_mode(self, run_mode):
        """
        処理モードを変数定義ファイルチェックに設定

        Arguments:
            run_mode: 処理モード　LC_RUN_MODE_STD/LC_RUN_MODE_VARFILE
        """
        global LV_RUN_MODE
        LV_RUN_MODE = run_mode

    def get_run_mode(self):
        """
        処理モード取得

        returns:
            処理モード　LC_RUN_MODE_STD/LC_RUN_MODE_VARFILE
        """
        return LV_RUN_MODE

    def get_cpf_vars_master(self, in_cpf_var_name, WS_DB):
        """
        ファイル管理の情報をデータベースより取得する。
        
        Arguments:
            in_cpf_var_name: CPF変数名
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_cpf_key: PKey格納変数
            in_cpf_file_name: ファイル格納変数
        """
        
        in_cpf_key = ""
        in_cpf_file_name = ""
        
        where = "WHERE  CONTENTS_FILE_VARS_NAME = '" + in_cpf_var_name + "' and DISUSE_FLAG = '0'"
        
        data_list = WS_DB.table_select("T_ANSC_CONTENTS_FILE", where, [])

        if len(data_list) < 1:
            return True, in_cpf_key, in_cpf_file_name
        
        for data in data_list:
            in_cpf_key = data["CONTENTS_FILE_ID"]
            in_cpf_file_name = data["CONTENTS_FILE"]
        
        return True, in_cpf_key, in_cpf_file_name

    def chk_cpf_vars_master_reg(self, ina_cpf_vars_list, WS_DB):
        """
        CPF変数がファイル管理に登録されているか判定
        
        Arguments:
            ina_cpf_vars_list: CPF変数リスト
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            tmp_ina_cpf_vars_list: CPF変数リスト
            in_errmsg: エラーメッセージ
        """
        bool_ret = True
        fatal_error = False
        in_errmsg = ""
        tmp_ina_cpf_vars_list = {}
        
        ams = AnsibleMakeMessage()
        
        # CPF変数がファイル管理に登録されているか判定
        for role_name, tgt_file_list in ina_cpf_vars_list.items():
            for tgt_file, line_no_list in tgt_file_list.items():
                for line_no, cpf_var_name_list in line_no_list.items():
                    for cpf_var_name, dummy in cpf_var_name_list.items():
                        
                        # CPF変数名からファイル管理とPkeyを取得する。
                        ret = self.get_cpf_vars_master(cpf_var_name, WS_DB)
                        
                        # CPF変数名が未登録の場合
                        if ret[1] == "":
                            if in_errmsg != "":
                                in_errmsg = in_errmsg + "\n"
                            
                            in_errmsg = in_errmsg + ams.AnsibleMakeMessage(self.get_run_mode(), "MSG-10408", [role_name, tgt_file, line_no, cpf_var_name])
                            bool_ret = False
                            break
                        else:
                            # ファイル名が未登録の場合
                            if ret[2] == "":
                                if in_errmsg != "":
                                    in_errmsg = in_errmsg + "\n"
                            
                                in_errmsg = in_errmsg + ams.AnsibleMakeMessage(self.get_run_mode(), "MSG-10409", [role_name, tgt_file, line_no, cpf_var_name])
                                bool_ret = False
                                continue
                        
                        if role_name not in tmp_ina_cpf_vars_list:
                            tmp_ina_cpf_vars_list[role_name] = {}
                        if tgt_file not in tmp_ina_cpf_vars_list[role_name]:
                            tmp_ina_cpf_vars_list[role_name][tgt_file] = {}
                        if line_no not in tmp_ina_cpf_vars_list[role_name][tgt_file]:
                            tmp_ina_cpf_vars_list[role_name][tgt_file][line_no] = {}
                        if cpf_var_name not in tmp_ina_cpf_vars_list[role_name][tgt_file][line_no]:
                            tmp_ina_cpf_vars_list[role_name][tgt_file][line_no][cpf_var_name] = {}

                        tmp_ina_cpf_vars_list[role_name][tgt_file][line_no][cpf_var_name]['CONTENTS_FILE_ID'] = ret[1]
                        tmp_ina_cpf_vars_list[role_name][tgt_file][line_no][cpf_var_name]['CONTENTS_FILE'] = ret[2]
                        
                    if fatal_error:
                        break
                    
                if fatal_error:
                    break
            
            if fatal_error:
                break

        return bool_ret, tmp_ina_cpf_vars_list, in_errmsg
    
    def get_tpf_vars_master(self, in_tpf_var_name, WS_DB):
        """
        テンプレート管理の情報をデータベースより取得する。
        
        Arguments:
            in_cpf_var_name: TPF変数名
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            ina_row: 登録情報
        """
        
        where = "WHERE  ANS_TEMPLATE_VARS_NAME = '" + in_tpf_var_name + "' AND DISUSE_FLAG = '0'"
        
        data_list = WS_DB.table_select("T_ANSC_TEMPLATE_FILE", where, [])
        
        ina_row = []
        
        if len(data_list) < 1:
            return True, ina_row
        
        for data in data_list:
            ina_row.append(data)
        
        return True, ina_row
    
    def chk_tpf_vars_master_reg(self, ina_tpf_vars_list, WS_DB):
        """
        TPF変数がテンプレート管理に登録されているか判定
        
        Arguments:
            ina_tpf_vars_list: TPF変数リスト
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            ina_tpf_vars_list: TPF変数リスト
            in_errmsg: エラーメッセージ
        """
        
        bool_ret = True
        in_errmsg = ""
        fatal_error = False
        tmp_ina_tpf_vars_list = {}
        
        ams = AnsibleMakeMessage()
        
        # TPF変数にファイル管理に登録されているか判定
        for role_name, tgt_file_list in ina_tpf_vars_list.items():
            for tgt_file, line_no_list in tgt_file_list.items():
                for line_no, tpf_var_name_list in line_no_list.items():
                    for tpf_var_name, dummy in tpf_var_name_list.items():
                        ret = self.get_tpf_vars_master(tpf_var_name, WS_DB)
                        
                        tpf_key = ""
                        tpf_file_name = ""
                        role_only_flag = ""
                        vars_list = ""
                        var_struct_anal_json_string = ""
                        
                        if len(ret[1]) != 0:
                            tpf_key = ret[1][0]['ANS_TEMPLATE_ID']
                            tpf_file_name = ret[1][0]['ANS_TEMPLATE_FILE']
                            role_only_flag = ret[1][0]['ROLE_ONLY_FLAG']
                            vars_list = ret[1][0]['VARS_LIST']
                            var_struct_anal_json_string = ret[1][0]['VARSTRUCT_ANAL_JSON_STRING']
                        
                        # TPF変数名が未登録の場合
                        if tpf_key == "":
                            if in_errmsg != "":
                                in_errmsg = in_errmsg + "\n"
                            
                            in_errmsg = in_errmsg + ams.AnsibleMakeMessage(self.get_run_mode(), "MSG-10559", [role_name, tgt_file, line_no, tpf_var_name])
                            bool_ret = False
                            continue
                        
                        else:
                            if tpf_var_name == "":
                                if in_errmsg != "":
                                    in_errmsg = in_errmsg + "\n"
                            
                                in_errmsg = in_errmsg + ams.AnsibleMakeMessage(self.get_run_mode(), "MSG-10557", [role_name, tgt_file, line_no, tpf_var_name])
                                bool_ret = False
                                continue
                        
                        if role_name not in tmp_ina_tpf_vars_list:
                            tmp_ina_tpf_vars_list[role_name] = {}
                        if tgt_file not in tmp_ina_tpf_vars_list[role_name]:
                            tmp_ina_tpf_vars_list[role_name][tgt_file] = {}
                        if line_no not in tmp_ina_tpf_vars_list[role_name][tgt_file]:
                            tmp_ina_tpf_vars_list[role_name][tgt_file][line_no] = {}
                        if tpf_var_name not in tmp_ina_tpf_vars_list[role_name][tgt_file][line_no]:
                            tmp_ina_tpf_vars_list[role_name][tgt_file][line_no][tpf_var_name] = {}
                        
                        tmp_ina_tpf_vars_list[role_name][tgt_file][line_no][tpf_var_name]['CONTENTS_FILE_ID'] = tpf_key
                        tmp_ina_tpf_vars_list[role_name][tgt_file][line_no][tpf_var_name]['CONTENTS_FILE'] = tpf_file_name
                        tmp_ina_tpf_vars_list[role_name][tgt_file][line_no][tpf_var_name]['ROLE_ONLY_FLAG'] = role_only_flag
                        tmp_ina_tpf_vars_list[role_name][tgt_file][line_no][tpf_var_name]['VARS_LIST'] = vars_list
                        tmp_ina_tpf_vars_list[role_name][tgt_file][line_no][tpf_var_name]['VAR_STRUCT_ANAL_JSON_STRING'] = var_struct_anal_json_string
                        
                        if fatal_error:
                            break
                        
                    if fatal_error:
                        break
                
                if fatal_error:
                    break
                
        return bool_ret, tmp_ina_tpf_vars_list, in_errmsg
    
    def get_gbl_vars_master(self, in_gbl_var_name, WS_DB):
        """
        グローバル管理の情報をデータベースより取得する。
        
        Arguments:
            in_gbl_var_name: GBL変数名
            WS_DB: WorkspaceDBインスタンス
    
        Returns:
            is success:(bool)
            in_gbl_key: PKey格納変数
        """

        in_gbl_key = ""
        
        where = "WHERE VARS_NAME = '" + in_gbl_var_name + "' AND DISUSE_FLAG = '0'"
        
        data_list = WS_DB.table_select("T_ANSC_GLOBAL_VAR", where, [])
        
        if len(data_list) < 1:
            return True, in_gbl_key
        
        for data in data_list:
            in_gbl_key = data['GBL_VARS_NAME_ID']
        
        return True, in_gbl_key
        
    def chk_gbl_vars_master_reg(self, ina_gbl_vars_list, WS_DB):
        """
        GBL変数がファイル管理に登録されているか判定
        
        Arguments:
            ina_gbl_vars_list: GBL変数リスト
            WS_DB: WorkspaceDBインスタンス
    
        Returns:
            is success:(bool)
            ina_gbl_vars_list: GBL変数リスト
            in_errmsg: エラーメッセージ
        """
        
        bool_ret = True
        fatal_error = False
        in_errmsg = ""
        tmp_ina_gbl_vars_list = {}
        
        ams = AnsibleMakeMessage()
        
        # GBL変数にファイル管理に登録されているか判定
        for role_name, tgt_file_list in ina_gbl_vars_list.items():
            for tgt_file, line_no_list in tgt_file_list.items():
                for line_no, gbl_var_name_list in line_no_list.items():
                    for gbl_var_name, dummy in gbl_var_name_list.items():
                        
                        ret = self.get_gbl_vars_master(gbl_var_name, WS_DB)
                        
                        # GBL変数名が未登録の場合
                        if ret[1] == "":
                            if in_errmsg != "":
                                in_errmsg = in_errmsg + "\n"
                            
                            in_errmsg = in_errmsg + ams.AnsibleMakeMessage(self.get_run_mode(), "MSG-10571", [role_name, tgt_file, line_no, gbl_var_name])
                            bool_ret = False
                            break
                        
                        if role_name not in tmp_ina_gbl_vars_list:
                            tmp_ina_gbl_vars_list[role_name] = {}
                        if tgt_file not in tmp_ina_gbl_vars_list[role_name]:
                            tmp_ina_gbl_vars_list[role_name][tgt_file] = {}
                        if line_no not in tmp_ina_gbl_vars_list[role_name][tgt_file]:
                            tmp_ina_gbl_vars_list[role_name][tgt_file][line_no] = {}
                        if line_no not in tmp_ina_gbl_vars_list[role_name][tgt_file][line_no]:
                            tmp_ina_gbl_vars_list[role_name][tgt_file][line_no][gbl_var_name] = {}
    
                        tmp_ina_gbl_vars_list[role_name][tgt_file][line_no][gbl_var_name]['CONTENTS_FILE_ID'] = ret[1]
                        
                    if fatal_error:
                        break
                    
                if fatal_error:
                    break
            
            if fatal_error:
                break
        
        return bool_ret, ina_gbl_vars_list, in_errmsg
    
    def common_varss_aanalys(self, in_filename, out_filename, fillter_vars=False):
        """
        Legacy/PioneerでアップロードされるPlaybook素材よの共通変数を抜き出す
        FileUploadColumn:checkTempFileBeforeMoveOnPreLoadイベント用
        
        Arguments:
            in_filename: アップロードされたデータが格納されているファイル名

        Returns:
            ret_array: is success, エラーメッセージ
        """

        bool_ret = True
        
        playbook_data_string = open(in_filename)
        
        local_vars = []
        vars_line_array = []
        vars_array = []
        str_err_msg = None
        
        wsra = WrappedStringReplaceAdmin()
        # インベントリ追加オプションに定義されている変数を抜き出す。
        ret = wsra.SimpleFillterVerSearch("CPF_", playbook_data_string, vars_line_array, vars_array, local_vars, fillter_vars)

        cpf_vars_list = []
        for vars_info, no in ret[1]:
            for var_name, line_no in vars_info:
                cpf_vars_list['dummy']['Upload file'][line_no][var_name] = 0
                
        ret = wsra.SimpleFillterVerSearch("TPF_", playbook_data_string, vars_line_array, vars_array, local_vars, fillter_vars)
        
        tpf_vars_list = []
        for vars_info, no in ret[1]:
            for var_name, line_no in vars_info:
                tpf_vars_list['dummy']['Upload file'][line_no][var_name] = 0
        
        ret = wsra.SimpleFillterVerSearch("GBL_", playbook_data_string, vars_line_array, vars_array, local_vars, fillter_vars)
        
        gbl_vars_list = []
        for vars_info, no in ret[1]:
            for var_name, line_no in vars_info:
                gbl_vars_list['dummy']['Upload file'][line_no][var_name] = 0
        
        gbl_vars = '1'
        cpf_vars = '2'
        tpf_vars = '3'
        save_vars_list = []
        save_vars_list[gbl_vars] = []
        save_vars_list[cpf_vars] = []
        save_vars_list[tpf_vars] = []
        
        if bool_ret:
            for tgt_file_list, role_name in cpf_vars_list:
                for line_no_list, tgt_file in tgt_file_list:
                    for cpf_var_name_list, line_no in line_no_list:
                        for dummy, cpf_var_name in cpf_var_name_list:
                            save_vars_list[cpf_vars][cpf_var_name] = 0
        
        if bool_ret:
            for tgt_file_list, tgt_file_list in tpf_vars_list:
                for line_no_list, tgt_file in tgt_file_list:
                    for tpf_var_name_list, line_no in line_no_list:
                        for dummy, tpf_var_name in tpf_var_name_list:
                            save_vars_list[tpf_vars][tpf_var_name] = 0
        
        if bool_ret:
            for tgt_file_list, tgt_file_list in gbl_vars_list:
                for line_no_list, tgt_file in tgt_file_list:
                    for gbl_var_name_list, line_no in line_no_list:
                        for dummy, gbl_var_name in gbl_var_name_list:
                            save_vars_list[gbl_var_name][tpf_var_name] = 0
                            
        if bool_ret:
            json_encode = json.dump(save_vars_list)
            path = out_filename
            
            try:
                Path(path).write_text(json_encode, encoding="utf-8")
            except Exception:
                bool_ret = False
                str_err_msg = g.appmsg.get_api_message('MSG-10570', [])
        
        if len(str_err_msg) != 0:
            str_err_msg.replace('\n', '<BR>')
        
        ret_array = list[bool_ret, str_err_msg]
        
        return ret_array
    
    def select_db_recodes(self, in_sql, in_key, WS_DB):
        """
        指定されたデータベースの全有効レコードを取得する。
        
        Arguments:
            in_sql: SQL
            in_key: 登録レコードの配列のキー項目
            WS_DB: WorkspaceDBインスタンス

        Returns:
            ina_row: 取得レコードの配列
        """
        
        data_list = WS_DB.sql_execute(in_sql, [])
        
        ina_row = {}
        for data in data_list:
            ina_row[data[in_key]] = data
        
        return ina_row
    
    def GetDataFromParameterSheet(self, exec_type, operation_id, movement_id, WS_DB):
        """
        代入値自動登録とパラメータシートを抜く
        """
        
        global g_null_data_handling_def
        global warning_flag
        global error_flag
        
        # 処理区分が変数抜出処理
        if exec_type == '2':
            template_list = self.getTemplateVarList(WS_DB)
            host_list = self.getTargetHostList(WS_DB)
            
            return True, template_list, host_list
        
        # インターフェース情報からNULLデータを代入値管理に登録するかのデフォルト値を取得する。
        ret = self.getIFInfoDB(WS_DB)

        if ret[0] == 0:
            error_flag = 1
            raise ValidationException(ret[2])
        
        lv_if_info = ret[1]
        g_null_data_handling_def = lv_if_info["NULL_DATA_HANDLING_FLG"]
        
        # 代入値自動登録設定からカラム毎の変数の情報を取得
        # トレースメッセージ
        traceMsg = g.appmsg.get_api_message("MSG-10804")
        frame = inspect.currentframe().f_back
        g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        ret = self.readValAssign(WS_DB)
        
        if ret[0] == 0:
            error_flag = 1
            errorMsg = g.appmsg.get_api_message("MSG-10353")
            raise ValidationException(errorMsg)
        
        lv_tableNameToMenuIdList = ret[1]
        lv_tabColNameToValAssRowList = ret[2]
        lv_tableNameToPKeyNameList = ret[3]
        
        # 紐付メニューへのSELECT文を生成する。
        ret = self.createQuerySelectCMDB(lv_tableNameToMenuIdList, lv_tabColNameToValAssRowList, lv_tableNameToPKeyNameList, WS_DB)
        # 代入値紐付メニュー毎のSELECT文配列
        lv_tableNameToSqlList = ret
        
        # 紐付メニューから具体値を取得する。
        traceMsg = g.appmsg.get_api_message("MSG-10805")
        frame = inspect.currentframe().f_back
        g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        ret = self.getCMDBdata(lv_tableNameToSqlList, lv_tableNameToMenuIdList, lv_tabColNameToValAssRowList, WS_DB)
        lv_varsAssList = ret[0]
        lv_arrayVarsAssList = ret[1]
        warning_flag = ret[2]
        
        # トランザクション開始 
        traceMsg = g.appmsg.get_api_message("MSG-10785")
        frame = inspect.currentframe().f_back
        g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        WS_DB.db_transaction_start()
        
        # 代入値管理のデータを全件読み込む
        ret = self.getVarsAssignRecodes(WS_DB)
        if ret[0] == 0:
            # 異常フラグON  例外処理へ
            error_flag = 1
            errorMsg = g.appmsg.get_api_message("MSG-10467")
            raise ValidationException(errorMsg)
        
        lv_VarsAssignRecodes = ret[1]
        lv_ArryVarsAssignRecodes = [2]
        
        # 作業対象ホストに登録が必要な配列初期化
        lv_phoLinkList = {}
        
        # 一般変数・複数具体値変数を紐付けている紐付メニューの具体値を代入値管理に登録
        # トレースメッセージ
        traceMsg = g.appmsg.get_api_message("MSG-10833")
        frame = inspect.currentframe().f_back
        g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        for varsAssRecord in lv_varsAssList.values():
            # 処理対象外のデータかを判定
            if varsAssRecord['STATUS'] == 0:
                continue
            if not operation_id == varsAssRecord['OPERATION_ID'] or not movement_id == varsAssRecord['MOVEMENT_ID']:
                continue
            
            # 代入値管理に具体値を登録
            ret = self.addStg1StdListVarsAssign(varsAssRecord, lv_tableNameToMenuIdList, lv_VarsAssignRecodes)
            lv_VarsAssignRecodes = ret[1]
            if ret[0] == 0:
                error_flag = 1
                # FileUploadColumnのディレクトリを元に戻す
                ret = FileUPloadColumnRestore()
                
                errorMsg = g.appmsg.get_api_message("MSG-10466")
                raise ValidationException(errorMsg)
            
            # 多次元変数を紐付けている紐付メニューの具体値を代入値管理に登録
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10834")
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            for varsAssRecord in lv_arrayVarsAssList.values():
                # 処理対象外のデータかを判定
                if varsAssRecord['STATUS'] == 0:
                    continue
                
                ret = self.addStg1ArrayVarsAssign(varsAssRecord, lv_tableNameToMenuIdList, lv_ArryVarsAssignRecodes)
                lv_ArryVarsAssignRecodes = ret[1]
                if ret[0] == 0:
                    # FileUploadColumnのディレクトリを元に戻す
                    ret = self.FileUPloadColumnRestore()
                    error_flag = 1
                    errorMsg = g.appmsg.get_api_message("MSG-10441")
                    raise ValidationException(errorMsg)
                
                # 作業対象ホストに登録が必要な情報を退避
                lv_phoLinkList[varsAssRecord['OPERATION_ID']] = {}
                lv_phoLinkList[varsAssRecord['OPERATION_ID']][varsAssRecord['MOVEMENT_ID']] = {}
                lv_phoLinkList[varsAssRecord['OPERATION_ID']][varsAssRecord['MOVEMENT_ID']][varsAssRecord['SYSTEM_ID']] = {}
                
            # 代入値管理から不要なデータを削除する
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10809")
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            ret = self.deleteVarsAssign(lv_VarsAssignRecodes)
            if ret[0] == 0:
                # FileUploadColumnのディレクトリを元に戻す
                ret = self.FileUPloadColumnRestore()
                error_flag = 1
                errorMsg = g.appmsg.get_api_message("MSG-10372")
                raise ValidationException(errorMsg)
            
            ret = self.deleteVarsAssign(lv_ArryVarsAssignRecodes)
            if ret[0] == 0:
                # FileUploadColumnのディレクトリを元に戻す
                ret = self.FileUPloadColumnRestore()
                error_flag = 1
                errorMsg = g.appmsg.get_api_message("MSG-10372")
                raise ValidationException(errorMsg)
            
            del lv_tableNameToMenuIdList
            del lv_VarsAssignRecodes
            del lv_ArryVarsAssignRecodes
            del lv_varsAssList
            del lv_arrayVarsAssList
            
            # コミット(レコードロックを解除)
            WS_DB.db_commit()
            
            # トランザクション終了
            WS_DB.db_transaction_end(True)
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10785")
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            WS_DB.db_transaction_start()
            
            # 対象ホスト管理のデータを全件読込
            lv_PhoLinkRecodes = {}
            ret = self.getPhoLinkRecodes()
            lv_PhoLinkRecodes = ret[1]
            
            # 代入値管理で登録したオペ+作業パターン+ホストが作業対象ホストに登録されているか判定し、未登録の場合は登録する
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10810")
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            for ope_id, ptn_list in lv_phoLinkList.items():
                for ptn_id, host_list in ptn_list.items():
                    for host_id, access_auth in host_list.items():
                        lv_phoLinkData = {'OPERATION_ID': ope_id, 'MOVEMENT_ID': ptn_id, 'SYSTEM_ID': host_id}
                        ret = self.addStg1PhoLink(lv_phoLinkData, lv_PhoLinkRecodes)
                        lv_PhoLinkRecodes = ret[1]
                        
                        if ret[0] == 0:
                            error_flag = 1
                            errorMsg = g.appmsg.get_api_message("MSG-10373")
                            raise ValidationException(errorMsg)
            
            # 作業対象ホストから不要なデータを削除する
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10811")
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            ret = self.deletePhoLink(lv_PhoLinkRecodes)
            if ret == 0:
                error_flag = 1
                errorMsg = g.appmsg.get_api_message("MSG-10374")
                raise ValidationException(errorMsg)
            
            del lv_phoLinkList
            del lv_PhoLinkRecodes
        
        # コミット(レコードロックを解除)
        # トランザクション終了
        WS_DB.db_transaction_end(True)
        
        return True
        
    def getAnsible_RolePackage_file(self, in_dir, in_pkey, in_filename):
        intNumPadding = 10
        
        # sible実行時の子Playbookファイル名は Pkey(10桁)-子Playbookファイル名 する
        file = in_dir + '/' + in_pkey.rjust(intNumPadding, '0') + '/' + in_filename
        return file
    
    def getPhoLinkRecodes(self, in_PhoLinkRecodes, WS_DB):
        """
        作業対象ホストの全データ読込
        
        Arguments:
            in_PhoLinkRecodes: 作業対象ホストの全データ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_PhoLinkRecodes: 作業対象ホストの全データ配列
        """
        
        global db_valautostup_user_id
        global strCurTablePhoLnk
        global strJnlTablePhoLnk
        global strSeqOfCurTablePhoLnk
        global strSeqOfJnlTablePhoLnk
        global arrayConfigOfPhoLnk
        global arrayValueTmplOfPhoLnk
        
        where = "WHERE PHO_LINK_ID <> '0'"
        WS_DB.table_lock(["T_ANSR_TGT_HOST"])
        data_list = WS_DB.table_select("T_ANSR_TGT_HOST", where)
        
        for row in data_list.values():
            key = row["OPERATION_ID"] + "_"
            key += row["MOVEMENT_ID"] + "_"
            key += row["SYSTEM_ID"] + "_"
            key += row["DISUSE_FLAG"] + "_"
            
            in_PhoLinkRecodes[key] = row
        
        return True, in_PhoLinkRecodes
    
    def addStg1PhoLink(self, in_phoLinkData, in_PhoLinkRecodes, WS_DB):
        """
        作業対象ホストの全データ読込
        
        Arguments:
            in_phoLinkData: 作業対象ホスト更新情報配列
            in_PhoLinkRecodes: 作業対象ホストの全データ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_PhoLinkRecodes: 作業対象ホストの全データ配列
        """
        global db_valautostup_user_id
        global strCurTablePhoLnk
        global strJnlTablePhoLnk
        global strSeqOfCurTablePhoLnk
        global strSeqOfJnlTablePhoLnk
        global arrayConfigOfPhoLnk
        global arrayValueTmplOfPhoLnk
        
        key = in_phoLinkData["OPERATION_ID"] + "_"
        key += in_phoLinkData["MOVEMENT_ID"] + "_"
        key += in_phoLinkData["SYSTEM_ID"] + "_0"
        
        objmenu = load_table.loadTable(WS_DB, "20408")
        
        if key in in_PhoLinkRecodes:
            # 廃止レコードを復活または新規レコード追加
            ret = self.addStg2PhoLink(in_phoLinkData, in_PhoLinkRecodes)
            in_PhoLinkRecodes = ret[1]
            return ret[0]
        else:
            tgt_row = in_PhoLinkRecodes[key]
            # 同一なので処理終了
            del in_PhoLinkRecodes[key]
            
            # 最終更新者が自分でない場合、更新処理はスキップする
            if not tgt_row["LAST_UPDATE_USER"] == db_valautostup_user_id:
                # トレースメッセージ
                traceMsg = g.appmsg.get_api_message("MSG-10828", [tgt_row['PHO_LINK_ID']])
                frame = inspect.currentframe().f_back
                g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
                
                # 更新処理はスキップ
                return True
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10847", [tgt_row['PHO_LINK_ID'],
                                                        tgt_row['OPERATION_ID'],
                                                        tgt_row['MOVEMENT_ID'],
                                                        tgt_row['SYSTEM_ID']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            tgt_row['DISUSE_FLAG'] = "0"
            tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
            
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "note": tgt_row['NOTE'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {},
                "type":"Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['PHO_LINK_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        
        return status_code, in_PhoLinkRecodes

    def addStg2PhoLink(self, in_phoLinkData, in_PhoLinkRecodes, WS_DB):
        """
        作業対象ホストの廃止レコードを復活または新規レコード追加
        
        Arguments:
            in_phoLinkData: 作業対象ホスト更新情報配列
            in_PhoLinkRecodes: 作業対象ホストの全データ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_PhoLinkRecodes: 作業対象ホストの全データ配列
        """
        global db_valautostup_user_id
        global strCurTablePhoLnk
        global strJnlTablePhoLnk
        global strSeqOfCurTablePhoLnk
        global strSeqOfJnlTablePhoLnk
        global arrayConfigOfPhoLnk
        global arrayValueTmplOfPhoLnk
        
        arrayValue = arrayValueTmplOfVarA
        
        key = in_phoLinkData["OPERATION_ID"] + "_"
        key += in_phoLinkData["MOVEMENT_ID"] + "_"
        key += in_phoLinkData["SYSTEM_ID"] + "_1"
        
        objmenu = load_table.loadTable(WS_DB, "20408")
        
        if key in in_PhoLinkRecodes:
            action = "INSERT"
            tgt_row = arrayValue
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10821", [in_phoLinkData['OPERATION_ID'], in_phoLinkData["MOVEMENT_ID"], in_phoLinkData["SYSTEM_ID"]])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        else:
            # 廃止なので復活する。
            action = "UPDATE"
            tgt_row = in_PhoLinkRecodes[key]
            
            del in_PhoLinkRecodes[key]
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10822", [in_phoLinkData['OPERATION_ID'], in_phoLinkData["MOVEMENT_ID"], in_phoLinkData["SYSTEM_ID"]])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        if action == "INSERT":
            # 更新対象の作業対象ホスト管理主キー値を退避
            inout_phoLinkId = str(WS_DB._uuid_create())
            
            # 登録する情報設定
            tgt_row['PHO_LINK_ID'] = inout_phoLinkId
            tgt_row['OPERATION_ID'] = in_phoLinkData['OPERATION_ID']
            tgt_row['MOVEMENT_ID'] = in_phoLinkData['MOVEMENT_ID']
            tgt_row['SYSTEM_ID'] = in_phoLinkData['SYSTEM_ID']
        
        tgt_row['DISUSE_FLAG'] = "0"
        tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
        
        if action == "INSERT":
            parameter = {
                "pho_link_id": tgt_row['PHO_LINK_ID'],
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "note": tgt_row['NOTE'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {},
                "type": "Register"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters)
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        elif action == "UPDATE":
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "note": tgt_row['NOTE'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {},
                "type": "Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['PHO_LINK_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        
        return True, in_PhoLinkRecodes
    
    def deletePhoLink(self, in_PhoLinkRecodes, WS_DB):
        """
        作業管理対象ホスト管理から不要なレコードを廃止
        
        Arguments:
            in_PhoLinkRecodes: 不要な作業管理対象ホストの配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
        """
        global db_valautostup_user_id
        global strCurTablePhoLnk
        global strJnlTablePhoLnk
        global strSeqOfCurTablePhoLnk
        global strSeqOfJnlTablePhoLnk
        global arrayConfigOfPhoLnk
        global arrayValueTmplOfPhoLnk
        
        objmenu = load_table.loadTable(WS_DB, "20408")
        
        for key, tgt_row in in_PhoLinkRecodes.items():
            if tgt_row['DISUSE_FLAG'] == '1':
                # 廃止レコードはなにもしない。
                continue
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10823", [tgt_row['PHO_LINK_ID']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            # 最終更新者が自分でない場合、廃止処理はスキップする。
            if not tgt_row['LAST_UPDATE_USER'] == db_valautostup_user_id:
                # トレースメッセージ
                traceMsg = g.appmsg.get_api_message("MSG-10828", [tgt_row['PHO_LINK_ID']])
                frame = inspect.currentframe().f_back
                g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
                
                #更新処理はスキップ
                continue
            
            tgt_row['DISUSE_FLAG'] = "0"
            tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
            
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "note": tgt_row['NOTE'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {},
                "type":"Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['PHO_LINK_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
            
            return True
    
    def createQuerySelectCMDB(self, in_tableNameToMenuIdList, in_tabColNameToValAssRowList, in_tableNameToPKeyNameList, WS_DB):
        """
        代入値紐付メニューへのSELECT文を生成する。
        
        Arguments:
            in_tableNameToMenuIdList: テーブル名配列
            in_tabColNameToValAssRowList: テーブル名+カラム名配列
            in_tableNameToPKeyNameList: テーブル主キー名配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            defvarsList: 抽出した変数
        """
        
        opeid_chk_sql = "( SELECT \n"
        opeid_chk_sql += " OPERATION_ID \n"
        opeid_chk_sql += " FROM T_COMN_OPERATION \n"
        opeid_chk_sql += " WHERE OPERATION_ID = TBL_A.OPERATION_ID AND \n"
        opeid_chk_sql += " DISUSE_FLAG = '0' \n"
        opeid_chk_sql += ") AS  OPERATION_ID , \n"
        
        # 機器一覧にホストが登録されているかを判定するSQL
        hostid_chk_sql = "( SELECT \n"
        hostid_chk_sql += "   COUNT(*) \n"
        hostid_chk_sql += " FROM T_ANSC_DEVICE \n"
        hostid_chk_sql += " WHERE SYSTEM_ID = TBL_A.HOST_ID AND \n"
        hostid_chk_sql += " DISUSE_FLAG = '0' \n"
        hostid_chk_sql += " ) AS " + AnscConst.DF_ITA_LOCAL_HOST_CNT + ", \n"
        
        # テーブル名+カラム名配列からテーブル名と配列名を取得
        for table_name, col_list in in_tabColNameToValAssRowList.items():
            pkey_name = in_tableNameToPKeyNameList[table_name]
            
            col_sql = ""
            for col_name in col_list.keys():
                col_sql = col_sql + ", TBL_A." + col_name + " \n"
            
            if col_sql == "":
                # SELECT対象の項目なし
                # エラーがあるのでスキップ
                msgstr = g.appmsg.get_api_message("MSG-10356", [in_tableNameToMenuIdList[table_name]])
                frame = inspect.currentframe().f_back
                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                # 次のテーブルへ
                continue
            
            # SELECT文を生成
            make_sql = "SELECT \n "
            make_sql += opeid_chk_sql + " \n "
            make_sql += hostid_chk_sql + " \n "
            make_sql += " TBL_A." + pkey_name + " AS " + AnscConst.DF_ITA_LOCAL_PKEY + " \n "
            make_sql += ", TBL_A.HOST_ID \n "
            make_sql += col_sql + " \n "
            make_sql += " FROM " + table_name + " TBL_A \n "
            make_sql += " WHERE DISUSE_FLAG = '0' \n "
            
            # メニューテーブルのSELECT SQL文退避
            inout_tableNameToSqlList = {}
            inout_tableNameToSqlList[table_name] = make_sql
            
        return inout_tableNameToSqlList
    
    def getVarsAssignRecodes(self, WS_DB):
        """
        代入値管理の情報を取得
        
        Arguments:
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_VarsAssignRecodes: 代入値管理に登録されている変数リスト
            in_ArryVarsAssignRecodes: 代入値管理に登録されている多段変数リスト
        """
        
        global strCurTableVarsAss
        global strJnlTableVarsAss
        global strSeqOfCurTableVarsAss
        global strSeqOfJnlTableVarsAss
        global arrayConfigOfVarAss
        global arrayValueTmplOfVarAss
        global warning_flag
        
        vg_varass_menuID = "2100020311"
        
        in_VarsAssignRecodes = {}
        in_ArryVarsAssignRecodes = {}
        
        # 廃止レコードも含めてる。 WHERE句がないと全件とれない模様
        temp_array = {'WHERE': "$strPkey>'0'"}
        
        sqlUtnBody = "SELECT "
        sqlUtnBody += " ASSIGN_ID, "
        sqlUtnBody += " OPERATION_ID, "
        sqlUtnBody += " MOVEMENT_ID, "
        sqlUtnBody += " SYSTEM_ID, "
        sqlUtnBody += " MVMT_VAR_LINK_ID, "
        sqlUtnBody += " COL_SEQ_COMBINATION_ID, "
        sqlUtnBody += " VARS_ENTRY, "
        sqlUtnBody += " SENSITIVE_FLAG, "
        sqlUtnBody += " VARS_ENTRY_FILE, "
        sqlUtnBody += " VARS_ENTRY_USE_TPFVARS, "
        sqlUtnBody += " ASSIGN_SEQ, "
        sqlUtnBody += " DISUSE_FLAG, "
        sqlUtnBody += " NOTE, "
        sqlUtnBody += " DATE_FORMAT(LAST_UPDATE_TIMESTAMP,'%Y/%m/%d %H:%i:%s') LAST_UPDATE_TIMESTAMP, "
        sqlUtnBody += " CASE WHEN LAST_UPDATE_TIMESTAMP IS NULL THEN 'VALNULL' ELSE CONCAT('T_',DATE_FORMAT(LAST_UPDATE_TIMESTAMP,'%Y%m%d%H%i%s%f')) END UPD_UPDATE_TIMESTAMP, "
        sqlUtnBody += " LAST_UPDATE_USER "
        sqlUtnBody += " FROM T_ANSR_VALUE "
        sqlUtnBody += " ASSIGN_ID>'0' "
        
        ret = WS_DB.table_lock(['T_ANSR_VALUE'])
        
        data_list = WS_DB.sql_execute(sqlUtnBody, [])
        
        obj = FileUploadColumnDirectoryControl()
        for row in data_list:
            ColumnName = 'VARS_ENTRY_FILE'
            FileName = row['VARS_ENTRY_FILE']
            Pkey = row['ASSIGN_ID']
            row['VARS_ENTRY_FILE_MD5'] = ""
            row['VARS_ENTRY_FILE_PATH'] = ""
            
            if not FileName == "":
                FilePath = obj.getFileUpLoadFilePath(vg_varass_menuID, ColumnName, Pkey, FileName)
                if not os.path.exists(FilePath):
                    frame = inspect.currentframe().f_back
                    msgstr = g.appmsg.get_api_message('MSG-10149', [row['ASSIGN_ID'], FilePath])
                    g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                    warning_flag = True
                    continue
                
                row['VARS_ENTRY_FILE_PATH'] = FilePath
                row['VARS_ENTRY_FILE_MD5'] = self.md5_file(FilePath)
                
            key = row["OPERATION_ID"] + "_"
            key += row["MOVEMENT_ID"] + "_"
            key += row["SYSTEM_ID"] + "_"
            key += row["MVMT_VAR_LINK_ID"] + "_"
            key += row["COL_SEQ_COMBINATION_ID"] + "_"
            key += row["ASSIGN_SEQ"] + "_"
            key += row["DISUSE_FLAG"] + "_"
            
            if len(row["COL_SEQ_COMBINATION_ID"]) is None:
                in_VarsAssignRecodes[key] = row
            else:
                in_ArryVarsAssignRecodes[key] = row
        
        return True, in_VarsAssignRecodes, in_ArryVarsAssignRecodes
    
    def checkVerticalMenuVarsAssignData(self, lv_tableVerticalMenuList, inout_varsAssList):
        """
        縦メニューでまとまり全てNULLの場合、代入値管理への登録・更新を対象外とする
        
        Arguments:
            lv_tableVerticalMenuList: 縦メニューテーブルのカラム情報配列

        Returns:
            is success:(bool)
            defvarsList: 抽出した変数
        """
        
        chk_vertical_col = {}
        chk_vertical_val = {}
        
        for tbl_name, col_list in lv_tableVerticalMenuList.items():
            for col_name in col_list.values():
                for index, vars_ass_list in inout_varsAssList.items():
                    # 縦メニュー以外はチェック対象外
                    if not tbl_name == vars_ass_list['TABLE_NAME']:
                        continue
                    
                    if not tbl_name == vars_ass_list['COL_NAME']:
                        continue
                    
                    # テーブル名とROW_IDをキーとした代入値チェック用の辞書を作成
                    if tbl_name not in chk_vertical_val:
                        chk_vertical_val[tbl_name] = {}
                    
                    chk_vertical_val[tbl_name] = {}
                    chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']] = {}
                    if vars_ass_list['COL_ROW_ID'] not in chk_vertical_val[tbl_name]:
                        chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']]['CHK_START'] = False
                        chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']]['NULL_VAL'] = {}
                        
                    # リピート開始カラムをチェック
                    if col_name == vars_ass_list['START_COL_NAME']:
                        chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']]['CHK_START'] = True
                        if tbl_name not in chk_vertical_col:
                            chk_vertical_val[tbl_name]['COL_CNT'] = 0
                            chk_vertical_val[tbl_name]['REPEAT_CNT'] = 0
                            chk_vertical_val[tbl_name]['COL_CNT_MAX'] = vars_ass_list['COL_CNT']
                            chk_vertical_val[tbl_name]['REPEAT_CNT_MAX'] = vars_ass_list['REPEAT_CNT']
                    
                    # リピート開始前の場合は次のカラムへ以降
                    if chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']]['CHK_START'] == 0:
                        continue
                    
                    # 具体値が NULL の場合は、代入値管理登録データのインデックスを保持
                    if vars_ass_list['VARS_ENTRY'] == "":
                        chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']]['NULL_VAL'] = {}
                        chk_vertical_val[tbl_name][vars_ass_list['COL_ROW_ID']]['NULL_VAL']['INDEX'] = index
                
                # リピート開始前の場合は次のカラムへ以降
                if tbl_name not in chk_vertical_col:
                    continue
                
                # チェック完了済みカラムをカウントアップ
                chk_vertical_col[tbl_name]['COL_CNT'] += 1
                
                # まとまり単位のチェック完了時の場合
                if chk_vertical_col[tbl_name]['COL_CNT'] >= chk_vertical_col[tbl_name]['COL_CNT_MAX']:
                    # まとまり単位の具体値が全て NULL の場合は代入値管理への登録対象外とする
                    if tbl_name in chk_vertical_val:
                        for row_id, vertical_val_info in chk_vertical_val[tbl_name]:
                            if len(vertical_val_info['NULL_VAL']) >= chk_vertical_col[tbl_name]['COL_CNT_MAX']:
                                for index in vertical_val_info['NULL_VAL'].values():
                                    inout_varsAssList[index]['STATUS'] = False
                            # 保持している代入値管理登録データのインデックスをリセット
                            del chk_vertical_val[tbl_name][row_id]['NULL_VAL']
                            chk_vertical_val[tbl_name][row_id]['NULL_VAL'] = {}
                    
                    # リピート数をカウントアップ
                    chk_vertical_col[tbl_name]['REPEAT_CNT'] += 1
                    
                    # チェック完了済みカラムのカウントをリセット
                    chk_vertical_col[tbl_name]['COL_CNT'] = 0
                
                # リピート終了済みの場合は以降のカラムはチェックしない
                if chk_vertical_col[tbl_name]['REPEAT_CNT'] >= chk_vertical_col[tbl_name]['REPEAT_CNT_MAX']:
                    break
        
        return inout_varsAssList
    
    def addStg1StdListVarsAssign(self, in_varsAssignList, in_tableNameToMenuIdList, in_VarsAssignRecodes, WS_DB):
        """
        代入値管理（一般変数・複数具体値変数）を更新する。
        
        Arguments:
            in_varsAssignList: 代入値管理更新情報配列
            in_tableNameToMenuIdList: テーブル名配列
            in_VarsAssignRecodes: 代入値管理の全テータ配列

        Returns:
            is success:(bool)
            in_VarsAssignRecodes: 代入値管理の全テータ配列
        """
        
        global strCurTableVarsAss
        global strJnlTableVarsAss
        global strSeqOfCurTableVarsAss
        global strSeqOfJnlTableVarsAss
        global arrayConfigOfVarAss
        global arrayValueTmplOfVarAss
        global vg_FileUPloadColumnBackupFilePath
        global db_update_flg
        db_valautostup_user_id = "-100019"
        
        key = in_varsAssignList["OPERATION_ID"] + "_"
        key += in_varsAssignList["MOVEMENT_ID"] + "_"
        key += in_varsAssignList["SYSTEM_ID"] + "_"
        key += in_varsAssignList["MVMT_VAR_LINK_ID"] + "_" 
        key +=  ""  + "_"
        key += in_varsAssignList["ASSIGN_SEQ"] + "_0"
        
        objmenu = load_table.loadTable(WS_DB, "20409")
        
        hit_flg = False
        
        val_list = {}
        
        # 代入値管理に登録されているか判定
        if key in in_VarsAssignRecodes:
            # 具体値が一致しているか判定
            tgt_row = in_VarsAssignRecodes[key]
            ret = self.chkSubstitutionValueListRecodedifference(tgt_row, in_varsAssignList)
            diff = ret[0]
            befFileDel = ret[1]
            AftFileCpy = ret[2]
            
            if diff == 0:
                # 代入値管理に必要なレコードを削除
                del in_VarsAssignRecodes[key]
                
                # トレースメッセージ
                traceMsg = g.appmsg.get_api_message("MSG-10815", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
                frame = inspect.currentframe().f_back
                g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
                
                return True, in_VarsAssignRecodes
            else:
                hit_flg = True
                
                # 具体値を退避
                val_list = [in_varsAssignList['VARS_ENTRY'], in_VarsAssignRecodes[key]['VARS_ENTRY']]
                del in_VarsAssignRecodes[key]
                
        # 代入値管理に有効レコードが未登録か判定
        if hit_flg == 0:
            # 廃止レコードの復活または新規レコード追加する。
            ret = self.addStg2StdListVarsAssign(in_varsAssignList, in_tableNameToMenuIdList, in_VarsAssignRecodes, )
        else:
            action = "UPDATE"
            
            # 最終更新者が自分でない場合、更新処理はスキップする
            if not tgt_row['LAST_UPDATE_USER'] == db_valautostup_user_id:
                # トレースメッセージ
                traceMsg = g.appmsg.get_api_message("MSG-10835", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
                frame = inspect.currentframe().f_back
                g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
                
                # 更新処理はスキップ
                return True
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10814", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                        in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
        VARS_ENTRY_USE_TPFVARS = "0"
        # 具体値にテンプレート変数が記述されているか判定
        for val in val_list.values():
            pattern = "/{{(\s)" + "TPF_" + "[a-zA-Z0-9_]*(\s)}}/"

            ret = re.match(pattern, val)
            if ret:
                if not ret.group() == "":
                    # テンプレート変数が記述されていることを記録
                    VARS_ENTRY_USE_TPFVARS = "1"
                    db_update_flg = True
                    break
        
        # ロール管理ジャーナルに登録する情報設定
        tgt_row['VARS_ENTRY'] = in_varsAssignList['VARS_ENTRY']
        tgt_row["VARS_ENTRY_FILE"] = in_varsAssignList['VARS_ENTRY_FILE']
        tgt_row["SENSITIVE_FLAG"] = in_varsAssignList['SENSITIVE_FLAG']
        tgt_row["VARS_ENTRY_USE_TPFVARS"] = VARS_ENTRY_USE_TPFVARS
        tgt_row['COL_SEQ_COMBINATION_ID']  = ""
        tgt_row['DISUSE_FLAG'] = "0"
        tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
        
        if action == "INSERT":
            parameter = {
                "assign_id": tgt_row['ASSIGN_ID'],
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Register"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters)
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        elif action == "UPDATE":
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type": "Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['ASSIGN_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        
        if befFileDel == 1 or AftFileCpy == 1:
            ret = self.FileUPloadColumnBackup()
            if ret[0] == 0:
                return False
            
            # FileUploadColumn用ファイル配置
            ret = self.CreateFileUpLoadMenuColumnFileDirectory(befFileDel, AftFileCpy, tgt_row["ASSIGN_ID"], tgt_row['VARS_ENTRY_FILE_PATH'], in_varsAssignList['COL_FILEUPLOAD_PATH'])
            if ret[0] == 0:
                return False
        
        return True, in_VarsAssignRecodes

    def chkSubstitutionValueListRecodedifference(BefInfo, AftInfo):
        diff = False
        befFileDel = False
        AftFileCpy = False
        
        if AftInfo['COL_CLASS'] == 'FileUploadColumn' and AftInfo['REG_TYPE']  == 'Value':
            AftInfo['VARS_ENTRY_FILE'] = AftInfo['VARS_ENTRY']
            AftInfo['VARS_ENTRY'] = ""
        else:
            AftInfo['VARS_ENTRY_FILE'] = ""
        
        if not BefInfo['SENSITIVE_FLAG'] == AftInfo['SENSITIVE_FLAG'] or \
                not BefInfo['VARS_ENTRY_FILE'] == AftInfo['VARS_ENTRY_FILE'] or \
                not BefInfo['VARS_ENTRY_FILE_MD5'] == AftInfo['COL_FILEUPLOAD_MD5'] or \
                not BefInfo['VARS_ENTRY'] == AftInfo['VARS_ENTRY']:
            diff = True
        
        if diff == 1:
            # 代入値管理の具体値がファイルの場合
            if not BefInfo['VARS_ENTRY_FILE'] == AftInfo['VARS_ENTRY_FILE'] or \
                    not BefInfo['VARS_ENTRY_FILE_MD5'] == AftInfo['COL_FILEUPLOAD_MD5']:
                if not BefInfo['VARS_ENTRY_FILE'] == "":
                    befFileDel = True
            
            # パラメータシートの具体値がファイルの場合
            if not BefInfo['VARS_ENTRY_FILE'] == AftInfo['VARS_ENTRY_FILE'] or \
                    not BefInfo['VARS_ENTRY_FILE_MD5'] == AftInfo['COL_FILEUPLOAD_MD5']:
                if not AftInfo['VARS_ENTRY_FILE'] == "" and AftInfo['REG_TYPE'] == 'Value':
                    AftFileCpy = True
        
        return diff, befFileDel, AftFileCpy
    
    def addStg2StdListVarsAssign(self, in_varsAssignList, in_tableNameToMenuIdList, in_ArryVarsAssignRecodes, WS_DB):
        """
        代入値管理（一般変数・複数具体値変数）の廃止レコードの復活またき新規レコード追加
        
        Arguments:
            in_varsAssignList: 代入値管理更新情報配列
            in_varsAssignList: テーブル名配列
            in_ArryVarsAssignRecodes: 代入値管理の全テータ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_ArryVarsAssignRecodes: 代入値管理の全テータ配列
        """
        
        global strCurTableVarsAss
        global strJnlTableVarsAss
        global strSeqOfCurTableVarsAss
        global strSeqOfJnlTableVarsAss
        global arrayConfigOfVarAss
        global arrayValueTmplOfVarAss
        global vg_FileUPloadColumnBackupFilePath
        global db_update_flg
        
        arrayValue = arrayValueTmplOfVarAss
        db_valautostup_user_id = "-100019"
        
        key = in_varsAssignList["OPERATION_ID"] + "_"
        key += in_varsAssignList["MOVEMENT_ID"] + "_"
        key += in_varsAssignList["SYSTEM_ID"] + "_"
        key += in_varsAssignList["MVMT_VAR_LINK_ID"] + "_" 
        key += ""  + "_"
        key += in_varsAssignList["ASSIGN_SEQ"] + "_1"
        
        objmenu = load_table.loadTable(WS_DB, "20409")

        befFileDel = False
        AftFileCpy = False
        
        # 代入値管理に登録されているか判定
        if key not in in_ArryVarsAssignRecodes:
            action  = "INSERT"
            tgt_row = arrayValue
            
            if in_varsAssignList['COL_CLASS'] == 'FileUploadColumn' and in_varsAssignList['REG_TYPE']  == 'Value':
                in_varsAssignList['VARS_ENTRY_FILE'] = in_varsAssignList['VARS_ENTRY']
                in_varsAssignList['VARS_ENTRY'] = ""
                if not in_varsAssignList['VARS_ENTRY_FILE'] == "":
                    AftFileCpy = True
            else:
                in_varsAssignList['VARS_ENTRY_FILE'] = ""
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10812", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        else:
            # 廃止レコードがあるので復活する。
            action = "UPDATE"
            tgt_row = in_ArryVarsAssignRecodes[key]
            
            ret = self.chkSubstitutionValueListRecodedifference(tgt_row, in_varsAssignList)
            befFileDel = ret[1]
            AftFileCpy = ret[2]
            
            del in_ArryVarsAssignRecodes[key]
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10813", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        if action == "INSERT":
            
            # DBの項目ではないがFileUploadCloumn用のディレクトリ作成で必要な項目の初期化
            tgt_row['VARS_ENTRY_FILE_PATH']   = ""
            
            # 登録する情報設定
            tgt_row['ASSIGN_ID'] = str(WS_DB._uuid_create())
            tgt_row['OPERATION_ID'] = in_varsAssignList['OPERATION_ID']
            tgt_row['MOVEMENT_ID'] = in_varsAssignList['MOVEMENT_ID']
            tgt_row['SYSTEM_ID'] = in_varsAssignList['SYSTEM_ID']
            tgt_row['MVMT_VAR_LINK_ID'] = in_varsAssignList['MVMT_VAR_LINK_ID']
            tgt_row['ASSIGN_SEQ'] = in_varsAssignList['ASSIGN_SEQ']
        
        # 具体値にテンプレート変数が記述されているか判定
        VARS_ENTRY_USE_TPFVARS = "0"
        pattern = "/{{(\s)" + "TPF_" + "[a-zA-Z0-9_]*(\s)}}/"

        ret = re.match(pattern, in_varsAssignList['VARS_ENTRY'])
        if ret:
            if not ret.group() == "":
                # テンプレート変数が記述されていることを記録
                VARS_ENTRY_USE_TPFVARS = "1"
                db_update_flg = True
        
        # ロール管理ジャーナルに登録する情報設定
        tgt_row['VARS_ENTRY'] = in_varsAssignList['VARS_ENTRY']
        tgt_row["VARS_ENTRY_FILE"] = in_varsAssignList['VARS_ENTRY_FILE']
        tgt_row["SENSITIVE_FLAG"] = in_varsAssignList['SENSITIVE_FLAG']
        tgt_row["VARS_ENTRY_USE_TPFVARS"] = VARS_ENTRY_USE_TPFVARS
        tgt_row['DISUSE_FLAG'] = "0"
        tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
        
        if action == "INSERT":
            parameter = {
                "assign_id": tgt_row['ASSIGN_ID'],
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Register"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters)
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        elif action == "UPDATE":
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['ASSIGN_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        
        if befFileDel == 1 or AftFileCpy == 1:
            ret = self.FileUPloadColumnBackup()
            if ret[0] == 0:
                return False
            
            # FileUploadColumn用ファイル配置
            ret = self.CreateFileUpLoadMenuColumnFileDirectory(befFileDel, AftFileCpy, tgt_row["ASSIGN_ID"], tgt_row['VARS_ENTRY_FILE_PATH'], in_varsAssignList['COL_FILEUPLOAD_PATH'])
            if ret[0] == 0:
                return False
        
        return True, in_ArryVarsAssignRecodes
    
    def addStg1ArrayVarsAssign(self, in_varsAssignList, in_tableNameToMenuIdList, in_ArryVarsAssignRecodes, WS_DB):
        """
        代入値管理（多次元配列変数）を更新する。
        
        Arguments:
            in_varsAssignList: 代入値管理更新情報配列
            in_tableNameToMenuIdList: テーブル名配列
            in_ArryVarsAssignRecodes: 代入値管理の全テータ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_ArryVarsAssignRecodes: 代入値管理の全テータ配列
        """
        
        global strCurTableVarsAss
        global strJnlTableVarsAss
        global strSeqOfCurTableVarsAss
        global strSeqOfJnlTableVarsAss
        global arrayConfigOfVarAss
        global arrayValueTmplOfVarAss
        global vg_FileUPloadColumnBackupFilePath
        global db_update_flg

        db_valautostup_user_id = "-100019"
        
        key = in_varsAssignList["OPERATION_ID"] + "_"
        key += in_varsAssignList["MOVEMENT_ID"] + "_"
        key += in_varsAssignList["SYSTEM_ID"] + "_"
        key += in_varsAssignList["MVMT_VAR_LINK_ID"] + "_" 
        key += "" + "_"
        key += in_varsAssignList["ASSIGN_SEQ"] + "_0"
        
        objmenu = load_table.loadTable(WS_DB, "20409")
        
        val_list = {}
        
        hit_flg = False
        # 代入値管理に登録されているか判定
        if key in in_ArryVarsAssignRecodes:
            # 具体値が一致しているか判定
            tgt_row = in_ArryVarsAssignRecodes[key]
            
            ret = self.chkSubstitutionValueListRecodedifference(tgt_row, in_varsAssignList)
            diff = ret[0]
            befFileDel = ret[1]
            AftFileCpy = ret[2]
            
            if diff == 0:
                FREE_LOG = g.appmsg.get_api_message("MSG-10815", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
                frame = inspect.currentframe().f_back
                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
                
                # 代入値管理に必要なレコードはリストから削除
                del in_ArryVarsAssignRecodes[key]
                return True
            
            hit_flg = True
            
            # 具体値を退避
            val_list = {}
            val_list[0] = in_ArryVarsAssignRecodes[key]['VARS_ENTRY']
            val_list[1] = in_varsAssignList['VARS_ENTRY']
            
            # 代入値管理に必要なレコードはリストから削除
            del in_ArryVarsAssignRecodes[key]
            
        # 代入値管理に有効レコードが未登録か判定
        if hit_flg == 0:
            # 廃止レコードの復活または新規レコード追加する。
            return self.addStg2ArrayVarsAssign(in_varsAssignList, in_tableNameToMenuIdList, in_ArryVarsAssignRecodes)
        else:
            action = "UPDATE"
            
            # 最終更新者が自分でない場合、更新処理はスキップする
            if not tgt_row['LAST_UPDATE_USER'] == db_valautostup_user_id:
                # トレースメッセージ
                traceMsg = g.appmsg.get_api_message("MSG-10835", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
                frame = inspect.currentframe().f_back
                g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
                
                # 更新処理はスキップ
                return True
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10814", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                        in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
        VARS_ENTRY_USE_TPFVARS = "0"
        # 具体値にテンプレート変数が記述されているか判定
        for val in val_list.values():
            pattern = "/{{(\s)" + "TPF_" + "[a-zA-Z0-9_]*(\s)}}/"

            ret = re.match(pattern, val)
            if ret:
                if not ret.group() == "":
                    # テンプレート変数が記述されていることを記録
                    VARS_ENTRY_USE_TPFVARS = "1"
                    db_update_flg = True
                    break
        
        # ロール管理ジャーナルに登録する情報設定
        tgt_row['VARS_ENTRY'] = in_varsAssignList['VARS_ENTRY']
        tgt_row["VARS_ENTRY_FILE"] = in_varsAssignList['VARS_ENTRY_FILE']
        tgt_row["SENSITIVE_FLAG"] = in_varsAssignList['SENSITIVE_FLAG']
        tgt_row["VARS_ENTRY_USE_TPFVARS"] = VARS_ENTRY_USE_TPFVARS
        tgt_row['COL_SEQ_COMBINATION_ID']  = ""
        tgt_row['DISUSE_FLAG'] = "0"
        tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
        
        if action == "INSERT":
            parameter = {
                "assign_id": tgt_row['ASSIGN_ID'],
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Register"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters)
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        elif action == "UPDATE":
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['ASSIGN_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        
        if befFileDel == 1 or AftFileCpy == 1:
            # ファイルアップロードカラムのディレクトリバックアップ
            ret = self.FileUPloadColumnBackup()
            if ret[0] == 0:
                return False
            
            # FileUploadColumn用ファイル配置
            ret = self.CreateFileUpLoadMenuColumnFileDirectory(befFileDel, AftFileCpy, tgt_row["ASSIGN_ID"], tgt_row['VARS_ENTRY_FILE_PATH'], in_varsAssignList['COL_FILEUPLOAD_PATH'])
            if ret[0] == 0:
                return False
        
        return True, in_ArryVarsAssignRecodes
    
    def addStg2ArrayVarsAssign(self, in_varsAssignList, in_tableNameToMenuIdList, in_ArryVarsAssignRecodes, WS_DB):
        """
        代入値管理（多次元配列変数）の廃止レコードの復活またき新規レコード追加
        
        Arguments:
            in_varsAssignList: 代入値管理更新情報配列
            in_tableNameToMenuIdList: テーブル名配列
            in_ArryVarsAssignRecodes: 代入値管理の全テータ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            in_ArryVarsAssignRecodes: 代入値管理の全テータ配列
        """
        
        global strCurTableVarsAss
        global strJnlTableVarsAss
        global strSeqOfCurTableVarsAss
        global strSeqOfJnlTableVarsAss
        global arrayConfigOfVarAss
        global arrayValueTmplOfVarAss
        global vg_FileUPloadColumnBackupFilePath
        global db_update_flg

        arrayValue = arrayValueTmplOfVarAss
        vg_varass_menuID = "2100020311"
        db_valautostup_user_id = "-100019"
        
        key = in_varsAssignList["OPERATION_ID"] + "_"
        key += in_varsAssignList["MOVEMENT_ID"] + "_"
        key += in_varsAssignList["SYSTEM_ID"] + "_"
        key += in_varsAssignList["MVMT_VAR_LINK_ID"] + "_" 
        key += ""  + "_"
        key += in_varsAssignList["ASSIGN_SEQ"] + "_1"
        
        objmenu = load_table.loadTable(WS_DB, "20409")
        
        hit_flg = False

        befFileDel = False
        AftFileCpy = False
        
        # 代入値管理に登録されているか判定
        if key not in in_ArryVarsAssignRecodes:
            action  = "INSERT"
            tgt_row = arrayValue
            
            if in_varsAssignList['COL_CLASS'] == 'FileUploadColumn' and in_varsAssignList['REG_TYPE']  == 'Value':
                in_varsAssignList['VARS_ENTRY_FILE'] = in_varsAssignList['VARS_ENTRY']
                in_varsAssignList['VARS_ENTRY'] = ""
                if not in_varsAssignList['VARS_ENTRY_FILE'] == "":
                    AftFileCpy = True
            else:
                in_varsAssignList['VARS_ENTRY_FILE'] = ""
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10812", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        else:
            # 廃止レコードがあるので復活する。
            action = "UPDATE"
            tgt_row = in_ArryVarsAssignRecodes[key]
            
            ret = self.chkSubstitutionValueListRecodedifference(tgt_row, in_varsAssignList)
            diff = ret[0]
            befFileDel = ret[1]
            AftFileCpy = ret[2]
            
            del in_ArryVarsAssignRecodes[key]
            
            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10813", [in_varsAssignList['OPERATION_ID'], in_varsAssignList['MOVEMENT_ID'], in_varsAssignList['SYSTEM_ID'],
                                                            in_varsAssignList['MVMT_VAR_LINK_ID'], in_varsAssignList['ASSIGN_SEQ']])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        if action == "INSERT":
            
            # DBの項目ではないがFileUploadCloumn用のディレクトリ作成で必要な項目の初期化
            tgt_row['VARS_ENTRY_FILE_PATH']   = ""
            
            # 登録する情報設定
            tgt_row['ASSIGN_ID'] = str(WS_DB._uuid_create())
            tgt_row['OPERATION_ID'] = in_varsAssignList['OPERATION_ID']
            tgt_row['MOVEMENT_ID'] = in_varsAssignList['MOVEMENT_ID']
            tgt_row['SYSTEM_ID'] = in_varsAssignList['SYSTEM_ID']
            tgt_row['MVMT_VAR_LINK_ID'] = in_varsAssignList['MVMT_VAR_LINK_ID']
            tgt_row['ASSIGN_SEQ'] = in_varsAssignList['ASSIGN_SEQ']
        
        # 具体値にテンプレート変数が記述されているか判定
        VARS_ENTRY_USE_TPFVARS = "0"
        pattern = "/{{(\s)" + "TPF_" + "[a-zA-Z0-9_]*(\s)}}/"

        ret = re.match(pattern, in_varsAssignList['VARS_ENTRY'])
        if ret:
            if not ret.group() == "":
                # テンプレート変数が記述されていることを記録
                VARS_ENTRY_USE_TPFVARS = "1"
                db_update_flg = True
        
        # ロール管理ジャーナルに登録する情報設定
        tgt_row['VARS_ENTRY'] = in_varsAssignList['VARS_ENTRY']
        tgt_row["VARS_ENTRY_FILE"] = in_varsAssignList['VARS_ENTRY_FILE']
        tgt_row["SENSITIVE_FLAG"] = in_varsAssignList['SENSITIVE_FLAG']
        tgt_row["VARS_ENTRY_USE_TPFVARS"] = VARS_ENTRY_USE_TPFVARS
        tgt_row['DISUSE_FLAG'] = "0"
        tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
        
        if action == "INSERT":
            parameter = {
                "assign_id": tgt_row['ASSIGN_ID'],
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Register"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters)
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        elif action == "UPDATE":
            parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

            parameters = {
                "parameter": parameter,
                "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
                "type":"Update"
            }
            status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['ASSIGN_ID'])
            
            if status_code != '000-00000':
                if status_code is None:
                    status_code = '999-99999'
                elif len(status_code) == 0:
                    status_code = '999-99999'
                if isinstance(msg, list):
                    log_msg_args = msg
                    api_msg_args = msg
                else:
                    log_msg_args = [msg]
                    api_msg_args = [msg]
                raise AppException(status_code, log_msg_args, api_msg_args)
        
        if befFileDel == 1 or AftFileCpy == 1:
            # ファイルアップロードカラムのディレクトリバックアップ
            ret = self.FileUPloadColumnBackup()
            if ret[0] == 0:
                return False
            
            # FileUploadColumn用ファイル配置
            ret = self.CreateFileUpLoadMenuColumnFileDirectory(befFileDel, tgt_row["ASSIGN_ID"], tgt_row['VARS_ENTRY_FILE_PATH'],in_varsAssignList['COL_FILEUPLOAD_PATH'])
            if ret[0] == 0:
                return False
        
        return True, in_ArryVarsAssignRecodes
    
    def deleteVarsAssign(self, lv_VarsAssignRecodes, WS_DB):
        """
        代入値管理から不要なレコードを廃止
        
        Arguments:
            in_VarsAssignRecodes: 代入値管理の全テータ配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
        """
        
        global strCurTableVarsAss
        global strJnlTableVarsAss
        global strSeqOfCurTableVarsAss
        global strSeqOfJnlTableVarsAss
        global arrayConfigOfVarAss
        global arrayValueTmplOfVarAss
        global vg_FileUPloadColumnBackupFilePath
        global db_update_flg 
        
        strCurTable = strCurTableVarsAss
        strJnlTable = strJnlTableVarsAss
        arrayConfig = arrayConfigOfVarAss
        arrayValue = arrayValueTmplOfVarAss
        strSeqOfCurTable = strSeqOfCurTableVarsAss
        strSeqOfJnlTable = strSeqOfJnlTableVarsAss
        strPkey = "ASSIGN_ID"
        vg_varass_menuID = "2100020311"
        
        db_valautostup_user_id = "-100019"
        
        objmenu = load_table.loadTable(WS_DB, "20409")
        
        for key, tgt_row in in_VarsAssignRecodes.items():
            if tgt_row['DISUSE_FLAG'] == '1':
                # 廃止レコードはなにもしない。
                continue
        
            # 最終更新者が自分でない場合、廃止処理はスキップする。
            if not tgt_row["LAST_UPDATE_USER"] == db_valautostup_user_id:
                # トレースメッセージ
                traceMsg = g.appmsg.get_api_message("MSG-10827", [tgt_row['ASSIGN_ID']])
                frame = inspect.currentframe().f_back
                g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
                # 更新処理はスキップ
                continue
        
        # 廃止レコードにする。
        
        # トレースメッセージ
        traceMsg = g.appmsg.get_api_message("MSG-10820", [tgt_row['ASSIGN_ID']])
        frame = inspect.currentframe().f_back
        g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
        
        # 具体値にテンプレート変数が記述されているか判定
        if db_update_flg == 0:
            pattern = "/{{(\s)" + "TPF_" + "[a-zA-Z0-9_]*(\s)}}/"

            ret = re.match(pattern, tgt_row['VARS_ENTRY'])
            if ret:
                if not ret.group() == "":
                    # テンプレート変数が記述されていることを記録
                    db_update_flg = True

        tgt_row['DISUSE_FLAG'] = '1'
        tgt_row['LAST_UPDATE_USER'] = db_valautostup_user_id
        
        # ロール管理ジャーナルに登録する情報設定
        parameter = {
                "operation_id": tgt_row['OPERATION_ID'],
                "execution_no": tgt_row['EXECUTION_NO'],
                "movement_id": tgt_row['MOVEMENT_ID'],
                "system_id": tgt_row['SYSTEM_ID'],
                "mvmt_var_link_id": tgt_row['MVMT_VAR_LINK_ID'],
                "col_seq_combination_id": tgt_row['COL_SEQ_COMBINATION_ID'],
                "vars_entry": tgt_row['VARS_ENTRY'],
                "sensitive_flag": tgt_row['SENSITIVE_FLAG'],
                "vars_entry_file": "VARS_ENTRY_FILE",
                "assign_seq": tgt_row['ASSIGN_SEQ'],
                "vars_entry_use_tpfvars": tgt_row['VARS_ENTRY_USE_TPFVARS'],
                "note": tgt_row['NOTE'],
                "disuse_flag": tgt_row['DISUSE_FLAG'],
                "last_update_date_time": tgt_row['LAST_UPDATE_TIMESTAMP'],
                "last_updated_user": tgt_row['LAST_UPDATE_USER']
            }

        parameters = {
            "parameter": parameter,
            "file": {"vars_entry_file": tgt_row['VARS_ENTRY_FILE']},
            "type":"Update"
        }
        status_code, result, msg = objmenu.rest_maintenance(parameters, tgt_row['ASSIGN_ID'])
        
        if status_code != '000-00000':
            if status_code is None:
                status_code = '999-99999'
            elif len(status_code) == 0:
                status_code = '999-99999'
            if isinstance(msg, list):
                log_msg_args = msg
                api_msg_args = msg
            else:
                log_msg_args = [msg]
                api_msg_args = [msg]
            raise AppException(status_code, log_msg_args, api_msg_args)
        
        return True
    
    def FileUPloadColumnRestore(self):
        """
        FileUploadColumnのディレクトリを元に戻す

        Returns:
            is success:(bool)
        """
        global vg_FileUPloadColumnBackupFilePath
        
        vg_varass_menuID = "2100020311"
        
        # バックアップが失敗している場合は、バックアップファイルは削除されている
        if not vg_FileUPloadColumnBackupFilePath == "":
            if os.path.exists(vg_FileUPloadColumnBackupFilePath):
                FUCobj = FileUploadColumnDirectoryControl()
                ret = FUCobj.FileUPloadColumnRestore(vg_varass_menuID,"VARS_ENTRY_FILE",vg_FileUPloadColumnBackupFilePath)
                error_msg = FUCobj.GetLastError()
                
                if ret == 0:
                    FREE_LOG = g.appmsg.get_api_message("MSG-10168", [error_msg])
                    frame = inspect.currentframe().f_back
                    g.applogger.error(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
                    del FUCobj
                    return False
                
                del FUCobj
        
        return True
        
    def FileUPloadColumnBackup(self):
        """
        ファイルアップロードカラムのディレクトリバックアップ

        Returns:
            is success:(bool)
        """
        global vg_FileUPloadColumnBackupFilePath

        vg_varass_menuID = "2100020311"
        
        # ファイルアップロードカラムのディレクトリバックアップ
        FUCobj = FileUploadColumnDirectoryControl()
        
        # アップロードカラム用のディレクトリが存在しない場合があるので、ここで作成
        ret = FUCobj.CreateFileUpLoadMenuColumnDirectory(vg_varass_menuID,"VARS_ENTRY_FILE")
        error_msg = FUCobj.GetLastError()
        if ret == 0:
            FREE_LOG = g.appmsg.get_api_message("MSG-10169", [error_msg])
            frame = inspect.currentframe().f_back
            g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
            del FUCobj
            return False
        
        ret = FUCobj.FileUPloadColumnBackup(vg_varass_menuID,"VARS_ENTRY_FILE", vg_FileUPloadColumnBackupFilePath)
        vg_FileUPloadColumnBackupFilePath = ret[1]
        error_msg = FUCobj.GetLastError()
        if ret == 0:
            FREE_LOG = g.appmsg.get_api_message("MSG-10167", [error_msg])
            frame = inspect.currentframe().f_back
            g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
            del FUCobj
            return False
        
        del FUCobj
        
        return True
    
    def CreateFileUpLoadMenuColumnFileDirectory(self, befFileDel, AftFileCpy, Pkey, oldFileName, newFileName):
        """
        FileUploadColumn用ファイル配置
        
        Arguments:
            befFileDel: 配置前ファイル判定
            AftFileCpy: 配置後ファイル判定
            oldFileName: 配置前ファイル名
            newFileName: 配置後ファイル名

        Returns:
            is success:(bool)
        """
        vg_varass_menuID = "2100020311"
        if befFileDel == 1 or AftFileCpy == 1:
            # FileUploadColumn履歴ディレクトリ作成
            FilePath = ""
            JnlFilePath = ""
            FUCobj = FileUploadColumnDirectoryControl()
            ret = FUCobj.CreateFileUpLoadMenuColumnFileDirectory(vg_varass_menuID, "VARS_ENTRY_FILE", Pkey, ".", FilePath, JnlFilePath)
            error_msg = FUCobj.GetLastError()
            if ret == 0:
                FREE_LOG = g.appmsg.get_api_message("MSG-10169", [error_msg])
                frame = inspect.currentframe().f_back
                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
                del FUCobj
                return False
            
            del FUCobj
            
            if befFileDel == 1:
                tgtFile = oldFileName.replace("'", "\'")
                cmd = "/bin/rm -f %s" % ("'" + tgtFile + "'")
                cp = subprocess.run(cmd + " 2>&1", capture_output=True)
                if not cp.returncode == 0:
                    FREE_LOG = g.appmsg.get_api_message("MSG-10170", [cmd, cp.stderr])
                    frame = inspect.currentframe().f_back
                    g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
                    return False
            
                if AftFileCpy == 1:
                    From = newFileName
                    cmd = "/bin/rm -f %s %s" % ("'" + From + "'", "'" + FilePath + "'")
                    cp = subprocess.run(cmd + " 2>&1", capture_output=True)
                    if not cp.returncode == 0:
                        FREE_LOG = g.appmsg.get_api_message("MSG-10170", [cmd, cp.stderr])
                        frame = inspect.currentframe().f_back
                        g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
                        return False
                    
                    cmd = "/bin/rm -f %s %s" % ("'" + From + "'", "'" + JnlFilePath + "'")
                    cp = subprocess.run(cmd + " 2>&1", capture_output=True)
                    if not cp.returncode == 0:
                        FREE_LOG = g.appmsg.get_api_message("MSG-10170", [cmd, cp.stderr])
                        frame = inspect.currentframe().f_back
                        g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + FREE_LOG)
                        return False
        return True
    
    def getIFInfoDB(self, WS_DB):
        """
        インターフェース情報を取得する。
        
        Arguments:
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            ina_if_info: インターフェース情報
            in_error_msg: エラーメッセージ
        """
        
        where = "WHERE DISUSE_FLAG = '0'"
        data_list = WS_DB.table_select("T_ANSC_IF_INFO", where, [])
        
        ina_if_info = None
        in_error_msg = ""
        
        if data_list is None:
            msgstr = g.appmsg.get_api_message("MSG-10176")
            in_error_msg = msgstr
            g.applogger.debug(msgstr)
            return False, ina_if_info, in_error_msg
        
        for data in data_list:
            ina_if_info = data
        
        return True, ina_if_info, in_error_msg
    
    def getCMDBdata(self, in_tableNameToSqlList, in_tableNameToMenuIdList, in_tabColNameToValAssRowList, WS_DB):
        """
        CMDB代入値紐付対象メニューから具体値を取得する。
        
        Arguments:
            in_tableNameToSqlList: CMDB代入値紐付メニュー毎のSELECT文配列
            in_tableNameToMenuIdList: テーブル名配列
            in_tabColNameToValAssRowList: カラム情報配列
            ina_vars_ass_list: 一般変数・複数具体値変数用 代入値登録情報配列
            ina_array_vars_ass_list: 多次元変数配列変数用 代入値登録情報配列
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            ina_if_info: インターフェース情報
            in_error_msg: エラーメッセージ
        """
        
        VariableColumnAry = {}
        VariableColumnAry['T_ANSC_TEMPLATE_FILE'] = {}
        VariableColumnAry['T_ANSC_TEMPLATE_FILE']['ANS_TEMPLATE_VARS_NAME'] = 0
        VariableColumnAry['T_ANSC_CONTENTS_FILE'] = {}
        VariableColumnAry['T_ANSC_TEMPLATE_FILE']['CONTENTS_FILE_VARS_NAME'] = 0
        VariableColumnAry['T_ANSC_GLOBAL_VAR'] = {}
        VariableColumnAry['T_ANSC_GLOBAL_VAR']['VARS_NAME'] = 0
        
        # オペ+作業+ホスト+変数の組合せの代入順序 重複確認用
        lv_varsAssChkList = {}
        # オペ+作業+ホスト+変数+メンバ変数の組合せの代入順序 重複確認用
        lv_arrayVarsAssChkList = {}
        
        ina_vars_ass_list = {}
        lv_arrayVarsAssList = {}
        
        continue_flg = 0
        
        for table_name, sql in in_tableNameToSqlList.items():
            if continue_flg == 1:
                continue

            # トレースメッセージ
            traceMsg = g.appmsg.get_api_message("MSG-10806", [in_tableNameToMenuIdList[table_name]])
            frame = inspect.currentframe().f_back
            g.applogger.debug(os.path.basename(__file__) + str(frame.f_lineno) + traceMsg)
            
            data_list = WS_DB.sql_execute(sql, [])
            
            # FETCH行数を取得
            if len(data_list) == 0:
                msgstr = g.appmsg.get_api_message("MSG-10368", [in_tableNameToMenuIdList[table_name]])
                frame = inspect.currentframe().f_back
                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                # 次のテーブルへ
                continue
            
            for row in data_list:
                # 代入値紐付メニューに登録されているオペレーションIDを確認
                if len(row['OPERATION_ID']) is None:
                    # オペレーションID未登録
                    msgstr = g.appmsg.get_api_message("MSG-10360", [in_tableNameToMenuIdList[table_name], row[AnscConst.DF_ITA_LOCAL_PKEY]])
                    frame = inspect.currentframe().f_back
                    g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                    
                    warning_flag = 1
                    # 次のデータへ
                    continue
                
                operation_id = row['OPERATION_ID']
                
                # 代入値紐付メニューに登録されているホストIDの紐付確認
                if row[AnscConst.DF_ITA_LOCAL_HOST_CNT] == 0:
                    # ホストIDの紐付不正
                    msgstr = g.appmsg.get_api_message("MSG-10359", [in_tableNameToMenuIdList[table_name], row[AnscConst.DF_ITA_LOCAL_PKEY], row['HOST_ID']])
                    frame = inspect.currentframe().f_back
                    g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                    
                    warning_flag = 1
                    # 次のデータへ
                    continue
                
                # 代入値紐付メニューに登録されているホストIDを確認
                if len(row['HOST_ID']) is None:
                    msgstr = g.appmsg.get_api_message("MSG-10361", [in_tableNameToMenuIdList[table_name], row[AnscConst.DF_ITA_LOCAL_PKEY]])
                    frame = inspect.currentframe().f_back
                    g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                    
                    warning_flag = 1
                    # 次のデータへ
                    continue
                
                host_id = row['HOST_ID']
                
                # 代入値自動登録設定に登録されている変数に対応する具体値を取得する
                for col_name, col_val in row.items():
                    col_val_key = col_val
                    
                    # パラメータシート側の項番取得
                    if AnscConst.DF_ITA_LOCAL_PKEY == col_name:
                        col_row_id = col_val
                
                # 具体値カラム以外を除外
                search_list = [AnscConst.DF_ITA_LOCAL_OPERATION_CNT, AnscConst.DF_ITA_LOCAL_HOST_CNT, AnscConst.DF_ITA_LOCAL_DUP_CHECK_ITEM, "OPERATION_ID", "HOST_ID", AnscConst.DF_ITA_LOCAL_PKEY]
                if col_name in search_list:
                    continue_flg = 1
                    continue
                
                # 再度カラムをチェック
                if table_name in in_tabColNameToValAssRowList:
                    if col_name not in in_tabColNameToValAssRowList[table_name]:
                        continue
                
                for col_data in in_tabColNameToValAssRowList[table_name][col_name]:
                    # IDcolumnの場合は参照元から具体値を取得する
                    if not col_data['REF_TABLE_NAME'] == "":
                        sql = ""
                        sql = sql + "SELECT " + col_data['REF_COL_NAME'] + " "
                        sql = sql + "FROM " + col_data['REF_TABLE_NAME'] + " "
                        where = "WHERE " + col_data['REF_PKEY_NAME'] + "=%" + col_data['REF_PKEY_NAME'] + " AND DISUSE_FLAG='0'"
                        count = WS_DB.table_count(col_data['REF_TABLE_NAME'], where, [col_val_key])
                        
                        col_val = ""
                        # 0件ではない場合
                        if not count == 0:
                            data_list = WS_DB.table_select(col_data['REF_TABLE_NAME'], where, [col_val_key])
                            for tgt_row in data_list:
                                col_val = tgt_row[col_data['REF_COL_NAME']]
                                # TPF/CPF変数カラム判定
                                if col_data['REF_TABLE_NAME'] in VariableColumnAry:
                                    if col_data['REF_COL_NAME'] in VariableColumnAry[col_data['REF_TABLE_NAME']]:
                                        col_val = "'{{ col_val }}'"
                        else:
                            # プルダウン選択先のレコードが廃止されている
                            msgstr = g.appmsg.get_api_message("MSG-10438", [in_tableNameToMenuIdList[table_name], row[AnscConst.DF_ITA_LOCAL_PKEY], col_data['COL_TITLE']])
                            frame = inspect.currentframe().f_back
                            g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                            warning_flag = 1
                            # 次のデータへ
                            continue
                    
                    ret = self.getMenuColumnInfo(in_tableNameToMenuIdList[table_name], col_name)
                    col_name_rest = ret[0]
                    col_class = ret[1]
                    col_filepath = ""
                    col_file_md5 = ""
                    if col_class == "FileUploadColumn":
                        col_filepath = ""
                        if not col_val == "":
                            col_filepath = "/uploadfiles" + in_tableNameToMenuIdList[table_name] + col_name_rest
                            if not os.path.exists(col_filepath):
                                msgstr = g.appmsg.get_api_message("MSG-10166", [table_name, col_name, col_row_id, col_filepath])
                                frame = inspect.currentframe().f_back
                                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                                warning_flag = 1
                                # 次のデータへ
                                continue
                            
                            col_file_md5 = self.md5_file(col_filepath)

                    # 代入値管理の登録に必要な情報を生成
                    ret = self.makeVarsAssignData(table_name,
                                        col_name,
                                        col_val,
                                        col_row_id,
                                        col_class,
                                        col_filepath,
                                        col_file_md5,
                                        col_data['NULL_DATA_HANDLING_FLG'],
                                        operation_id,
                                        host_id,
                                        col_data,
                                        ina_vars_ass_list,
                                        lv_varsAssChkList,
                                        ina_array_vars_ass_list,
                                        lv_arrayVarsAssChkList,
                                        in_tableNameToMenuIdList[table_name],
                                        row[AnscConst.DF_ITA_LOCAL_PKEY])
                    
                    ina_vars_ass_list = ret[0]
                    ina_array_vars_ass_list = ret[2]
        
        return ina_vars_ass_list, ina_array_vars_ass_list, warning_flag

    def makeVarsAssignData(self,
                            in_table_name,
                            in_col_name,
                            in_col_val,
                            in_col_row_id,
                            in_col_class,
                            in_col_filepath,
                            in_col_file_md5,
                            in_null_data_handling_flg,
                            in_operation_id,
                            in_host_id,
                            in_col_list,
                            ina_vars_ass_list,
                            ina_vars_ass_chk_list,
                            ina_array_vars_ass_list,
                            ina_array_vars_ass_chk_list,
                            in_menu_id,
                            in_row_id):
        """
        CMDB代入値紐付対象メニューの情報から代入値管理に登録する情報を生成
        
        Arguments:
            in_table_name: テーブル名
            in_col_name: カラム名
            in_col_val: カラムの具体値
            in_col_row_id: パラメータシートの項番
            in_col_class: カラムのクラス名
            in_col_filepath: パターンID
            in_vars_link_id: 変数ID
            in_col_seq_combination_id: メンバー変数ID
            in_vars_assign_seq: 代入順序
            in_col_val: 具体値
            in_col_row_id: パラメータシートの項番
            in_col_class: カラムのクラス名
            in_col_filepath: FileUpLoadColumnのファイルパス
            in_sensitive_flg: sensitive設定
            ina_vars_ass_chk_list: 一般変数・複数具体値変数用 代入順序重複チェック配列
            ina_array_vars_ass_chk_list: 多次元変数配列変数用 列順序重複チェック配列
            in_menu_id: 紐付メニューID
            in_column_id: 代入値自動登録設定
            keyValueType: Value/Key
            in_row_id: 紐付テーブル主キー値
        Retruns:
            str: ファイルのMD5ハッシュ値
        """
        
        # 外部CMDBメニューでColumnGroupを使用したカラムを読取ると
        # ロードテーブルより読み取るとColumnGroup名/ColumnTitleになる。
        # 代入値管理への登録はColumnTitleのみにする。
        col_name_array = in_col_list['COL_TITLE'].split('/')
        if col_name_array == 0 or len(col_name_array) == 1:
            col_name = in_col_list['COL_TITLE']
        else:
            idx = len(col_name_array)
            idx = idx - 1
            col_name = col_name_array[idx]
        
        # カラムタイプを判定
        if in_col_list['COL_TYPE'] == AnscConst.DF_COL_TYPE_VAL:
            # Value型カラムの場合
            # 具体値が空白か判定
            ret = self.validateValueTypeColValue(in_col_val, in_null_data_handling_flg, in_menu_id, in_row_id, in_col_list['COL_TITLE'])
            if ret == 0:
                return ina_vars_ass_list, ina_vars_ass_chk_list, ina_array_vars_ass_list, ina_array_vars_ass_chk_list
            
            # checkAndCreateVarsAssignDataの戻りは判定しない。
            ret = self.checkAndCreateVarsAssignData(in_table_name,
                                            in_col_name,
                                            in_col_list['VAL_VAR_TYPE'],
                                            in_operation_id,
                                            in_host_id,
                                            in_col_list['PATTERN_ID'],
                                            in_col_list['VAL_VARS_LINK_ID'],
                                            in_col_list['VAL_COL_SEQ_COMBINATION_ID'],
                                            in_col_list['VAL_ASSIGN_SEQ'],
                                            col_name,
                                            in_col_row_id,
                                            in_col_class,
                                            in_col_filepath,
                                            in_col_file_md5,
                                            in_col_list['VALUE_SENSITIVE_FLAG'],
                                            ina_vars_ass_list,
                                            ina_vars_ass_chk_list,
                                            ina_array_vars_ass_list,
                                            ina_array_vars_ass_chk_list,
                                            in_menu_id,
                                            in_col_list['COLUMN_ID'],
                                            "Value",
                                            in_row_id)
            
            ina_vars_ass_list = ret[0]
            ina_vars_ass_chk_list = ret[1]
            ina_array_vars_ass_list = ret[2]
            ina_array_vars_ass_chk_list = ret[3]
        
        if in_col_list['COL_TYPE'] == AnscConst.DF_COL_TYPE_KEY:
            # 具体値が空白か判定
            ret = self.validateKeyTypeColValue(in_col_val, in_menu_id, in_row_id, in_col_list['COL_TITLE'])
            if ret == 0:
                return ina_vars_ass_list, ina_vars_ass_chk_list, ina_array_vars_ass_list, ina_array_vars_ass_chk_list
            
            # checkAndCreateVarsAssignDataの戻りは判定しない。
            ret = self.checkAndCreateVarsAssignData(in_table_name,
                                            in_col_name,
                                            in_col_list['KEY_VAR_TYPE'],
                                            in_operation_id,
                                            in_host_id,
                                            in_col_list['PATTERN_ID'],
                                            in_col_list['KEY_VARS_LINK_ID'],
                                            in_col_list['KEY_COL_SEQ_COMBINATION_ID'],
                                            in_col_list['KEY_ASSIGN_SEQ'],
                                            col_name,
                                            in_col_row_id,
                                            in_col_class,
                                            in_col_filepath,
                                            in_col_file_md5,
                                            in_col_list['KEY_SENSITIVE_FLAG'],
                                            ina_vars_ass_list,
                                            ina_vars_ass_chk_list,
                                            ina_array_vars_ass_list,
                                            ina_array_vars_ass_chk_list,
                                            in_menu_id,
                                            in_col_list['COLUMN_ID'],
                                            "Key",
                                            in_row_id)
            
            ina_vars_ass_list = ret[0]
            ina_vars_ass_chk_list = ret[1]
            ina_array_vars_ass_list = ret[2]
            ina_array_vars_ass_chk_list = ret[3]
        
        return ina_vars_ass_list, ina_vars_ass_chk_list, ina_array_vars_ass_list, ina_array_vars_ass_chk_list
    
    def md5_file(self, file):
        """
        指定したファイルのMD5ハッシュ値を計算する
        
        Arguments:
            file (str): Input file.
        Retruns:
            str: ファイルのMD5ハッシュ値
        """
        md5 = hashlib.md5()
        with open(file, 'rb') as f:
            for block in iter(lambda: f.read(65536), b''):
                md5.update(block)
        return md5.hexdigest()
    
    def validateValueTypeColValue(self, in_col_val, in_null_data_handling_flg, in_menu_id, in_row_id, in_menu_title):
        """
        具体値が空白か判定(Value型)
        
        Arguments:
            in_col_val: 具体値
            in_null_data_handling_flg: 代入値自動登録設定のNULL登録フラグ
            in_menu_id: 紐付メニューID
            in_row_id: 紐付テーブル主キー値
            in_menu_title: 紐付メニュー名

        Returns:
            id: '1':有効    '2':無効
        """
        # 具体値が空白の場合
        if len(in_col_val) == 0:
            # 具体値が空でも代入値管理NULLデータ連携が有効か判定する
            if not self.getNullDataHandlingID(in_null_data_handling_flg == '1'):
                msgstr = g.appmsg.get_api_message("MSG-10375", [in_menu_id, in_row_id, in_menu_title])
                frame = inspect.currentframe().f_back
                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
                
                return False
        
        return True
    
    def validateKeyTypeColValue(in_col_val, in_menu_id, in_row_id, in_menu_title):
        """
        具体値が空白か判定(Key型)
        
        Arguments:
            in_col_val: 具体値
            in_menu_id: 紐付メニューID
            in_row_id: 紐付テーブル主キー値
            in_menu_title: 紐付メニュー名

        Returns:
            is success:(bool)
        """
        # 具体値が空白の場合
        if len(in_col_val) == 0:
            msgstr = g.appmsg.get_api_message("MSG-10377", [in_menu_id, in_row_id, in_menu_title])
            frame = inspect.currentframe().f_back
            g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
            
            return False
        
        return True
    
    def getMenuColumnInfo(self, in_menu_id, in_col_name, WS_DB):
        """
        メニュー・カラム紐付管理から項目名(REST）とカラムクラスを取得する
        
        Arguments:
            in_menu_id: 紐付メニューID
            in_col_name: カラム名
            WS_DB: WorkspaceDBインスタンス

        Returns:
            column_name_rest: 項目名(REST）
            column_class: カラムクラス
        """
        
        column_name_rest = ""
        column_class = ""

        sql = " SELECT COLUMN_NAME_REST, "
        sql += " COLUMN_CLASS "
        sql += " FROM T_COMN_MENU_COLUMN_LINK "
        sql += " WHERE MENU_ID '" + in_menu_id + "'"
        sql += " AND COL_NAME '" + in_col_name + "'"
        sql += " AND DISUSE_FLAG = '0'"
        
        data_list = WS_DB.sql_execute(sql)

        for data in data_list:
            column_name_rest = data['COLUMN_NAME_REST']
            column_class = data['COLUMN_CLASS']
        
        return column_name_rest, column_class

    def getNullDataHandlingID(self, in_null_data_handling_flg, WS_DB):
        """
        パラメータシートの具体値がNULLの場合でも代入値管理ら登録するかを判定
        
        Arguments:
            in_null_data_handling_flg: 代入値自動登録設定のNULL登録フラグ
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
        """
        
        # インターフェース情報からNULLデータを代入値管理に登録するかのデフォルト値を取得する。
        ret = self.getIFInfoDB(WS_DB)
        
        if ret[0] == 0:
            error_flag = 1
            raise ValidationException(ret[2])
        
        lv_if_info = ret[1]
        g_null_data_handling_def = lv_if_info["NULL_DATA_HANDLING_FLG"]
        
        # 代入値自動登録設定のNULL登録フラグ判定
        if in_null_data_handling_flg == '1':
            id = '1'
        elif in_null_data_handling_flg == '2':
            id = '2'
        else:
            # インターフェース情報のNULL登録フラグ判定
            if g_null_data_handling_def == '1':
                id = '1'
            elif g_null_data_handling_def == '2':
                id = '2'
        
        return id
    
    def checkAndCreateVarsAssignData(in_table_name,
                                    in_col_name,
                                    in_vars_attr,
                                    in_operation_id,
                                    in_host_id,
                                    in_patten_id,
                                    in_vars_link_id,
                                    in_col_seq_combination_id,
                                    in_vars_assign_seq,
                                    in_col_val,
                                    in_col_row_id,
                                    in_col_class,
                                    in_col_filepath,
                                    in_col_file_md5,
                                    in_sensitive_flg,
                                    ina_vars_ass_chk_list,
                                    ina_array_vars_ass_chk_list,
                                    in_menu_id,
                                    in_column_id,
                                    keyValueType,
                                    in_row_id):
        """
        CMDB代入値紐付対象メニューの情報から代入値管理に登録する情報を生成
        
        Arguments:
            in_table_name: テーブル名
            in_col_name: カラム名
            in_vars_attr: 変数区分 (1:一般変数, 2:複数具体値, 3:多次元変数)
            in_operation_id: オペレーションID
            in_host_id: ホスト名
            in_patten_id: パターンID
            in_vars_link_id: 変数ID
            in_col_seq_combination_id: メンバー変数ID
            in_vars_assign_seq: 代入順序
            in_col_val: 具体値
            in_col_row_id: パラメータシートの項番
            in_col_class: カラムのクラス名
            in_col_filepath: FileUpLoadColumnのファイルパス
            in_sensitive_flg: sensitive設定
            ina_vars_ass_chk_list: 一般変数・複数具体値変数用 代入順序重複チェック配列
            ina_array_vars_ass_chk_list: 多次元変数配列変数用 列順序重複チェック配列
            in_menu_id: 紐付メニューID
            in_column_id: 代入値自動登録設定
            keyValueType: Value/Key
            in_row_id: 紐付テーブル主キー値

        Returns:
            is success:(bool)
        """
        
        chk_status = False
        chk_flg = True
        
        # 変数のタイプを判定
        if in_vars_attr == AnscConst.GC_VARS_ATTR_STD or in_vars_attr == AnscConst.GC_VARS_ATTR_LIST:
            # 一般変数・複数具体値
            # オペ+作業+ホスト+変数の組合せで代入順序が重複していないか判定
            if in_operation_id in ina_vars_ass_chk_list:
                if in_patten_id in ina_vars_ass_chk_list[in_operation_id]:
                    if in_host_id in ina_vars_ass_chk_list[in_operation_id][in_patten_id]:
                        if in_vars_link_id in ina_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id]:
                            if in_vars_assign_seq in ina_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id]:
                                # 既に登録されている
                                dup_info = ina_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id][in_vars_assign_seq]
                                chk_flg = False
                                
                                msgstr = g.appmsg.get_api_message("MSG-10369", [dup_info['COLUMN_ID'], in_column_id, in_column_id, in_operation_id, in_host_id, keyValueType])
                                frame = inspect.currentframe().f_back
                                g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
            if chk_flg == 1:
                chk_status = True
                # オペ+作業+ホスト+変数+メンバ変数の組合せの代入順序退避
                ina_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id][in_vars_assign_seq] = {'COLUMN_ID': in_column_id}
            
            if in_col_class == "FileUploadColumn" and keyValueType == "Key":
                in_col_file_md5 = ""
            # 代入値管理の登録に必要な情報退避
            ina_vars_ass_list = {'TABLE_NAME': in_table_name,
                                'COL_NAME': in_col_name,
                                'COL_ROW_ID': in_col_row_id,
                                'COL_CLASS': in_col_class,
                                'COL_FILEUPLOAD_PATH': in_col_filepath,
                                'COL_FILEUPLOAD_MD5': in_col_file_md5,
                                'REG_TYPE': keyValueType,
                                'OPERATION_NO_UAPK': in_operation_id,
                                'PATTERN_ID': in_patten_id,
                                'SYSTEM_ID': in_host_id,
                                'VARS_LINK_ID': in_vars_link_id,
                                'ASSIGN_SEQ': in_vars_assign_seq,
                                'VARS_ENTRY': in_col_val,
                                'SENSITIVE_FLAG': in_sensitive_flg,
                                'VAR_TYPE': in_vars_attr,
                                'STATUS': chk_status}
        elif in_vars_attr == AnscConst.GC_VARS_ATTR_M_ARRAY:
            # 多次元変数
            # オペ+作業+ホスト+変数+メンバ変数の組合せで代入順序が重複していないか判定
            if in_operation_id in ina_array_vars_ass_chk_list:
                if in_patten_id in ina_array_vars_ass_chk_list[in_operation_id]:
                    if in_host_id in ina_array_vars_ass_chk_list[in_operation_id][in_patten_id]:
                        if in_vars_link_id in ina_array_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id]:
                            if in_col_seq_combination_id in ina_array_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id]:
                                if in_vars_assign_seq in ina_array_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id][in_col_seq_combination_id]:
                                    # 既に登録されている
                                    dup_info = ina_array_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id][in_col_seq_combination_id][in_vars_assign_seq]
                                    chk_flg = False
                                    
                                    msgstr = g.appmsg.get_api_message("MSG-10369", [dup_info['COLUMN_ID'], in_column_id, in_column_id, in_operation_id, in_host_id, keyValueType])
                                    frame = inspect.currentframe().f_back
                                    g.applogger.debnug(os.path.basename(__file__) + frame.f_lineno + msgstr)
            if chk_flg == 1:
                chk_status = True
                # オペ+作業+ホスト+変数+メンバ変数の組合せの代入順序退避
                ina_array_vars_ass_chk_list[in_operation_id][in_patten_id][in_host_id][in_vars_link_id][in_vars_assign_seq] = {'COLUMN_ID': in_column_id}
            
            if in_col_class == "FileUploadColumn" and keyValueType == "Key":
                in_col_file_md5 = ""
            # 代入値管理の登録に必要な情報退避
            ina_array_vars_ass_list = {'TABLE_NAME': in_table_name,
                                'COL_NAME': in_col_name,
                                'COL_ROW_ID': in_col_row_id,
                                'COL_CLASS': in_col_class,
                                'COL_FILEUPLOAD_PATH': in_col_filepath,
                                'COL_FILEUPLOAD_MD5': in_col_file_md5,
                                'REG_TYPE': keyValueType,
                                'OPERATION_NO_UAPK': in_operation_id,
                                'PATTERN_ID': in_patten_id,
                                'SYSTEM_ID': in_host_id,
                                'VARS_LINK_ID': in_vars_link_id,
                                'ASSIGN_SEQ': in_vars_assign_seq,
                                'VARS_ENTRY': in_col_val,
                                'SENSITIVE_FLAG': in_sensitive_flg,
                                'VAR_TYPE': in_vars_attr,
                                'STATUS': chk_status}
        
        return ina_vars_ass_list, ina_vars_ass_chk_list, ina_array_vars_ass_list, ina_array_vars_ass_chk_list
    
    def readValAssign(self, WS_DB):
        """
        代入値自動登録設定からカラム情報を取得する。
        
        Arguments:
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            inout_tableNameToMenuIdList: テーブル名配列
            inout_tabColNameToValAssRowList: カラム情報配列
            inout_tableNameToPKeyNameList: テーブル主キー名配列
        """
        
        global lv_val_assign_tbl
        global lv_pattern_link_tbl
        global lv_array_member_tbl
        global lv_member_col_comb_tbl
        global lv_ptn_vars_link_tbl
        
        inout_tableNameToPKeyNameList = {}
        
        sql = " SELECT                                                            \n"
        sql += "   TBL_A.COLUMN_ID                                             ,  \n"
        sql += "   TBL_A.MENU_ID                                               ,  \n"
        sql += "   TBL_C.TABLE_NAME                                            ,  \n"
        sql += "   TBL_C.PK_COLUMN_NAME_REST                                   ,  \n"
        sql += "   TBL_C.DISUSE_FLAG  AS TBL_DISUSE_FLAG                       ,  \n"
        sql += "   TBL_A.COLUMN_LIST_ID                                        ,  \n"
        sql += "   TBL_B.COL_NAME                                              ,  \n"
        sql += "   TBL_B.REF_TABLE_NAME                                        ,  \n"
        sql += "   TBL_B.REF_PKEY_NAME                                         ,  \n"
        sql += "   TBL_B.REF_COL_NAME                                          ,  \n"
        sql += "   TBL_B.COLUMN_CLASS                                          ,  \n"
        sql += "   TBL_B.AUTOREG_HIDE_ITEM                                     ,  \n"
        sql += "   TBL_B.AUTOREG_ONLY_ITEM                                     ,  \n"
        
        sql += "   TBL_B.DISUSE_FLAG  AS COL_DISUSE_FLAG                       ,  \n"
        sql += "   TBL_A.COL_TYPE                                              ,  \n"
        
        # 代入値管理データ連携フラグ
        sql += "   TBL_A.NULL_DATA_HANDLING_FLG                                ,  \n"
        
        # 作業パターン詳細の登録確認
        sql += "   TBL_A.MOVEMENT_ID                                           ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       COUNT(*)                                                   \n"
        sql += "     FROM                                                         \n"
        sql += lv_pattern_link_tbl + "                                            \n"
        sql += "     WHERE                                                        \n"
        sql += "       MOVEMENT_ID  = TBL_A.MOVEMENT_ID AND                       \n"
        sql += "       DISUSE_FLAG = '0'                                          \n"
        sql += "   ) AS PATTERN_CNT                                            ,  \n"
        sql += "                                                                  \n"
        
        # (Val)作業パターン変数紐付の登録確認
        sql += "   TBL_A.VAL_MVMT_VAR_LINK_ID                                  ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       COUNT(*)                                                   \n"
        sql += "     FROM                                                         \n"
        sql += lv_ptn_vars_link_tbl + "                                           \n"
        sql += "     WHERE                                                        \n"
        sql += "       MOVEMENT_ID    = TBL_A.MOVEMENT_ID        AND              \n"
        sql += "       MVMT_VAR_LINK_ID  = TBL_A.VAL_MVMT_VAR_LINK_ID  AND        \n"
        sql += "       DISUSE_FLAG   = '0'                                        \n"
        sql += "   ) AS VAL_PTN_VARS_LINK_CNT                                  ,  \n"
        
        # (Val)多次元変数配列組合せ管理
        sql += "   TBL_A.VAL_COL_SEQ_COMBINATION_ID                            ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       COL_COMBINATION_MEMBER_ALIAS                               \n"
        sql += "     FROM                                                         \n"
        sql += lv_member_col_comb_tbl + "                                         \n"
        sql += "     WHERE                                                        \n"
        sql += "       MVMT_VAR_LINK_ID IN (                                      \n"
        sql += "         SELECT                                                   \n"
        sql += "           VARS_NAME                                              \n"
        sql += "         FROM                                                     \n"
        sql += lv_ptn_vars_link_tbl + "                                           \n"
        sql += "         WHERE                                                    \n"
        sql += "           MOVEMENT_ID    = TBL_A.MOVEMENT_ID        AND          \n"
        sql += "           MVMT_VAR_LINK_ID  = TBL_A.VAL_MVMT_VAR_LINK_ID  AND    \n"
        sql += "           DISUSE_FLAG   = '0'                                    \n"
        sql += "         )                                                        \n"
        sql += "       AND                                                        \n"
        sql += "       COL_SEQ_COMBINATION_ID = TBL_A.VAL_COL_SEQ_COMBINATION_ID AND     \n"
        sql += "       DISUSE_FLAG = '0'                                          \n"
        sql += "   ) AS VAL_COL_COMBINATION_MEMBER_ALIAS                       ,  \n"
        
        # (Val)多次元変数メンバー管理
        sql += "   TBL_A.VAL_ASSIGN_SEQ                                        ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       ASSIGN_SEQ_NEED                                            \n"
        sql += "     FROM                                                         \n"
        sql += lv_array_member_tbl + "                                            \n"
        sql += "     WHERE                                                        \n"
        sql += "       MVMT_VAR_LINK_ID IN (                                      \n"
        sql += "         SELECT                                                   \n"
        sql += "           VARS_NAME                                              \n"
        sql += "         FROM                                                     \n"
        sql += lv_ptn_vars_link_tbl + "                                           \n"
        sql += "         WHERE                                                    \n"
        sql += "           MOVEMENT_ID    = TBL_A.MOVEMENT_ID        AND          \n"
        sql += "           MVMT_VAR_LINK_ID  = TBL_A.VAL_MVMT_VAR_LINK_ID  AND    \n"
        sql += "           DISUSE_FLAG   = '0'                                    \n"
        sql += "         )                                                        \n"
        sql += "       AND                                                        \n"
        sql += "       ARRAY_MEMBER_ID IN (                                       \n"
        sql += "         SELECT                                                   \n"
        sql += "           ARRAY_MEMBER_ID                                        \n"
        sql += "         FROM                                                     \n"
        sql += lv_member_col_comb_tbl + "                                         \n"
        sql += "         WHERE                                                    \n"
        sql += "           COL_SEQ_COMBINATION_ID = TBL_A.KEY_COL_SEQ_COMBINATION_ID AND \n"
        sql += "           DISUSE_FLAG   = '0'                                    \n"
        sql += "         )                                                        \n"
        sql += "       AND                                                        \n"
        sql += "       DISUSE_FLAG = '0'                                          \n"
        sql += "   ) AS VAL_ASSIGN_SEQ_NEED                                    ,  \n"
        
        # (Key)作業パターン変数紐付の登録確認
        sql += "   TBL_A.KEY_MVMT_VAR_LINK_ID                                  ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       COUNT(*)                                                   \n"
        sql += "     FROM                                                         \n"
        sql += lv_ptn_vars_link_tbl + "                                           \n"
        sql += "     WHERE                                                        \n"
        sql += "       MOVEMENT_ID    = TBL_A.MOVEMENT_ID        AND              \n"
        sql += "       MVMT_VAR_LINK_ID  = TBL_A.KEY_MVMT_VAR_LINK_ID  AND        \n"
        sql += "       DISUSE_FLAG   = '0'                                        \n"
        sql += "   ) AS KEY_PTN_VARS_LINK_CNT                                  ,  \n"
        
        # (Key)多次元変数配列組合せ管理
        sql += "   TBL_A.KEY_COL_SEQ_COMBINATION_ID                            ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       COL_COMBINATION_MEMBER_ALIAS                               \n"
        sql += "     FROM                                                         \n"
        sql += lv_member_col_comb_tbl + "                                         \n"
        sql += "     WHERE                                                        \n"
        sql += "       VAL_MVMT_VAR_LINK_ID IN (                                  \n"
        sql += "         SELECT                                                   \n"
        sql += "           VARS_NAME                                              \n"
        sql += "         FROM                                                     \n"
        sql += lv_ptn_vars_link_tbl + "                                           \n"
        sql += "         WHERE                                                    \n"
        sql += "           MOVEMENT_ID    = TBL_A.MOVEMENT_ID        AND          \n"
        sql += "           MVMT_VAR_LINK_ID  = TBL_A.KEY_MVMT_VAR_LINK_ID  AND    \n"
        sql += "           DISUSE_FLAG   = '0'                                    \n"
        sql += "         )                                                        \n"
        sql += "       AND                                                        \n"
        sql += "       COL_SEQ_COMBINATION_ID = TBL_A.KEY_COL_SEQ_COMBINATION_ID AND     \n"
        sql += "       DISUSE_FLAG = '0'                                          \n"
        sql += "   ) AS KEY_COL_COMBINATION_MEMBER_ALIAS                       ,  \n"
        
        # (Key)多次元変数メンバー管理
        sql += "   TBL_A.KEY_ASSIGN_SEQ                                        ,  \n"
        sql += "   (                                                              \n"
        sql += "     SELECT                                                       \n"
        sql += "       ASSIGN_SEQ_NEED                                            \n"
        sql += "     FROM                                                         \n"
        sql += lv_array_member_tbl + "                                            \n"
        sql += "     WHERE                                                        \n"
        sql += "       MVMT_VAR_LINK_ID IN (                                      \n"
        sql += "         SELECT                                                   \n"
        sql += "           VARS_NAME                                              \n"
        sql += "         FROM                                                     \n"
        sql += lv_ptn_vars_link_tbl + "                                           \n"
        sql += "         WHERE                                                    \n"
        sql += "           MOVEMENT_ID    = TBL_A.MOVEMENT_ID        AND          \n"
        sql += "           MVMT_VAR_LINK_ID  = TBL_A.KEY_MVMT_VAR_LINK_ID  AND    \n"
        sql += "           DISUSE_FLAG   = '0'                                    \n"
        sql += "         )                                                        \n"
        sql += "       AND                                                        \n"
        sql += "       ARRAY_MEMBER_ID IN (                                       \n"
        sql += "         SELECT                                                   \n"
        sql += "           ARRAY_MEMBER_ID                                        \n"
        sql += "         FROM                                                     \n"
        sql += lv_member_col_comb_tbl + "                                         \n"
        sql += "         WHERE                                                    \n"
        sql += "           COL_SEQ_COMBINATION_ID = TBL_A.KEY_COL_SEQ_COMBINATION_ID AND \n"
        sql += "           DISUSE_FLAG   = '0'                                    \n"
        sql += "         )                                                        \n"
        sql += "       AND                                                        \n"
        sql += "       DISUSE_FLAG = '0'                                          \n"
        sql += "   ) AS KEY_ASSIGN_SEQ_NEED,                                      \n"
        sql += "   TBL_D.DISUSE_FLAG AS ANSIBLE_TARGET_TABLE                      \n"
        sql += " FROM                                                             \n"
        sql += lv_val_assign_tbl + "  TBL_A                                       \n"
        sql += "   LEFT JOIN T_COMN_MENU_COLUMN_LINK TBL_B ON                     \n"
        sql += "          (TBL_A.COLUMN_LIST_ID = TBL_B.COLUMN_DEFINITION_ID)     \n"
        sql += "          OR (TBL_B.AUTOREG_ONLY_ITEM = 1)                        \n"
        sql += "   LEFT JOIN T_COMN_MENU_TABLE_LINK          TBL_C ON             \n"
        sql += "          (TBL_B.MENU_ID        = TBL_C.MENU_ID)                  \n"
        sql += "   LEFT JOIN T_COMN_MENU   TBL_D ON                               \n"
        sql += "          (TBL_C.MENU_ID        = TBL_D.MENU_ID)                  \n"
        sql += " WHERE                                                            \n"
        sql += "   TBL_A.DISUSE_FLAG='0'                                          \n"
        sql += "   AND TBL_B.AUTOREG_HIDE_ITEM='0'                                \n"
        sql += " ORDER BY TBL_A.COLUMN_ID                                         \n"

        data_list = WS_DB.sql_execute(sql)

        inout_tableNameToMenuIdList = {}
        inout_tabColNameToValAssRowList = {}
        for data in data_list:
            # CMDB代入値紐付メニューが廃止されているか判定
            if data['TBL_DISUSE_FLAG'] != '0':
                msgstr = g.get_api_message("MSG-10337", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10337", [data['COLUMN_ID']])
            
            # SHEET_TYPEが1(ホスト・オペレーション)で廃止レコードでないかを判定
            if data['ANSIBLE_TARGET_TABLE'] != '0':
                msgstr = g.get_api_message("MSG-10437", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10437", [data['COLUMN_ID']])
            
            # CMDB代入値紐付メニューのカラムが廃止されているか判定
            if data['COL_DISUSE_FLAG'] != '0':
                msgstr = g.get_api_message("MSG-10339", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10339", [data['COLUMN_ID']])
            
            # 作業パターン詳細に作業パターンが未登録
            if data['PATTERN_CNT'] == '0':
                msgstr = g.get_api_message("MSG-10336", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10336", [data['COLUMN_ID']])
            
            # CMDB代入値紐付メニューが登録されているか判定
            if len(data['TABLE_NAME']) is None:
                msgstr = g.get_api_message("MSG-10338", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10338", [data['COLUMN_ID']])
            
            # CMDB代入値紐付メニューの主キーが登録されているか判定
            if len(data['PK_COLUMN_NAME_REST']) is None:
                msgstr = g.get_api_message("MSG-10404", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10404", [data['COLUMN_ID']])
            
            # CMDB代入値紐付メニューのカラムが未登録か判定
            if len(data['COL_NAME']) is None:
                msgstr = g.get_api_message("MSG-10340", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10340", [data['COLUMN_ID']])
            
            type_chk = [AnscConst.DF_COL_TYPE_VAL, AnscConst.DF_COL_TYPE_KEY]
            col_type = data['COL_TYPE']
            if col_type in type_chk:
                msgstr = g.get_api_message("MSG-10341", [data['COLUMN_ID']])
                # 次のカラムへ
                raise ValidationException("MSG-10341", [data['COLUMN_ID']])
            
            # Value型変数の変数タイプ
            val_vars_attr = ""
            key_vars_attr = ""
            
            # Key項目・Value項目の検査（当該レコード）
            # カラムタイプにより処理分岐
            
            if col_type == AnscConst.DF_COL_TYPE_VAL:
                ret = self.valAssColumnValidate("Value",
                                                val_vars_attr,
                                                data,
                                                "VAL_VARS_LINK_ID",
                                                "VAL_VARS_NAME",
                                                "VAL_PTN_VARS_LINK_CNT",
                                                "VAL_VARS_ATTRIBUTE_01",
                                                "VAL_COL_SEQ_COMBINATION_ID",
                                                "VAL_COL_COMBINATION_MEMBER_ALIAS",
                                                "VAL_ASSIGN_SEQ",
                                                "VAL_ASSIGN_SEQ_NEED"
                                                )
            
                if ret == 0:
                    continue
            
            if col_type == AnscConst.DF_COL_TYPE_KEY:
                ret = self.valAssColumnValidate("Key",
                                                key_vars_attr,
                                                data,
                                                "KEY_VARS_LINK_ID",
                                                "KEY_VARS_NAME",
                                                "KEY_PTN_VARS_LINK_CNT",
                                                "KEY_VARS_ATTRIBUTE_01",
                                                "KEY_COL_SEQ_COMBINATION_ID",
                                                "KEY_COL_COMBINATION_MEMBER_ALIAS",
                                                "KEY_ASSIGN_SEQ",
                                                "KEY_ASSIGN_SEQ_NEED"
                                                )
            
                if ret == 0:
                    continue

            inout_tableNameToMenuIdList[data['TABLE_NAME']] = data['MENU_ID']
            
            # PasswordColumnかを判定
            key_sensitive_flg = AnscConst.DF_SENSITIVE_OFF
            value_sensitive_flg = AnscConst.DF_SENSITIVE_OFF
            if data['COLUMN_CLASS'] == 'PasswordColumn':
                value_sensitive_flg = AnscConst.DF_SENSITIVE_ON
            
            inout_tabColNameToValAssRowList[data['TABLE_NAME']] = {}
            inout_tabColNameToValAssRowList[data['TABLE_NAME']][data['COL_NAME']] = {}
            inout_tabColNameToValAssRowList[data['TABLE_NAME']][data['COL_NAME']]['data'] = {
                                                                            'COLUMN_ID': data['COLUMN_ID'],
                                                                            'COL_TYPE': data['COL_TYPE'],
                                                                            'COLUMN_CLASS': data['COLUMN_CLASS'],
                                                                            'REF_TABLE_NAME': data['REF_TABLE_NAME'],
                                                                            'REF_PKEY_NAME': data['REF_PKEY_NAME'],
                                                                            'REF_COL_NAME': data['REF_COL_NAME'],
                                                                            'MOVEMENT_ID': data['MOVEMENT_ID'],
                                                                            'VAL_MVMT_VAR_LINK_ID': data['VAL_MVMT_VAR_LINK_ID'],
                                                                            'VAL_VAR_TYPE': val_vars_attr,
                                                                            'VAL_COL_SEQ_COMBINATION_ID': data['VAL_COL_SEQ_COMBINATION_ID'],
                                                                            'VAL_COL_COMBINATION_MEMBER_ALIAS': data['VAL_COL_COMBINATION_MEMBER_ALIAS'],
                                                                            'VAL_ASSIGN_SEQ': data['VAL_ASSIGN_SEQ'],
                                                                            'VALUE_SENSITIVE_FLAG': value_sensitive_flg,
                                                                            'KEY_MVMT_VAR_LINK_ID': data['KEY_MVMT_VAR_LINK_ID'],
                                                                            'KEY_VAR_TYPE': key_vars_attr,
                                                                            'KEY_COL_SEQ_COMBINATION_ID': data['KEY_COL_SEQ_COMBINATION_ID'],
                                                                            'KEY_ASSIGN_SEQ': data['KEY_ASSIGN_SEQ'],
                                                                            'NULL_DATA_HANDLING_FLG': data['NULL_DATA_HANDLING_FLG'],
                                                                            'KEY_SENSITIVE_FLAG': key_sensitive_flg}
        
            # テーブルの主キー名退避
            inout_tableNameToPKeyNameList = {data['TABLE_NAME']: data['PK_COLUMN_NAME_REST']}
        
        return True, inout_tableNameToMenuIdList, inout_tabColNameToValAssRowList, inout_tableNameToPKeyNameList

    
    def valAssColumnValidate(WS_DB, 
                            in_col_type, 
                            row, in_vars_link_id, 
                            in_vars_name, 
                            in_ptn_vars_link_cnt,
                            in_vars_attribute_01,
                            in_col_seq_combination_id,
                            in_col_combination_member_alias,
                            in_assign_seq,
                            in_assign_seq_need):
        """
        代入値自動登録設定のカラム情報を検査する。
        
        Arguments:
            WS_DB: WorkspaceDBインスタンス

        Returns:
            is success:(bool)
            ina_if_info: インターフェース情報
            in_error_msg: エラーメッセージ
        """
        
        # 変数の選択判定
        if len(row[in_vars_link_id]) is None:
            msgstr = g.appmsg.get_api_message("MSG-10354", [row['COLUMN_ID'], in_col_type])
            g.applogger.debnug(msgstr)
            return False
        
        # 変数が作業パターン変数紐付にあるか判定
        if len(row[in_ptn_vars_link_cnt]) is None:
            msgstr = g.appmsg.get_api_message("MSG-10348", [row['COLUMN_ID'], in_col_type])
            g.applogger.debnug(msgstr)
            return False
        
        # 設定されている変数が変数一覧にあるか判定
        if len(row[in_vars_name]) is None:
            msgstr = g.appmsg.get_api_message("MSG-10345", [row['COLUMN_ID'], in_col_type])
            g.applogger.debnug(msgstr)
            return False
        
        if row[in_vars_attribute_01] in [AnscConst.GC_VARS_ATTR_STD, AnscConst.GC_VARS_ATTR_LIST, AnscConst.GC_VARS_ATTR_M_ARRAY]:
            inout_vars_attr = row[in_vars_attribute_01]
        else:
            msgstr = g.appmsg.get_api_message("MSG-10439", [row['COLUMN_ID'], in_col_type])
            g.applogger.debnug(msgstr)
            return False
        
        # メンバー変数がメンバー変数一覧にあるか判定
        if inout_vars_attr == AnscConst.GC_VARS_ATTR_STD:
            # メンバー変数の選択判定
            if len(row[in_col_seq_combination_id]) is None:
                msgstr = g.appmsg.get_api_message("MSG-10419", [row['COLUMN_ID'], in_col_type])
                g.applogger.debnug(msgstr)
                return False
        
            # カラムタイプ型に設定されているメンバー変数がメンバー変数一覧にあるか判定
            if len(row[in_col_combination_member_alias]) is None:
                msgstr = g.appmsg.get_api_message("MSG-10349", [row['COLUMN_ID'], in_col_type])
                g.applogger.debnug(msgstr)
                return False
        else:
            if not len(row[in_col_seq_combination_id]) is None:
                msgstr = g.appmsg.get_api_message("MSG-10418", [row['COLUMN_ID'], in_col_type])
                g.applogger.debnug(msgstr)
                return False
        
        if inout_vars_attr == AnscConst.GC_VARS_ATTR_LIST:
            if len(row[in_assign_seq]) is None:
                msgstr = g.appmsg.get_api_message("MSG-10350", [row['COLUMN_ID'], in_col_type])
                g.applogger.debnug(msgstr)
                return False
        
        elif inout_vars_attr == AnscConst.GC_VARS_ATTR_M_ARRAY:
            if row[in_assign_seq_need] == 1 and row[in_assign_seq] is None:
                msgstr = g.appmsg.get_api_message("MSG-10350", [row['COLUMN_ID'], in_col_type])
                g.applogger.debnug(msgstr)
                return False
        
        return True
    
    def getTemplateVarList(self, WS_DB):
        """
        代入値自動登録とパラメータシートから具体値に設定されているTPF変数名を抜出す
        
        Arguments:
            WS_DB: WorkspaceDBインスタンス

        Returns:
            value_list: 抽出した変数リスト
        """
        
        value_list = {}
        sql = " SELECT "
        sql += "  MOVEMENT_ID, "
        sql += "  VAL_MVMT_VAR_LINK_ID, "
        sql += "  FROM  T_ANSR_VALUE_AUTOREG "
        sql += "  AND DISUSE_FLAG ='0' "
        
        data_list = WS_DB.sql_execute(sql)
        
        for row in data_list:
            pattern = "/{{(\s)" + "TPF_" + "[a-zA-Z0-9_]*(\s)}}/"

            ret = re.match(pattern, row['VAL_MVMT_VAR_LINK_ID'])
            if ret:
                if not ret.group() == "":
                    # テンプレート変数が記述されていることを記録
                    value_list['MOVEMENT_ID'] = row['MOVEMENT_ID']
                    value_list['MOVEMENT_ID'] = {}
                    value_list['MOVEMENT_ID']['VAL_MVMT_VAR_LINK_ID'] = row['VAL_MVMT_VAR_LINK_ID']
        
        return value_list
    
    def getTemplgetTargetHostList(self, WS_DB):
        """
        代入値自動登録とパラメータシートから具体値に設定されている作業対象ホストを抜出す
        
        Arguments:
            WS_DB: WorkspaceDBインスタンス

        Returns:
            value_list: 抽出した変数リスト
        """
        
        value_list = {}
        
        sql = " SELECT "
        sql += "  OPERATION_ID, "
        sql += "  MOVEMENT_ID, "
        sql += "  SYSTEM_ID "
        sql += "  FROM  T_ANSR_TGT_HOST "
        sql += "  WHERE DISUSE_FLAG ='0' "
        
        data_list = WS_DB.sql_execute(sql)
        
        for row in data_list:
            value_list['MOVEMENT_ID'] = row['MOVEMENT_ID']
            value_list['MOVEMENT_ID'] = {}
            value_list['MOVEMENT_ID']['OPERATION_ID'] = row['OPERATION_ID']
            value_list['MOVEMENT_ID']['SYSTEM_ID'] = row['SYSTEM_ID']
        
        return value_list