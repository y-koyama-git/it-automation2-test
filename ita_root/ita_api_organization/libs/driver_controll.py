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


from flask import g  # noqa: F401

from common_libs.common import *  # noqa: F403
from common_libs.loadtable import *  # noqa: F403

def insert_execution_list(objdbca, menu, parameter, type):
    """
        作業実行を登録
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            menu:メニュー名 string
            parameter: bodyの中身
            type: 'execute' or 'dry_run' or 'check_parameter' 
        RETRUN:
            data
    """

    return {"execution_no": "aaaaaaaaaaaaaaaaaaaaa"}
