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

import json
import os
import re
import subprocess

from abc import ABC, abstractclassmethod
from jinja2 import Template, FileSystemLoader, Environment


class AnsibleAgent(ABC):

    def __init__(self, organization_id, workspace_id):
        self._host_storage_path = os.getenv('HOST_STORAGEPATH')
        self._organization_id = organization_id
        self._workspace_id = workspace_id

    @abstractclassmethod
    def container_start_up(self, execution_no, conductor_instance_id, driver_path, conductor_path):
        pass

    @abstractclassmethod
    def is_container_running(self, execution_no):
        pass

    @abstractclassmethod
    def container_kill(self, execution_no):
        pass

    def get_unique_name(self, execution_no):
        return "%s_%s_%s" % (self._organization_id, self._workspace_id, execution_no)

    # 定期巡回して、completeのコンテナを消すやつが必要（dockerもkubernetesも）


class DockerMode(AnsibleAgent):

    def __init__(self, organization_id, workspace_id):
        super().__init__(organization_id, workspace_id)

    def container_start_up(self, execution_no, conductor_instance_id, driver_path, conductor_path):
        '''
        '''
        print("method: container_start_up")

        # create path string
        host_mount_path_driver = os.environ.get('HOST_STORAGEPATH') + driver_path
        container_mount_path_driver = os.environ.get('STORAGEPATH') + driver_path
        host_mount_path_conductor = os.environ.get('HOST_STORAGEPATH') + conductor_path
        container_mount_path_conductor = os.environ.get('STORAGEPATH') + conductor_path
        project_name = self.get_unique_name(execution_no)

        # generate execute manifest
        fileSystemLoader = FileSystemLoader(searchpath="templates")
        env = Environment(loader=fileSystemLoader)
        template = env.get_template('docker-compose.yml')
        exec_manifest = "%s/.tmp/.docker-compose.yml" % (container_mount_path_driver)

        with open(exec_manifest, 'w') as f:
            f.write(template.render(
                organization_id=self._organization_id,
                workspace_id=self._workspace_id,
                execution_no=execution_no,
                HTTP_PROXY=os.getenv('HTTP_PROXY', ""),
                HTTPS_PROXY=os.getenv('HTTPS_PROXY', ""),
                host_mount_path_driver=host_mount_path_driver,
                container_mount_path_driver=container_mount_path_driver,
                host_mount_path_conductor=host_mount_path_conductor,
                container_mount_path_conductor=container_mount_path_conductor
            ))

        # create command string
        docker_compose_command = ["/usr/local/bin/docker-compose", "-f", exec_manifest, "-p", project_name, "up", "-d"]
        command = ["sudo"] + docker_compose_command

        # # docker-compose -f file -p project up
        # complete_process = subprocess.run(command, capture_output=True)

        # # check result
        # print("return_code: %s" % complete_process.returncode)
        # print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        # print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))
        # complete_process.check_returncode()

    def is_container_running(self, execution_no):
        '''
        '''
        print("method: is_container_running")

        # docker-compose -p project ps
        project_name = self.get_unique_name(execution_no)
        docker_compose_command = ["/usr/local/bin/docker-compose", "-p", project_name, "ps", "--format", "json"]
        command = ["sudo"] + docker_compose_command

        complete_process = subprocess.run(command, capture_output=True)

        # check result
        # print("return_code: %s" % complete_process.returncode)
        # print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        # print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))
        complete_process.check_returncode()

        # 戻りをjsonデコードして、runningのものが一つだけ存在しているか確認
        result_obj = json.loads(complete_process.stdout.decode('utf-8'))
        if len(result_obj) > 0 and result_obj[0]['State'] == "running":
            return True

        return False

    def container_kill(self, execution_no):
        '''
        '''
        print("method: container_kill")

        # docker-compose -p project kill
        project_name = self.get_unique_name(execution_no)
        docker_compose_command = ["/usr/local/bin/docker-compose", "-p", project_name, "kill"]
        command = ["sudo"] + docker_compose_command

        complete_process = subprocess.run(command, capture_output=True)

        print("return_code: %s" % complete_process.returncode)
        print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))
        complete_process.check_returncode()

        # docker-compose -p project rm -f
        docker_compose_command = ["/usr/local/bin/docker-compose", "-p", project_name, "rm", "-f"]
        command = ["sudo"] + docker_compose_command

        # complete_process = subprocess.run(command, capture_output=True)

        # print("return_code: %s" % complete_process.returncode)
        # print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        # print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))
        # complete_process.check_returncode()


class KubernetesMode(AnsibleAgent):

    def __init__(self, organization_id, workspace_id):
        super().__init__(organization_id, workspace_id)

    def container_start_up(self, execution_no, conductor_instance_id, driver_path, conductor_path):
        '''
        '''
        print("method: container_start_up")

        # create namespace
        # error(namespace already exists でも処理続行)
        namespace = 'ita-ansible-agent'
        complete_process = subprocess.run(["/usr/local/bin/kubectl", "create", "namespace", namespace], capture_output=True)
        print("return_code: %s" % complete_process.returncode)
        print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))

        # create path string
        host_mount_path_driver = os.environ.get('HOST_STORAGEPATH') + driver_path
        container_mount_path_driver = os.environ.get('STORAGEPATH') + driver_path
        host_mount_path_conductor = os.environ.get('HOST_STORAGEPATH') + conductor_path
        container_mount_path_conductor = os.environ.get('STORAGEPATH') + conductor_path
        unique_name = self.get_unique_name(execution_no)
        unique_name = re.sub(r'_', '-', unique_name).lower()

        # generate execute manifest
        fileSystemLoader = FileSystemLoader(searchpath="./templates")
        env = Environment(loader=fileSystemLoader)
        template = env.get_template('k8s_pod.yml')
        exec_manifest = "%s/.tmp/.k8s_pod.yml" % (container_mount_path_driver)

        with open(exec_manifest, 'w') as f:
            f.write(template.render(
                unique_name=unique_name,
                HTTP_PROXY=os.getenv('HTTP_PROXY', ""),
                HTTPS_PROXY=os.getenv('HTTPS_PROXY', ""),
                host_mount_path_driver=host_mount_path_driver,
                container_mount_path_driver=container_mount_path_driver,
                host_mount_path_conductor=host_mount_path_conductor,
                container_mount_path_conductor=container_mount_path_conductor
            ))

        # create command string
        command = ["/usr/local/bin/kubectl", "apply", "-f", exec_manifest, "-n", namespace]

        # kubectl apply -f file -n ita-ansible-agent
        # complete_process = subprocess.run(' '.join(command), capture_output=True, shell=True)

        # # check result
        # print("return_code: %s" % complete_process.returncode)
        # print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        # print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))
        # complete_process.check_returncode()

    def is_container_running(self, execution_no):
        '''
        '''
        print("method: is_container_running")

        namespace = 'ita-ansible-agent'

        # create command string
        ansible_role_driver_middle_path = "driver/ansible/legacy_role"
        container_mount_path_driver = "/storage/%s/%s/%s/%s" % (self._organization_id, self._workspace_id, ansible_role_driver_middle_path, execution_no)  # noqa E501
        unique_name = self.get_unique_name(execution_no)
        unique_name = re.sub(r'_', '-', unique_name).lower()
        command = ["/usr/local/bin/kubectl", "get", "pod", "-n", namespace, 'it-ansible-agent-' + unique_name, "-o", "json"]

        complete_process = subprocess.run(' '.join(command), capture_output=True, shell=True)

        # check result
        # print("return_code: %s" % complete_process.returncode)
        # print("stdout:\n%s" % complete_process.stdout.decode('utf-8'))
        # print("stderr:\n%s" % complete_process.stderr.decode('utf-8'))
        complete_process.check_returncode()

        # 戻りをjsonデコードして、runningのものが一つだけ存在しているか確認
        result_obj = json.loads(complete_process.stdout.decode('utf-8'))
        if result_obj['status']['phase'] == "running":
            return True

        return False

    def container_kill(self, execution_no):
        '''
        '''

        namespace = 'ita-ansible-agent'

        # create command string
        ansible_role_driver_middle_path = "driver/ansible/legacy_role"
        container_mount_path_driver = "/storage/%s/%s/%s/%s" % (self._organization_id, self._workspace_id, ansible_role_driver_middle_path, execution_no)  # noqa E501
        exec_manifest = "%s/.tmp/.k8s_pod.yml" % (container_mount_path_driver)

        command = ["/usr/local/bin/kubectl", "delete", "-f", exec_manifest, "-n", namespace, "--force=true", "--grace-period=0"]

        # complete_process = subprocess.run(' '.join(command), capture_output=True, shell=True)

        print("method: container_kill")
