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


def get_conductor_class_data(organization_id, workspace_id, conductor_class_id):  # noqa: E501
    """get_conductor_class_data

    ConductorClassの情報取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_class_id: Conductor Class ID
    :type conductor_class_id: str

    :rtype: InlineResponse20011
    """
    return 'do some magic!'


def get_conductor_class_info(organization_id, workspace_id):  # noqa: E501
    """get_conductor_class_info

    ConductorClassの基本情報取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str

    :rtype: InlineResponse20012
    """
    return 'do some magic!'


def get_conductor_info(organization_id, workspace_id, conductor_instance_id):  # noqa: E501
    """get_conductor_info

    Conductorの基本情報取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_instance_id: Conductor Instance ID
    :type conductor_instance_id: str

    :rtype: InlineResponse20012
    """
    return 'do some magic!'


def get_conductor_instance_data(organization_id, workspace_id, conductor_instance_id):  # noqa: E501
    """get_conductor_instance_data

    Conductor作業の情報取得 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_instance_id: Conductor Instance ID
    :type conductor_instance_id: str

    :rtype: InlineResponse20011
    """
    return 'do some magic!'


def patch_conductor_data(organization_id, workspace_id, conductor_class_id, body=None):  # noqa: E501
    """patch_conductor_data

    Conductorの更新 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_class_id: Conductor Class ID
    :type conductor_class_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse20011
    """
    if connexion.request.is_json:
        body = object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def post_conductor_cansel(organization_id, workspace_id, conductor_instance_id):  # noqa: E501
    """post_conductor_cansel

    Conductor作業の予約取り消し # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_instance_id: Conductor Instance ID
    :type conductor_instance_id: str

    :rtype: InlineResponse20011
    """
    return 'do some magic!'


def post_conductor_data(organization_id, workspace_id, body=None):  # noqa: E501
    """post_conductor_data

    Conductorの新規登録 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse20011
    """
    if connexion.request.is_json:
        body = object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def post_conductor_excecute(organization_id, workspace_id, body=None):  # noqa: E501
    """post_conductor_excecute

    Conductor作業実行 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param body: 
    :type body: dict | bytes

    :rtype: InlineResponse20011
    """
    if connexion.request.is_json:
        body = object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def post_conductor_rels_ase(organization_id, workspace_id, conductor_instance_id, node_instance_id):  # noqa: E501
    """post_conductor_rels_ase

    Conductor作業の一時停止解除 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_instance_id: Conductor Instance ID
    :type conductor_instance_id: str
    :param node_instance_id: Node Instance ID
    :type node_instance_id: str

    :rtype: InlineResponse20011
    """
    return 'do some magic!'


def post_conductor_scram(organization_id, workspace_id, conductor_instance_id):  # noqa: E501
    """post_conductor_scram

    Conductor作業の緊急停止 # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param conductor_instance_id: Conductor Instance ID
    :type conductor_instance_id: str

    :rtype: InlineResponse20011
    """
    return 'do some magic!'
