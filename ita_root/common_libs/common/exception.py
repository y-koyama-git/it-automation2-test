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
exception module for application
"""
from flask import g


class AppException(Exception):
    """
    exception class for application
    """
    def __init__(self, *args):
        """
        constructor
            make exception-message (result_code, msg)

        Arguments:
            result_code: "500-0001"
            format_strings: list for message args
        Returns:
            
        """
        result_code, format_strings = args

        # get message
        msg = g.appmsg.get_message(result_code, format_strings)
        self.args = result_code, msg

    # def __str__(self):
