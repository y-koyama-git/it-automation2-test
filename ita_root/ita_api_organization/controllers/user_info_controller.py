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

def get_menu_group_panels(organization_id, workspace_id, user_id):  # noqa: E501
    """get_menu_group_panels

    メニューグループの画像を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param user_id: ユーザID
    :type user_id: str

    :rtype: InlineResponse2003
    """
    return 'do some magic!'


def get_user_auth(organization_id, workspace_id, user_id):  # noqa: E501
    """get_user_auth

    ユーザの権限情報を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param user_id: ユーザID
    :type user_id: str

    :rtype: InlineResponse2003
    """
    return 'do some magic!'


def get_user_menus(organization_id, workspace_id, user_id):  # noqa: E501
    """get_user_menus

    ユーザがアクセス可能なメニューグループ・メニューの一覧を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param user_id: ユーザID
    :type user_id: str

    :rtype: InlineResponse2003
    """
    return 'do some magic!'
