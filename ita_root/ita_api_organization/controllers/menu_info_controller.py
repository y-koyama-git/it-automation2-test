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



def get_basic_info(workspace, menu):  # noqa: E501
    """get_basic_info

    メニューの基本情報を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_column_info(workspace, menu):  # noqa: E501
    """get_column_info

    メニューの項目情報を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_info(workspace, menu):  # noqa: E501
    """get_info

    メニューの基本情報および項目情報を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_info_pulldown_list(workspace, menu, restname):  # noqa: E501
    """get_info_pulldown_list

    項目のプルダウン選択用の一覧を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str
    :param restname: REST用項目名
    :type restname: str

    :rtype: List[str]
    """
    return 'do some magic!'
