from flask import request, g
import os

from common_libs.common.logger import AppLog


def before_request_handler():
    try:
        # create app log instance - ita-api-adminはworkspaceが作られていないので、DBでログレベル設定は行わない
        g.applogger = AppLog()

        user_id = request.headers.get("User-Id")
        role_id = request.headers.get("Role-Id")
        language = request.headers.get("Language")
        if user_id is None or role_id is None or language is None:
            return "request-header paramater(User-Id and Role-Id and Language) is required", 400

        os.environ['USER_ID'] = user_id
        os.environ['ROLE_ID'] = role_id
        os.environ['LANGUAGE'] = language

        # languageを元にメッセージファイルを読み込む

    except Exception as e:
        g.applogger.error(e)
