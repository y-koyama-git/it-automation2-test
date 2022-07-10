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
admin common function module
"""
from flask import request, g
import os
import ast

from common_libs.common.exception import AppException
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate
from common_libs.api import set_api_timestamp, get_api_timestamp, app_exception_response, exception_response, check_request_body


def before_request_handler():
    try:
        set_api_timestamp()
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate()

        check_request_body()

        # request-header check
        user_id = request.headers.get("User-Id")
        roles = ast.literal_eval(request.headers.get("Roles"))
        if user_id is None or roles is None or type(roles) is not list:
            raise AppException("400-00001", ["User-Id and Roles"], ["User-Id and Roles"])

        g.USER_ID = user_id
        g.ROLES = roles

        debug_args = [request.method + ":" + request.url]
        g.applogger.info("[ts={}][api-start]url: {}".format(get_api_timestamp(), *debug_args))

        # set language
        language = request.headers.get("Language")
        if language:
            g.appmsg.set_lang(language)
            g.applogger.info("LANGUAGE({}) is set".format(language))
        else:
            language = os.environ.get("DEFAULT_LANGUAGE")
        g.LANGUAGE = language
    except AppException as e:
        # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
        return app_exception_response(e)
    except Exception as e:
        # catch - other all error
        return exception_response(e)
