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

# from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
# from swagger_server import util


def maintenance_all(body, workspace, menu):  # noqa: E501
    """maintenance_all

    レコードを一括で登録/更新/廃止/復活する # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2001
    """
    if connexion.request.is_json:
        body = object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
