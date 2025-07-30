# DIM Plugins (Python)

[![License](https://img.shields.io/github/license/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dimchat/sdk-py/pulls)
[![Platform](https://img.shields.io/badge/Platform-Python%203-brightgreen.svg)](https://github.com/dimchat/sdk-py/wiki)
[![Issues](https://img.shields.io/github/issues/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/issues)
[![Repo Size](https://img.shields.io/github/repo-size/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/archive/refs/heads/main.zip)
[![Tags](https://img.shields.io/github/tag/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/tags)
[![Version](https://img.shields.io/pypi/v/dimplugins)](https://pypi.org/project/dimplugins)

[![Watchers](https://img.shields.io/github/watchers/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/watchers)
[![Forks](https://img.shields.io/github/forks/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/forks)
[![Stars](https://img.shields.io/github/stars/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/stargazers)
[![Followers](https://img.shields.io/github/followers/dimchat)](https://github.com/orgs/dimchat/followers)

## Plugins

1. Data Coding
   * Base-58
   * Base-64
   * Hex
   * UTF-8
   * JsON
   * PNF _(Portable Network File)_
   * TED _(Transportable Encoded Data)_
2. Digest Digest
   * MD-5
   * SHA-1
   * SHA-256
   * Keccak-256
   * RipeMD-160
3. Cryptography
   * AES-256 _(AES/CBC/PKCS7Padding)_
   * RSA-1024 _(RSA/ECB/PKCS1Padding)_, _(SHA256withRSA)_
   * ECC _(Secp256k1)_
4. Address
   * BTC
   * ETH
5. Meta
   * MKM _(Default)_
   * BTC
   * ETH
6. Document
   * Visa _(User)_
   * Profile
   * Bulletin _(Group)_

## Extends

### Address

```python
from typing import Optional

from dimsdk import ConstantString
from dimsdk import EntityType
from dimsdk import Address, ANYWHERE, EVERYWHERE
from dimplugins import BTCAddress, ETHAddress
from dimplugins import BaseAddressFactory


class CompatibleAddressFactory(BaseAddressFactory):

    # Override
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
            # assert False, 'invalid address: %s' % address
            res = None
        #
        #  TODO: other types of address
        #
        if res is None and 4 <= size <= 64:
            res = UnknownAddress(address=address)
        assert res is not None, 'invalid address: %s' % address
        return res


class UnknownAddress(ConstantString, Address):
    """
        Unsupported Address
        ~~~~~~~~~~~~~~~~~~~
    """

    def __init__(self, address: str):
        super().__init__(string=address)

    @property  # Override
    def network(self) -> int:
        return EntityType.USER.value
```

### Meta

```python
from typing import Optional

from dimsdk import VerifyKey
from dimsdk import TransportableData
from dimsdk import Meta
from dimsdk.plugins import SharedAccountExtensions
from dimplugins import DefaultMeta, BTCMeta, ETHMeta
from dimplugins import BaseMetaFactory


class CompatibleMetaFactory(BaseMetaFactory):

    def __init__(self, version: str):
        super().__init__(version=version)

    # Override
    def create_meta(self, public_key: VerifyKey, seed: Optional[str], fingerprint: Optional[TransportableData]) -> Meta:
        version = self.type
        if version == Meta.MKM:
            # MKM
            out = DefaultMeta(version='1', public_key=public_key, seed=seed, fingerprint=fingerprint)
        elif version == Meta.BTC:
            # BTC
            out = BTCMeta(version='2', public_key=public_key)
        elif version == Meta.ETH:
            # ETH
            out = ETHMeta(version='4', public_key=public_key)
        else:
            raise TypeError('unknown meta type: %d' % version)
        assert out.valid, 'meta error: %s' % out
        return out

    # Override
    def parse_meta(self, meta: dict) -> Optional[Meta]:
        ext = SharedAccountExtensions()
        version = ext.helper.get_meta_type(meta=meta, default='')
        if version in ['1', 'mkm', 'MKM']:
            # MKM
            out = DefaultMeta(meta=meta)
        elif version in ['2', 'btc', 'BTC']:
            # BTC
            out = BTCMeta(meta=meta)
        elif version in ['4', 'eth', 'ETH']:
            # ETH
            out = ETHMeta(meta=meta)
        else:
            raise TypeError('unknown meta type: %d' % version)
        if out.valid:
            return out
```

### Plugin Loader

```python
from dimsdk import Address, Meta
from dimplugins import PluginLoader

from .address import CompatibleAddressFactory
from .meta import CompatibleMetaFactory


class CompatiblePluginLoader(PluginLoader):

    # Override
    def _register_address_factory(self):
        Address.set_factory(factory=CompatibleAddressFactory())

    # Override
    def _register_meta_factories(self):
        mkm = CompatibleMetaFactory(version=Meta.MKM)
        btc = CompatibleMetaFactory(version=Meta.BTC)
        eth = CompatibleMetaFactory(version=Meta.ETH)
        Meta.set_factory(version='1', factory=mkm)
        Meta.set_factory(version='2', factory=btc)
        Meta.set_factory(version='4', factory=eth)
        Meta.set_factory(version='mkm', factory=mkm)
        Meta.set_factory(version='btc', factory=btc)
        Meta.set_factory(version='eth', factory=eth)
        Meta.set_factory(version='MKM', factory=mkm)
        Meta.set_factory(version='BTC', factory=btc)
        Meta.set_factory(version='ETH', factory=eth)
```

## Usage

You must load all plugins before your business run:

```python
from dimsdk.plugins import ExtensionLoader

from .compat_loader import CompatiblePluginLoader


if __name__ == '__main__':
  ExtensionLoader().run()
  CompatiblePluginLoader().run()
  # do your jobs after all extensions & plugins loaded
```

You must ensure that every ```Address``` you extend has a ```Meta``` type that can correspond to it one by one.

----

Copyright &copy; 2018 Albert Moky
[![Followers](https://img.shields.io/github/followers/moky)](https://github.com/moky?tab=followers)
