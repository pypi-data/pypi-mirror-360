# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
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
from dimp import Message


class CipherKeyDelegate(ABC):

    """
        Situations:
                      +-------------+-------------+-------------+-------------+
                      |  receiver   |  receiver   |  receiver   |  receiver   |
                      |     is      |     is      |     is      |     is      |
                      |             |             |  broadcast  |  broadcast  |
                      |    user     |    group    |    user     |    group    |
        +-------------+-------------+-------------+-------------+-------------+
        |             |      A      |             |             |             |
        |             +-------------+-------------+-------------+-------------+
        |    group    |             |      B      |             |             |
        |     is      |-------------+-------------+-------------+-------------+
        |    null     |             |             |      C      |             |
        |             +-------------+-------------+-------------+-------------+
        |             |             |             |             |      D      |
        +-------------+-------------+-------------+-------------+-------------+
        |             |      E      |             |             |             |
        |             +-------------+-------------+-------------+-------------+
        |    group    |             |             |             |             |
        |     is      |-------------+-------------+-------------+-------------+
        |  broadcast  |             |             |      F      |             |
        |             +-------------+-------------+-------------+-------------+
        |             |             |             |             |      G      |
        +-------------+-------------+-------------+-------------+-------------+
        |             |      H      |             |             |             |
        |             +-------------+-------------+-------------+-------------+
        |    group    |             |      J      |             |             |
        |     is      |-------------+-------------+-------------+-------------+
        |    normal   |             |             |      K      |             |
        |             +-------------+-------------+-------------+-------------+
        |             |             |             |             |             |
        +-------------+-------------+-------------+-------------+-------------+

    """

    @classmethod
    def destination_for_message(cls, msg: Message) -> ID:
        """ get destination for cipher key vector: (sender, destination) """
        receiver = msg.receiver
        group = ID.parse(identifier=msg.get('group'))
        return cls.get_destination(receiver=receiver, group=group)

    @classmethod
    def get_destination(cls, receiver: ID, group: Optional[ID]) -> ID:
        if group is None and receiver.is_group:
            # Transform:
            #     (B) => (J)
            #     (D) => (G)
            group = receiver
        # check group
        if group is None:
            # A : personal message (or hidden group message)
            # C : broadcast message for anyone
            assert receiver.is_user, 'receiver error: %s' % receiver
            return receiver
        assert group.is_group, 'group error: %s, receiver: %s' % (group, receiver)
        if group.is_broadcast:
            # E : unencrypted message for someone
            #     return group as broadcast ID for disable encryption
            # F : broadcast message for anyone
            # G : (receiver == group) broadcast group message
            assert receiver.is_user or receiver == group, 'receiver error: %s' % receiver
            return group
        elif receiver.is_broadcast:
            # K : unencrypted group message, usually group command
            #     return receiver as broadcast ID for disable encryption
            assert receiver.is_user, 'receiver error: %s, group: %s' % (receiver, group)
            return receiver
        else:
            # H    : group message split for someone
            # J    : (receiver == group) non-split group message
            return group

    @abstractmethod
    async def get_cipher_key(self, sender: ID, receiver: ID, generate: bool = False) -> Optional[SymmetricKey]:
        """
        Get cipher key for encrypt message from 'sender' to 'receiver'

        :param sender:   user or contact ID
        :param receiver: contact or user/group ID
        :param generate: generate when key not exists
        :return:         cipher key
        """
        raise NotImplemented

    @abstractmethod
    async def cache_cipher_key(self, key: SymmetricKey, sender: ID, receiver: ID):
        """
        Cache cipher key for reusing, with direction (from 'sender' to 'receiver')

        :param key:      cipher key from a contact
        :param sender:   user or contact ID
        :param receiver: contact or user/group ID
        """
        raise NotImplemented
