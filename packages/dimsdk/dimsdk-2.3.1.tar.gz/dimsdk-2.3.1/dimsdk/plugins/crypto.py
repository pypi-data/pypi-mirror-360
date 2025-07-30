# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2021 Albert Moky
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

from dimp import Converter, Wrapper
from dimp import SymmetricKey, SymmetricKeyFactory
from dimp import PublicKey, PublicKeyFactory
from dimp import PrivateKey, PrivateKeyFactory

from dimp.plugins import GeneralCryptoHelper
from dimp.plugins import SymmetricKeyHelper
from dimp.plugins import PrivateKeyHelper, PublicKeyHelper


class CryptographyKeyGeneralFactory(GeneralCryptoHelper, SymmetricKeyHelper,
                                    PrivateKeyHelper, PublicKeyHelper):

    def __init__(self):
        super().__init__()
        # str(algorithm) -> SymmetricKey.Factory
        self.__symmetric_key_factories: Dict[str, SymmetricKeyFactory] = {}
        # str(algorithm) -> PublicKey.Factory
        self.__public_key_factories: Dict[str, PublicKeyFactory] = {}
        # str(algorithm) -> PrivateKey.Factory
        self.__private_key_factories: Dict[str, PrivateKeyFactory] = {}

    # Override
    def get_key_algorithm(self, key: Dict[str, Any], default: Optional[str]) -> Optional[str]:
        """ get key algorithm name """
        value = key.get('algorithm')
        return Converter.get_str(value=value, default=default)

    #
    #   SymmetricKey
    #

    # Override
    def set_symmetric_key_factory(self, algorithm: str, factory: SymmetricKeyFactory):
        self.__symmetric_key_factories[algorithm] = factory

    # Override
    def get_symmetric_key_factory(self, algorithm: str) -> Optional[SymmetricKeyFactory]:
        return self.__symmetric_key_factories.get(algorithm)

    # Override
    def generate_symmetric_key(self, algorithm: str) -> Optional[SymmetricKey]:
        factory = self.get_symmetric_key_factory(algorithm=algorithm)
        assert factory is not None, 'key algorithm not support: %s' % algorithm
        return factory.generate_symmetric_key()

    # Override
    def parse_symmetric_key(self, key: Any) -> Optional[SymmetricKey]:
        if key is None:
            return None
        if isinstance(key, SymmetricKey):
            return key
        info = Wrapper.get_dict(key)
        if info is None:
            # assert False, 'key error: %s' % key
            return None
        algorithm = self.get_key_algorithm(key=info, default=None)
        # assert algorithm is not None, 'symmetric key error: %s' % key
        factory = None if algorithm is None else self.get_symmetric_key_factory(algorithm=algorithm)
        if factory is None:
            # unknown algorithm, get default key factory
            factory = self.get_symmetric_key_factory(algorithm='*')  # unknown
            if factory is None:
                # assert False, 'default symmetric key factory not found: %s' % key
                return None
        return factory.parse_symmetric_key(key=info)

    #
    #   PublicKey
    #

    # Override
    def set_public_key_factory(self, algorithm: str, factory: PublicKeyFactory):
        self.__public_key_factories[algorithm] = factory

    # Override
    def get_public_key_factory(self, algorithm: str) -> Optional[PublicKeyFactory]:
        return self.__public_key_factories.get(algorithm)

    # Override
    def parse_public_key(self, key: Any) -> Optional[PublicKey]:
        if key is None:
            return None
        elif isinstance(key, PublicKey):
            return key
        info = Wrapper.get_dict(key)
        if info is None:
            # assert False, 'key error: %s' % key
            return None
        algorithm = self.get_key_algorithm(key=info, default=None)
        # assert algorithm is not None, 'public key error: %s' % key
        factory = None if algorithm is None else self.get_public_key_factory(algorithm=algorithm)
        if factory is None:
            # unknown algorithm, get default key factory
            factory = self.get_public_key_factory(algorithm='*')  # unknown
            if factory is None:
                # assert False, 'default public key factory not found: %s' % key
                return None
        return factory.parse_public_key(key=info)

    #
    #   PrivateKey
    #

    # Override
    def set_private_key_factory(self, algorithm: str, factory: PrivateKeyFactory):
        self.__private_key_factories[algorithm] = factory

    # Override
    def get_private_key_factory(self, algorithm: str) -> Optional[PrivateKeyFactory]:
        return self.__private_key_factories.get(algorithm)

    # Override
    def generate_private_key(self, algorithm: str) -> Optional[PrivateKey]:
        factory = self.get_private_key_factory(algorithm=algorithm)
        assert factory is not None, 'key algorithm not support: %s' % algorithm
        return factory.generate_private_key()

    # Override
    def parse_private_key(self, key: Any) -> Optional[PrivateKey]:
        if key is None:
            return None
        elif isinstance(key, PrivateKey):
            return key
        info = Wrapper.get_dict(key)
        if info is None:
            # assert False, 'key error: %s' % key
            return None
        algorithm = self.get_key_algorithm(key=info, default=None)
        # assert algorithm is not None, 'private key error: %s' % key
        factory = None if algorithm is None else self.get_private_key_factory(algorithm=algorithm)
        if factory is None:
            # unknown algorithm, get default key factory
            factory = self.get_private_key_factory(algorithm='*')  # unknown
            if factory is None:
                # assert False, 'default private key factory not found: %s' % key
                return None
        return factory.parse_private_key(key=info)
