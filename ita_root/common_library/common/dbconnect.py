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

"""
database connection agent module
"""

import pymysql.cursors  # https://pymysql.readthedocs.io/en/latable_name/
import uuid
import datetime


class DBConnectAgent:
    """
    database connection agnet class for mariadb
    """

    _db_con = None  # database connection
    __db = "ita_db"  # prefix of database name
    __is_transaction = False  # state of transaction
    __COLUMN_NAME_TIMESTAMP = 'LAST_UPDATE_TIMESTAMP'

    def __init__(self, workspace_name):
        """
        constructor

        Arguments:
            workspace_name: workspace name
        """
        self.__host = "192.168.141.53"
        self.__db_user = "root"
        self.__db_passwd = "root"

        # decide database name
        self.__workspace_name = workspace_name
        self.__db += "_workspace_{}".format(workspace_name)
        # print(self.__db)

        # connect database
        self.db_connect()

    def __del__(self):
        """
        destructor
        """
        self.db_disconnect()

    def db_connect(self):
        """
        connect database

        Returns:
            is success:(bool) 
        """
        if self._db_con is not None and self._db_con.open is True:
            return True

        try:
            self._db_con = pymysql.connect(
                host=self.__host,
                user=self.__db_user,
                passwd=self.__db_passwd,
                database=self.__db,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.Error as e:
            msg = "Dabase Connect Error db_name={} : {}".format(self.__db, e)
            raise Exception(msg)

        return True

    def db_disconnect(self):
        """
        disconnect database
        """
        if self._db_con is not None and self._db_con.open is True:
            self._db_con.close()

        self._db_con = None
        self.__is_transaction = False

    def db_transaction_start(self):
        """
        begin

        Returns:
            is success:(bool) 
        """
        res = False
        if self._db_con.open is True and self.__is_transaction is False:
            try:
                self._db_con.begin()
                res = True
            except pymysql.Error as e:
                msg = "SQL Error : db_name={}: {}".format(self.__db, e)
                res = False
                raise Exception(msg)

            if res is True:
                self.__is_transaction = True

        return res

    def db_transaction_end(self, flg):
        """
        transaction end

        Arguments:
            flg: True(1):commit, False(0):rollback
        Returns:
            is success:(bool) 
        """
        res = False
        if self._db_con.open is True:
            if flg is True:
                res = self.db_commit()
            else:
                res = self.db_rollback()
        return res

    def db_commit(self):
        """
        commit

        Returns:
            is success:(bool) 
        """
        res = False
        if self._db_con.open is True and self.__is_transaction is True:
            try:
                self._db_con.commit()
                res = True
            except pymysql.Error as e:
                msg = "SQL Error : db_name={}: {}".format(self.__db, e)
                res = False
                raise Exception(msg)

            if res is True:
                self.__is_transaction = False

        return res

    def db_rollback(self):
        """
        rollback

        Returns:
            is success:(bool) 
        """
        res = False
        if self._db_con.open is True and self.__is_transaction is True:
            try:
                self._db_con.rollback()
                res = True
            except pymysql.Error as e:
                msg = "SQL Error : db_name={}: {}".format(self.__db, e)
                res = False
                raise Exception(msg)
            if res is True:
                self.__is_transaction = False
        return res

    def sql_execute(self, sql, bind_value_list=[]):
        """
        execute sql

        Arguments:
            sql: sql statement ex."SELECT * FROM table_name WHERE name = %s and number = %s"
            bind_value_list: value list ex.["hoge taro", 5]
        Returns:
            table data list: list(tuple)
        """
        db_cursor = self._db_con.cursor()

        try:
            db_cursor.execute(sql, tuple(bind_value_list))
        except pymysql.Error as e:
            msg = "SQL Error : db_name={}, sql='{}', bind_value={} : {}".format(self.__db, sql, bind_value_list, e)
            raise Exception(msg)

        data_list = list(db_cursor.fetchall())  # counter plan for 0 data
        db_cursor.close()

        return data_list

    def table_columns_get(self, table_name):
        """
        get table column name list

        Arguments:
            table_name: table name
        Returns:
            tupple(column_name_list, primary_key_name)
                column name list: ex.['id', 'name', 'number']
                primary_key list: ex.['id']
        """
        sql = "SHOW COLUMNS FROM {}".format(table_name)
        data_list = self.sql_execute(sql)

        column_list = []
        primary_key_list = []
        for data in data_list:
            # print(data)
            column_list.append(data['Field'])
            if(data['Key'] == 'PRI'):
                primary_key_list.append(data['Field'])

        return (column_list, primary_key_list)

    def table_select(self, table_name, where_str="", bind_value_list=[]):
        """
        select table

        Arguments:
            table_name: table name
            where_str: sql statement of WHERE sentence ex."WHERE name = %s and number = %s"
            bind_value_list: value list ex.["hoge taro", 5]
        Returns:
            table data list: list(tuple)
        """
        where_str = " {}".format(where_str) if where_str else ""
        sql = "SELECT * FROM {}{}".format(table_name, where_str)
        data_list = self.sql_execute(sql, bind_value_list)

        return data_list

    def table_count(self, table_name, where_str="", bind_value_list=[]):
        """
        select count table

        Arguments:
            table_name: table name
            where_str: sql statement of WHERE sentence ex."WHERE name = %s and number = %s"
            bind_value_list: value list ex.["hoge taro", 5]
        Returns:
            data count: int
        """
        where_str = " {}".format(where_str) if where_str else ""
        sql = "SELECT COUNT(*) FROM {}{}".format(table_name, where_str)
        data_list = self.sql_execute(sql, bind_value_list)

        for data in data_list:
            for res in data.values():
                return res

    def table_insert(self, table_name, data_list, primary_key_name, is_register_history=True):
        """
        insert table

        Arguments:
            data_list: data list for insert ex.[{"name":"なまえ", "number":"3"}]
            primary_key_name: primary key column name
            is_register_history: (bool)is register history table
        Returns:
            table data list: list(tuple)
            or
            update failure: (bool)False
        """
        if isinstance(data_list, dict):
            data_list = [data_list]

        is_last_res = True
        for data in data_list:
            # auto set
            timestamp = str(datetime.datetime.now())
            data[primary_key_name] = str(self.__uuid_create())
            data[self.__COLUMN_NAME_TIMESTAMP] = timestamp

            # make sql statement
            column_list = list(data.keys())
            prepared_list = list(map(lambda a: "%s", column_list))
            value_list = list(data.values())

            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name, ','.join(column_list), ','.join(prepared_list))
            # print(data)
            # print(sql)
            # print(value_list)
            res = self.sql_execute(sql, value_list)
            if res is False:
                is_last_res = False
                break

            if is_register_history is False:
                continue
            # insert history table
            history_table_name = table_name + "_JNL"
            add_data = self.__make_history_table_data("INSERT", timestamp)
            # make history data
            history_data = dict(data, **add_data)

            # make sql statement
            column_list = list(history_data.keys())
            prepared_list = list(map(lambda a: "%s", column_list))
            value_list = list(history_data.values())

            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(history_table_name, ','.join(column_list), ','.join(prepared_list))
            # print(history_data)
            # print(sql)
            # print(value_list)
            res = self.sql_execute(sql, value_list)
            if res is False:
                is_last_res = False
                break

        return data_list if is_last_res is True else is_last_res

    def table_update(self, table_name, data_list, primary_key_name, is_register_history=True):
        """
        update table

        Arguments:
            data_list: data list for update ex.[{primary_key_name:"{uuid}", "name":"なまえ", "number":"3"}]
            primary_key_name: primary key column name
            is_register_history: (bool)is register history table
        Returns:
            table data list: list(tuple)
            or
            update failure: (bool)False
        """
        if isinstance(data_list, dict):
            data_list = [data_list]

        is_last_res = True
        for data in data_list:
            # auto set
            timestamp = str(datetime.datetime.now())
            data[self.__COLUMN_NAME_TIMESTAMP] = timestamp

            # make sql statement
            prepared_list = list(map(lambda k: "`" + k + "`=%s", data.keys()))
            value_list = list(data.values())
            primary_key_value = data[primary_key_name]

            sql = "UPDATE `{}` SET {} WHERE `{}` = '{}'".format(table_name, ','.join(prepared_list), primary_key_name, primary_key_value)
            # print(data)
            # print(sql)
            # print(value_list)
            res = self.sql_execute(sql, value_list)
            if res is False:
                is_last_res = False
                break

            if is_register_history is False:
                continue
            # insert history table
            history_table_name = table_name + "_JNL"
            add_data = self.__make_history_table_data("UPDATE", timestamp)

            # re-get all column data
            data = self.table_select(table_name, "WHERE `{}` = '{}'".format(primary_key_name, primary_key_value))
            if len(data) == 0:
                return False
            data = dict(data[0])
            # make history data
            history_data = dict(data, **add_data)

            # make sql statement
            column_list = list(history_data.keys())
            prepared_list = list(map(lambda a: "%s", column_list))
            value_list = list(history_data.values())

            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(history_table_name, ','.join(column_list), ','.join(prepared_list))
            # print(history_data)
            # print(sql)
            # print(value_list)
            res = self.sql_execute(sql, value_list)
            if res is False:
                is_last_res = False
                break

        return data_list if is_last_res is True else is_last_res

    def table_lock(self, table_name_list=[]):
        """
        lock table of table-list-table

        Arguments:
            table_name_list: table_name list
        Returns:
            is success:(bool) 
        """
        if isinstance(table_name_list, str):
            table_name_list = [table_name_list]

        prepared_list = list(map(lambda t: "%s", table_name_list))

        sql = "SELECT `TABLE_NAME` FROM `T_COMN_RECODE_LOCK_TABLE` WHERE `TABLE_NAME` IN ({}) FOR UPDATE".format(",".join(prepared_list))

        res = self.sql_execute(sql, table_name_list)
        return res

    def __uuid_create(self):
        """
        make uuid of version4
        """
        return uuid.uuid4()

    def __make_history_table_data(self, action_class, timestamp):
        """
        make addtinal data for history JNL table

        Arguments:
            action_class: "INSERT" or "UPDATE"
            timestamp: timestamp
        Returns:
            addtinal data for history JNL table: tupple
        """
        return {
            'JOURNAL_SEQ_NO': str(self.__uuid_create()),
            'JOURNAL_REG_DATETIME': timestamp,
            'JOURNAL_ACTION_CLASS': action_class
        }


if __name__ == '__main__':
    pass

