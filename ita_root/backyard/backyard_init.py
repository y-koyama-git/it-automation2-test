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
from flask import Flask, g
from dotenv import load_dotenv  # python-dotenv
import traceback

from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate
from common_libs.common.exception import AppException
from common_libs.common.util import arrange_stacktrace_format  # noqa: F401
from backyard_main import backyard_main


def main():
    # load environ variables
    load_dotenv(override=True)

    flask_app = Flask(__name__)

    with flask_app.app_context():
        try:
            wrapper_job()
        except AppException as e:
            # catch - raise AppException("xxx-xxxxx", log_format)
            app_exception(e)
        except Exception as e:
            # catch - other all error
            exception(e)


def wrapper_job():
    '''
    backyard job wrapper
    '''
    # create app log instance and message class instance
    g.applogger = AppLog()
    g.appmsg = MessageTemplate()

    common_db = DBConnectCommon()  # noqa: F405
    g.applogger.debug("ITA_DB is connected")

    # get organization_info_list
    organization_info_list = common_db.table_select("T_COMN_ORGANIZATION_DB_INFO", "WHERE `DISUSE_FLAG`=0 ORDER BY `LAST_UPDATE_TIMESTAMP`")

    for organization_info in organization_info_list:
        g.applogger.set_level("DEBUG")

        organization_id = organization_info['ORGANIZATION_ID']

        g.ORGANIZATION_ID = organization_id
        # database connect info
        g.db_connect_info = {}
        g.db_connect_info["ORGDB_HOST"] = organization_info["DB_HOST"]
        g.db_connect_info["ORGDB_PORT"] = str(organization_info["DB_PORT"])
        g.db_connect_info["ORGDB_USER"] = organization_info["DB_USER"]
        g.db_connect_info["ORGDB_PASSWORD"] = organization_info["DB_PASSWORD"]
        g.db_connect_info["ORGDB_ROOT_PASSWORD"] = organization_info["DB_ROOT_PASSWORD"]
        g.db_connect_info["ORGDB_DATADBASE"] = organization_info["DB_DATADBASE"]
        # gitlab connect info
        g.gitlab_connect_info = {}
        g.gitlab_connect_info["GITLAB_USER"] = organization_info["GITLAB_USER"]
        g.gitlab_connect_info["GITLAB_TOKEN"] = organization_info["GITLAB_TOKEN"]

        # job for organization
        try:
            organization_job(organization_id)
        except AppException as e:
            # catch - raise AppException("xxx-xxxxx", log_format)
            app_exception(e)
        except Exception as e:
            # catch - other all error
            exception(e)


def organization_job(organization_id):
    '''
    job for organization unit
    
    Argument:
        organization_id
    '''
    org_db = DBConnectOrg(organization_id)  # noqa: F405
    g.applogger.debug("ORG_DB:{} can be connected".format(organization_id))

    # get workspace_info_list
    workspace_info_list = org_db.table_select('T_COMN_WORKSPACE_DB_INFO', 'WHERE `DISUSE_FLAG`=0 ORDER BY `LAST_UPDATE_TIMESTAMP`')

    for workspace_info in workspace_info_list:
        g.applogger.set_level("DEBUG")

        workspace_id = workspace_info['WORKSPACE_ID']

        g.WORKSPACE_ID = workspace_id
        g.db_connect_info["WSDB_HOST"] = workspace_info["DB_HOST"]
        g.db_connect_info["WSDB_PORT"] = str(workspace_info["DB_PORT"])
        g.db_connect_info["WSDB_USER"] = workspace_info["DB_USER"]
        g.db_connect_info["WSDB_PASSWORD"] = workspace_info["DB_PASSWORD"]
        g.db_connect_info["WSDB_DATADBASE"] = workspace_info["DB_DATADBASE"]

        ws_db = DBConnectWs(workspace_id)  # noqa: F405
        g.applogger.debug("WS_DB:{} can be connected".format(workspace_id))

        # set log-level for user setting
        # g.applogger.set_user_setting(ws_db)
        ws_db.db_disconnect()

        # job for workspace
        try:
            backyard_main(organization_id, workspace_id)
        except AppException as e:
            # catch - raise AppException("xxx-xxxxx", log_format)
            app_exception(e)
        except Exception as e:
            # catch - other all error
            exception(e)

        g.pop('WORKSPACE_ID')
        g.db_connect_info.pop("WSDB_HOST")
        g.db_connect_info.pop("WSDB_PORT")
        g.db_connect_info.pop("WSDB_USER")
        g.db_connect_info.pop("WSDB_PASSWORD")
        g.db_connect_info.pop("WSDB_DATADBASE")


def app_exception(e):
    '''
    called when AppException occured
    
    Argument:
        e: AppException
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            args = args[0].args
        elif isinstance(args[0], Exception):
            return exception(args[0])
        else:
            is_arg = True

    # catch - raise AppException("xxx-xxxxx", log_format), and get message
    result_code, log_msg_args, api_msg_args = args
    log_msg = g.appmsg.get_log_message(result_code, log_msg_args)
    g.applogger.error("[error]{}".format(log_msg))


def exception(e):
    '''
    called when Exception occured
    
    Argument:
        e: Exception
    '''
    args = e.args
    is_arg = False
    while is_arg is False:
        if isinstance(args[0], AppException):
            return app_exception(args[0])
        elif isinstance(args[0], Exception):
            args = args[0].args
        else:
            is_arg = True

    # catch - other all error
    t = traceback.format_exc()
    # g.applogger.exception("[error]")
    g.applogger.error("[error] {}".format(arrange_stacktrace_format(t)))


if __name__ == '__main__':
    main()
