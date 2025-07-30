# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2024 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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

from dimp import *
from dimp.plugins import *

from ..dkd import GeneralCommandFactory, HistoryCommandFactory, GroupCommandFactory
from ..msg import MessageFactory

from .crypto import CryptographyKeyGeneralFactory
from .format import FormatGeneralFactory
from .account import AccountGeneralFactory
from .message import MessageGeneralFactory
from .command import CommandGeneralFactory


class ExtensionLoader:

    def __init__(self):
        super().__init__()
        self.__loaded = False

    def run(self):
        if self.__loaded:
            # no need to load it again
            return
        else:
            # mark it to loaded
            self.__loaded = True
        # try to load all extensions
        self._load()

    def _load(self):
        """ Register core factories """
        self._register_core_helpers()
        self._register_message_factories()
        self._register_content_factories()
        self._register_command_factories()

    def _register_core_helpers(self):
        """ Core extensions """
        self._register_crypto_helpers()
        self._register_format_helpers()
        self._register_account_helpers()
        self._register_message_helpers()
        self._register_command_helpers()

    # noinspection PyMethodMayBeStatic
    def _register_crypto_helpers(self):
        # crypto
        helper = CryptographyKeyGeneralFactory()
        ext = SharedCryptoExtensions()
        ext.symmetric_helper = helper
        ext.private_helper = helper
        ext.public_helper = helper
        ext.helper = helper

    # noinspection PyMethodMayBeStatic
    def _register_format_helpers(self):
        # format
        helper = FormatGeneralFactory()
        ext = SharedFormatExtensions()
        ext.pnf_helper = helper
        ext.ted_helper = helper
        ext.helper = helper

    # noinspection PyMethodMayBeStatic
    def _register_account_helpers(self):
        # mkm
        helper = AccountGeneralFactory()
        ext = SharedAccountExtensions()
        ext.address_helper = helper
        ext.id_helper = helper
        ext.meta_helper = helper
        ext.doc_helper = helper
        ext.helper = helper

    # noinspection PyMethodMayBeStatic
    def _register_message_helpers(self):
        # dkd
        helper = MessageGeneralFactory()
        ext = SharedMessageExtensions()
        ext.content_helper = helper
        ext.envelope_helper = helper
        ext.instant_helper = helper
        ext.secure_helper = helper
        ext.reliable_helper = helper
        ext.helper = helper

    # noinspection PyMethodMayBeStatic
    def _register_command_helpers(self):
        # cmd
        helper = CommandGeneralFactory()
        ext = SharedCommandExtensions()
        ext.cmd_helper = helper
        ext.helper = helper

    # noinspection PyMethodMayBeStatic
    def _register_message_factories(self):
        """ Message factories """
        factory = MessageFactory()
        # Envelope factory
        Envelope.set_factory(factory=factory)
        # Message factories
        InstantMessage.set_factory(factory=factory)
        SecureMessage.set_factory(factory=factory)
        ReliableMessage.set_factory(factory=factory)

    def _register_content_factories(self):
        """ Core content factories """
        # Text
        self._set_content_factory(msg_type=ContentType.TEXT, alias='text', content_class=BaseTextContent)

        # File
        self._set_content_factory(msg_type=ContentType.FILE, alias='file', content_class=BaseFileContent)
        # Image
        self._set_content_factory(msg_type=ContentType.IMAGE, alias='image', content_class=ImageFileContent)
        # Audio
        self._set_content_factory(msg_type=ContentType.AUDIO, alias='audio', content_class=AudioFileContent)
        # Video
        self._set_content_factory(msg_type=ContentType.VIDEO, alias='video', content_class=VideoFileContent)

        # Web Page
        self._set_content_factory(msg_type=ContentType.PAGE, alias='page', content_class=WebPageContent)

        # Name Card
        self._set_content_factory(msg_type=ContentType.NAME_CARD, alias='card', content_class=NameCardContent)

        # Quote
        self._set_content_factory(msg_type=ContentType.QUOTE, alias='quote', content_class=BaseQuoteContent)

        # Money
        self._set_content_factory(msg_type=ContentType.MONEY, alias='money', content_class=BaseMoneyContent)
        self._set_content_factory(msg_type=ContentType.TRANSFER, alias='transfer', content_class=TransferMoneyContent)
        # ...

        # Command
        self._set_content_factory(msg_type=ContentType.COMMAND, alias='command', factory=GeneralCommandFactory())

        # History Command
        self._set_content_factory(msg_type=ContentType.HISTORY, alias='history', factory=HistoryCommandFactory())

        # Content Array
        self._set_content_factory(msg_type=ContentType.ARRAY, alias='array', content_class=ListContent)

        # Combine and Forward
        self._set_content_factory(ContentType.COMBINE_FORWARD, alias='combine', content_class=CombineForwardContent)

        # Top-Secret
        self._set_content_factory(msg_type=ContentType.FORWARD, alias='forward', content_class=SecretContent)

        # Unknown Content Type
        self._set_content_factory(msg_type=ContentType.ANY, alias='*', content_class=BaseContent)

    # noinspection PyMethodMayBeStatic
    def _set_content_factory(self, msg_type: str, alias: str,
                             content_class=None, factory: ContentFactory = None):
        if factory is not None:
            Content.set_factory(msg_type, factory=factory)
            Content.set_factory(alias, factory=factory)
        if content_class is not None:
            factory = ContentParser(content_class=content_class)
            Content.set_factory(msg_type, factory=factory)
            Content.set_factory(alias, factory=factory)

    def _register_command_factories(self):
        """ Core command factories """
        # Meta Command
        self._set_command_factory(cmd=Command.META, command_class=BaseMetaCommand)

        # Document Command
        self._set_command_factory(cmd=Command.DOCUMENTS, command_class=BaseDocumentCommand)

        # Receipt Command
        self._set_command_factory(cmd=Command.RECEIPT, command_class=BaseReceiptCommand)

        # Group Commands
        self._set_command_factory(cmd='group', factory=GroupCommandFactory())
        self._set_command_factory(cmd=GroupCommand.INVITE, command_class=InviteGroupCommand)
        # 'expel' is deprecated (use 'reset' instead)
        self._set_command_factory(cmd=GroupCommand.EXPEL, command_class=ExpelGroupCommand)
        self._set_command_factory(cmd=GroupCommand.JOIN, command_class=JoinGroupCommand)
        self._set_command_factory(cmd=GroupCommand.QUIT, command_class=QuitGroupCommand)
        self._set_command_factory(cmd=GroupCommand.QUERY, command_class=QueryGroupCommand)
        self._set_command_factory(cmd=GroupCommand.RESET, command_class=ResetGroupCommand)
        # Group Admin Commands
        self._set_command_factory(cmd=GroupCommand.HIRE, command_class=HireGroupCommand)
        self._set_command_factory(cmd=GroupCommand.FIRE, command_class=FireGroupCommand)
        self._set_command_factory(cmd=GroupCommand.RESIGN, command_class=ResignGroupCommand)

    # noinspection PyMethodMayBeStatic
    def _set_command_factory(self, cmd: str,
                             command_class=None, factory: CommandFactory = None):
        if factory is not None:
            Command.set_factory(cmd=cmd, factory=factory)
        if command_class is not None:
            factory = CommandParser(command_class=command_class)
            Command.set_factory(cmd=cmd, factory=factory)


class ContentParser(ContentFactory):

    def __init__(self, content_class):
        super().__init__()
        self.__class = content_class

    # Override
    def parse_content(self, content: Dict[str, Any]) -> Optional[Content]:
        # return self.__class(content=content)
        return self.__class(content)


class CommandParser(CommandFactory):

    def __init__(self, command_class):
        super().__init__()
        self.__class = command_class

    # Override
    def parse_command(self, content: Dict[str, Any]) -> Optional[Command]:
        # return self.__class(content=content)
        return self.__class(content)
