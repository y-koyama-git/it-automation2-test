#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the 'License');
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an 'AS IS' BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re


def chk_format(c_data={}):
    """
    check format

    Arguments:
        c_data: conductor infomation(dict)
    Returns:
        (tuple)
        - retBool (bool)
        - err msg code ("xxx-xxxxxx")
        - err msg args (list)
    """
    err_msg_args = []

    # check config
    if 'config' in c_data:
        del c_data['config']
    else:
        err_msg_args.append('config')

    # check conductor
    if 'conductor' in c_data:
        del c_data['conductor']
    else:
        err_msg_args.append('conductor')

    # check node and edge and extra
    is_exist_node = False
    is_exist_edge = False
    is_exist_extra = False
    for key in c_data:
        if re.fullmatch(r'node-\d{1,}', key):
            is_exist_node = True
            continue
        if re.fullmatch(r'line-\d{1,}', key):
            is_exist_edge = True
            continue
        is_exist_extra = True

    if is_exist_node is False:
        err_msg_args.append('node')
    if is_exist_edge is False:
        err_msg_args.append('edge')
    if is_exist_extra is True:
        err_msg_args.append('extra')

    if len(err_msg_args) != 0:
        return False, 'xxx-xxxxxx', [','.join(err_msg_args)]
    else:
        return True,


def chk_connected_nodes(c_data={}):
    """
    check is node is conneted

    Arguments:
        c_data: conductor infomation(dict)
    Returns:
        (tuple)
        - retBool (bool)
        - err msg code ("xxx-xxxxxx")
        - err msg args (list)
    """
    del c_data['config']
    del c_data['conductor']

    err_msg_args = []

    # make c_data only node-data and make check-node-id-list
    chk_node_id_list = []
    for key, block_1 in dict(c_data).items():
        if not re.fullmatch(r'node-\d{1,}', key):
            del c_data[key]
            continue

        chk_node_id_list.append(block_1['id'])
    print(chk_node_id_list)

    # check
    for key, value in c_data.items():
        block_err_msg_args = []

        if 'terminal' in value:
            for terminalname, terminalnameinfo in value['terminal'].items():
                if 'targetNode' in terminalnameinfo:
                    if not terminalnameinfo['targetNode']:
                        block_err_msg_args.append('targetNode in terminal.{} is empty'.format(terminalname))
                    else:
                        if terminalnameinfo['targetNode'] not in chk_node_id_list:
                            block_err_msg_args.append('targetNode in terminal.{} is invalid'.format(terminalname))
                else:
                    block_err_msg_args.append('targetNode in terminal.{} not found'.format(terminalname))

                if 'edge' in terminalnameinfo:
                    if not terminalnameinfo['edge']:
                        block_err_msg_args.append('edge in terminal.{} is empty'.format(terminalname))
                else:
                    block_err_msg_args.append('edge in terminal.{} not found'.format(terminalname))
        else:
            block_err_msg_args.append('terminal not found')

        if len(block_err_msg_args) != 0:
            err_msg_args.append(key + '(' + ','.join(block_err_msg_args) + ')')

    if len(err_msg_args) != 0:
        return False, 'xxx-xxxxxx', [','.join(err_msg_args)]
    else:
        return True,


def chk_conductor(_c_data={}):
    """
    check conductor block

    Arguments:
        c_data: conductor infomation(dict)
    Returns:
        (tuple)
        - retBool (bool)
        - err msg code ("xxx-xxxxxx")
        - err msg args (list)
    """
    err_msg_args = []

    c_data = _c_data['conductor']

    if 'id' not in c_data:
        err_msg_args.append('id')

    if 'conductor_name' not in c_data:
        err_msg_args.append('conductor_name')
    else:
        val = c_data['conductor_name']
        if val:
            err_msg_args.append('conductor_name')
        # 重複チェックいる？

    if 'note' not in c_data:
        err_msg_args.append('note')
        # 文字数チェックいる？

    if 'last_update_date_time' not in c_data:
        err_msg_args.append('last_update_date_time')

    if len(err_msg_args) != 0:
        return False, 'xxx-xxxxxx', [','.join(err_msg_args)]
    else:
        return True,


def chk_node(c_data={}):
    """
    check node block

    Arguments:
        c_data: conductor infomation(dict)
    Returns:
        (tuple)
        - retBool (bool)
        - err msg code ("xxx-xxxxxx")
        - err msg args (list)
    """
    retCode = ''
    retMsgList = ['node']

    return False, retCode, retMsgList


def chk_edge(c_data={}):
    """
    check edge block

    Arguments:
        c_data: conductor infomation(dict)
    Returns:
        (tuple)
        - retBool (bool)
        - err msg code ("xxx-xxxxxx")
        - err msg args (list)
    """
    err_msg_args = []

    for key, block_1 in c_data.items():
        if not re.fullmatch(r'line-\d{1,}', key):
            continue

        block_err_msg_args = []

        if 'id' not in block_1:
            block_err_msg_args.append('id')
        else:
            val = block_1['id']
            if not re.fullmatch(r'line-\d{1,}', val):
                block_err_msg_args.append('id')

        if 'type' not in block_1:
            block_err_msg_args.append('type')
        else:
            val = block_1['type']
            if val not in ['edge']:
                block_err_msg_args.append('type')

        if 'inNode' not in block_1:
            block_err_msg_args.append('inNode')
        else:
            val = block_1['inNode']
            if not re.fullmatch(r'node-\d{1,}', val):
                block_err_msg_args.append('inNode')

        if 'inTerminal' not in block_1:
            block_err_msg_args.append('inTerminal')
        else:
            val = block_1['inTerminal']
            if not re.fullmatch(r'terminal-\d{1,}', val):
                block_err_msg_args.append('inTerminal')

        if 'outNode' not in block_1:
            block_err_msg_args.append('outNode')
        else:
            val = block_1['outNode']
            if not re.fullmatch(r'node-\d{1,}', val):
                block_err_msg_args.append('outNode')

        if 'outTerminal' not in block_1:
            block_err_msg_args.append('outTerminal')
        else:
            val = block_1['outTerminal']
            if not re.fullmatch(r'terminal-\d{1,}', val):
                block_err_msg_args.append('outTerminal')

        if len(block_err_msg_args) != 0:
            err_msg_args.append(key + '(' + ','.join(block_err_msg_args) + ')')

    if len(err_msg_args) != 0:
        return False, 'xxx-xxxxxx', [','.join(err_msg_args)]
    else:
        return True,


def chk_node_terminal(c_data={}):
    retCode = ''
    retMsgList = []

    return False, retCode, retMsgList


def chk_call_loop(c_data={}):
    retCode = ''
    retMsgList = []

    return False, retCode, retMsgList


def chk_node_idlink(c_data={}):
    retCode = ''
    retMsgList = []

    return False, retCode, retMsgList
