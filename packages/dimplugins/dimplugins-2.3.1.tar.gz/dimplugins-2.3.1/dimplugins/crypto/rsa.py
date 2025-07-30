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

from typing import Optional, Union, Any, Dict

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5

from dimp import AsymmetricAlgorithms
from dimp import EncryptKey, DecryptKey
from dimp import PublicKey, PublicKeyFactory
from dimp import PrivateKey, PrivateKeyFactory
from dimp import BaseKey, BasePublicKey, BasePrivateKey


class RSAPublicKey(BasePublicKey, EncryptKey):
    """ RSA Public Key """

    def __init__(self, key: Dict[str, Any]):
        super().__init__(key)
        self.__key = None
        self.__data = None

    @property  # private
    def rsa_key(self) -> RSA.RsaKey:
        if self.__key is None:
            # data in 'PEM' format
            data = self.get('data')
            assert data is not None, 'failed to get key data: %s' % self
            self.__key = RSA.importKey(data)
        return self.__key

    @property  # Override
    def data(self) -> bytes:
        if self.__data is None:
            rsa_key = self.rsa_key
            assert rsa_key is not None, 'rsa key error: %s' % self
            self.__data = rsa_key.exportKey(format='DER')
        return self.__data

    @property
    def size(self) -> int:
        return self.bits >> 3

    @property
    def bits(self) -> int:
        bits = self.get('sizeInBits')
        if bits is None:
            return 1024  # RSA-1024
        else:
            return int(bits)

    # Override
    def encrypt(self, data: bytes, extra: Optional[Dict]) -> bytes:
        cipher = Cipher_PKCS1_v1_5.new(self.rsa_key)
        return cipher.encrypt(data)

    # Override
    def verify(self, data: bytes, signature: bytes) -> bool:
        try:
            hash_obj = SHA256.SHA256Hash(data)
            verifier = Signature_PKCS1_v1_5.new(self.rsa_key)
            verifier.verify(hash_obj, signature)
            return True
        except ValueError:
            # raise ValueError("Invalid signature")
            return False


class RSAPrivateKey(BasePrivateKey, DecryptKey):
    """ RSA Private Key """

    def __init__(self, key: Dict[str, Any]):
        super().__init__(key)
        # check key data
        pem: str = key.get('data')
        if pem is None or len(pem) == 0:
            # generate private key data
            rsa_key, data = generate(bits=self.bits)
            # store private key in PKCS#1 format
            pem = data.decode('utf-8')
            self.__key = rsa_key
            self.__data = data
            self['data'] = pem
            self['mode'] = 'ECB'
            self['padding'] = 'PKCS1'
            self['digest'] = 'SHA256'
        else:
            self.__key = None
            self.__data = None

    @property  # private
    def rsa_key(self) -> RSA.RsaKey:
        if self.__key is None:
            # data in 'PEM' format
            data = self.get('data')
            assert data is not None, 'failed to get key data: %s' % self
            tag1 = '-----BEGIN RSA PRIVATE KEY-----'
            tag2 = '-----END RSA PRIVATE KEY-----'
            pos2 = data.rfind(tag2)
            if pos2 > 0:
                pos1 = data.find(tag1)
                data = data[pos1: pos2 + len(tag2)]
            self.__key = RSA.importKey(data)
        return self.__key

    @property  # Override
    def data(self) -> bytes:
        if self.__data is None:
            rsa_key = self.rsa_key
            assert rsa_key is not None, 'rsa key error: %s' % self
            self.__data = rsa_key.exportKey(format='DER')
        return self.__data

    @property
    def size(self) -> int:
        return self.bits >> 3

    @property
    def bits(self) -> int:
        bits = self.get('sizeInBits')
        if bits is None:
            return 1024  # RSA-1024
        else:
            return int(bits)

    @property  # Override
    def public_key(self) -> Union[PublicKey, EncryptKey]:
        pub = self.rsa_key.publickey()
        pem = pub.exportKey().decode('utf-8')
        info = {
            'algorithm': AsymmetricAlgorithms.RSA,
            'data': pem,
            'mode': 'ECB',
            'padding': 'PKCS1',
            'digest': 'SHA256'
        }
        return RSAPublicKey(info)

    # Override
    def decrypt(self, data: bytes, params: Optional[Dict]) -> Optional[bytes]:
        sentinel: Optional[bytes] = None
        try:
            cipher = Cipher_PKCS1_v1_5.new(self.rsa_key)
            return cipher.decrypt(data, sentinel)
        except ValueError:
            return None

    # Override
    def sign(self, data: bytes) -> bytes:
        hash_obj = SHA256.SHA256Hash(data)
        signer = Signature_PKCS1_v1_5.new(self.rsa_key)
        return signer.sign(hash_obj)

    # Override
    def match_encrypt_key(self, key: EncryptKey) -> bool:
        return BaseKey.match_encrypt_key(encrypt_key=key, decrypt_key=self)


def generate(bits: int) -> (RSA.RsaKey, bytes):
    key = RSA.generate(bits=bits)
    return key, key.exportKey()


"""
    Key Factories
    ~~~~~~~~~~~~~
"""


class RSAPublicKeyFactory(PublicKeyFactory):

    # Override
    def parse_public_key(self, key: dict) -> Optional[PublicKey]:
        return RSAPublicKey(key)


class RSAPrivateKeyFactory(PrivateKeyFactory):

    # Override
    def generate_private_key(self) -> Optional[PrivateKey]:
        key = {'algorithm': AsymmetricAlgorithms.RSA}
        return RSAPrivateKey(key)

    # Override
    def parse_private_key(self, key: dict) -> Optional[PrivateKey]:
        return RSAPrivateKey(key)
