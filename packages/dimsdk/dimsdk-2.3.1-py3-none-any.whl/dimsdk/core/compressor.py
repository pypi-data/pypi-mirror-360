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
from typing import Optional, Dict

from dimp import json_encode, json_decode
from dimp import utf8_encode, utf8_decode

from .compress_keys import Shortener


class Compressor(ABC):

    @abstractmethod
    def compress_content(self, content: Dict, key: Dict) -> bytes:
        raise NotImplemented

    @abstractmethod
    def extract_content(self, data: bytes, key: Dict) -> Optional[Dict]:
        raise NotImplemented

    @abstractmethod
    def compress_symmetric_key(self, key: Dict) -> bytes:
        raise NotImplemented

    @abstractmethod
    def extract_symmetric_key(self, data: bytes) -> Optional[Dict]:
        raise NotImplemented

    @abstractmethod
    def compress_reliable_message(self, msg: Dict) -> bytes:
        raise NotImplemented

    @abstractmethod
    def extract_reliable_message(self, data: bytes) -> Optional[Dict]:
        raise NotImplemented


class MessageCompressor(Compressor):

    def __init__(self, shortener: Shortener):
        super().__init__()
        self.__shortener = shortener

    @property  # protected
    def shortener(self) -> Shortener:
        return self.__shortener

    #
    #   Compress Content
    #

    # Override
    def compress_content(self, content: Dict, key: Dict) -> bytes:
        content = self.shortener.compress_content(content=content)
        json = json_encode(obj=content)
        return utf8_encode(string=json)

    # Override
    def extract_content(self, data: bytes, key: Dict) -> Optional[Dict]:
        json = utf8_decode(data=data)
        if json is None:
            # assert False, 'content data error: %d' % len(data)
            return None
        info = json_decode(string=json)
        if info is not None:
            info = self.shortener.extract_content(content=info)
            return info

    #
    #   Compress SymmetricKey
    #

    # Override
    def compress_symmetric_key(self, key: Dict) -> bytes:
        key = self.shortener.compress_symmetric_key(key=key)
        json = json_encode(obj=key)
        return utf8_encode(string=json)

    # Override
    def extract_symmetric_key(self, data: bytes) -> Optional[Dict]:
        json = utf8_decode(data=data)
        if json is None:
            # assert False, 'symmetric key error: %d' % len(data)
            return None
        key = json_decode(string=json)
        if key is not None:
            key = self.shortener.extract_symmetric_keys(key=key)
            return key

    #
    #   Compress ReliableMessage
    #

    # Override
    def compress_reliable_message(self, msg: Dict) -> bytes:
        msg = self.shortener.compress_reliable_message(msg=msg)
        json = json_encode(obj=msg)
        return utf8_encode(string=json)

    # Override
    def extract_reliable_message(self, data: bytes) -> Optional[Dict]:
        json = utf8_decode(data=data)
        if json is None:
            # assert False, 'reliable message error: %d' % len(data)
            return None
        msg = json_decode(string=json)
        if msg is not None:
            msg = self.shortener.extract_reliable_message(msg=msg)
            return msg
