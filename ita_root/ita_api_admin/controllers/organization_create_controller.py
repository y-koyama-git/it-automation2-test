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
"""
controller
organization_create
"""
# import connexion
from flask import g

from libs import api_common
from common_libs.common.exception import AppException
from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.common.util import ky_encrypt
import os


@api_common.api_filter
def organization_create(body, organization_id):  # noqa: E501
    """organization_create

    Organizationを作成する # noqa: E501

    :param body:
    :type body: dict | bytes
    :param organization_id: OrganizationID
    :type organization_id: str

    :rtype: InlineResponse200
    """
    msg = ""

    common_db = DBConnectCommon()  # noqa: F405
    connect_info = common_db.get_orgdb_connect_info(organization_id)
    if connect_info:
        try:
            # try to connect organization-db
            org_db = DBConnectOrg(organization_id)  # noqa: F405

            # organization-db already exists
            g.applogger.debug("ORG_DB:{} can be connected".format(organization_id))
            return '', "ALREADY EXISTS"
        except AppException:
            # organization-db connect info is imperfect, so remake
            org_root_db = DBConnectOrgRoot(organization_id)  # noqa: F405
            org_root_db.database_drop(connect_info['DB_DATADBASE'])
            org_root_db.user_drop(connect_info['DB_USER'])
            org_root_db.db_disconnect()
            data = {
                'PRIMARY_KEY': connect_info['PRIMARY_KEY'],
                'DISUSE_FLAG': 1
            }
            try:
                common_db.db_transaction_start()
                common_db.table_update("T_COMN_ORGANIZATION_DB_INFO", data, "PRIMARY_KEY")
                common_db.db_commit()
            except AppException:
                common_db.db_rollback()
            msg = "REBUILD"

    # register organization-db connect infomation
    user_name, user_password = common_db.userinfo_generate("ORG")
    org_db_name = user_name
    try:
        data = {
            'ORGANIZATION_ID': organization_id,
            'DB_HOST': os.environ.get('DB_HOST'),
            'DB_PORT': int(os.environ.get('DB_PORT')),
            'DB_USER': user_name,
            'DB_PASSWORD': ky_encrypt(user_password),
            'DB_DATADBASE': org_db_name,
            'DB_ROOT_PASSWORD': ky_encrypt(os.environ.get('DB_ROOT_PASSWORD')),
            'DISUSE_FLAG': 0
        }
        common_db.db_transaction_start()
        common_db.table_insert("T_COMN_ORGANIZATION_DB_INFO", data, "PRIMARY_KEY")
        common_db.db_commit()

    # except AppException as e:
    #     common_db.db_rollback()
    #     # raise AppException(*e.args)
    #     raise AppException(e)
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

    return '', msg
