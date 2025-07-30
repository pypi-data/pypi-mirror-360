# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2020 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
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

from dimp import InstantMessage, SecureMessage, ReliableMessage

from .dkd import InstantMessageDelegate, SecureMessageDelegate, ReliableMessageDelegate
from .msg import InstantMessagePacker, SecureMessagePacker, ReliableMessagePacker
from .msg import MessageUtils
from .core import Packer
from .core import Archivist, Compressor

from .facebook import Facebook
from .messenger import Messenger
from .twins import TwinsHelper


class MessagePacker(TwinsHelper, Packer, ABC):

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__instant_packer = self._create_instant_message_packer(messenger=messenger)
        self.__secure_packer = self._create_secure_message_packer(messenger=messenger)
        self.__reliablePacker = self._create_reliable_message_packer(messenger=messenger)

    # noinspection PyMethodMayBeStatic
    def _create_instant_message_packer(self, messenger: InstantMessageDelegate):
        return InstantMessagePacker(messenger=messenger)

    # noinspection PyMethodMayBeStatic
    def _create_secure_message_packer(self, messenger: SecureMessageDelegate):
        return SecureMessagePacker(messenger=messenger)

    # noinspection PyMethodMayBeStatic
    def _create_reliable_message_packer(self, messenger: ReliableMessageDelegate):
        return ReliableMessagePacker(messenger=messenger)

    @property  # protected
    def instant_packer(self) -> InstantMessagePacker:
        return self.__instant_packer

    @property  # protected
    def secure_packer(self) -> SecureMessagePacker:
        return self.__secure_packer

    @property  # protected
    def reliable_packer(self) -> ReliableMessagePacker:
        return self.__reliablePacker

    @property  # protected
    @abstractmethod
    def compressor(self) -> Compressor:
        raise NotImplemented

    @property  # protected
    def archivist(self) -> Optional[Archivist]:
        facebook = self.facebook
        if facebook is not None:
            return facebook.archivist

    #
    #   InstantMessage -> SecureMessage -> ReliableMessage -> Data
    #

    # Override
    async def encrypt_message(self, msg: InstantMessage) -> Optional[SecureMessage]:
        # TODO: check receiver before calling this, make sure the visa.key exists;
        #       otherwise, suspend this message for waiting receiver's visa/meta;
        #       if receiver is a group, query all members' visa too!

        # NOTICE: before sending group message, you can decide whether expose the group ID
        #       (A) if you don't want to expose the group ID,
        #           you can split it to multi-messages before encrypting,
        #           replace the 'receiver' to each member and keep the group hidden in the content;
        #           in this situation, the packer will use the personal message key (user to user);
        #       (B) if the group ID is overt, no need to worry about the exposing,
        #           you can keep the 'receiver' being the group ID, or set the group ID as 'group'
        #           when splitting to multi-messages to let the remote packer knows it;
        #           in these situations, the local packer will use the group msg key (user to group)
        #           to encrypt the message, and the remote packer can get the overt group ID before
        #           decrypting to take the right message key.
        receiver = msg.receiver

        #
        #   1. get message key with direction (sender -> receiver) or (sender -> group)
        #
        password = await self.messenger.get_encrypt_key(msg=msg)
        assert password is not None, 'failed to get msg key: %s => %s, %s' % (msg.sender, receiver, msg.get('group'))

        #
        #   2. encrypt 'content' to 'data' for receiver/group members
        #
        if receiver.is_group:
            # group message
            members = await self.facebook.get_members(identifier=receiver)
            assert len(members) > 0, 'group not ready: %s' % receiver
            # a station will never send group message, so here must be a client;
            # the client messenger should check the group's meta & members before encrypting,
            # so we can trust that the group members MUST exist here.
            s_msg = await self.instant_packer.encrypt_message(msg=msg, password=password, members=members)
        else:
            # personal message (or split group message)
            s_msg = await self.instant_packer.encrypt_message(msg=msg, password=password)
        if s_msg is None:
            # public key for encryption not found
            # TODO: suspend this message for waiting receiver's meta
            # assert False, 'failed to encrypt message: %s' % msg
            return None

        # NOTICE: copy content type to envelope
        #         this help the intermediate nodes to recognize message type
        s_msg.envelope.type = msg.content.type

        # OK
        return s_msg

    # Override
    async def sign_message(self, msg: SecureMessage) -> ReliableMessage:
        assert len(msg.data) > 0, 'message data cannot be empty: %s' % msg
        # sign 'data' by sender
        return await self.secure_packer.sign_message(msg=msg)

    # Override
    async def serialize_message(self, msg: ReliableMessage) -> bytes:
        compressor = self.compressor
        return compressor.compress_reliable_message(msg=msg.dictionary)

    #
    #   Data -> ReliableMessage -> SecureMessage -> InstantMessage
    #

    # Override
    async def deserialize_message(self, data: bytes) -> Optional[ReliableMessage]:
        compressor = self.compressor
        info = compressor.extract_reliable_message(data=data)
        return ReliableMessage.parse(msg=info)

    async def _check_attachments(self, msg: ReliableMessage) -> bool:
        """ Check meta & visa """
        sender = msg.sender
        # [Meta Protocol]
        meta = MessageUtils.get_meta(msg=msg)
        if meta is not None:
            await self.archivist.save_meta(meta=meta, identifier=sender)
        # [Visa Protocol]
        visa = MessageUtils.get_visa(msg=msg)
        if visa is not None:
            await self.archivist.save_document(document=visa)
        #
        # NOTICE: check [Visa Protocol] before calling this
        #         make sure the sender's meta(visa) exists
        #         (do it by application)
        #
        return True

    # Override
    async def verify_message(self, msg: ReliableMessage) -> Optional[SecureMessage]:
        # make sure sender's meta exists before verifying message
        if not await self._check_attachments(msg=msg):
            return None
        assert len(msg.signature) > 0, 'message signature cannot be empty: %s' % msg
        # verify 'data' with 'signature'
        return await self.reliable_packer.verify_message(msg=msg)

    # Override
    async def decrypt_message(self, msg: SecureMessage) -> Optional[InstantMessage]:
        # TODO: check receiver before calling this, make sure you are the receiver,
        #       or you are a member of the group when this is a group message,
        #       so that you will have a private key (decrypt key) to decrypt it.
        receiver = msg.receiver
        me = await self.facebook.select_local_user(receiver=receiver)
        if me is None:
            # not for you?
            raise LookupError('receiver error: %s, from %s, %s' % (receiver, msg.sender, msg.group))
        assert len(msg.data) > 0, 'message data empty: %s => %s, %s' % (msg.sender, msg.receiver, msg.group)
        # decrypt 'data' to 'content'
        return await self.secure_packer.decrypt_message(msg=msg, receiver=me)
        # TODO: check top-secret message
        #       (do it by application)
