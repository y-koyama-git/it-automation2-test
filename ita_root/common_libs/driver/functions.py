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
from common_libs.common.util import get_timestamp
import os


def operation_LAST_EXECUTE_TIMESTAMP_update(wsDb, operation_id):
    # 最終実施日を設定する
    data = {
        "OPERATION_ID": operation_id,
        "LAST_EXECUTE_TIMESTAMP": get_timestamp(),
        "LAST_UPDATE_USER": os.environ.get("LAST_UPDATE_USER_ID")
    }
    wsDb.table_update('T_COMN_OPERATION', [data], 'OPERATION_ID')
