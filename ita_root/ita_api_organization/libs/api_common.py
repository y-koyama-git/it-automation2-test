# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
api common function module
"""
from flask import request, g, session
import os
import traceback

from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.common.exception import AppException
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate


def make_response(data=None, msg="", result_code="000-00000", status_code=200):
    """
    make http response
    
    Argument:
        data: data
        msg: message
        result_code: xxx-xxxxx
        status_code: http status code
    Returns:
        (flask)response
    """
    if result_code == "000-00000" and not msg:
        msg = "SUCCESS"

    res_body = {
        "result": result_code,
        "message": msg
    }
    if not data:
        return res_body, status_code
    
    res_body["data"] = data
    return res_body, status_code


def app_exception_response(name, e):
    '''
    make response when AppException occured
    
    Argument:
        name: location for AppException occured
        e: AppException
    Returns:
        (flask)response
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            args = args[0].args
        elif isinstance(args[0], Exception):
            return exception_response(name, args[0])
        else:
            is_arg = True

    # catch - raise AppException("xxx-xxxxx", log_format, msg_format), and get message
    if len(args) == 3:
        result_code, log_msg_args, api_msg_args = args
    elif len(args) == 2:
        result_code, log_msg_args = args
        api_msg_args = []
    else:
        result_code = args
        api_msg_args = []
        log_msg_args = []

    log_msg = g.appmsg.get_log_message(result_code, log_msg_args)
    api_msg = g.appmsg.get_api_message(result_code, api_msg_args)
    
    # get http status code
    status_code = int(result_code[0:3])
    if 500 <= status_code:
        status_code = 500

    res = make_response(None, api_msg, result_code, status_code)
    g.applogger.error("[api-error] {}".format(log_msg))
    g.applogger.debug("[{}][error] response: {}".format(name, res))
    return res


def exception_response(name, e):
    '''
    make response when Exception occured
    
    Argument:
        name: location for Exception occured
        e: Exception
    Returns:
        (flask)response
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            return app_exception_response(name, args[0])
        elif isinstance(args[0], Exception):
            args = args[0].args
        else:
            is_arg = True

    # catch - other all error
    # exception_block_arr = traceback.format_exc(limit=3).split("Traceback (most recent call last):\n")
    # exception_block = exception_block_arr[1]  # most deep exception called
    # exception_block = re.sub(r'\n\nDuring handling of the above.*?\n\n', '', exception_block)
    # print(exception_block)
    
    # if exception_block[0:7] == '  File ':
    #     # print(exception_block)
    #     trace_block_arr = re.split('  File ', exception_block)
    #     for trace_block in trace_block_arr:
    #         trace_block = re.sub(r'\n\nDuring handling of the above.*?\n\n', '', trace_block)
    #         print(trace_block)
    t = traceback.format_exc()
    print(t)

    res = make_response(None, "SYSTEM ERROR", "999-99999", 500)
    # g.applogger.error("[api-error] {}".format(e))
    g.applogger.debug("[{}][error] response: {}".format(name, res))
    return res


def before_request_handler():
    """
    called before controller is excuted
    """
    try:
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate()

        # request-header check(base)
        user_id = request.headers.get("User-Id")
        roles = request.headers.get("Roles")
        if user_id is None or roles is None:
            raise AppException("400-00001", ["User-Id and Roles"], ["User-Id and Roles"])

        session['USER_ID'] = user_id
        session['ROLES'] = roles

        # set language
        language = request.headers.get("Language")
        if not language:
            language = os.environ.get("DEFAULT_LANGUAGE")
        session['LANGUAGE'] = language

        g.appmsg.set_lang(language)
        g.applogger.debug("LANGUAGE({}) is set".format(language))

        # get organization_id
        organization_id = request.path.split("/")[2]
        session['ORGANIZATION_ID'] = organization_id

        # initialize setting organization-db connect_info and connect check
        common_db = DBConnectCommon()  # noqa: F405
        g.applogger.debug("ITA_DB is connected")

        orgdb_connect_info = common_db.get_orgdb_connect_info(organization_id)
        common_db.db_disconnect()
        if orgdb_connect_info is False:
            raise AppException("999-00001", ["ORGANIZATION_ID=" + organization_id])

        g.db_connect_info = {}
        g.db_connect_info["ORGDB_HOST"] = orgdb_connect_info["DB_HOST"]
        g.db_connect_info["ORGDB_PORT"] = str(orgdb_connect_info["DB_PORT"])
        g.db_connect_info["ORGDB_USER"] = orgdb_connect_info["DB_USER"]
        g.db_connect_info["ORGDB_PASSWORD"] = orgdb_connect_info["DB_PASSWORD"]
        g.db_connect_info["ORGDB_ROOT_PASSWORD"] = orgdb_connect_info["DB_ROOT_PASSWORD"]
        g.db_connect_info["ORGDB_DATADBASE"] = orgdb_connect_info["DB_DATADBASE"]

        # get workspace_id
        workspace_id = request.path.split("/")[4]
        if workspace_id:
            session['WORKSPACE_ID'] = workspace_id

            # initialize setting workspcae-db connect_info and connect check
            org_db = DBConnectOrg()  # noqa: F405
            g.applogger.debug("ORG_DB:{} can be connected".format(organization_id))

            wsdb_connect_info = org_db.get_wsdb_connect_info(workspace_id)
            org_db.db_disconnect()
            if wsdb_connect_info is False:
                raise AppException("999-00001", ["WORKSPACE_ID=" + workspace_id])

            g.db_connect_info["WSDB_HOST"] = wsdb_connect_info["DB_HOST"]
            g.db_connect_info["WSDB_PORT"] = str(wsdb_connect_info["DB_PORT"])
            g.db_connect_info["WSDB_USER"] = wsdb_connect_info["DB_USER"]
            g.db_connect_info["WSDB_PASSWORD"] = wsdb_connect_info["DB_PASSWORD"]
            g.db_connect_info["WSDB_DATADBASE"] = wsdb_connect_info["DB_DATADBASE"]

            ws_db = DBConnectWs(workspace_id)  # noqa: F405
            g.applogger.debug("WS_DB:{} can be connected".format(workspace_id))

            # set log-level for user setting
            g.applogger.set_user_setting(ws_db)
            ws_db.db_disconnect()
    except AppException as e:
        # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
        return app_exception_response("before-request", e)
    except Exception as e:
        # catch - other all error
        return exception_response("before-request", e)


def api_filter(func):
    '''
    wrap api controller
    
    Argument:
        func: controller(def)
    Returns:
        controller wrapper
    '''

    def wrapper(*args, **kwargs):
        '''
        controller wrapper
        
        Argument:
            *args, **kwargs: controller args
        Returns:
            (flask)response
        '''
        try:
            # controller start
            g.applogger.debug("[api-start] {} -> {}, list:{} dict:{}".format(func.__module__, func.__name__, args, kwargs))

            # controller execute and make response
            controller_res = func(*args, **kwargs)
            res = make_response(*controller_res)

            # controller end
            g.applogger.debug("[api-end][success] response: {}".format(res))
            return res
        except AppException as e:
            # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
            return app_exception_response("api-end", e)
        except Exception as e:
            # catch - other all error
            return exception_response("api-end", e)

    return wrapper
