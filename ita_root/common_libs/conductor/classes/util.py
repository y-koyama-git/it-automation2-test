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

    _node_type_list = ['start', 'end', 'movement', 'call', 'parallel-branch', 'conditional-branch', 'merge', 'pause', 'status-file-branch']

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

        # check node block and whether node is conneted
        res_chk_node = self.chk_node(self.node_datas)
        if res_chk_node[0] is False:
            return False, err_code, res_chk_node[1]

        # check edge block
        res_chk_edge = self.chk_edge(self.edge_datas)
        if res_chk_edge[0] is False:
            return False, err_code, res_chk_edge[1]

        # check node terminal
        res_chk_node = self.chk_node_terminal(self.node_datas)
        if res_chk_node[0] is False:
            return False, err_code, res_chk_node[1]

        return True,

    def chk_format(self, c_data={}):
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

    def chk_config(self, c_data={}):
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

    def chk_conductor(self, c_data={}):
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

    def chk_node(self, c_data={}):
        """
        check node block and whether node is conneted

        Arguments:
            c_data: node_datas in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        # check node block and make chk_node_id_list
        chk_node_id_list = []
        for key, block_1 in dict(c_data).items():
            block_err_msg_args = []

            if 'id' not in block_1:
                block_err_msg_args.append('id')
            else:
                val = block_1['id']
                if not re.fullmatch(r'node-\d{1,}', val):
                    block_err_msg_args.append('id')

            if 'type' not in block_1:
                block_err_msg_args.append('type')
            else:
                val = block_1['type']
                if val not in self._node_type_list:
                    block_err_msg_args.append('type')

            if 'terminal' not in block_1:
                block_err_msg_args.append('terminal')
            else:
                val = block_1['terminal']
                if not val:
                    block_err_msg_args.append('terminal')

            if 'x' not in block_1:
                block_err_msg_args.append('x')
            else:
                val = block_1['x']
                if type(val) is not int:
                    block_err_msg_args.append('x')

            if 'y' not in block_1:
                block_err_msg_args.append('y')
            else:
                val = block_1['y']
                if type(val) is not int:
                    block_err_msg_args.append('y')

            if 'w' not in block_1:
                block_err_msg_args.append('w')
            else:
                val = block_1['w']
                if type(val) is not int:
                    block_err_msg_args.append('w')

            if 'h' not in block_1:
                block_err_msg_args.append('h')
            else:
                val = block_1['h']
                if type(val) is not int:
                    block_err_msg_args.append('h')

            if len(block_err_msg_args) != 0:
                err_msg_args.append(key + '(' + ','.join(block_err_msg_args) + ')')
            else:
                chk_node_id_list.append(block_1['id'])

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]

        # check whether node is conneted
        for key, value in c_data.items():
            block_err_msg_args = []

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

            if len(block_err_msg_args) != 0:
                err_msg_args.append(key + '(' + ','.join(block_err_msg_args) + ')')

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_edge(self, c_data={}):
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

    def chk_node_terminal(self, c_data={}):
        """
        check node terminal

        Arguments:
            c_data: node_datas in conductor infomation(dict)
        Returns:
            (tuple)
            - retBool (bool)
            - err msg args (list)
        """
        err_msg_args = []

        if len(err_msg_args) != 0:
            return False, [','.join(err_msg_args)]
        else:
            return True,

    def chk_call_loop(self, c_data={}):
        retCode = 'xxx-xxxxx'
        retMsgList = []

        return False, retCode, retMsgList

    def chk_node_idlink(self, c_data={}):
        retCode = 'xxx-xxxxx'
        retMsgList = []

        return False, retCode, retMsgList
