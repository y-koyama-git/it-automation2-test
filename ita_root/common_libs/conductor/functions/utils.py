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

import re


def chk_format(c_data={}):
    retBool = False
    retCode = ""
    retMsgList = []

    # check config
    if "config" in c_data:
        del c_data["config"]
    else:
        retMsgList.append("configキーがありません")

    # check conductor
    if "conductor" in c_data:
        del c_data["conductor"]
    else:
        retMsgList.append("conductorキーがありません")

    # check node and edge and extra
    is_exist_node = False
    is_exist_edge = False
    is_exist_extra = False
    for block_1 in c_data:
        if re.fullmatch(r'node-\d{1,}', block_1):
            is_exist_node = True
            continue
        if re.fullmatch(r'line-\d{1,}', block_1):
            is_exist_edge = True
            continue
        is_exist_extra = True

    if is_exist_node is False:
        retMsgList.append("nodeキーがありません")
    if is_exist_edge is False:
        retMsgList.append("edgeキーがありません")
    if is_exist_extra is True:
        retMsgList.append("不要なキーがあります")

    if len(retMsgList) != 0:
        retCode = "xxx-xxxxxx"
    else:
        retBool = True

    return retBool, retCode, retMsgList


def chk_connected_nodes(c_data={}):
    retBool = False
    retCode = ""
    retMsgList = []

    return retBool, retCode, retMsgList


def chk_conductor(_c_data={}):
    retBool = False
    retCode = ""
    retMsgList = []

    c_data = _c_data["conductor"]

    if "id" not in c_data:
        retMsgList.append("idキーがありません")

    if "conductor_name" not in c_data:
        retMsgList.append("conductor_nameキーがありません")

    if "note" not in c_data:
        retMsgList.append("noteキーがありません")

    if "LUT4U" not in c_data:
        retMsgList.append("LUT4Uキーがありません")

    if len(retMsgList) != 0:
        retCode = "xxx-xxxxxx"
    else:
        retBool = True

    return retBool, retCode, retMsgList
