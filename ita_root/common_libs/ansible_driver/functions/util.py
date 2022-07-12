from flask import g
import os
"""
  Ansible共通モジュール
"""


def get_AnsibleDriverTmpPath():
    """
      Ansible用tmpバスを取得する。
      Arguments:
        なし
      Returns:
        Ansible用tmpバス
    """
    return "{}{}/{}/{}".format(os.environ["PYTHONPATH"], g.get('ORGANIZATION_ID'), g.get('WORKSPACE_ID'), "tmp/driver/ansible")
