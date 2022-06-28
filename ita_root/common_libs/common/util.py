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

import base64
import codecs
from pathlib import Path


class UtilClass:
    """

    共通関数 class
    """

    def ky_encrypt(lcStr):
        """
        Encode a string

        Arguments:
            lcStr: Encoding target value
        Returns:
            Encoded string
        """
        
        return codecs.encode(base64.b64encode(lcStr.encode()), "rot_13")

    def ky_decrypt(lcStr):
        """
        Decode a string

        Arguments:
            lcStr: Decoding target value
        Returns:
            Decoded string
        """
        tmp_lcstr = base64.b64decode(codecs.decode(lcStr, "rot_13").encode())

        # String型に変換してreturn
        return tmp_lcstr.decode()
    
    def ky_file_encrypt(self, src_file, dest_file):
        """
        Encode a file

        Arguments:
            src_file: Encoding target file
            dest_file: Encoded file
        Returns:
            is success:(bool)
        """
        try:
            fsrc = open(src_file)
            text = Path(src_file).read_text(encoding="utf-8")
            
            # エンコード関数呼び出し
            enc_data = self.ky_encrypt(self, text)
            Path(src_file).write_text(enc_data, encoding="utf-8")
        except Exception:
            return False
        finally:
            fsrc.close()
        
        return True

    def ky_file_decrypt(self, src_file, dest_file):
        """
        Decode a file

        Arguments:
            src_file: Decoding target file
            dest_file: Decoded file
        Returns:
            is success:(bool)
        """
        try:
            fsrc = open(src_file)
            text = Path(src_file).read_text(encoding="utf-8")
            
            # デコード関数呼び出し
            enc_data = self.ky_decrypt(self, text)
            Path(src_file).write_text(enc_data, encoding="utf-8")
        except Exception:
            return False
        finally:
            fsrc.close()
        
        return True

        if __name__ == "__main__":
            self.ky_encrypt("aaa")
