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
database connection agent module for workspace-db on mariadb
"""
from .dbconnect_common import DBConnectCommon
from .dbconnect_org import DBConnectOrg
from common_libs.common.exception import AppException


class DBConnectWs(DBConnectCommon):
    """
    database connection agnet class for workspace-db on mariadb
    """

    _workspace_id = ""

    def __init__(self, workspace_id, organization_id=None):
        """
        constructor

        Arguments:
            workspace_id: workspace id
        """
        # decide database name, prefix+workspace_id
        self._workspace_id = workspace_id

        org_db = DBConnectOrg(organization_id)
        self._db = org_db.get_wsdb_name(workspace_id)

        # get db-connect-infomation from organization-db
        connect_info = org_db.get_wsdb_connect_info(self._db)
        if connect_info is False:
            raise AppException("9990001", [self._db])

        self._host = connect_info['DB_HOST']
        self._port = int(connect_info['DB_PORT'])
        self._db_user = connect_info['DB_USER']
        self._db_passwd = connect_info['DB_PASSWORD']

        # connect database
        self.db_connect()

    def __del__(self):
        """
        destructor
        """
        self.db_disconnect()

    def table_insert(self, table_name, data_list, primary_key_name, is_register_history=True):
        return super().table_insert(table_name, data_list, primary_key_name, is_register_history)

    def table_update(self, table_name, data_list, primary_key_name, is_register_history=True):
        return super().table_update(table_name, data_list, primary_key_name, is_register_history)
