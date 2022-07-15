from flask import g
import requests  # noqa F401
import os
import json

from common_libs.common.dbconnect import DBConnectCommon
from common_libs.common.exception import AppException


class GitLabAgent:
    """
    GitLab connection agnet class for Ansible Automation Controller
    """
    __api_base_url = ""
    __token = ""

    def __init__(self):
        host = os.environ.get('GITLAB_HOST')
        port = os.environ.get('GITLAB_PORT')
        self.__api_base_url = "http://{}:{}/api/v4/".format(host, port)

        organization_id = g.get('ORGANIZATION_ID')
        if not organization_id:
            # organization create controller
            self.__token = os.environ.get('GITLAB_ROOT_TOKEN')
        else:
            common_db = DBConnectCommon()
            where = "WHERE `ORGANIZATION_ID`=%s and `DISUSE_FLAG`=0 LIMIT 1"
            data_list = common_db.table_select("T_COMN_ORGANIZATION_DB_INFO", where, [organization_id])
            if len(data_list) == 0:
                raise AppException("999-00004", ["ORGANIZATION_ID=" + organization_id])

            self.__token = data_list[0]['GITLAB_TOKEN']

    def send_api(self, method, resource, data=None, get_params=None):
        url = self.__api_base_url + resource
        headers = {
            "PRIVATE-TOKEN": self.__token,
            "Content-Type": "application/json"
        }

        response = eval('requests.{}'.format(method.lower()))(url, headers=headers, params=get_params, data=json.dumps(data))
        if response.headers.get('Content-Type') == 'application/json':
            if 200 <= response.status_code < 299:
                res = response.json()

                if "error" in res:
                    err_msg = "{}:{} paramas={}, data={} -> {}:{}".format(method, resource, get_params, data, response.status_code, response.text)
                    raise AppException("999-00005", [])
                else:
                    print(res)
                    return res
            else:
                err_msg = "{}:{} paramas={}, data={} -> {}:{}".format(method, resource, get_params, data, response.status_code, response.text)
                raise AppException("999-00005", [err_msg])
        else:
            if 200 <= response.status_code < 299:
                return True
            else:
                err_msg = "{}:{} paramas={}, data={} -> {}:{}".format(method, resource, get_params, data, response.status_code, response.text)
                raise AppException("999-00005", [err_msg])

    def get_user(self, username=""):
        if not username:
            params = {}
        else:
            params = {
                "username": username
            }

        return self.send_api(method="get", resource="users", get_params=params)

    def create_user(self, username):
        payload = {
            "name": username,
            "username": username,
            "email": "hogehoge@example.com",
            "can_create_group": False,
            "admin": False,
            "external": False,  # can_create_project
            "force_random_password": True,
            "projects_limit": 1000,
            "skip_confirmation": True
        }

        return self.send_api(method="post", resource="users", data=payload)

    def delete_user(self, user_id):
        payload = {
            "id": user_id,
            'hard_delete': True
        }

        return self.send_api(method="delete", resource="users/{}".format(user_id), data=payload)

    def create_personal_access_tokens(self, user_id, username):
        payload = {
            "user_id": user_id,
            "name": username,
            # "expires_at": "YYYY-MM-DD",
            "scopes": ["api"]
        }

        return self.send_api(method="post", resource="users/{}/personal_access_tokens".format(user_id), data=payload)

    def create_project(self, project_name):
        payload = {
            "name": project_name,
            # "path": project_path,
            "visibility": "private",
            "emails_disabled": True
        }

        return self.send_api(method="post", resource="projects", data=payload)
