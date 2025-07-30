# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
#
#                                Written in 2021 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2021 Albert Moky
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

from typing import Optional, Any, Dict

from dimp import DateTime, Converter, Wrapper
from dimp import ID
from dimp import Content, ContentFactory
from dimp import Envelope, EnvelopeFactory
from dimp import InstantMessage, InstantMessageFactory
from dimp import SecureMessage, SecureMessageFactory
from dimp import ReliableMessage, ReliableMessageFactory

from dimp.plugins import GeneralMessageHelper
from dimp.plugins import ContentHelper
from dimp.plugins import EnvelopeHelper
from dimp.plugins import InstantMessageHelper
from dimp.plugins import SecureMessageHelper
from dimp.plugins import ReliableMessageHelper


class MessageGeneralFactory(GeneralMessageHelper, ContentHelper, EnvelopeHelper,
                            InstantMessageHelper, SecureMessageHelper, ReliableMessageHelper):

    def __init__(self):
        super().__init__()
        # int(msg_type) -> content factory
        self.__content_factories: Dict[str, ContentFactory] = {}
        # envelope factory
        self.__envelope_factory: Optional[EnvelopeFactory] = None
        # message factories
        self.__instant_message_factory: Optional[InstantMessageFactory] = None
        self.__secure_message_factory: Optional[SecureMessageFactory] = None
        self.__reliable_message_factory: Optional[ReliableMessageFactory] = None

    # Override
    def get_content_type(self, content: Dict, default: Optional[str]) -> Optional[str]:
        value = content.get('type')
        return Converter.get_str(value=value, default=default)

    #
    #   Content
    #

    # Override
    def set_content_factory(self, msg_type: str, factory: ContentFactory):
        self.__content_factories[msg_type] = factory

    # Override
    def get_content_factory(self, msg_type: str) -> Optional[ContentFactory]:
        return self.__content_factories.get(msg_type)

    # Override
    def parse_content(self, content: Any) -> Optional[Content]:
        if content is None:
            return None
        elif isinstance(content, Content):
            return content
        info = Wrapper.get_dict(content)
        if info is None:
            # assert False, 'message content error: %s' % content
            return None
        # get factory by content type
        msg_type = self.get_content_type(content=info, default=None)
        # assert msg_type is not None, 'content error: %s' % content
        factory = None if msg_type is None else self.get_content_factory(msg_type)
        if factory is None:
            # unknown content type, get default content factory
            factory = self.get_content_factory('*')  # unknown
            if factory is None:
                # assert False, 'default content factory not found: %s' % content
                return None
        return factory.parse_content(content=info)

    #
    #   Envelope
    #

    # Override
    def set_envelope_factory(self, factory: EnvelopeFactory):
        self.__envelope_factory = factory

    # Override
    def get_envelope_factory(self) -> Optional[EnvelopeFactory]:
        return self.__envelope_factory

    # Override
    def create_envelope(self, sender: ID, receiver: ID, time: Optional[DateTime]) -> Envelope:
        factory = self.get_envelope_factory()
        assert factory is not None, 'envelope factory not ready'
        return factory.create_envelope(sender=sender, receiver=receiver, time=time)

    # Override
    def parse_envelope(self, envelope: Any) -> Optional[Envelope]:
        if envelope is None:
            return None
        elif isinstance(envelope, Envelope):
            return envelope
        info = Wrapper.get_dict(envelope)
        if info is None:
            # assert False, 'message envelope error: %s' % envelope
            return None
        factory = self.get_envelope_factory()
        assert factory is not None, 'envelope factory not ready'
        return factory.parse_envelope(envelope=info)

    #
    #   InstantMessage
    #

    # Override
    def set_instant_message_factory(self, factory: InstantMessageFactory):
        self.__instant_message_factory = factory

    # Override
    def get_instant_message_factory(self) -> Optional[InstantMessageFactory]:
        return self.__instant_message_factory

    # Override
    def create_instant_message(self, head: Envelope, body: Content) -> InstantMessage:
        factory = self.get_instant_message_factory()
        assert factory is not None, 'instant message factory not ready'
        return factory.create_instant_message(head=head, body=body)

    # Override
    def parse_instant_message(self, msg: Any) -> Optional[InstantMessage]:
        if msg is None:
            return None
        elif isinstance(msg, InstantMessage):
            return msg
        info = Wrapper.get_dict(msg)
        if info is None:
            # assert False, 'instant message error: %s' % msg
            return None
        factory = self.get_instant_message_factory()
        assert factory is not None, 'instant message factory not ready'
        return factory.parse_instant_message(msg=info)

    # Override
    def generate_serial_number(self, msg_type: Optional[str], now: Optional[DateTime]) -> int:
        factory = self.get_instant_message_factory()
        assert factory is not None, 'instant message factory not ready'
        return factory.generate_serial_number(msg_type, now)

    #
    #   SecureMessage
    #

    # Override
    def set_secure_message_factory(self, factory: SecureMessageFactory):
        self.__secure_message_factory = factory

    # Override
    def get_secure_message_factory(self) -> Optional[SecureMessageFactory]:
        return self.__secure_message_factory

    # Override
    def parse_secure_message(self, msg: Any) -> Optional[SecureMessage]:
        if msg is None:
            return None
        elif isinstance(msg, SecureMessage):
            return msg
        info = Wrapper.get_dict(msg)
        if info is None:
            # assert False, 'secure message error: %s' % msg
            return None
        factory = self.get_secure_message_factory()
        assert factory is not None, 'secure message factory not ready'
        return factory.parse_secure_message(msg=info)

    #
    #   ReliableMessage
    #

    # Override
    def set_reliable_message_factory(self, factory: ReliableMessageFactory):
        self.__reliable_message_factory = factory

    # Override
    def get_reliable_message_factory(self) -> Optional[ReliableMessageFactory]:
        return self.__reliable_message_factory

    # Override
    def parse_reliable_message(self, msg: Any) -> Optional[ReliableMessage]:
        if msg is None:
            return None
        elif isinstance(msg, ReliableMessage):
            return msg
        info = Wrapper.get_dict(msg)
        if info is None:
            # assert False, 'reliable message error: %s' % msg
            return None
        factory = self.get_reliable_message_factory()
        assert factory is not None, 'reliable message factory not ready'
        return factory.parse_reliable_message(msg=info)
