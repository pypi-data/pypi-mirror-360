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
from abc import abstractmethod
from typing import Optional

from dimp import SecureMessage, ReliableMessage

from ..dkd import ReliableMessageDelegate


class ReliableMessagePacker:

    def __init__(self, messenger: ReliableMessageDelegate):
        super().__init__()
        self.__transceiver = weakref.ref(messenger)

    @property
    def delegate(self) -> ReliableMessageDelegate:
        return self.__transceiver()

    """
        Verify the Reliable Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |  1. verify(data, signature, sender.PK)
            | key/keys |      | key/keys |
            | signature|      +----------+
            +----------+
    """

    @abstractmethod
    async def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        """
        Verify 'data' and 'signature' field with sender's public key

        :param msg: network message
        :return: SecureMessage object if signature matched
        """
        transceiver = self.delegate
        #
        #   0. Decode 'message.data' to encrypted content data
        #
        ciphertext = msg.data
        if len(ciphertext) == 0:
            # assert False, 'failed to decode message data: %s => %s, %s'\
            #               % (msg.sender, msg.receiver, msg.group)
            return None
        #
        #   1. Decode 'message.signature' from String (Base64)
        #
        signature = msg.signature
        if len(signature) == 0:
            # assert False, 'failed to decode message signature: %s => %s, %s'\
            #               % (msg.sender, msg.receiver, msg.group)
            return None
        #
        #   2. Verify the message data and signature with sender's public key
        #
        ok = await transceiver.verify_data_signature(data=ciphertext, signature=signature, msg=msg)
        if not ok:
            # assert False, 'message signature not match: %s => %s, %s'\
            #               % (msg.sender, msg.receiver, msg.group)
            return None
        # OK, pack message
        info = msg.copy_dictionary(deep_copy=False)
        info.pop('signature', None)
        return SecureMessage.parse(msg=info)
