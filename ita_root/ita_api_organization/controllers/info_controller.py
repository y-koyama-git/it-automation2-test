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

# from swagger_server import util


def get_info(workspace, menu):  # noqa: E501
    """get_info

    メニューの情報を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_info_columun(workspace, menu):  # noqa: E501
    """get_info_columun

    メニューの項目情報を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_info_list(workspace, menu, list_name):  # noqa: E501
    """get_info_list

    項目のプルダウン用のリストを取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str
    :param list_name: REST用項目名
    :type list_name: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_info_menu(workspace, menu):  # noqa: E501
    """get_info_menu

    メニューの基本情報を取得する # noqa: E501

    :param workspace: ワークスペース名
    :type workspace: str
    :param menu: メニュー名
    :type menu: str

    :rtype: List[str]
    """
    return 'do some magic!'
