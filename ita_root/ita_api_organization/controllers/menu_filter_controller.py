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
from libs import menu_filter
from flask import jsonify

import sys
sys.path.append('../../')
from common_libs.loadtable.load_table import loadTable
from common_libs.api import api_filter


@api_filter
def get_filter_count(organization_id, workspace_id, menu):  # noqa: E501
    """get_filter_count

    レコード全件の件数を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2004
    """
    return 'do some magic!',


@api_filter
def get_filter(organization_id, workspace_id, menu):  # noqa: E501
    """get_filter

    レコードを全件取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2003
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    filter_parameter = {}
    result_data = menu_filter.rest_filter(objdbca, menu, filter_parameter)
    return result_data,


@api_filter
def get_journal(organization_id, workspace_id, menu, uuid):  # noqa: E501
    """get_journal

    レコードの履歴を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param uuid: UUID
    :type uuid: str

    :rtype: InlineResponse2003
    """

    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405

    result_data = menu_filter.rest_filter_journal(objdbca, menu, uuid)
    return result_data,


@api_filter
def post_filter(organization_id, workspace_id, menu, body=None):  # noqa: E501
    """post_filter

    検索条件を指定し、レコードを取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse2005
    """

    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    filter_parameter = {}
    if connexion.request.is_json:
        body = dict(connexion.request.get_json())
        filter_parameter = body
        
    # メニューのカラム情報を取得
    result_data = menu_filter.rest_filter(objdbca, menu, filter_parameter)
    return result_data,


@api_filter
def post_filter_count(organization_id, workspace_id, menu, body=None):  # noqa: E501
    """post_filter_count

    検索条件を指定し、レコードの件数する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse2005
    """
    if connexion.request.is_json:
        body = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
