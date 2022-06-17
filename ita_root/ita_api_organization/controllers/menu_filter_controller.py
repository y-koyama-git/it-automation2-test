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


def get_filter(workspace_id, menu):  # noqa: E501
    """get_filter

    レコードを全件取得する # noqa: E501

    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2002
    """
    return 'do some magic!'


def post_filter(body, workspace_id, menu):  # noqa: E501
    """post_filter

    検索条件を指定し、レコードを取得する # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse200
    """
    if connexion.request.is_json:
        body = object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
