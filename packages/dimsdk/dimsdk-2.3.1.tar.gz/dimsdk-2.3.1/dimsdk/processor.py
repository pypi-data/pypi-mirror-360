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

from abc import abstractmethod
from typing import List

from dimp import ContentType
from dimp import Content, Envelope
from dimp import InstantMessage, SecureMessage, ReliableMessage

from .dkd import ContentProcessorFactory
from .core import Processor

from .facebook import Facebook
from .messenger import Messenger
from .twins import TwinsHelper


class MessageProcessor(TwinsHelper, Processor):

    def __init__(self, facebook: Facebook, messenger: Messenger):
        super().__init__(facebook=facebook, messenger=messenger)
        self.__factory = self._create_factory(facebook=facebook, messenger=messenger)

    @property  # private
    def factory(self) -> ContentProcessorFactory:
        """ CPU Factory """
        return self.__factory

    @abstractmethod  # protected
    def _create_factory(self, facebook: Facebook, messenger: Messenger) -> ContentProcessorFactory:
        raise NotImplemented

    #
    #  Processing Message
    #

    # Override
    async def process_package(self, data: bytes) -> List[bytes]:
        messenger = self.messenger
        # 1. deserialize message
        msg = await messenger.deserialize_message(data=data)
        if msg is None:
            # no valid message received
            return []
        # 2. process message
        responses = await messenger.process_reliable_message(msg=msg)
        if len(responses) == 0:
            # nothing to respond
            return []
        # 3. serialize messages
        packages = []
        for res in responses:
            pack = await messenger.serialize_message(msg=res)
            if pack is None:
                # should not happen
                continue
            packages.append(pack)
        return packages

    # Override
    async def process_reliable_message(self, msg: ReliableMessage) -> List[ReliableMessage]:
        # TODO: override to check broadcast message before calling it
        messenger = self.messenger
        # 1. verify message
        s_msg = await messenger.verify_message(msg=msg)
        if s_msg is None:
            # TODO: suspend and waiting for sender's meta if not exists
            return []
        # 2. process message
        responses = await messenger.process_secure_message(msg=s_msg, r_msg=msg)
        if len(responses) == 0:
            # nothing to respond
            return []
        # 3. sign message
        messages = []
        for res in responses:
            signed = await messenger.sign_message(msg=res)
            if signed is None:
                # should not happen
                continue
            messages.append(signed)
        return messages
        # TODO: override to deliver to the receiver when catch exception "receiver error ..."

    # Override
    async def process_secure_message(self, msg: SecureMessage, r_msg: ReliableMessage) -> List[SecureMessage]:
        messenger = self.messenger
        # 1. decrypt message
        i_msg = await messenger.decrypt_message(msg=msg)
        if i_msg is None:
            # cannot decrypt this message, not for you?
            # delivering message to other receiver?
            return []
        # 2. process message
        responses = await messenger.process_instant_message(msg=i_msg, r_msg=r_msg)
        if len(responses) == 0:
            # nothing to respond
            return []
        # 3. encrypt messages
        messages = []
        for res in responses:
            encrypted = await messenger.encrypt_message(msg=res)
            if encrypted is None:
                # should not happen
                continue
            messages.append(encrypted)
        return messages

    # Override
    async def process_instant_message(self, msg: InstantMessage, r_msg: ReliableMessage) -> List[InstantMessage]:
        messenger = self.messenger
        # 1. process content from sender
        responses = await messenger.process_content(content=msg.content, r_msg=r_msg)
        if len(responses) == 0:
            # nothing to respond
            return []
        # 2. select a local user to build message
        sender = msg.sender
        receiver = msg.receiver
        facebook = self.facebook
        me = await facebook.select_local_user(receiver=receiver)
        if me is None:
            # assert False, 'receiver error: %s' % receiver
            return []
        # 3. package messages
        messages = []
        for res in responses:
            assert res is not None, 'should not happen'
            env = Envelope.create(sender=me, receiver=sender)
            msg = InstantMessage.create(head=env, body=res)
            assert msg is not None, 'should not happen'
            messages.append(msg)
        return messages

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        factory = self.factory
        # TODO: override to check group
        cpu = factory.get_content_processor(content=content)
        if cpu is None:
            # default content processor
            cpu = factory.get_content_processor_for_type(ContentType.ANY)
            assert cpu is not None, 'default CPU not defined'
        return await cpu.process_content(content=content, r_msg=r_msg)
        # TODO: override to filter the response
