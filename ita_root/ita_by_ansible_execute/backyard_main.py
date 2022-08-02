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
from flask import g
from common_libs.common.exception import AppException
from common_libs.ansible_driver.classes.gitlab import GitLabAgent
import os


def backyard_main(organization_id, workspace_id):
    print("backyard_main ita_by_ansible_execute called")

    gitlab = GitLabAgent()

    # # 確認用
    # if organization_id == 'company_A' and workspace_id == 'prj_A':
    #     pass
    # else:
    #     return

    # 作業実行単位のループ
    for job_no in range(21):
        job_name = "job20220727-" + str(job_no)

        try:
            # make project
            # プロジェクト名 = リポジトリ、ユニークの必要あり
            project_name = job_name
            # raise AppException('999-99999')  # 確認用
            gitlab.create_project(project_name)
            g.applogger.info("gitlab project({}) is made".format(project_name))

            # clone
            repositories_base_path = os.environ.get("STORAGEPATH") + "{}/{}/driver/ansible/git_repositories/".format(organization_id, workspace_id)
            os.chdir(repositories_base_path)
            http_repo_url = gitlab.get_http_repo_url(project_name)
            os.system('git clone {}'.format(http_repo_url))

            repositories_path = repositories_base_path + project_name
            os.chdir(repositories_path)

            # commit
            print('commit')
            os.system('touch a.txt')
            os.system('git add a.txt')
            os.system('git commit -m "First commit"')
            
            # push
            print('push')
            os.system('git push origin main')

            # pull
            print('pull')
            os.system('git pull origin main')
        except Exception as e:
            # delete project
            trg_project = gitlab.get_project_by_name(project_name)
            if trg_project:
                gitlab.delete_project(trg_project['id'])

            # 作業実行単位のエラーでループを止めない場合はraiseしない
            raise Exception(e)
