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
FROM    registry.access.redhat.com/ubi8/ubi-init

RUN dnf install -y \
    openssh-clients \
    python39 \
    python39-devel \
&&  pip3.9 install --upgrade pip setuptools \
&&  pip3.9 install \
    ansible

COPY .ita_root/ita_by_ansible_execute/ita_ansible_agent/config/ansible.cfg /etc/ansible/ansible.cfg

CMD ["ansible-playbook"]
