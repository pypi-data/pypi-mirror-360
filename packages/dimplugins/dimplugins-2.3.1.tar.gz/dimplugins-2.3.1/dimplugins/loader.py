# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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

from dimp import *

from .format import *
from .crypto import *
from .mkm import *


# noinspection PyMethodMayBeStatic
class PluginLoader:

    def __init__(self):
        super().__init__()
        self.__loaded = False

    def run(self):
        if self.__loaded:
            # no need to load it again
            return
        else:
            # mark it to loaded
            self.__loaded = True
        # try to load all plugins
        self._load()

    def _load(self):
        """ Register plugins """
        self._register_data_coders()
        self._register_data_digesters()

        self._register_symmetric_key_factories()
        self._register_asymmetric_key_factories()

        self._register_id_factory()
        self._register_address_factory()
        self._register_meta_factories()
        self._register_document_factories()

    def _register_data_coders(self):
        """ Data coders """
        self._register_base58_coder()
        self._register_base64_coder()
        self._register_hex_coder()

        self._register_utf8_coder()
        self._register_json_coder()

        self._register_pnf_factory()
        self._register_ted_factory()

    def _register_base58_coder(self):
        # Base58 coding
        Base58.coder = Base58Coder()

    def _register_base64_coder(self):
        # Base64 coding
        Base64.coder = Base64Coder()

    def _register_hex_coder(self):
        # HEX coding
        Hex.coder = HexCoder()

    def _register_utf8_coder(self):
        # UTF8
        UTF8.coder = UTF8Coder()

    def _register_json_coder(self):
        # JSON
        JSON.coder = JSONCoder()

    def _register_pnf_factory(self):
        # PNF
        factory = BaseNetworkFileFactory()
        PortableNetworkFile.set_factory(factory=factory)

    def _register_ted_factory(self):
        # TED
        factory = Base64DataFactory()
        TransportableData.set_factory(algorithm=EncodeAlgorithms.BASE_64, factory=factory)
        # TransportableData.register(algorithm=EncodeAlgorithms.DEFAULT, factory=factory)
        TransportableData.set_factory(algorithm='*', factory=factory)

    def _register_data_digesters(self):
        """ Data digesters """
        self._register_md5_digester()
        self._register_sha1_digester()
        self._register_sha256_digester()
        self._register_keccak256_digester()
        self._register_ripemd160_digester()

    def _register_md5_digester(self):
        # MD5
        MD5.digester = MD5Digester()

    def _register_sha1_digester(self):
        # SHA1
        SHA1.digester = SHA1Digester()

    def _register_sha256_digester(self):
        # SHA256
        SHA256.digester = SHA256Digester()

    def _register_keccak256_digester(self):
        # KECCAK256
        KECCAK256.digester = Keccak256Digester()

    def _register_ripemd160_digester(self):
        # RIPEMD160
        RIPEMD160.digester = RipeMD160Digester()

    def _register_symmetric_key_factories(self):
        """ Symmetric key parsers """
        self._register_aes_key_factory()
        self._register_plain_key_factory()

    def _register_aes_key_factory(self):
        # Symmetric Key: AES
        factory = AESKeyFactory()
        SymmetricKey.set_factory(algorithm=SymmetricAlgorithms.AES, factory=factory)
        SymmetricKey.set_factory(algorithm='AES/CBC/PKCS7Padding', factory=factory)

    def _register_plain_key_factory(self):
        # Symmetric Key: Plain
        factory = PlainKeyFactory()
        SymmetricKey.set_factory(algorithm=SymmetricAlgorithms.PLAIN, factory=factory)

    def _register_asymmetric_key_factories(self):
        """ Asymmetric key parsers """
        self._register_rsa_key_factories()
        self._register_ecc_key_factories()

    def _register_rsa_key_factories(self):
        # Public Key: RSA
        rsa_pub = RSAPublicKeyFactory()
        PublicKey.set_factory(algorithm=AsymmetricAlgorithms.RSA, factory=rsa_pub)
        PublicKey.set_factory(algorithm='SHA256withRSA', factory=rsa_pub)
        PublicKey.set_factory(algorithm='RSA/ECB/PKCS1Padding', factory=rsa_pub)
        # Private Key: RSA
        rsa_pri = RSAPrivateKeyFactory()
        PrivateKey.set_factory(algorithm=AsymmetricAlgorithms.RSA, factory=rsa_pri)
        PrivateKey.set_factory(algorithm='SHA256withRSA', factory=rsa_pri)
        PrivateKey.set_factory(algorithm='RSA/ECB/PKCS1Padding', factory=rsa_pri)

    def _register_ecc_key_factories(self):
        # Public Key: ECC
        ecc_pub = ECCPublicKeyFactory()
        PublicKey.set_factory(algorithm=AsymmetricAlgorithms.ECC, factory=ecc_pub)
        PublicKey.set_factory(algorithm='SHA256withECDSA', factory=ecc_pub)
        # Private Key: ECC
        ecc_pri = ECCPrivateKeyFactory()
        PrivateKey.set_factory(algorithm=AsymmetricAlgorithms.ECC, factory=ecc_pri)
        PrivateKey.set_factory(algorithm='SHA256withECDSA', factory=ecc_pri)

    def _register_id_factory(self):
        """ ID factory """
        ID.set_factory(factory=GeneralIdentifierFactory())

    def _register_address_factory(self):
        """ Address factory """
        Address.set_factory(factory=BaseAddressFactory())

    def _register_meta_factories(self):
        """ Meta factories """
        self._set_meta_factory(version=MetaType.MKM, alias='mkm')
        self._set_meta_factory(version=MetaType.BTC, alias='btc')
        self._set_meta_factory(version=MetaType.ETH, alias='eth')

    def _set_meta_factory(self, version: str, alias: str, factory: MetaFactory = None):
        if factory is None:
            factory = BaseMetaFactory(version=version)
        Meta.set_factory(version=version, factory=factory)
        Meta.set_factory(version=alias, factory=factory)

    def _register_document_factories(self):
        """ Document factories """
        self._set_document_factory(doc_type=DocumentType.VISA)
        self._set_document_factory(doc_type=DocumentType.PROFILE)
        self._set_document_factory(doc_type=DocumentType.BULLETIN)

    def _set_document_factory(self, doc_type: str, factory: DocumentFactory = None):
        if factory is None:
            factory = GeneralDocumentFactory(doc_type=doc_type)
        Document.set_factory(doc_type=doc_type, factory=factory)
