# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
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

from typing import Optional, Any, Dict

from dimp import utf8_encode
from dimp import TransportableData
from dimp import VerifyKey, SignKey, PrivateKey
from dimp import EntityType, Address
from dimp import MetaType
from dimp import Meta, MetaFactory
from dimp import BaseMeta
from dimp.plugins import SharedAccountExtensions

from .btc import BTCAddress
from .eth import ETHAddress


"""
    Default Meta to build ID with 'name@address'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    version:
        0x01 - MKM

    algorithm:
        CT      = fingerprint = sKey.sign(seed);
        hash    = ripemd160(sha256(CT));
        code    = sha256(sha256(network + hash)).prefix(4);
        address = base58_encode(network + hash + code);
"""


class DefaultMeta(BaseMeta):

    def __init__(self, meta: Dict[str, Any] = None,
                 version: str = None, public_key: VerifyKey = None,
                 seed: Optional[str] = None, fingerprint: Optional[TransportableData] = None):
        super().__init__(meta=meta, version=version, public_key=public_key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__addresses = {}  # int -> Address

    @property  # Override
    def has_seed(self) -> bool:
        return True

    # Override
    def generate_address(self, network: int = None) -> Address:
        # assert self.type == 'MKM' or self.type == '1', 'meta version error: %s' % self.type
        assert network is not None, 'address type should not be empty'
        # check caches
        cached = self.__addresses.get(network)
        if cached is None:
            # generate and cache it
            data = self.fingerprint
            cached = BTCAddress.from_data(data, network=network)
            self.__addresses[network] = cached
        return cached


"""
    Meta to build BTC address for ID
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    version:
        0x02 - BTC
        0x03 - ExBTC

    algorithm:
        CT      = key.data;
        hash    = ripemd160(sha256(CT));
        code    = sha256(sha256(network + hash)).prefix(4);
        address = base58_encode(network + hash + code);
"""


class BTCMeta(BaseMeta):

    def __init__(self, meta: Dict[str, Any] = None,
                 version: str = None, public_key: VerifyKey = None,
                 seed: Optional[str] = None, fingerprint: Optional[TransportableData] = None):
        super().__init__(meta=meta, version=version, public_key=public_key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__addresses = {}  # int -> Address

    @property  # Override
    def has_seed(self) -> bool:
        return False

    # Override
    def generate_address(self, network: int = None) -> Address:
        # assert self.type == 'BTC' or self.type == '2', 'meta version error: %s' % self.type
        assert network is not None, 'address type should not be empty'
        # check caches
        cached = self.__addresses.get(network)
        if cached is None:
            # TODO: compress public key?
            key = self.public_key
            data = key.data
            # generate and cache it
            cached = BTCAddress.from_data(data, network=network)
            self.__addresses[network] = cached
        return cached


"""
    Meta to build ETH address for ID
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    version:
        0x04 - ETH
        0x05 - ExETH

    algorithm:
        fingerprint = key.data
        digest      = keccak256(fingerprint)
        address     = hex_encode(digest.suffix(20))
"""


class ETHMeta(BaseMeta):

    def __init__(self, meta: Dict[str, Any] = None,
                 version: str = None, public_key: VerifyKey = None,
                 seed: Optional[str] = None, fingerprint: Optional[TransportableData] = None):
        super().__init__(meta=meta, version=version, public_key=public_key, seed=seed, fingerprint=fingerprint)
        # caches
        self.__address: Optional[Address] = None

    @property  # Override
    def has_seed(self) -> bool:
        return False

    # Override
    def generate_address(self, network: int = None) -> Address:
        # assert self.type == 'ETH' or self.type == '4', 'meta version error: %s' % self.type
        assert network == EntityType.USER, 'ETH address type error: %d' % network
        # check cache
        cached = self.__address
        if cached is None:  # or cached.type != network:
            # 64 bytes key data without prefix 0x04
            key = self.public_key
            data = key.data
            # generate and cache it
            cached = ETHAddress.from_data(data)
            self.__address = cached
        return cached


class BaseMetaFactory(MetaFactory):

    def __init__(self, version: str):
        super().__init__()
        self.__type = version

    @property  # protected
    def type(self) -> str:
        return self.__type

    # Override
    def generate_meta(self, private_key: SignKey, seed: Optional[str]) -> Meta:
        if seed is None or len(seed) == 0:
            fingerprint = None
        else:
            sig = private_key.sign(data=utf8_encode(string=seed))
            fingerprint = TransportableData.create(data=sig)
        assert isinstance(private_key, PrivateKey), 'private key error: %s' % private_key
        public_key = private_key.public_key
        return self.create_meta(public_key=public_key, seed=seed, fingerprint=fingerprint)

    # Override
    def create_meta(self, public_key: VerifyKey, seed: Optional[str], fingerprint: Optional[TransportableData]) -> Meta:
        version = self.type
        if version == MetaType.MKM or version == 'mkm':
            out = DefaultMeta(version=version, public_key=public_key, seed=seed, fingerprint=fingerprint)
        elif version == MetaType.BTC or version == 'btc':
            out = BTCMeta(version=version, public_key=public_key)
        elif version == MetaType.ETH or version == 'eth':
            out = ETHMeta(version=version, public_key=public_key)
        else:
            raise TypeError('unknown meta type: %s' % version)
        assert out.valid, 'meta error: %s' % out
        return out

    # Override
    def parse_meta(self, meta: dict) -> Optional[Meta]:
        # # check 'type', 'key', 'seed', 'fingerprint'
        # if 'type' not in meta or 'key' not in meta:
        #     # meta.type should not be empty
        #     # meta.key should not be empty
        #     return None
        # elif 'seed' not in meta:
        #     if 'fingerprint' in meta:
        #         assert False, 'meta error: %s' % meta
        # elif 'fingerprint' not in meta:
        #     assert False, 'meta error: %s' % meta
        ext = SharedAccountExtensions()
        version = ext.helper.get_meta_type(meta=meta, default='')
        if version == MetaType.MKM or version == 'mkm':
            out = DefaultMeta(meta=meta)
        elif version == MetaType.BTC or version == 'btc':
            out = BTCMeta(meta=meta)
        elif version == MetaType.ETH or version == 'eth':
            out = ETHMeta(meta=meta)
        else:
            raise TypeError('unknown meta type: %s' % version)
        if out.valid:
            return out
