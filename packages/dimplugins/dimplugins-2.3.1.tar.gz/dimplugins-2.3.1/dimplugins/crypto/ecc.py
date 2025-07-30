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

import hashlib
from typing import Optional, Union, Any, Dict

import ecdsa

from dimp import AsymmetricAlgorithms
from dimp import PublicKey, PublicKeyFactory
from dimp import PrivateKey, PrivateKeyFactory
from dimp import BasePublicKey, BasePrivateKey


class ECCPublicKey(BasePublicKey):
    """ ECC Public Key """

    def __init__(self, key: Dict[str, Any]):
        super().__init__(key)
        self.__key = None
        self.__data = None

    @property
    def curve(self):
        return ecdsa.SECP256k1

    @property
    def hash_func(self):
        return hashlib.sha256

    @property
    def sig_decode(self):
        return ecdsa.util.sigdecode_der

    @property  # private
    def ecc_key(self) -> ecdsa.VerifyingKey:
        if self.__key is None:
            # data in 'PEM' format
            data = self.get('data')
            assert data is not None, 'failed to get key data: %s' % self
            data_len = len(data)
            if data_len == 130 or data_len == 128:
                data = bytes.fromhex(data)
                self.__key = ecdsa.VerifyingKey.from_string(data, curve=self.curve, hashfunc=self.hash_func)
            else:
                self.__key = ecdsa.VerifyingKey.from_pem(data, hashfunc=self.hash_func)
        return self.__key

    @property  # Override
    def data(self) -> bytes:
        if self.__data is None:
            ecc_key = self.ecc_key
            assert ecc_key is not None, 'ecc key error: %s' % self
            if self.compressed:
                encoding = 'compressed'
            else:
                encoding = 'uncompressed'
            self.__data = ecc_key.to_string(encoding=encoding)
        return self.__data

    @property
    def compressed(self) -> bool:
        return self.get_bool(key='compressed', default=False)

    @property
    def size(self) -> int:
        return self.bits >> 3

    @property
    def bits(self) -> int:
        bits = self.get('sizeInBits')
        if bits is None:
            return 256  # ECC-256
        else:
            return int(bits)

    # Override
    def verify(self, data: bytes, signature: bytes) -> bool:
        try:
            verifier = self.ecc_key
            return verifier.verify(signature=signature, data=data, hashfunc=self.hash_func, sigdecode=self.sig_decode)
        except ecdsa.BadSignatureError:
            return False


class ECCPrivateKey(BasePrivateKey):
    """ ECC Private Key """

    def __init__(self, key: Dict[str, Any]):
        super().__init__(key)
        # check key data
        pem: str = key.get('data')
        if pem is None or len(pem) == 0:
            # generate private key data
            ecc_key, data = generate(curve=self.curve, hash_func=self.hash_func)
            # store private key in PKCS#8 format
            pem = ecc_key.to_pem(format='pkcs8').decode('utf-8')
            # pem = data.hex()
            self.__key = ecc_key
            self.__data = data
            self['data'] = pem
            self['curve'] = 'SECP256k1'
            self['digest'] = 'SHA256'
        else:
            self.__key = None
            self.__data = None

    @property
    def curve(self):
        return ecdsa.SECP256k1

    @property
    def hash_func(self):
        return hashlib.sha256

    @property
    def sig_encode(self):
        return ecdsa.util.sigencode_der

    @property  # private
    def ecc_key(self) -> ecdsa.SigningKey:
        if self.__key is None:
            data = self.get('data')
            assert data is not None, 'failed to get key data: %s' % self
            if len(data) == 64:
                # key data in 'HEX' format
                data = bytes.fromhex(data)
                self.__key = ecdsa.SigningKey.from_string(data, curve=self.curve, hashfunc=self.hash_func)
            else:
                # key data in 'PEM' format
                self.__key = ecdsa.SigningKey.from_pem(data, hashfunc=self.hash_func)
        return self.__key

    @property  # Override
    def data(self) -> bytes:
        if self.__data is None:
            ecc_key = self.ecc_key
            assert ecc_key is not None, 'ecc key error: %s' % self
            self.__data = ecc_key.to_string()
        return self.__data

    @property
    def size(self) -> int:
        return self.bits >> 3

    @property
    def bits(self) -> int:
        bits = self.get('sizeInBits')
        if bits is None:
            return 256  # ECC-256
        else:
            return int(bits)

    @property  # Override
    def public_key(self) -> Union[PublicKey]:
        pub = self.ecc_key.get_verifying_key()
        pem = pub.to_pem().decode('utf-8')
        # pem = key.to_string(encoding='uncompressed').hex()
        info = {
            'algorithm': AsymmetricAlgorithms.ECC,
            'data': pem,
            'curve': 'SECP256k1',
            'digest': 'SHA256'
        }
        return ECCPublicKey(info)

    # Override
    def sign(self, data: bytes) -> bytes:
        signer = self.ecc_key
        return signer.sign(data=data, hashfunc=self.hash_func, sigencode=self.sig_encode)


def generate(curve, hash_func) -> (ecdsa.SigningKey, bytes):
    key = ecdsa.SigningKey.generate(curve=curve, hashfunc=hash_func)
    return key, key.to_string()


"""
    Key Factories
    ~~~~~~~~~~~~~
"""


class ECCPublicKeyFactory(PublicKeyFactory):

    # Override
    def parse_public_key(self, key: dict) -> Optional[PublicKey]:
        return ECCPublicKey(key)


class ECCPrivateKeyFactory(PrivateKeyFactory):

    # Override
    def generate_private_key(self) -> Optional[PrivateKey]:
        key = {'algorithm': AsymmetricAlgorithms.ECC}
        return ECCPrivateKey(key)

    # Override
    def parse_private_key(self, key: dict) -> Optional[PrivateKey]:
        return ECCPrivateKey(key)
