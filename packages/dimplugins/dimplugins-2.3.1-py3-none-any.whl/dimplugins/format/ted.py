# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
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

from typing import Dict, Any, Optional

from dimp import Dictionary
from dimp import BaseDataWrapper
from dimp import TransportableData
from dimp import TransportableDataFactory
from dimp import EncodeAlgorithms


class Base64Data(Dictionary, TransportableData):

    def __init__(self, dictionary: Dict = None, data: bytes = None):
        super().__init__(dictionary=dictionary)
        wrapper = BaseDataWrapper(dictionary=self.dictionary)
        if dictionary is None:
            # encode binary data with algorithm
            wrapper.algorithm = EncodeAlgorithms.BASE_64
            wrapper.data = data
        self.__wrapper = wrapper

    @property  # Override
    def algorithm(self) -> Optional[str]:
        """ encode algorithm """
        return self.__wrapper.algorithm

    @property  # Override
    def data(self) -> Optional[bytes]:
        """ binary data """
        return self.__wrapper.data

    #
    #   encoding
    #

    @property  # Override
    def object(self) -> Any:
        return self.__str__()

    # Override
    def __str__(self) -> str:
        # 0. "{BASE64_ENCODE}"
        # 1. "base64,{BASE64_ENCODE}"
        return self.__wrapper.__str__()

    def to_string(self, mime_type: str) -> str:
        # 2. "data:image/png;base64,{BASE64_ENCODE}"
        return self.__wrapper.encode(mime_type=mime_type)


class Base64DataFactory(TransportableDataFactory):

    # Override
    def create_transportable_data(self, data: bytes) -> TransportableData:
        return Base64Data(data=data)

    # Override
    def parse_transportable_data(self, ted: Dict[str, Any]) -> Optional[TransportableData]:
        # TODO: 1. check algorithm
        #       2. check data format
        return Base64Data(dictionary=ted)
