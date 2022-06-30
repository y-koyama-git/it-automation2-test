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
共通関数 module
"""
import secrets
import string
import base64
import codecs
from pathlib import Path


def ky_encrypt(lcstr):
    """
    Encode a string

    Arguments:
        lcstr: Encoding target value
    Returns:
        Encoded string
    """
    # BASE64でエンコード
    tmp_str = base64.b64encode(lcstr.encode())
    # rot13でエンコード
    return codecs.encode(tmp_str.decode(), "rot_13")


def ky_decrypt(lcstr):
    """
    Decode a string

    Arguments:
        lcstr: Decoding target value
    Returns:
        Decoded string
    """
    # rot13でデコード
    tmp_str = codecs.decode(lcstr, "rot_13")
    # base64でデコード
    return base64.b64decode(tmp_str.encode()).decode()


def ky_file_encrypt(src_file, dest_file):
    """
    Encode a file

    Arguments:
        src_file: Encoding target file
        dest_file: Encoded file
    Returns:
        is success:(bool)
    """
    try:
        # ファイルオープン
        fsrc = open(src_file)
        
        # ファイル読み込み
        lcstr = Path(src_file).read_text(encoding="utf-8")
        
        # エンコード関数呼び出し
        enc_data = ky_encrypt(lcstr)
        
        # ファイル書き込み
        Path(dest_file).write_text(enc_data, encoding="utf-8")
    except Exception:
        return False
    finally:
        # ファイルクローズ
        fsrc.close()
    
    return True


def ky_file_decrypt(src_file, dest_file):
    """
    Decode a file

    Arguments:
        src_file: Decoding target file
        dest_file: Decoded file
    Returns:
        is success:(bool)
    """
    try:
        # ファイルオープン
        fsrc = open(src_file)
        
        # ファイル読み込み
        lcstr = Path(src_file).read_text(encoding="utf-8")
        
        # デコード関数呼び出し
        enc_data = ky_decrypt(lcstr)
        
        # ファイル書き込み
        Path(dest_file).write_text(enc_data, encoding="utf-8")
    except Exception:
        return False
    finally:
        # ファイルクローズ
        fsrc.close()
    
    return True


def generate_secrets(length=16, punctuation=''):
    # string.ascii_letters - alfabet lower and upper
    # string.digits - number
    # string.punctuation - symbol  !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    pass_chars = string.ascii_letters + string.digits + punctuation
    secrets_val = ''.join(secrets.choice(pass_chars) for x in range(length))

    return secrets_val


if __name__ == '__main__':
    # print(generate_secrets())
    pass
