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

import random
import threading
from typing import Optional, Any, Dict

from dimp import DateTime
from dimp import ID
from dimp import Content, Envelope
from dimp import InstantMessage, SecureMessage, ReliableMessage
from dimp import EnvelopeFactory, InstantMessageFactory, SecureMessageFactory, ReliableMessageFactory
from dimp import MessageEnvelope, PlainMessage, EncryptedMessage, NetworkMessage


class MessageFactory(EnvelopeFactory, InstantMessageFactory, SecureMessageFactory, ReliableMessageFactory):

    def __init__(self):
        super().__init__()
        self.__sn = random.randint(1, 0x7fffffff)
        self.__lock = threading.Lock()

    def __next(self) -> int:
        """ return 1 ~ 2^31-1 """
        with self.__lock:
            if self.__sn < 0x7fffffff:  # 2 ** 31 - 1
                self.__sn += 1
            else:
                self.__sn = 1
            return self.__sn

    #
    #   EnvelopeFactory
    #

    # Override
    def create_envelope(self, sender: ID, receiver: ID, time: Optional[DateTime]) -> Envelope:
        return MessageEnvelope(sender=sender, receiver=receiver, time=time)

    # Override
    def parse_envelope(self, envelope: Dict[str, Any]) -> Optional[Envelope]:
        # check 'sender'
        if envelope.get('sender') is None:
            # env.sender should not empty
            return None
        return MessageEnvelope(envelope=envelope)

    #
    #   InstantMessageFactory
    #

    # Override
    def generate_serial_number(self, msg_type: Optional[str], now: Optional[DateTime]) -> int:
        # because we must make sure all messages in a same chat box won't have
        # same serial numbers, so we can't use time-related numbers, therefore
        # the best choice is a totally random number, maybe.
        return self.__next()

    # Override
    def create_instant_message(self, head: Envelope, body: Content) -> InstantMessage:
        return PlainMessage(head=head, body=body)

    # Override
    def parse_instant_message(self, msg: Dict[str, Any]) -> Optional[InstantMessage]:
        # check 'sender', 'content'
        if msg.get('sender') is None or msg.get('content') is None:
            # msg.sender should not be empty
            # msg.content should not be empty
            return None
        return PlainMessage(msg=msg)

    #
    #   SecureMessageFactory
    #

    # Override
    def parse_secure_message(self, msg: Dict[str, Any]) -> Optional[SecureMessage]:
        # check 'sender', 'data'
        if msg.get('sender') is None or msg.get('data') is None:
            # msg.sender should not be empty
            # msg.data should not be empty
            return None
        # check 'signature'
        if msg.get('signature') is not None:
            return NetworkMessage(msg=msg)
        return EncryptedMessage(msg=msg)

    #
    #   ReliableMessageFactory
    #

    # Override
    def parse_reliable_message(self, msg: Dict[str, Any]) -> Optional[ReliableMessage]:
        # check 'sender', 'data', 'signature'
        if msg.get('sender') is None or msg.get('data') is None or msg.get('signature') is None:
            # msg.sender should not be empty
            # msg.data should not be empty
            # msg.signature should not be empty
            return None
        return NetworkMessage(msg=msg)
