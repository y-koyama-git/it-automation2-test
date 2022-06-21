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
from flask import jsonify


def get_column_list(workspace_id, menu):  # noqa: E501
    """get_column_list

    メニューの項目一覧(REST用項目名)を取得する # noqa: E501

    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse200
    """
    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405
        
        # メニューのカラム情報を取得
        # ####メモ：langは取得方法検討中
        result_data = menu_info.collect_menu_column_info(objdbca, menu, 'ja')
        result = {
            "result": result_data[0],
            "data": result_data[1],
            "message": result_data[2]
        }
        
        return jsonify(result), 200
    
    except Exception as result:
        # ####メモ：Exceptionクラス作成後、resultをそのままreturnしたい。
        print(result)
        result_dummy = {
            "result": "StatusCode",
            "message": "aaa bbb ccc"
        }, 500
        return result_dummy


def get_menu_info(workspace_id, menu):  # noqa: E501
    """get_menu_info

    メニューの基本情報および項目情報を取得する # noqa: E501

    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2001
    """
    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405
        
        # メニューの基本情報および項目情報の取得
        # ####メモ：langは取得方法検討中
        result_data = menu_info.collect_menu_info(objdbca, menu, 'ja')
        result = {
            "result": result_data[0],
            "data": result_data[1],
            "message": result_data[2]
        }
        
        return jsonify(result), 200

    except Exception as result:
        # ####メモ：Exceptionクラス作成後、resultをそのままreturnしたい。
        print(result)
        result_dummy = {
            "result": "StatusCode",
            "message": "aaa bbb ccc"
        }, 500
        return result_dummy


def get_pulldown_list(workspace_id, menu, restname):  # noqa: E501
    """get_pulldown_list

    項目のプルダウン選択用の一覧を取得する # noqa: E501

    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param restname: REST用項目名
    :type restname: str

    :rtype: InlineResponse200
    """
    return 'do some magic!'
