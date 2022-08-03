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


class ConductorCommonLibs():
    config_data = {}
    conductor_data = {}
    node_datas = {}
    edge_datas = {}

    _node_type_list = ['start', 'end', 'call', 'movement', 'parallel-branch', 'conditional-branch', 'merge', 'pause', 'status-file-branch']

    _terminal_type_list = ['in', 'out']

    _node_connect_point_condition = {
        'start': {
            'in': [],
            'out': ['movement', 'call', 'parallel-branch']
        },
        'end': {
            'in': ['movement', 'call', 'conditional-branch', 'merge', 'pause', 'status-file-branch'],
            'out': []
        },
        'call': {
            'in': ['start', 'movement', 'call', 'parallel-branch', 'conditional-branch', 'merge', 'pause', 'status-file-branch'],
            'out': ['end', 'movement', 'call', 'parallel-branch', 'conditional-branch', 'merge', 'pause', 'status-file-branch']
        },
        'movement': {
            'in': ['start', 'movement', 'call', 'parallel-branch', 'conditional-branch', 'merge', 'pause', 'status-file-branch'],
            'out': ['end', 'movement', 'call', 'parallel-branch', 'conditional-branch', 'merge', 'pause', 'status-file-branch']
        },
        'parallel-branch': {
            'in': ['start', 'movement', 'call', 'conditional-branch', 'merge', 'pause', 'status-file-branch'],
            'out': ['movement', 'call']
        },
        'conditional-branch': {
            'in': ['movement', 'call'],
            'out': ['end', 'movement', 'call', 'parallel-branch', 'pause']
        },
        'merge': {
            'in': ['movement', 'call', 'pause'],
            'out': ['end', 'movement', 'call', 'parallel-branch', 'pause']
        },
        'pause': {
            'in': ['movement', 'call', 'parallel-branch', 'merge', 'status-file-branch'],
            'out': ['end', 'movement', 'call', 'parallel-branch', 'pause']
        },
        'status-file-branch': {
            'in': ['movement', 'call'],
            'out': ['end', 'movement', 'call', 'parallel-branch', 'pause']
        },
    }

    def __init__(self):
        pass

    def chk_format_all(self, c_all_data={}):
        err_code = 'xxx-xxxxxx'

        # check first block
        res_chk_format = self.chk_format(c_all_data)
        if res_chk_format[0] is False:
            return False, err_code, res_chk_format[1]

        # check config block
        res_chk_fonig = self.chk_config(self.config_data)
        if res_chk_fonig[0] is False:
            return False, err_code, res_chk_fonig[1]

        # check conductor block
        res_chk_conductor = self.chk_conductor(self.conductor_data)
        if res_chk_conductor[0] is False:
            return False, err_code, res_chk_conductor[1]

        # check node block
        res_chk_node = self.chk_node(self.node_datas)
        if res_chk_node[0] is False:
            return False, err_code, res_chk_node[1]
        else:
            chk_node_id_list = res_chk_node[1]

        # check node detail
        res_chk_node_detail = self.chk_node_detail(self.node_datas, chk_node_id_list)
        if res_chk_node_detail[0] is False:
            return False, err_code, res_chk_node_detail[1]

        # check edge block
        res_chk_edge = self.chk_edge(self.edge_datas)
        if res_chk_edge[0] is False:
            return False, err_code, res_chk_edge[1]

        return True,

    def chk_format(self, c_data):
        """
        check format

        Arguments:
            c_data: conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        # check config
        if 'config' in c_data:
            if not c_data['config']:
                err_msg_args.append('config')
            self.config_data = c_data['config']
            del c_data['config']
        else:
            err_msg_args.append('config')

        # check conductor
        if 'conductor' in c_data:
            if not c_data['conductor']:
                err_msg_args.append('conductor')
            self.conductor_data = c_data['conductor']
            del c_data['conductor']
        else:
            err_msg_args.append('conductor')

        # check node and edge and extra
        is_exist_node = False
        is_exist_edge = False
        is_exist_extra = False
        for key, value in c_data.items():
            if re.fullmatch(r'node-\d{1,}', key):
                self.node_datas[key] = value
                is_exist_node = True
                continue
            if re.fullmatch(r'line-\d{1,}', key):
                self.edge_datas[key] = value
                is_exist_edge = True
                continue
            is_exist_extra = True

        if is_exist_node is False:
            err_msg_args.append('node')
        if is_exist_edge is False:
            err_msg_args.append('edge')
        if is_exist_extra is True:
            err_msg_args.append('extra block is existed')

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_config(self, c_data):
        """
        check config block

        Arguments:
            c_data: config_data in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        if 'nodeNumber' not in c_data:
            err_msg_args.append('config.nodeNumber')
        else:
            if type(c_data['nodeNumber']) is not int:
                err_msg_args.append('config.nodeNumber')

        if 'terminalNumber' not in c_data:
            err_msg_args.append('config.terminalNumber')
        else:
            if type(c_data['terminalNumber']) is not int:
                err_msg_args.append('config.terminalNumber')

        if 'edgeNumber' not in c_data:
            err_msg_args.append('config.edgeNumber')
        else:
            if type(c_data['edgeNumber']) is not int:
                err_msg_args.append('config.edgeNumber')

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_conductor(self, c_data):
        """
        check conductor block

        Arguments:
            c_data: conductor_data in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        if 'id' not in c_data:
            err_msg_args.append('conductor.id')

        if 'conductor_name' not in c_data:
            err_msg_args.append('conductor.conductor_name')
        else:
            val = c_data['conductor_name']
            if not val:
                err_msg_args.append('conductor.conductor_name')
            # 重複チェックいる？
            # 文字数チェックいる？

        if 'note' not in c_data:
            err_msg_args.append('conductor.note')
        else:
            val = c_data['note']
            # 文字数チェックいる？

        if 'last_update_date_time' not in c_data:
            err_msg_args.append('conductor.last_update_date_time')
        else:
            val = c_data['last_update_date_time']
            # DBの更新時刻と比較？

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_node(self, c_data):
        """
        check node block

        Arguments:
            c_data: node_datas in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        # check node block
        chk_node_id_list = []
        chk_start_node = []
        for key, block_1 in c_data.items():
            block_err_msg_args = []

            if 'id' not in block_1 or not re.fullmatch(r'node-\d{1,}', block_1['id']):
                block_err_msg_args.append('id')

            if 'type' not in block_1 or block_1['type'] not in self._node_type_list:
                block_err_msg_args.append('type')

            if 'terminal' not in block_1 or not block_1['terminal']:
                block_err_msg_args.append('terminal')
            else:
                terminal_blcok = block_1['terminal']
                for terminalname, terminalinfo in terminal_blcok.items():
                    block2_err_msg_args = []

                    if 'id' not in terminalinfo or not re.fullmatch(r'terminal-\d{1,}', terminalinfo['id']):
                        block2_err_msg_args.append('id')

                    if 'type' not in terminalinfo or terminalinfo['type'] not in self._terminal_type_list:
                        block2_err_msg_args.append('type')

                    if 'targetNode' not in terminalinfo or not terminalinfo['targetNode']:
                        block2_err_msg_args.append('targetNode}')

                    if 'edge' not in terminalinfo or not terminalinfo['edge']:
                        block2_err_msg_args.append('edge')

                    # if 'x' not in terminalinfo or type(terminalinfo['x']) is not int:
                    #     block2_err_msg_args.append('x')

                    # if 'y' not in terminalinfo or type(terminalinfo['y']) is not int:
                    #     block2_err_msg_args.append('y')

                    if len(block2_err_msg_args) != 0:
                        block_err_msg_args.append(','.join(block2_err_msg_args) + ' in terminal.{}'.format(terminalname))

            if 'x' not in block_1 or type(block_1['x']) is not int:
                block_err_msg_args.append('x')

            if 'y' not in block_1 or type(block_1['y']) is not int:
                block_err_msg_args.append('y')

            if 'w' not in block_1 or type(block_1['w']) is not int:
                block_err_msg_args.append('w')

            if 'h' not in block_1 or type(block_1['h']) is not int:
                block_err_msg_args.append('h')

            if 'note' in block_1:
                # noteの文字数チェック
                pass

            if len(block_err_msg_args) != 0:
                err_msg_args.append('{}({})'.format(key, ','.join(block_err_msg_args)))
            else:
                # make chk_node_id_list
                chk_node_id_list.append(block_1['id'])
                if block_1['type'] == 'start':
                    chk_start_node.append(block_1['id'])

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            if len(chk_start_node) != 1:
                return False, ['node[type=start] is duplicate']

            return True, chk_node_id_list

    def chk_node_detail(self, c_data, chk_node_id_list):
        """
        check node detail

        Arguments:
            c_data: node_datas in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []
        for key, block_1 in c_data.items():
            node_type = block_1['type']

            if node_type == 'end':
                if 'end_type' not in block_1 or int(block_1['end_type']) not in [5, 7, 11]:
                    err_msg_args.append('{}.end_type'.format(key))
                    continue

            if node_type == 'movement':
                block_err_msg_args = []

                if 'movement_id' not in block_1 or not block_1['movement_id']:
                    block_err_msg_args.append('movement_id')
                    # db チェック

                if 'movement_name' not in block_1 or not block_1['movement_name']:
                    block_err_msg_args.append('movement_name')
                    # db チェック

                if 'skip_flg' not in block_1:
                    block_err_msg_args.append('skip_flg')

                if 'operation_id' not in block_1:
                    block_err_msg_args.append('operation_id')
                    # db チェック

                if 'operation_name' not in block_1:
                    block_err_msg_args.append('operation_name')
                    # db チェック

                if 'orchestra_id' not in block_1 or not block_1['orchestra_id']:
                    block_err_msg_args.append('orchestra_id')
                    # 設定値 チェック？？

                if len(block_err_msg_args) != 0:
                    err_msg_args.append('{}({})'.format(key, ','.join(block_err_msg_args)))
                    continue

            if node_type == 'call':
                block_err_msg_args = []

                if 'call_conductor_id' not in block_1 or not block_1['call_conductor_id']:
                    block_err_msg_args.append('movement_id')
                    # db チェック

                if 'call_conductor_name' not in block_1 or not block_1['call_conductor_name']:
                    block_err_msg_args.append('movement_name')
                    # db チェック

                if 'skip_flg' not in block_1:
                    block_err_msg_args.append('skip_flg')

                if 'operation_id' not in block_1:
                    block_err_msg_args.append('operation_id')
                    # db チェック

                if 'operation_name' not in block_1:
                    block_err_msg_args.append('operation_name')
                    # db チェック

                if len(block_err_msg_args) != 0:
                    err_msg_args.append('{}({})'.format(key, ','.join(block_err_msg_args)))
                    continue

            # check node terminal
            res_chk_node_terminal = self.chk_node_terminal(node_type, block_1['terminal'], chk_node_id_list)
            if res_chk_node_terminal[0] is False:
                err_msg_args.append('{}({})'.format(key, res_chk_node_terminal[1]))
                continue

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_node_terminal(self, node_type, terminal_blcok, chk_node_id_list):
        """
        check node terminal conditions

        Arguments:
            node_type: node type
            terminal_blcok: terminal dict in node
            chk_node_id_list: node id list
        Returns:
            (tuple)
            - retBool (bool)
            - err msg (str)
        """
        err_msg_args = []

        if node_type in self._node_connect_point_condition:
            connect_point_condition = self._node_connect_point_condition[node_type]
        else:
            connect_point_condition = []

        for terminalname, terminalinfo in terminal_blcok.items():
            # check whether node is connected
            if terminalinfo['targetNode'] not in chk_node_id_list:
                err_msg_args.append('targetNode not connected in terminal.{}'.format(terminalname))
                continue

            # check node connect point
            terminal_type = terminalinfo['type']
            target_node = terminalinfo['targetNode']
            target_node_type = self.node_datas[target_node]['type']
            if target_node_type not in connect_point_condition[terminal_type]:
                err_msg_args.append('target_node-connect-point is invalid in terminal.{}'.format(terminalname))
                continue

        if len(err_msg_args) != 0:
            return False, ','.join(err_msg_args)

        # check 'conditional-branch' status id
        if node_type == 'conditional-branch':
            err_msg_args = []
            for terminalname, terminalinfo in terminal_blcok.items():
                if terminalinfo['type'] == 'out':
                    if 'condition' not in terminalinfo or not terminalinfo['condition']:
                        err_msg_args.append('condition is empty in terminal.{}'.format(terminalname))
                        continue

            if len(err_msg_args) != 0:
                return False, ','.join(err_msg_args)

        # check 'status-file-branch' condition
        if node_type == 'status-file-branch':
            err_msg_args = []
            condition_val_list = []
            condition_caseno_list = []
            for terminalname, terminalinfo in terminal_blcok.items():
                if terminalinfo['type'] == 'out':
                    if 'case' not in terminalinfo or not terminalinfo['case']:
                        err_msg_args.append('case is empty in terminal.{}'.format(terminalname))
                        continue
                    else:
                        if terminalinfo['case'] == 'else':
                            continue

                    if 'condition' not in terminalinfo or not terminalinfo['condition'] or not terminalinfo['condition'][0]:
                        err_msg_args.append('condition is empty in terminal.{}'.format(terminalname))
                        continue

                    condtion_caseno = terminalinfo['case']
                    condition_val = terminalinfo['condition'][0]

                    if condtion_caseno not in condition_caseno_list:
                        condition_caseno_list.append(condtion_caseno)
                    else:
                        err_msg_args.append('case is invalid in terminal.{}'.format(terminalname))
                        continue

                    if condition_val not in condition_val_list:
                        condition_val_list.append(condition_val)
                    else:
                        err_msg_args.append('condition is duplicate in terminal.{}'.format(terminalname))
                        continue

            if len(err_msg_args) != 0:
                return False, ','.join(err_msg_args)

        return True,

    def chk_edge(self, c_data):
        """
        check edge block

        Arguments:
            c_data: edge_datas in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        for key, block_1 in c_data.items():
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
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_call_loop(self, c_data):
        retCode = 'xxx-xxxxx'
        retMsgList = []

        return False, retCode, retMsgList

    def chk_node_idlink(self, c_data):
        retCode = 'xxx-xxxxx'
        retMsgList = []

        return False, retCode, retMsgList
