import sys

from flask import Flask, g
from dotenv import load_dotenv  # python-dotenv

from common_libs.common.dbconnect import *  # noqa: F403
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate
from common_libs.common.exception import AppException
from common_libs.common.util import arrange_stacktrace_format  # noqa: F401
from backyard_test import *  # noqa: F403


def main():
    # load environ variables
    load_dotenv(override=True)

    flask_app = Flask(__name__)

    with flask_app.app_context():
        # コマンドラインから引数を受け取る["backyard_test以下のモジュール名", "関数名", "organization_id"]
        myfile_name, module_name, def_name, organization_id = sys.argv

        print("aaaa")
        # 事前処理
        if before_handler(organization_id) is True:
            try:
                org_db = DBConnectOrg()  # noqa: F405
                g.applogger.debug("ORG_DB:{} can be connected".format(organization_id))
                workspace_datalist = org_db.table_select('T_COMN_WORKSPACE_DB_INFO', 'WHERE `DISUSE_FLAG`=0')

                for workspace_data in workspace_datalist:
                    # initialize setting workspcae-db connect_info and connect check

                    # get workspace_id
                    workspace_id = workspace_data['WORKSPACE_ID']
                    g.WORKSPACE_ID = workspace_id

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
                    ws_db.db_disconnect()

                    # 引数から、モジュールファイルを実行
                    eval('{}.{}'.format(module_name, def_name))()
            except AppException as e:
                # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
                app_exception(e)
            except Exception as e:
                # catch - other all error
                exception(e)


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

    # catch - raise AppException("xxx-xxxxx", log_format, msg_format), and get message
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
    # t = traceback.format_exc(limit=3)
    g.applogger.exception("[error]")
    # g.applogger.error("[error]{}".format(arrange_stacktrace_format(t)))


def before_handler(organization_id):
    """
    called before controller is excuted
    """
    try:
        # create app log instance and message class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate()

        # get organization_id
        g.ORGANIZATION_ID = organization_id

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

        return True
    except AppException as e:
        # catch - raise AppException("xxx-xxxxx", log_format, msg_format)
        app_exception(e)
        return False
    except Exception as e:
        # catch - other all error
        exception(e)
        return False


if __name__ == '__main__':
    main()
