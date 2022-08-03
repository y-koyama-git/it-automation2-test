from flask import g
import sys
from common_libs.common import *  # noqa: F403
import os
import subprocess
from common_libs.ansible_driver.classes import *
from common_libs.ansible_driver.functions import *


def test_func():
    ary = {}
    organization_id = g.get('ORGANIZATION_ID')
    workspace_id = g.get('WORKSPACE_ID')
    WS_DB = DBConnectWs(workspace_id, organization_id)
    rows = WS_DB.sql_execute("SELECT * FROM T_COMN_MENU",[])
    for row in rows:
        row['MENU_ID']
        ary[row['MENU_ID']] = {}
        ary[row['MENU_ID']] = row
    print(ary['10101']['MENU_NAME_JA'])
    print(ary['10102']['MENU_NAME_JA'])
