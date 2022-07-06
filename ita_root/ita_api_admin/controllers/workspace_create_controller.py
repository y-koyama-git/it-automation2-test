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
controller
workspace_create
"""
# import connexion
from flask import g

from common_libs.api import api_filter
from common_libs.common.exception import AppException
from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.common.util import ky_encrypt
import re


@api_filter
def workspace_create(organization_id, workspace_id, body=None):  # noqa: E501
    """workspace_create

    Workspaceを作成する # noqa: E501

    :param organization_id: organizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse200
    """
    msg = ""

    org_db = DBConnectOrg(organization_id)  # noqa: F405
    connect_info = org_db.get_wsdb_connect_info(workspace_id)
    if connect_info:
        try:
            # try to connect workspace-db
            ws_db = DBConnectWs(workspace_id, organization_id)  # noqa: F405

            # workspace-db already exists
            g.applogger.debug("WS_DB:{} can be connected".format(workspace_id))
            return '', "ALREADY EXISTS"
        except AppException:
            # workspace-db connect info is imperfect, so remake
            org_root_db = DBConnectOrgRoot(organization_id)  # noqa: F405
            org_root_db.database_drop(connect_info['DB_DATADBASE'])
            org_root_db.user_drop(connect_info['DB_USER'])
            org_root_db.db_disconnect()
            data = {
                'PRIMARY_KEY': connect_info['PRIMARY_KEY'],
                'DISUSE_FLAG': 1
            }
            try:
                org_db.db_transaction_start()
                org_db.table_update("T_COMN_WORKSPACE_DB_INFO", data, "PRIMARY_KEY")
                org_db.db_commit()
            except AppException:
                org_db.db_rollback()
            msg = "REBUILD"

    # register workspace-db connect infomation
    user_name, user_password = org_db.userinfo_generate("WS")
    ws_db_name = user_name
    connect_info = org_db.get_connect_info()
    try:
        data = {
            'WORKSPACE_ID': workspace_id,
            'DB_HOST': connect_info['DB_HOST'],
            'DB_PORT': int(connect_info['DB_PORT']),
            'DB_USER': user_name,
            'DB_PASSWORD': ky_encrypt(user_password),
            'DB_DATADBASE': ws_db_name,
            'DISUSE_FLAG': 0,
            'LAST_UPDATE_USER': g.get('USER_ID')
        }
        org_db.db_transaction_start()
        org_db.table_insert("T_COMN_WORKSPACE_DB_INFO", data, "PRIMARY_KEY")

        org_db.db_commit()
    except Exception as e:
        org_db.db_rollback()
        raise Exception(e)

    org_root_db = DBConnectOrgRoot(organization_id)  # noqa: F405
    # create workspace-databse
    org_root_db.database_create(ws_db_name)
    # create workspace-user and grant user privileges
    org_root_db.user_create(user_name, user_password, ws_db_name)
    # print(user_name, user_password)
    org_root_db.db_disconnect()

    # connect workspace-db
    ws_db = DBConnectWs(workspace_id, organization_id)  # noqa: F405
    # create table of workspace-db
    ws_db.sqlfile_execute("sql/workspace.sql")
    # insert initial data of workspace-db
    role_id = str(body['role_id'])
    if role_id == "":
        raise Exception("role_id is not found in request body")

    with open("sql/workspace_master.sql", "r") as f:
        sql_list = f.read().split(";\n")
        for sql in sql_list:
            sql = sql.replace('__ROLE_ID__', role_id)
            if re.fullmatch(r'[\s\n\r]*', sql) is None:
                ws_db.sql_execute(sql)

    return '', msg


@api_filter
def workspace_delete(organization_id, workspace_id):  # noqa: E501
    """workspace_delete

    Workspaceを削除する # noqa: E501

    :param organization_id: organizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str

    :rtype: InlineResponse200
    """
    return 'do some magic!'
