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
GitLab connection agnet module for Ansible Automation Controller
"""
from flask import g
import requests  # noqa F401
import os
import json

from common_libs.common.exception import AppException


class GitLabAgent:
    """
    GitLab connection agnet class for Ansible Automation Controller
    """
    __api_base_url = ""
    __token = ""

    def __init__(self):
        """
        constructor
        """
        host = os.environ.get('GITLAB_HOST')
        port = os.environ.get('GITLAB_PORT')
        self.__api_base_url = "http://{}:{}/api/v4".format(host, port)

        organization_id = g.get('ORGANIZATION_ID')
        if not organization_id:
            # organization create controller
            self.__token = os.environ.get('GITLAB_ROOT_TOKEN')
        else:
            # backyard
            self.__token = g.gitlab_connect_info.get('GITLAB_TOKEN')

    def send_api(self, method, resource, data=None, get_params=None, as_row=False):
        """
        request gitlab RESTAPI

        Arguments:
            method: get or post or put or delete
            resource: url resource
            data: request body
            get_params: get query paramater
            as_row: whether return response-object or not
        Returns:
            http response body OR boolean OR response-object
        """
        url = self.__api_base_url + resource
        headers = {
            "PRIVATE-TOKEN": self.__token,
            "Content-Type": "application/json"
        }

        response = eval('requests.{}'.format(method.lower()))(url, headers=headers, params=get_params, data=json.dumps(data))
        if as_row is True:
            return response

        if response.headers.get('Content-Type') == 'application/json':
            if 200 <= response.status_code < 299:
                res = response.json()

                if "error" in res:
                    err_msg = "{}:{} paramas={}, data={} -> {}:{}".format(method, resource, get_params, data, response.status_code, response.text)
                    raise AppException("999-00004", [])
                else:
                    print(res)
                    return res
            else:
                err_msg = "{}:{} paramas={}, data={} -> {}:{}".format(method, resource, get_params, data, response.status_code, response.text)
                raise AppException("999-00004", [err_msg])
        else:
            if 200 <= response.status_code < 299:
                return True
            else:
                err_msg = "{}:{} paramas={}, data={} -> {}:{}".format(method, resource, get_params, data, response.status_code, response.text)
                raise AppException("999-00004", [err_msg])

    def get_user_self(self):
        # https://docs.gitlab.com/ee/api/users.html#for-normal-users-1

        res = self.send_api(method="get", resource="/user")
        return res

    def get_user_by_id(self, user_id):
        # 未使用中
        # https://docs.gitlab.com/ee/api/users.html#single-user

        return self.send_api(method="get", resource="/users/{}".format(user_id))

    def get_user_by_username(self, username=""):
        # https://docs.gitlab.com/ee/api/users.html#list-users
        if not username:
            params = {}
        else:
            params = {
                "username": username
            }

        return self.send_api(method="get", resource="/users", get_params=params)

    def create_user(self, username):
        # https://docs.gitlab.com/ee/api/users.html#user-creation
        payload = {
            "name": username,
            "username": username,
            "email": username + "@example.com",
            "can_create_group": False,
            "admin": False,
            "external": False,  # can_create_project
            "force_random_password": True,
            "projects_limit": 10000,
            "skip_confirmation": True
        }

        res = self.send_api(method="post", resource="/users", data=payload)
        return res

    def delete_user(self, user_id):
        # https://docs.gitlab.com/ee/api/users.html#user-deletion
        payload = {
            "id": user_id,
            'hard_delete': True
        }

        return self.send_api(method="delete", resource="/users/{}".format(user_id), data=payload)

    def create_personal_access_tokens(self, user_id, username):
        # https://docs.gitlab.com/ee/api/users.html#create-a-personal-access-token
        payload = {
            "user_id": user_id,
            "name": username,
            # "expires_at": "YYYY-MM-DD",
            "scopes": ["api"]
        }

        res = self.send_api(method="post", resource="/users/{}/personal_access_tokens".format(user_id), data=payload)
        return res.get('token')

    def get_project_by_user_id(self, user_id):
        # https://docs.gitlab.com/ee/api/projects.html#list-user-projects

        return self.send_api(method="get", resource="/users/{}/projects".format(user_id))

    def create_project(self, project_name, tag_list=[]):
        # https://docs.gitlab.com/ee/api/projects.html#create-project
        payload = {
            "name": project_name,
            # "path": project_path,
            "visibility": "private",
            "emails_disabled": True,
            "initialize_with_readme	": True,  # Allows you to immediately clone this project’s repository. Skip this if you plan to push up an existing repository.  # noqa E501
            "tag_list": tag_list
        }

        return self.send_api(method="post", resource="/projects", data=payload)

    def delete_project(self, project_id):
        # https://docs.gitlab.com/ee/api/projects.html#delete-project

        return self.send_api(method="delete", resource="/projects/{}".format(project_id))
