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
from dimp import SecureMessage


class SecureMessageDelegate(ABC):

    """
        Decrypt the Secure Message to Instant Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |  1. PW      = decrypt(key, receiver.SK)
            | data     |      | content  |  2. content = decrypt(data, PW)
            | key/keys |      +----------+
            +----------+
    """

    #
    #   Decrypt Key
    #

    # @abstractmethod
    # async def decode_key(self, key: Any, msg: SecureMessage) -> Optional[bytes]:
    #     """
    #     1. Decode 'message.key' to encrypted symmetric key data
    #
    #     :param key:      base64 string
    #     :param msg:      secure message object
    #     :return: encrypted symmetric key data
    #     """
    #     raise NotImplemented

    @abstractmethod
    async def decrypt_key(self, data: bytes, receiver: ID, msg: SecureMessage) -> Optional[bytes]:
        """
        2. Decrypt 'message.key' with receiver's private key

        :param data:     encrypted symmetric key data
        :param receiver: actual receiver (user, or group member)
        :param msg:      secure message object
        :return: serialized symmetric key
        """
        raise NotImplemented

    @abstractmethod
    async def deserialize_key(self, data: Optional[bytes], msg: SecureMessage) -> Optional[SymmetricKey]:
        """
        3. Deserialize message key from data (JsON / ProtoBuf / ...)
           (if key data is empty, means it should be reused, get it from key cache)

        :param data:     serialized key data, None for reused key
        :param msg:      secure message object
        :return: symmetric key
        """
        raise NotImplemented

    #
    #   Decrypt Content
    #

    # @abstractmethod
    # async def decode_data(self, data: Any, msg: SecureMessage) -> Optional[bytes]:
    #     """
    #     4. Decode 'message.data' to encrypted content data
    #
    #     :param data:     base64 string
    #     :param msg:      secure message object
    #     :return: encrypted content data
    #     """
    #     raise NotImplemented

    @abstractmethod
    async def decrypt_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[bytes]:
        """
        5. Decrypt 'message.data' with symmetric key

        :param data:     encrypted content data
        :param key:      symmetric key
        :param msg:      secure message object
        :return: serialized message content
        """
        raise NotImplemented

    @abstractmethod
    async def deserialize_content(self, data: bytes, key: SymmetricKey, msg: SecureMessage) -> Optional[Content]:
        """
        6. Deserialize message content from data (JsON / ProtoBuf / ...)

        :param data:     serialized content data
        :param key:      symmetric key (includes data compression algorithm)
        :param msg:      secure message object
        :return: message content
        """
        raise NotImplemented

    """
        Sign the Secure Message to Reliable Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |
            | key/keys |      | key/keys |
            +----------+      | signature|  1. signature = sign(data, sender.SK)
                              +----------+
    """

    #
    #   Signature
    #

    @abstractmethod
    async def sign_data(self, data: bytes, msg: SecureMessage) -> bytes:
        """
        1. Sign 'message.data' with sender's private key

        :param data:      encrypted message data
        :param msg:       secure message object
        :return: signature of encrypted message data
        """
        raise NotImplemented

    # @abstractmethod
    # async def encode_signature(self, signature: bytes, msg: SecureMessage) -> Any:
    #     """
    #     2. Encode 'message.signature' to String (Base64)
    #
    #     :param signature: signature of message.data
    #     :param msg:       secure message object
    #     :return: base64 string
    #     """
    #     raise NotImplemented
