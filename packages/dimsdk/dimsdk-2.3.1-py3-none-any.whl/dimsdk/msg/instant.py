# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
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

import weakref
from typing import Optional, List

from dimp import utf8_decode
from dimp import TransportableData
from dimp import SymmetricKey
from dimp import ID
from dimp import InstantMessage, SecureMessage
from dimp import BaseMessage

from ..dkd import InstantMessageDelegate


class InstantMessagePacker:

    def __init__(self, messenger: InstantMessageDelegate):
        super().__init__()
        self.__transceiver = weakref.ref(messenger)

    @property
    def delegate(self) -> InstantMessageDelegate:
        return self.__transceiver()

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

    async def encrypt_message(self, msg: InstantMessage, password: SymmetricKey,
                              members: List[ID] = None) -> Optional[SecureMessage]:
        """
        1. Encrypt message, replace 'content' field with encrypted 'data'
        2. Encrypt group message, replace 'content' field with encrypted 'data'

        :param msg:      plain message
        :param password: symmetric key
        :param members:  group members for group message
        :return: SecureMessage object, None on visa not found
        """
        # TODO: check attachment for File/Image/Audio/Video message content
        #       (do it by application)
        transceiver = self.delegate
        #
        #   1. Serialize 'message.content' to data (JsON / ProtoBuf / ...)
        #
        body = await transceiver.serialize_content(content=msg.content, key=password, msg=msg)
        assert len(body) > 0, 'failed to serialize content: %s' % msg.content
        #
        #   2. Encrypt content data to 'message.data' with symmetric key
        #
        ciphertext = await transceiver.encrypt_content(data=body, key=password, msg=msg)
        assert len(ciphertext) > 0, 'failed to encrypt content with key: %s' % password
        #
        #   3. Encode 'message.data' to String (Base64)
        #
        if BaseMessage.is_broadcast(msg=msg):
            # broadcast message content will not be encrypted (just encoded to JsON),
            # so no need to encode to Base64 here
            encoded_data = utf8_decode(data=ciphertext)
        else:
            # message content had been encrypted by a symmetric key,
            # so the data should be encoded here (with algorithm 'base64' as default).
            encoded_data = TransportableData.encode(data=ciphertext)
        assert encoded_data is not None, 'failed to encode content data: %s' % ciphertext
        # replace 'content' with encrypted 'data
        info = msg.copy_dictionary(deep_copy=False)
        info.pop('content', None)
        info['data'] = encoded_data
        #
        #   4. Serialize message key to data (JsON / ProtoBuf / ...)
        #
        pwd = await transceiver.serialize_key(key=password, msg=msg)
        if pwd is None:
            # A) broadcast message has no key
            # B) reused key
            return SecureMessage.parse(msg=info)
        # encrypt + encode key
        if members is None:
            # personal message
            receiver = msg.receiver
            assert receiver.is_user, 'message.receiver error: %s' % receiver
            #
            #   5. Encrypt key data to 'message.key/keys' with receiver's public key
            #
            encrypted_key = await transceiver.encrypt_key(data=pwd, receiver=receiver, msg=msg)
            if encrypted_key is None:
                # public key for encryption not found
                # TODO: suspend this message for waiting receiver's visa
                return None
            #
            #   6. Encode message key to String (Base64)
            #
            encoded_key = TransportableData.encode(data=encrypted_key)
            # insert as 'key'
            info['key'] = encoded_key
        else:
            # group message
            keys = {}
            for receiver in members:
                #
                #   5. Encrypt key data to 'message.keys' with member's public key
                #
                encrypted_key = await transceiver.encrypt_key(data=pwd, receiver=receiver, msg=msg)
                if encrypted_key is None:
                    # public key for member not found
                    # TODO: suspend this message for waiting member's visa
                    continue
                #
                #   6. Encode message key to String (Base64)
                #
                encoded_key = TransportableData.encode(data=encrypted_key)
                # insert to 'message.keys' with member ID
                keys[str(receiver)] = encoded_key
            if len(keys) == 0:
                # public key for member(s) not found
                # TODO: suspend this message for waiting member's visa
                return None
            # insert as 'keys'
            info['keys'] = keys
        # OK, pack message
        return SecureMessage.parse(msg=info)
