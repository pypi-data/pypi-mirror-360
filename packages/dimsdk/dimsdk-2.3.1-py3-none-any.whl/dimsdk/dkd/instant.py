# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
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

from abc import ABC, abstractmethod
from typing import Optional

from dimp import SymmetricKey
from dimp import ID
from dimp import Content
from dimp import InstantMessage


class InstantMessageDelegate(ABC):

    """
        Encrypt the Instant Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | content  |      | data     |  1. data = encrypt(content, PW)
            +----------+      | key/keys |  2. key  = encrypt(PW, receiver.PK)
                              +----------+
    """

    #
    #   Encrypt Content
    #

    @abstractmethod
    async def serialize_content(self, content: Content, key: SymmetricKey, msg: InstantMessage) -> bytes:
        """
        1. Serialize 'message.content' to data (JsON / ProtoBuf / ...)

        :param content:  message content
        :param key:      symmetric key (includes data compression algorithm)
        :param msg:      instant message object
        :return: serialized content data
        """
        raise NotImplemented

    @abstractmethod
    async def encrypt_content(self, data: bytes, key: SymmetricKey, msg: InstantMessage) -> bytes:
        """
        2. Encrypt content data to 'message.data' with symmetric key

        :param data:     serialized data of message.content
        :param key:      symmetric key
        :param msg:      instant message object
        :return: encrypted message content data
        """
        raise NotImplemented

    # @abstractmethod
    # async def encode_data(self, data: bytes, msg: InstantMessage) -> Any:
    #     """
    #     3. Encode 'message.data' to String (Base64)
    #
    #     :param data:     encrypted content data
    #     :param msg:      instant message object
    #     :return: base64 string
    #     """
    #     raise NotImplemented

    #
    #   Encrypt Key
    #

    @abstractmethod
    async def serialize_key(self, key: SymmetricKey, msg: InstantMessage) -> Optional[bytes]:
        """
        4. Serialize message key to data (JsON / ProtoBuf / ...)

        :param key:      symmetric key
        :param msg:      instant message object
        :return: serialized key data, None for reused (or broadcast message)
        """
        raise NotImplemented

    @abstractmethod
    async def encrypt_key(self, data: bytes, receiver: ID, msg: InstantMessage) -> Optional[bytes]:
        """
        5. Encrypt key data to 'message.key' with receiver's public key

        :param data:     serialized data of symmetric key
        :param receiver: actual receiver (user, or group member)
        :param msg:      instant message object
        :return: encrypted symmetric key data, None on visa not found
        """
        raise NotImplemented

    # @abstractmethod
    # async def encode_key(self, data: bytes, msg: InstantMessage) -> Any:
    #     """
    #     6. Encode 'message.key' to String (Base64)
    #
    #     :param data:     encrypted key data
    #     :param msg:      instant message object
    #     :return: base64 string
    #     """
    #     raise NotImplemented
