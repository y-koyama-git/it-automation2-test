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

from common_libs.common.exception import AppException
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate
from common_libs.common.util import get_timestamp, arrange_stacktrace_format


def make_response(data=None, msg="", result_code="000-00000", status_code=200, ts=None):
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
        "message": msg,
    }
    res_body["ts"] = ts if ts else str(get_timestamp())
    if data:
        res_body["data"] = data

    log_status = "success" if result_code == "000-00000" else "error"
    g.applogger.info("[api-end][{}]{}".format(log_status, (res_body, status_code)))
    return res_body, status_code


def app_exception_response(e):
    '''
    make response when AppException occured
    
    Argument:
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
            return exception_response(args[0])
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

    timestamp = str(get_timestamp())
    g.applogger.error("[error][ts={}]{}".format(timestamp, log_msg))
    return make_response(None, api_msg, result_code, status_code, timestamp)


def exception_response(e):
    '''
    make response when Exception occured
    
    Argument:
        e: Exception
    Returns:
        (flask)response
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            return app_exception_response(args[0])
        elif isinstance(args[0], Exception):
            args = args[0].args
        else:
            is_arg = True

    # catch - other all error
    timestamp = str(get_timestamp())
    t = traceback.format_exc(limit=3)
    # g.applogger.exception("[error][ts={}]".format(timestamp))
    g.applogger.error("[error][ts={}]{}".format(timestamp, arrange_stacktrace_format(t)))

    return make_response(None, "SYSTEM ERROR", "999-99999", 500, timestamp)


def before_request_handler():
    try:
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate()

        # request-header check
        user_id = request.headers.get("User-Id")
        roles = request.headers.get("Roles")
        if user_id is None or roles is None:
            raise AppException("400-00001", ["User-Id and Roles"], ["User-Id and Roles"])

        session['USER_ID'] = user_id
        session['ROLES'] = roles

        debug_args = [request.method + ":" + request.url]
        g.applogger.info("[api-start] url:{}".format(*debug_args))

        # set language
        language = request.headers.get("Language")
        if not language:
            language = os.environ.get("DEFAULT_LANGUAGE")
        session['LANGUAGE'] = language

        g.appmsg.set_lang(language)
        g.applogger.info("LANGUAGE({}) is set".format(language))
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
            g.applogger.debug("controller start -> {}".format(kwargs))

            # controller execute and make response
            controller_res = func(*args, **kwargs)

            return make_response(*controller_res)
        except AppException as e:
            # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
            return app_exception_response(e)
        except Exception as e:
            # catch - other all error
            return exception_response(e)

    return wrapper
