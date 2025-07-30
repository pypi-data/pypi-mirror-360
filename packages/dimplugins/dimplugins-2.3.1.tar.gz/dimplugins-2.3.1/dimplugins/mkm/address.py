# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
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

from abc import ABC
from typing import Optional, Dict

from dimp import Address, AddressFactory
from dimp import ANYWHERE, EVERYWHERE
from dimp import Meta

from .btc import BTCAddress
from .eth import ETHAddress


class BaseAddressFactory(AddressFactory, ABC):
    """
        Base Address Factory
        ~~~~~~~~~~~~~~~~~~~~
    """

    def __init__(self):
        super().__init__()
        self._addresses: Dict[str, Address] = {}

    # Override
    def generate_address(self, meta: Meta, network: int = None) -> Optional[Address]:
        address = meta.generate_address(network=network)
        if address is None:
            assert False, 'failed to generate address with meta: %s' % meta
        self._addresses[str(address)] = address
        return address

    # Override
    def parse_address(self, address: str) -> Optional[Address]:
        add = self._addresses.get(address)
        if add is None:
            add = self._parse(address=address)
            if add is not None:
                self._addresses[address] = add
        return add

    # noinspection PyMethodMayBeStatic
    def _parse(self, address: str) -> Optional[Address]:
        size = len(address)
        if size == 0:
            assert False, 'address should not be empty'
        elif size == 8:
            # "anywhere"
            if address.lower() == 'anywhere':
                return ANYWHERE
        elif size == 10:
            # "everywhere"
            if address.lower() == 'everywhere':
                return EVERYWHERE
        #
        #  checking normal address
        #
        if 26 <= size <= 35:
            res = BTCAddress.from_str(address=address)
        elif size == 42:
            res = ETHAddress.from_str(address=address)
        else:
            assert False, 'invalid address: %s' % address
        # TODO: other types of address
        assert res is not None, 'invalid address: %s' % address
        return res
