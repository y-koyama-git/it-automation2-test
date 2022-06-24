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

from common_libs.common import *  # noqa: F403
from libs import menu_filter
from flask import jsonify

import sys
sys.path.append('../../')
from common_libs.loadtable.load_table import loadTable


def get_filter(workspace_id, menu):  # noqa: E501
    """get_filter

    レコードを全件取得する # noqa: E501

    :param workspace_id: ワークスペース名
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2002
    """

    """
    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405
        
        # メニューのカラム情報を取得
        objmenu = loadTable(objdbca, menu)
        result_data = objmenu.rest_filter({})

        #### result_code,msg未対応
        result = {
            "result": "result_code", #result_data[0],
            "data": result_data, #result_data[1],
            "message": "msg" #result_data[2]
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
    """

    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405
        
        filter_parameter = {}
        # メニューのカラム情報を取得
        # ####メモ：langは取得方法検討中
        result_data = menu_filter.rest_filter(objdbca, menu, filter_parameter, 'ja')
        #### result_code,msg未対応
        result = {
            "result": "result_code", #result_data[0],
            "data": result_data, #result_data[1],
            "message": "msg" #result_data[2]
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
    """
    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405

        filter_parameter = {}
        if connexion.request.is_json:
            body = dict(connexion.request.get_json())
            filter_parameter = body
                
        # メニューのカラム情報を取得
        objmenu = loadTable(objdbca, menu)
        result_data = objmenu.rest_filter(filter_parameter)

        #### result_code,msg未対応
        result = {
            "result": "result_code", #result_data[0],
            "data": result_data, #result_data[1],
            "message": "msg" #result_data[2]
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
    """

    try:
        # DB接続
        objdbca = DBConnectWs(workspace_id)  # noqa: F405
        
        filter_parameter = {}
        if connexion.request.is_json:
            body = dict(connexion.request.get_json())
            filter_parameter = body
            
        # メニューのカラム情報を取得
        # ####メモ：langは取得方法検討中
        result_data = menu_filter.rest_filter(objdbca, menu, filter_parameter, 'ja')
        #### result_code,msg未対応
        result = {
            "result": "result_code", #result_data[0],
            "data": result_data, #result_data[1],
            "message": "msg" #result_data[2]
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