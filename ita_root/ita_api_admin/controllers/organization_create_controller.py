#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# import connexion

from common_libs.common import logger
from common_libs.common.dbconnect import *  # noqa: F403
import os


def organization_create(body, organization_id):  # noqa: E501
    """organization_create

    Organizationを作成する # noqa: E501

    :param body:
    :type body: dict | bytes
    :param organization_id: Organization名
    :type organization_id: str

    :rtype: InlineResponse200
    """

    try:
        # register organization-db connect infomation
        common_db = DBConnectCommon()  # noqa: F405
        org_db_name = common_db.get_orgdb_name(organization_id)
        user_name, user_password = common_db.userinfo_generate(org_db_name)

        try:
            data = {
                'DB_HOST': os.environ.get('DB_HOST'),
                'DB_PORT': int(os.environ.get('DB_PORT')),
                'DB_USER': user_name,
                'DB_PASSWORD': user_password,
                'DB_DATADBASE': org_db_name,
                'DB_ROOT_PASSWORD': os.environ.get('DB_ROOT_PASSWORD'),
            }
            common_db.db_transaction_start()
            connect_info = common_db.get_orgdb_connect_info(org_db_name)

            if connect_info is False:
                common_db.table_insert("T_COMN_ORGANIZATION_DB_INFO", data, "PRIMARY_KEY")
            else:
                data["PRIMARY_KEY"] = connect_info["PRIMARY_KEY"]
                common_db.table_update("T_COMN_ORGANIZATION_DB_INFO", data, "PRIMARY_KEY")

            common_db.db_commit()
        except Exception as e:
            common_db.db_rollback()
            raise Exception(e)

        org_root_db = DBConnectOrgRoot(organization_id)  # noqa: F405

        # create workspace-databse
        org_root_db.database_create(org_db_name)
        # create workspace-user and grant user privileges
        org_root_db.user_create(user_name, user_password, org_db_name)
        # print(user_name, user_password)
        org_root_db.db_disconnect()

        # connect organization-db
        org_db = DBConnectOrg(organization_id)  # noqa: F405
        # create table of organization-db
        org_db.sqlfile_execute("sql/organization.sql")

    except Exception as e:
        logger.app.error(e)  # noqa: F405
        return 'error'

    return 'success'
