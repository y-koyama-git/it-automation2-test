from flask import g
from common_libs.common import *  # noqa: F403
import os
import subprocess


class tgtclass:
    
    def __init__(self,ws_db):
        self.ws_db = ws_db
        
    def CreateOperationVariables(self, in_operation_id, ina_hostinfolist, mt_host_vars, mt_pioneer_template_host_vars):
        '''
          オペレーション用 予約変数設定
          Arguments:
            in_operation_id:                オペレーションID
            ina_hostinfolist:               機器一覧ホスト情報配列
            mt_host_vars:                   ホスト変数定義配列
            mt_pioneer_template_host_vars:  pioneer tamplate用 ホスト変数定義配列
          Returns:
            なし
        '''
        sql = ''' SELECT
                    OPERATION_NAME,
                    DATE_FORMAT(OPERATION_DATE, '%Y/%m/%d %H:%i') OPERATION_DATE
                  FROM
                    T_COMN_OPERATION
                  WHERE
                    OPERATION_ID = %s
              '''
        rows = self.ws_db.sql_execute(sql, [in_operation_id])

        #if (len(rows) != 1){
        #    msgstr = g.get_api_message("MSG-10178", [os.basename(__file__), self.lineno()])
        #    LocalLogPrint(msgstr)
        #    return false;
        #}

        operationStr = ""
        operationStr = "{}_{}:{}", rows[0]['OPERATION_DATE'], in_operation_id, rows[0]['OPERATION_NAME']

        # オペレーション用の予約変数生成
        for host_name, hostinfo in ina_hostinfolist.items():
            if host_name not in mt_host_vars:
                mt_host_vars[host_name] = {}
            mt_host_vars[host_name][self.LC_OPERATION_VAR_NAME] = operationStr
            # Pioneerの場合の処理
            #switch($this->getAnsibleDriverID()){
            #case DF_PIONEER_DRIVER_ID:
            #    $ina_pioneer_template_host_vars[$host_ip][self::LC_OPERATION_VAR_NAME] = $operationStr;
            #    break;
            #}
        return True
def test_func():
    workspace_id = g.get('WORKSPACE_ID')
    g.applogger.debug(workspace_id)
    ws_db = DBConnectWs(workspace_id)  # noqa: F405
#    row = ws_db.table_columns_get("T_ANSC_DEVICE")
    in_operation_id = "1"
    ina_hostinfolist = {}
    ina_hostinfolist['enomoto'] = {'var': 'var'}
    mt_host_vars = {}
    mt_pioneer_template_host_vars = {}
    obj = tgtclass(ws_db)
    obj.CreateOperationVariables()
    ret = obj.CreateOperationVariables(in_operation_id, ina_hostinfolist, mt_host_vars, mt_pioneer_template_host_vars)

#def test_func():
#    workspace_id = g.get('WORKSPACE_ID')
#    g.applogger.debug(workspace_id)
#    ws_db = DBConnectWs(workspace_id)  # noqa: F405
#    row = ws_db.table_columns_get("T_ANSC_DEVICE")
#    obj = ttt(ws_db)
#    obj.select()
#    print(len(row[0]))
#    list_a = []
#    list_a = [None] * 10
#    print(list_a)    
#    row = row[0]
#    print(row)    
#    row = dict(row)
#    print(row)   
#    sql = '''
#           SELECT
#                 ROLE_PACKAGE_ID,
#                 ROLE_ID,
#                 INCLUDE_SEQ
#               FROM
#                 {}
#               WHERE
#                 PATTERN_ID  = :PATTERN_ID AND
#                 DISUSE_FLAG = 0
#           '''.format('aaaaa')
#    print(sql)
#    ll = []
#    del ll [:]
#    rows = ws_db.table_select("T_COMN_BOOLEAN_FLAG","WHERE DISUSE_FLAG = :DISUSE_FLAG",["0"])
#    rows = ws_db.sql_execute("SELECT * FROM T_COMN_BOOLEAN_FLAG WHERE FLAG_NAME = %s",["False"])
#    print(rows)
#    for row in rows:
#        ll.append({row['LAST_UPDATE_TIMESTAMP'],row['LAST_UPDATE_TIMESTAMP']})
#    print(ll)
#def dbaccess_listToDict(list_row):
#    pass