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

from dimp import URI, json_encode
from dimp import DecryptKey
from dimp import Dictionary
from dimp import BaseFileWrapper
from dimp import TransportableData
from dimp import PortableNetworkFile
from dimp import PortableNetworkFileFactory


class BaseNetworkFile(Dictionary, PortableNetworkFile):

    def __init__(self, dictionary: Dict = None,
                 data: Optional[TransportableData] = None, filename: Optional[str] = None,
                 url: Optional[URI] = None, password: Optional[DecryptKey] = None):
        super().__init__(dictionary=dictionary)
        wrapper = BaseFileWrapper(dictionary=self.dictionary)
        if dictionary is None:
            if data is not None:
                wrapper.data = data
            if filename is not None:
                wrapper.filename = filename
            if url is not None:
                wrapper.url = url
            if password is not None:
                wrapper.password = password
        self.__wrapper = wrapper

    #
    #   file data
    #
    @property  # Override
    def data(self) -> Optional[bytes]:
        ted = self.__wrapper.data
        if ted is not None:
            return ted.data

    @data.setter  # Override
    def data(self, content: Optional[bytes]):
        self.__wrapper.set_data(binary=content)

    #
    #   file name
    #
    @property  # Override
    def filename(self) -> Optional[str]:
        return self.__wrapper.filename

    @filename.setter  # Override
    def filename(self, string: Optional[str]):
        self.__wrapper.filename = string

    #
    #   Download URL
    #
    @property  # Override
    def url(self) -> Optional[URI]:
        return self.__wrapper.url

    @url.setter  # Override
    def url(self, string: Optional[URI]):
        self.__wrapper.url = string

    #
    #   decrypt key
    #
    @property  # Override
    def password(self) -> Optional[DecryptKey]:
        return self.__wrapper.password

    @password.setter  # Override
    def password(self, key: Optional[DecryptKey]):
        self.__wrapper.password = key

    #
    #   encoding
    #

    # Override
    def __str__(self) -> str:
        url = self.__get_url()
        if url is not None:
            # only contains 'URL', return the URL string directly
            return url
        else:
            # not a single URL, encode the entire dictionary
            return json_encode(obj=self.dictionary)

    @property  # Override
    def object(self) -> Any:
        url = self.__get_url()
        if url is not None:
            # only contains 'URL', return the URL string directly
            return url
        else:
            # not a single URL, return the entire dictionary
            return self.dictionary

    def __get_url(self) -> Optional[str]:
        url = self.get_str(key='URL', default=None)
        if url is None:
            return None
        elif url.startswith('data:'):
            # 'data:...;...,...'
            return url
        count = len(self.dictionary)
        if count == 1:
            # if only contains 'URL' field, return the URL string directly
            return url
        elif count == 2 and 'filename' in self.dictionary:
            # ignore 'filename' field
            return url
        # not a single URL


class BaseNetworkFileFactory(PortableNetworkFileFactory):

    # Override
    def create_portable_network_file(self, data: Optional[TransportableData], filename: Optional[str],
                                     url: Optional[URI], password: Optional[DecryptKey]) -> PortableNetworkFile:
        return BaseNetworkFile(data=data, filename=filename, url=url, password=password)

    # Override
    def parse_portable_network_file(self, pnf: Dict[str, Any]) -> Optional[PortableNetworkFile]:
        return BaseNetworkFile(pnf)
