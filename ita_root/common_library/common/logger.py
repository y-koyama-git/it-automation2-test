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
application logging module
"""

import logging
import logging.config
import yaml
import os

app = None


class AppLog:
    """
    application logging class
    """

    # logging namespace ex."sassAppLogger" or "myAppLogger"
    __name__ = "sassAppLogger"

    # Instance of logging-Library（get from logging.getLogger）
    __logger_obj = None

    # logging dict-config
    _config = {}

    def __init__(self):
        """
        constructor
        """
        # is no-container-app or not(bool)
        isMyapp = True if os.getenv('IS_MYAPP') == "1" else False

        # read config.yml
        with open('logging.yml', 'r') as yml:
            dictConfig = yaml.safe_load(yml)

        self.__create_instance(isMyapp, dictConfig)

    def __create_instance(self, isMyapp, dictConfig={}):
        """
        create Instance of logging-Library and save it

        Arguments:
            isMyapp: (bool) True : no-container-app, False : container-app(Saas)
            dictConfig: (dict) logging dict-config
        Returns:
            
        """
        self.__name__ = "myAppLogger" if isMyapp is True else "sassAppLogger"

        if isMyapp is False:  # container-app(Saas)
            del dictConfig['loggers']["myAppLogger"]
            if "myfile" not in list(dictConfig['loggers']["sassAppLogger"]["handlers"]):
                del dictConfig['handlers']["myfile"]
        else:  # no-container-app
            del dictConfig['loggers']["sassAppLogger"]
            if "myfile" not in list(dictConfig['loggers']["myAppLogger"]["handlers"]):
                del dictConfig['handlers']["myfile"]
            # merge user settings
            dictConfig = self.__user_setting(dictConfig)

        # set config
        self._config = dictConfig
        logging.config.dictConfig(self._config)
        # set instance
        self.__logger_obj = logging.getLogger(self.__name__)
        self.__logger_obj.debug("create AppLog instance [{}]".format(self.__name__))

    def __user_setting(self, dictConfig={}):
        """
        merge user-settings to logging dict-config

        Arguments:
            dictConfig: (dict) logging dict-config
        Returns:
            dictConfig: (dict) logging dict-config
        """
        dictConfig['loggers'][self.__name__]['level'] = "INFO"
        return dictConfig

    def critical(self, message):
        """
        output critical log

        Arguments:
            message: message for output
        """
        self.__logger_obj.critical(message)

    def error(self, message):
        """
        output error log

        Arguments:
            message: message for output
        """
        self.__logger_obj.error(message)

    def warning(self, message):
        """
        output warning log

        Arguments:
            message: message for output
        """
        self.__logger_obj.warning(message)

    def info(self, message):
        """
        output info log

        Arguments:
            message: message for output
        """
        self.__logger_obj.info(message)

    def debug(self, message):
        """
        output debug log

        Arguments:
            message: message for output
        """
        self.__logger_obj.debug(message)


def app_log_init():
    """
    make logger instance
    """
    global app

    app = AppLog()
