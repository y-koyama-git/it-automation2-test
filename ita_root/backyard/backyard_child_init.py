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
# from flask import g
from common_libs.ci.util import app_context_start
from backyard_child_main import backyard_child_main
import sys


def main():
    # コマンドラインから引数を受け取る["自身のファイル名", "organization_id", "workspace_id"]
    args = sys.argv
    # print(args)
    organization_id = args[1]
    workspace_id = args[2]
    app_context_start(backyard_child_main, organization_id, workspace_id)


if __name__ == '__main__':
    main()
