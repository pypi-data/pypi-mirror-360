# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
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

from typing import Optional, Dict

from dimp import SymmetricAlgorithms
from dimp import SymmetricKey, SymmetricKeyFactory
from dimp import BaseSymmetricKey


class PlainKey(BaseSymmetricKey):
    """
        Symmetric key for broadcast message,
        which will do nothing when en/decoding message data
    """

    def __init__(self):
        key = {'algorithm': SymmetricAlgorithms.PLAIN}
        super().__init__(key)

    @property
    def size(self) -> int:
        return 0

    @property  # Override
    def data(self) -> bytes:
        return b''

    # Override
    def encrypt(self, data: bytes, extra: Optional[Dict]) -> bytes:
        return data

    # Override
    def decrypt(self, data: bytes, params: Optional[Dict]) -> Optional[bytes]:
        return data


"""
    Key Factory
    ~~~~~~~~~~~
"""


class PlainKeyFactory(SymmetricKeyFactory):

    def __init__(self):
        super().__init__()
        self.__plain_key = PlainKey()

    # Override
    def generate_symmetric_key(self) -> Optional[SymmetricKey]:
        return self.__plain_key

    # Override
    def parse_symmetric_key(self, key: dict) -> Optional[SymmetricKey]:
        return self.__plain_key
