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

from common_libs.common import *  # noqa: F403
from libs import menu_info
from common_libs.api import api_filter


@api_filter
def get_column_list(organization_id, workspace_id, menu):  # noqa: E501
    """get_column_list

    メニューの項目一覧(REST用項目名)を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2001
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    # メニューのカラム情報を取得
    data = menu_info.collect_menu_column_list(objdbca, menu)
    
    return data,


@api_filter
def get_menu_info(organization_id, workspace_id, menu):  # noqa: E501
    """get_menu_info

    メニューの基本情報および項目情報を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse200
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    # # メニューの基本情報および項目情報の取得
    data = menu_info.collect_menu_info(objdbca, menu)
    
    return data,


@api_filter
def get_pulldown_list(organization_id, workspace_id, menu):  # noqa: E501
    """get_pulldown_list

    IDColumn項目のプルダウン選択用の一覧を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2002
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405
    
    # 項目のプルダウン一覧の取得
    # data = menu_info.collect_pulldown_list(objdbca, menu, column)
    data = "改装中"
    
    return data,


def get_search_candidates(organization_id, workspace_id, menu, column):  # noqa: E501
    """get_search_candidates

    表示フィルタで利用するプルダウン検索の候補一覧を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param column: REST用項目名
    :type column: str

    :rtype: InlineResponse2003
    """
    return 'do some magic!'
