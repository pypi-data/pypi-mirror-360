# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
#
#                                Written in 2025 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2025 Albert Moky
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

from abc import ABC, abstractmethod
from typing import List, Dict


class Shortener(ABC):

    #
    #   Compress Content
    #

    @abstractmethod
    def compress_content(self, content: Dict) -> Dict:
        raise NotImplemented

    @abstractmethod
    def extract_content(self, content: Dict) -> Dict:
        raise NotImplemented

    #
    #   Compress SymmetricKey
    #

    @abstractmethod
    def compress_symmetric_key(self, key: Dict) -> Dict:
        raise NotImplemented

    @abstractmethod
    def extract_symmetric_keys(self, key: Dict) -> Dict:
        raise NotImplemented

    #
    #   Compress ReliableMessage
    #

    @abstractmethod
    def compress_reliable_message(self, msg: Dict) -> Dict:
        raise NotImplemented

    @abstractmethod
    def extract_reliable_message(self, msg: Dict) -> Dict:
        raise NotImplemented


class MessageShortener(Shortener):

    def __init__(self):
        super().__init__()
        # Compress Content
        self.__content_short_keys = [
            "T", "type",
            "N", "sn",
            "W", "time",       # When
            "G", "group",
        ]
        # Compress SymmetricKey
        self.__crypto_short_keys = [
            "A", "algorithm",
            "D", "data",
            "I", "iv",         # Initial Vector
        ]
        # Compress ReliableMessage
        self.__message_short_keys = [
            "F", "sender",     # From
            "R", "receiver",   # Rcpt to
            "W", "time",       # When
            "T", "type",
            "G", "group",
            # ------------------
            "K", "key",        # or "keys"
            "D", "data",
            "V", "signature",  # Verify
            # ------------------
            "M", "meta",
            "P", "visa",       # Profile
        ]

    # noinspection PyMethodMayBeStatic
    def _move_key(self, from_key: str, to_key: str, info: Dict):
        value = info.get(from_key)
        if value is not None:
            info.pop(from_key, None)
            info[to_key] = value

    def _shorten_keys(self, keys: List[str], info: Dict):
        size = len(keys)
        i = 1
        while i < size:
            self._move_key(from_key=keys[i], to_key=keys[i - 1], info=info)
            i += 2

    def _restore_keys(self, keys: List[str], info: Dict):
        size = len(keys)
        i = 1
        while i < size:
            self._move_key(from_key=keys[i - 1], to_key=keys[i], info=info)
            i += 2

    #
    #   Compress Content
    #

    @property
    def content_short_keys(self) -> List[str]:
        return self.__content_short_keys

    @content_short_keys.setter
    def content_short_keys(self, keys: List[str]):
        self.__content_short_keys = keys

    # Override
    def compress_content(self, content: Dict) -> Dict:
        self._shorten_keys(keys=self.content_short_keys, info=content)
        return content

    # Override
    def extract_content(self, content: Dict) -> Dict:
        self._restore_keys(keys=self.content_short_keys, info=content)
        return content

    #
    #   Compress SymmetricKey
    #

    @property
    def crypto_short_keys(self) -> List[str]:
        return self.__crypto_short_keys

    @crypto_short_keys.setter
    def crypto_short_keys(self, keys: List[str]):
        self.__crypto_short_keys = keys

    # Override
    def compress_symmetric_key(self, key: Dict) -> Dict:
        self._shorten_keys(keys=self.crypto_short_keys, info=key)
        return key

    # Override
    def extract_symmetric_keys(self, key: Dict) -> Dict:
        self._restore_keys(keys=self.crypto_short_keys, info=key)
        return key

    #
    #   Compress ReliableMessage
    #

    @property
    def message_short_keys(self) -> List[str]:
        return self.__message_short_keys

    @message_short_keys.setter
    def message_short_keys(self, keys: List[str]):
        self.__message_short_keys = keys

    # Override
    def compress_reliable_message(self, msg: Dict) -> Dict:
        self._move_key(from_key='keys', to_key='K', info=msg)
        self._shorten_keys(keys=self.message_short_keys, info=msg)
        return msg

    # Override
    def extract_reliable_message(self, msg: Dict) -> Dict:
        keys = msg.get('K')
        if keys is None:
            # assert 'data' in msg, 'message data should not empty: %s' % msg
            pass
        elif isinstance(keys, Dict):
            assert 'keys' not in msg, 'message keys duplicated: %s' % msg
            msg.pop('K', None)
            msg['keys'] = keys
        elif isinstance(keys, str):
            assert 'key' not in msg, 'message key duplicated: %s' % msg
            msg.pop('K', None)
            msg['key'] = keys
        else:
            assert False, 'message key error: %s' % msg
        self._restore_keys(keys=self.message_short_keys, info=msg)
        return msg
