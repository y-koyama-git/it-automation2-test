from flask import request, g
import os
import re

from common_libs.common.dbconnect import *  # noqa: F403
# from common_libs.common.exception import AppException
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate


def before_request_handler():
    try:
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate()

        # request-header check(base)
        user_id = request.headers.get("User-Id")
        role_id = request.headers.get("Role-Id")
        language = request.headers.get("Language")
        if user_id is None or role_id is None or language is None:
            raise Exception("request-header paramater(User-Id and Role-Id and Language) is required")

        os.environ['USER_ID'] = user_id
        os.environ['ROLE_ID'] = role_id
        os.environ['LANGUAGE'] = language

        # set language for message class
        g.appmsg.set_lang(language)
        g.applogger.debug("LANGUAGE is set for {}".format(language))

        # request-header check(Organization-Id)
        organization_id = request.headers.get("Organization-Id")
        if organization_id is None:
            raise Exception("request-header paramater(Organization-Id) is required")
        os.environ['ORGANIZATION_ID'] = organization_id

        # initialize setting organization-db connect_info and connect check
        common_db = DBConnectCommon()  # noqa: F405
        g.applogger.debug("ITA_DB is connected")
        org_db_name = common_db.get_orgdb_name(organization_id)
        orgdb_connect_info = common_db.get_orgdb_connect_info(org_db_name)
        if orgdb_connect_info is False:
            raise Exception("ORGANIZATION_ID is invalid")

        os.environ["ORGDB_HOST"] = orgdb_connect_info["DB_HOST"]
        os.environ["ORGDB_PORT"] = str(orgdb_connect_info["DB_PORT"])
        os.environ["ORGDB_USER"] = orgdb_connect_info["DB_USER"]
        os.environ["ORGDB_PASSWORD"] = orgdb_connect_info["DB_PASSWORD"]
        os.environ["ORGDB_ROOT_PASSWORD"] = orgdb_connect_info["DB_ROOT_PASSWORD"]
        os.environ["ORGDB_DATADBASE"] = orgdb_connect_info["DB_DATADBASE"]
        g.applogger.debug("DB:{} connect-info is set".format(org_db_name))

        match = re.match(r'.*\/workspaces\/(.*?)\/', request.path)
        workspace_id = match.group(1) if match is not None else ""

        if workspace_id:
            os.environ['WORKSPACE_ID'] = workspace_id

            # initialize setting workspcae-db connect_info and connect check
            org_db = DBConnectOrg()  # noqa: F405
            g.applogger.debug("DB:{} can be connected".format(org_db_name))
            ws_db_name = org_db.get_wsdb_name(workspace_id)
            wsdb_connect_info = org_db.get_wsdb_connect_info(ws_db_name)
            if wsdb_connect_info is False:
                raise Exception("WORKSPACE_ID is invalid")

            os.environ["WSDB_HOST"] = wsdb_connect_info["DB_HOST"]
            os.environ["WSDB_PORT"] = str(wsdb_connect_info["DB_PORT"])
            os.environ["WSDB_USER"] = wsdb_connect_info["DB_USER"]
            os.environ["WSDB_PASSWORD"] = wsdb_connect_info["DB_PASSWORD"]
            os.environ["WSDB_DATADBASE"] = wsdb_connect_info["DB_DATADBASE"]
            g.applogger.debug("DB:{} connect-info is set".format(ws_db_name))

            ws_db = DBConnectWs(workspace_id)  # noqa: F405
            g.applogger.debug("DB:{} can be connected".format(ws_db_name))

            # set log-level for user setting
            log_level = g.applogger.set_user_setting(ws_db)
            g.applogger.debug("LOG-LEVEL is set for {}".format(log_level))

    except Exception as e:
        g.applogger.error(e)

        return str(e), 400
