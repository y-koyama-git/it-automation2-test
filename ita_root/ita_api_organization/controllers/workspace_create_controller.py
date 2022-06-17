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


def workspace_create(workspace_id):  # noqa: E501
    """workspace_create

    ワークスペースを作成する # noqa: E501

    :param workspace_id: ワークスペース名
    :type workspace_id: str

    :rtype: InlineResponse200
    """
    return 'do some magic!'
