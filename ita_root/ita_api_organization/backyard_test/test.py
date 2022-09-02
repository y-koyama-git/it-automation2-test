from flask import g
from common_libs.common import *  # noqa: F403
from common_libs.ansible_driver.functions.util import get_AnsibleDriverTmpPath
from common_libs.ansible_driver.classes.CheckAnsibleRoleFiles import VarStructAnalysisFileAccess
from common_libs.ansible_driver.classes.VarStructAnalJsonConvClass import VarStructAnalJsonConv


def test_func():
    workspace_id = g.get('WORKSPACE_ID')
    ws_db = DBConnectWs(workspace_id)  # noqa: F405
    objtable = ""
    option = ""
    external_host_name_valid_before(ws_db, objtable, option)


def external_host_name_valid_before(objDBCA, objtable, option):
    """
    登録前ホストネームバリデーション(登録/更新/廃止)
    ARGS:
        objdbca :DB接続クラスインスタンス
        objtabl :メニュー情報、カラム紐付、関連情報
        option :パラメータ、その他設定値
        
    RETRUN:
        retBoo :True/ False
        msg :エラーメッセージ
        option :受け取ったもの
    """
    def_vars_list = {}
    def_varsval_list = {}
    def_array_vars_list = {}
    cpf_vars_list = {}
    tpf_vars_list = {}
    gbl_vars_list = {}
    ITA2User_var_list = {}
    User2ITA_var_list = {}
    save_vars_array = {}
    disuse_role_chk = True

    global_vars_master_list = {}
    template_master_list = {}
    objMTS = ""
    FileID = "3"
    obj = VarStructAnalysisFileAccess(objMTS,
                                      objDBCA,
                                      global_vars_master_list,
                                      template_master_list,
                                      '',
                                      False,
                                      False)
    JsonObj = VarStructAnalJsonConv()
    zip_file_path = ""
    role_package_name = ""
    PkeyID = ""
    if option["cmd_type"] == "Register" or option["cmd_type"] == "Update":
        # ファイルが変更されている場合
        if zip_file_path != "":
            retAry = obj.RolePackageAnalysis(zip_file_path,
                                             role_package_name,
                                             PkeyID,
                                             disuse_role_chk,
                                             def_vars_list,
                                             def_varsval_list,
                                             def_array_vars_list,
                                             True,
                                             cpf_vars_list,
                                             True,
                                             tpf_vars_list,
                                             gbl_vars_list,
                                             ITA2User_var_list,
                                             User2ITA_var_list,
                                             save_vars_array)
            retBool = retAry[0][0]
            intErrorType = retAry[0][1]
            aryErrMsgBody = retAry[0][2]
            retStrBody = retAry[0][3]
            def_vars_list = retAry[1]
            def_array_vars_list = retAry[2]
            def_varsval_list = retAry[3]
            cpf_vars_list = retAry[4]
            tpf_vars_list = retAry[5]
            gbl_vars_list = retAry[6]
            ITA2User_var_list = retAry[7]
            User2ITA_var_list = retAry[8]
            save_vars_array = retAry[9]
            if retBool is False:
                pass

            if retBool is True:
                # 変数構造解析結果を退避
                JsonStr = JsonObj.VarStructAnalJsonDumps(def_vars_list, def_array_vars_list, tpf_vars_list, ITA2User_var_list, gbl_vars_list)

                # VAR_STRUCT_ANAL_JSON_STRING

            if retBool is True:
                ret = CommnVarsUsedListUpdate(PkeyID, FileID, save_vars_array)
                if ret is False:
                    # web_log($dbObj->GetLastErrorMsg());
                    retBool = False
                    # $retStrBody = $dbObj->GetLastErrorMsg();
                            
        elif option["cmd_type"] == "Discard" or option["cmd_type"] == "Restore":
            if option["cmd_type"] == "Discard":
                modeValue_sub = "on"
            if option["cmd_type"] == "Restore":
                modeValue_sub = "off"
            # 廃止の場合、関連レコードを廃止
            # 復活の場合、関連レコードを復活
            ret = CommnVarsUsedListDisuseSet(PkeyID, FileID, modeValue_sub)
            if ret is False:
                # web_log($dbObj->GetLastErrorMsg());
                retBool = False
                # $retStrBody = $dbObj->GetLastErrorMsg();
                pass
        if retBool is True:
            # 登録・更新・復活の場合
            if option["cmd_type"] == "Register" or option["cmd_type"] == "Update" or option["cmd_type"] == "Restore":
                # ファイルの更新されていない場合
                if len(tmpFile) == 0:
                    # 変数構造解析結果を取得
                    sql = "SELECT * FROM T_ANSR_MATL_COLL WHERE ROLE_PACKAGE_ID = %s AND DISUSE_FLAG = '0'"
                    rows = objDBCA.sql_execute(sql, [PkeyID])
                    if len(rows) != 1:
                        retAry = JsonObj.VarStructAnalJsonLoads(rows[0]["VAR_STRUCT_ANAL_JSON_STRING"])
                        def_vars_list = retAry[0]
                        def_array_vars_list = retAry[1]
                        tpf_vars_list = retAry[2]
                        ITA2User_var_list = retAry[3]
                        gbl_vars_list = retAry[4]

                if retBool is True:
                    del obj
                    obj = VarStructAnalysisFileAccess(objMTS,
                                                      objDBCA,
                                                      global_vars_master_list,
                                                      template_master_list,
                                                      '',
                                                      False,
                                                      True)

                    # 他ロールパッケージで同じ変数を使用している場合に、変数定義が一致しているか判定
                    ret = obj.AllRolePackageAnalysis(PkeyID,
                                                     role_package_name,
                                                     def_vars_list,
                                                     def_array_vars_list)
                    if ret is False:
                        retBool = False
                        errmsg = obj.getlasterror()
                        retStrBody = errmsg[0]
