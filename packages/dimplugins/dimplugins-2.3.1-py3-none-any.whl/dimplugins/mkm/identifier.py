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

from typing import Optional

from dimp import ID, IDFactory, Identifier
from dimp import Address
from dimp import Meta


class GeneralIdentifierFactory(IDFactory):
    """ General ID Factory """

    def __init__(self):
        super().__init__()
        self._identifiers = {}  # str -> ID

    # Override
    def generate_identifier(self, meta: Meta, network: int, terminal: Optional[str]) -> ID:
        address = Address.generate(meta=meta, network=network)
        assert address is not None, 'failed to generate ID with meta: %s' % meta
        return ID.create(address=address, name=meta.seed, terminal=terminal)

    # Override
    def create_identifier(self, name: Optional[str], address: Address, terminal: Optional[str]) -> ID:
        identifier = Identifier.concat(address=address, name=name, terminal=terminal)
        cid = self._identifiers.get(identifier)
        if cid is None:
            cid = self._new_id(identifier=identifier, name=name, address=address, terminal=terminal)
            self._identifiers[identifier] = cid
        return cid

    # Override
    def parse_identifier(self, identifier: str) -> Optional[ID]:
        cid = self._identifiers.get(identifier)
        if cid is None:
            cid = self._parse(identifier=identifier)
            if cid is not None:
                self._identifiers[identifier] = cid
        return cid

    # noinspection PyMethodMayBeStatic
    def _new_id(self, identifier: str, name: Optional[str], address: Address, terminal: Optional[str]) -> ID:
        """ override for customized ID """
        return Identifier(identifier=identifier, name=name, address=address, terminal=terminal)

    def _parse(self, identifier: str) -> Optional[ID]:
        # split ID string
        pair = identifier.split('/')
        # assert len(pair[0]) > 0, 'ID error: %s' % identifier
        # terminal
        if len(pair) == 1:
            # no terminal
            terminal = None
        else:
            # got terminal
            terminal = pair[1]
            # assert len(terminal) > 0, 'ID.terminal error: %s' % identifier
        # name @ address
        pair = pair[0].split('@')
        # assert len(pair[0]) > 0, 'ID error: %s' % identifier
        if len(pair) == 1:
            # got address without name
            name = None
            address = Address.parse(address=pair[0])
        elif len(pair) == 2:
            # got name & address
            name = pair[0]
            address = Address.parse(address=pair[1])
        else:
            # assert False, 'ID error: %s' % identifier
            return None
        if address is not None:
            return self._new_id(identifier=identifier, name=name, address=address, terminal=terminal)
        else:
            assert False, 'ID error: %s' % identifier
