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


def define_and_execute_menu_create(organization_id, workspace_id, body=None):  # noqa: E501
    """define_and_execute_menu_create

    メニュー定義および作成の実行 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse2009
    """
    if connexion.request.is_json:
        body = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def execute_menu_create(organization_id, workspace_id, body=None):  # noqa: E501
    """execute_menu_create

    メニュー作成実行 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse2009
    """
    if connexion.request.is_json:
        body = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_exist_menu_create_data(organization_id, workspace_id, menu_create_id):  # noqa: E501
    """get_exist_menu_create_data

    メニュー定義・作成(既存)用の情報取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu_create_id: Menu create ID
    :type menu_create_id: str

    :rtype: InlineResponse2009
    """
    return 'do some magic!'


def get_menu_create_data(organization_id, workspace_id):  # noqa: E501
    """get_menu_create_data

    メニュー定義・作成(新規)用の情報取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str

    :rtype: InlineResponse2009
    """
    return 'do some magic!'


def get_pulldown_initial(organization_id, workspace_id, column_name):  # noqa: E501
    """get_pulldown_initial

    「プルダウン選択」項目で選択した対象の「初期値」候補一覧取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param column_name: 「プルダウン選択」項目のカラム名(rest用)
    :type column_name: str

    :rtype: InlineResponse2009
    """
    return 'do some magic!'


def get_reference_item(organization_id, workspace_id, column_name):  # noqa: E501
    """get_reference_item

    「プルダウン選択」項目で選択した対象の「参照項目」候補一覧取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param column_name: 「プルダウン選択」項目のカラム名(rest用)
    :type column_name: str

    :rtype: InlineResponse2009
    """
    return 'do some magic!'
