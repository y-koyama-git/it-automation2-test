from flask import request, g
import os

from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate


def before_request_handler():
    try:
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appMsg = MessageTemplate()

        # request-header check(base)
        user_id = request.headers.get("User-Id")
        role_id = request.headers.get("Role-Id")
        language = request.headers.get("Language")
        if user_id is None or role_id is None or language is None:
            return "request-header paramater(User-Id and Role-Id and Language) is required", 400

        os.environ['USER_ID'] = user_id
        os.environ['ROLE_ID'] = role_id
        os.environ['LANGUAGE'] = language

        # set language for message class
        g.appMsg.set_lang(language)

    except Exception as e:
        g.applogger.error(e)
