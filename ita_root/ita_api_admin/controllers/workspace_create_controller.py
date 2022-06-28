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
from flask import request, g

from common_libs.common.dbconnect import *  # noqa: F403

import os
import re


def workspace_create(body, organization_id, workspace_id):  # noqa: E501
    """workspace_create

    Workspaceを作成する # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param organization_id: organizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str

    :rtype: InlineResponse200
    """

    try:
        organization_id = request.headers.get('Organization-Id')
        if organization_id is None:
            raise Exception("Organization-Id is not found in request header")

        org_root_db = DBConnectOrgRoot(organization_id)  # noqa: F405
        ws_db_name = org_root_db.get_wsdb_name(workspace_id)
        # print(db_name)

        # create workspace-databse
        org_root_db.database_create(ws_db_name)
        # create workspace-user and grant user privileges
        user_name, user_password = org_root_db.userinfo_generate(ws_db_name)
        org_root_db.user_create(user_name, user_password, ws_db_name)
        # print(user_name, user_password)
        org_root_db.db_disconnect()

        # register workspace-db connect infomation
        org_db = DBConnectOrg(organization_id)  # noqa: F405

        try:
            data = {
                'DB_HOST': os.environ.get('DB_HOST'),
                'DB_PORT': int(os.environ.get('DB_PORT')),
                'DB_USER': user_name,
                'DB_PASSWORD': user_password,
                'DB_DATADBASE': ws_db_name,
            }

            org_db.db_transaction_start()
            connect_info = org_db.get_wsdb_connect_info(ws_db_name)

            if connect_info is False:
                org_db.table_insert("T_COMN_WORKSPACE_DB_INFO", data, "PRIMARY_KEY")
            else:
                data["PRIMARY_KEY"] = connect_info["PRIMARY_KEY"]
                org_db.table_update("T_COMN_WORKSPACE_DB_INFO", data, "PRIMARY_KEY")

            org_db.db_commit()
        except Exception as e:
            org_db.db_rollback()
            raise Exception(e)

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
                sql.replace('__ROLE_ID__', role_id)
                if re.fullmatch(r'[\s\n\r]*', sql) is None:
                    ws_db.sql_execute(sql)

    except Exception as e:
        g.applogger.error(e)
        return 'error'

    return 'success'
