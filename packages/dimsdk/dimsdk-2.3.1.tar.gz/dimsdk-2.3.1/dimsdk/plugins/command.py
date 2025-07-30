# -*- coding: utf-8 -*-
#
#   DIMP : Decentralized Instant Messaging Protocol
#
#                                Written in 2022 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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

from dimp import Wrapper, Converter
from dimp import Command, CommandFactory

from dimp.plugins import GeneralCommandHelper, CommandHelper
from dimp.plugins import SharedMessageExtensions


class CommandGeneralFactory(GeneralCommandHelper, CommandHelper):

    def __init__(self):
        super().__init__()
        self.__command_factories: Dict[str, CommandFactory] = {}

    # Override
    def get_cmd(self, content: Dict, default: Optional[str]) -> Optional[str]:
        cmd = content.get('command')
        return Converter.get_str(value=cmd, default=default)

    #
    #   Command
    #

    # Override
    def set_command_factory(self, cmd: str, factory: CommandFactory):
        self.__command_factories[cmd] = factory

    # Override
    def get_command_factory(self, cmd: str) -> Optional[CommandFactory]:
        return self.__command_factories.get(cmd)

    # Override
    def parse_command(self, content: Any) -> Optional[Command]:
        if content is None:
            return None
        elif isinstance(content, Command):
            return content
        info = Wrapper.get_dict(content)
        if info is None:
            # assert False, 'command content error: %s' % content
            return None
        # get factory by command name
        cmd = self.get_cmd(content=info, default=None)
        # assert cmd is not None, 'command name not found: %s' % content
        factory = None if cmd is None else self.get_command_factory(cmd=cmd)
        if factory is None:
            # unknown command name, get base command factory
            factory = default_factory(info=info)
            if factory is None:
                # assert False, 'cannot parse command: %s' % content
                return None
        return factory.parse_command(content=info)


def default_factory(info: Dict[str, Any]) -> Optional[CommandFactory]:
    ext = SharedMessageExtensions()
    msg_type = ext.helper.get_content_type(content=info, default=None)
    # assert msg_type is not None, 'content type not found: %s' % info
    fact = None if msg_type is None else ext.content_helper.get_content_factory(msg_type)
    if isinstance(fact, CommandFactory):
        return fact
    # assert False, 'cannot parse command: %s' % info
