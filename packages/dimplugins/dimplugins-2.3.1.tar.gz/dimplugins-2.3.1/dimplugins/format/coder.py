# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Base Coder
    ~~~~~~~~~~

    Base58
"""

import base64
import json
from typing import Optional, Any

import base58

from dimp import DataCoder, ObjectCoder, StringCoder


class Base64Coder(DataCoder):

    # Override
    def encode(self, data: bytes) -> str:
        """ BASE-64 Encode """
        return base64.b64encode(data).decode('utf-8')

    # Override
    def decode(self, string: str) -> Optional[bytes]:
        """ BASE-64 Decode """
        return base64.b64decode(string)


class Base58Coder(DataCoder):

    # Override
    def encode(self, data: bytes) -> str:
        """ BASE-58 Encode """
        return base58.b58encode(data).decode('utf-8')

    # Override
    def decode(self, string: str) -> Optional[bytes]:
        """ BASE-58 Decode """
        return base58.b58decode(string)


class HexCoder(DataCoder):

    # Override
    def encode(self, data: bytes) -> str:
        """ HEX Encode """
        # return binascii.b2a_hex(data).decode('utf-8')
        return data.hex()

    # Override
    def decode(self, string: str) -> Optional[bytes]:
        """ HEX Decode """
        # return binascii.a2b_hex(string)
        return bytes.fromhex(string)


class JSONCoder(ObjectCoder):

    # Override
    def encode(self, obj: Any) -> str:
        """ JsON encode """
        return json.dumps(obj)

    # Override
    def decode(self, string: str) -> Optional[Any]:
        """ JsON decode """
        return json.loads(string)


class UTF8Coder(StringCoder):

    # Override
    def encode(self, string: str) -> bytes:
        """ UTF-8 encode """
        return string.encode('utf-8')

    # Override
    def decode(self, data: bytes) -> Optional[str]:
        """ UTF-8 decode """
        return data.decode('utf-8')
