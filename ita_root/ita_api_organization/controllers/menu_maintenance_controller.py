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

import connexion
import six

from common_libs.common import *  # noqa: F403
from libs import menu_maintenance
from flask import jsonify

import sys
sys.path.append('../../')
from common_libs.loadtable.load_table import loadTable
from libs import api_common


@api_common.api_filter
def maintenance_register(body, organization_id, workspace_id, menu):  # noqa: E501
    """maintenance_register

    レコードを登録する # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2004
    """

    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    cmd_type = 'Register'
    target_uuid = ''
    parameter = {}
    if connexion.request.is_json:
        body = dict(connexion.request.get_json())
        parameter = body
        parameter.setdefault('maintenance_type', cmd_type)

    result_data = menu_maintenance.rest_maintenance(objdbca, menu, parameter, target_uuid)
    return result_data,


@api_common.api_filter
def maintenance_update(body, organization_id, workspace_id, menu, uuid):  # noqa: E501
    """maintenance_update

    レコードを更新/廃止/復活する # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param uuid: 対象のUUID
    :type uuid: str

    :rtype: InlineResponse2004
    """

    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    target_uuid = uuid
    parameter = {}
    if connexion.request.is_json:
        body = dict(connexion.request.get_json())
        parameter = body

    result_data = menu_maintenance.rest_maintenance(objdbca, menu, parameter, target_uuid)
    return result_data,
