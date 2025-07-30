# Decentralized Instant Messaging (Python SDK)

[![License](https://img.shields.io/github/license/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dimchat/sdk-py/pulls)
[![Platform](https://img.shields.io/badge/Platform-Python%203-brightgreen.svg)](https://github.com/dimchat/sdk-py/wiki)
[![Issues](https://img.shields.io/github/issues/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/issues)
[![Repo Size](https://img.shields.io/github/repo-size/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/archive/refs/heads/main.zip)
[![Tags](https://img.shields.io/github/tag/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/tags)
[![Version](https://img.shields.io/pypi/v/dimsdk)](https://pypi.org/project/dimsdk)

[![Watchers](https://img.shields.io/github/watchers/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/watchers)
[![Forks](https://img.shields.io/github/forks/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/forks)
[![Stars](https://img.shields.io/github/stars/dimchat/sdk-py)](https://github.com/dimchat/sdk-py/stargazers)
[![Followers](https://img.shields.io/github/followers/dimchat)](https://github.com/orgs/dimchat/followers)

## Dependencies

* Latest Versions

| Name | Version | Description |
|------|---------|-------------|
| [Ming Ke Ming (名可名)](https://github.com/dimchat/mkm-py) | [![Version](https://img.shields.io/pypi/v/mkm)](https://pypi.org/project/mkm) | Decentralized User Identity Authentication |
| [Dao Ke Dao (道可道)](https://github.com/dimchat/dkd-py) | [![Version](https://img.shields.io/pypi/v/dkd)](https://pypi.org/project/dkd) | Universal Message Module |
| [DIMP (去中心化通讯协议)](https://github.com/dimchat/core-py) | [![Version](https://img.shields.io/pypi/v/dimp)](https://pypi.org/project/dimp) | Decentralized Instant Messaging Protocol |

## Extensions

### 1. extends Content

extends [CustomizedContent](https://github.com/dimchat/core-py#extends-content)

### 2. extends ContentProcessor

```python
from abc import ABC, abstractmethod
from typing import Optional, List

from dimsdk import ID
from dimsdk import ReliableMessage
from dimsdk import Content
from dimsdk.cpu import BaseContentProcessor

from ...common import CustomizedContent


class CustomizedContentHandler(ABC):
    """
        Handler for Customized Content
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    async def handle_action(self, act: str, sender: ID,
                            content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        """
        Do your job

        @param act:     action
        @param sender:  user ID
        @param content: customized content
        @param msg:     network message
        @return contents
        """
        raise NotImplemented


class CustomizedContentProcessor(BaseContentProcessor, CustomizedContentHandler):
    """
        Customized Content Processing Unit
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, CustomizedContent), 'customized content error: %s' % content
        # 1. check app id
        app = content.application
        responses = self._filter(app, content=content, msg=r_msg)
        if responses is not None:
            # app id not found
            return responses
        # 2. get handler with module name
        mod = content.module
        handler = self._fetch(mod, content=content, msg=r_msg)
        if handler is None:
            # module not support
            return []
        # 3. do the job
        act = content.action
        sender = r_msg.sender
        return await handler.handle_action(act, sender=sender, content=content, msg=r_msg)

    def _filter(self, app: str, content: CustomizedContent, msg: ReliableMessage) -> Optional[List[Content]]:
        # Override for your application
        """
        Check for application

        :param app:     app ID
        :param content: customized content
        :param msg:     received message
        :return: None on app ID matched
        """
        text = 'Content not support.'
        return self._respond_receipt(text=text, content=content, envelope=msg.envelope, extra={
            'template': 'Customized content (app: ${app}) not support yet!',
            'replacements': {
                'app': app,
            }
        })

    def _fetch(self, mod: str, content: CustomizedContent, msg: ReliableMessage) -> Optional[CustomizedContentHandler]:
        """ Override for you module """
        # if the application has too many modules, I suggest you to
        # use different handler to do the job for each module.
        return self

    # Override
    async def handle_action(self, act: str, sender: ID,
                            content: CustomizedContent, msg: ReliableMessage) -> List[Content]:
        """ Override for customized actions """
        app = content.application
        mod = content.module
        text = 'Content not support.'
        return self._respond_receipt(text=text, content=content, envelope=msg.envelope, extra={
            'template': 'Customized content (app: ${app}, mod: ${mod}, act: ${act}) not support yet!',
            'replacements': {
                'app': app,
                'mod': mod,
                'act': act,
            }
        })
```

### 3. extends ExtensionLoader

```python
from dimsdk import ContentType
from dimsdk.plugins import ExtensionLoader

from ..protocol import HandshakeCommand
from ..protocol import AppCustomizedContent


class CommonLoader(ExtensionLoader):

    def _register_customized_factories(self):
        # Application Customized
        self._set_content_factory(msg_type=ContentType.APPLICATION, content_class=AppCustomizedContent)
        self._set_content_factory(msg_type=ContentType.CUSTOMIZED, content_class=AppCustomizedContent)

    # Override
    def _register_content_factories(self):
        super()._register_content_factories()
        self._register_customized_factories()

    # Override
    def _register_command_factories(self):
        super()._register_command_factories()
        # Handshake
        self._set_command_factory(cmd=HandshakeCommand.HANDSHAKE, command_class=HandshakeCommand)
```

## Usages

You must load all extensions before your business run:

```python
from ..common import CommonLoader


if __name__ == '__main__':
  loader = CommonLoader()
  loader.run()
  # do your jobs after all extensions loaded.
```

Also, to let your **CustomizedContentProcessor** start to work,
you must override ```BaseContentProcessorCreator``` for message types:

1. ContentType.APPLICATION 
2. ContentType.CUSTOMIZED

and then set your **creator** for ```GeneralContentProcessorFactory``` in the ```MessageProcessor```.

----

Copyright &copy; 2018 Albert Moky
[![Followers](https://img.shields.io/github/followers/moky)](https://github.com/moky?tab=followers)
