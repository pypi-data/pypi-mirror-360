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

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import EntityType
from dimp import VerifyKey, EncryptKey
from dimp import ID, Meta, Document

from ..mkm import User, BaseUser
from ..mkm import Group, BaseGroup
from ..mkm import Station, Bot, ServiceProvider


class Barrack(ABC):
    """
        Entity Factory
        ~~~~~~~~~~~~~~
        Entity pool to manage User/Group instances
    """

    @abstractmethod
    def cache_user(self, user: User):
        raise NotImplemented

    @abstractmethod
    def cache_group(self, group: Group):
        raise NotImplemented

    @abstractmethod
    def get_user(self, identifier: ID) -> Optional[User]:
        raise NotImplemented

    @abstractmethod
    def get_group(self, identifier: ID) -> Optional[Group]:
        raise NotImplemented

    # noinspection PyMethodMayBeStatic
    def create_user(self, identifier: ID) -> Optional[User]:
        """
        Create user when visa.key exists

        :param identifier: user ID
        :return: user, None on not ready
        """
        assert identifier.is_user, 'user ID error: %s' % identifier
        network = identifier.type
        # check user type
        if network == EntityType.STATION:
            return Station(identifier=identifier)
        elif network == EntityType.BOT:
            return Bot(identifier=identifier)
        # general user, or 'anyone@anywhere'
        return BaseUser(identifier=identifier)

    # noinspection PyMethodMayBeStatic
    def create_group(self, identifier: ID) -> Optional[Group]:
        """
        Create group when members exist

        :param identifier: group ID
        :return: group, None on not ready
        """
        assert identifier.is_group, 'group ID error: %s' % identifier
        network = identifier.type
        # check group type
        if network == EntityType.ISP:
            return ServiceProvider(identifier=identifier)
        # general group, or 'everyone@everywhere'
        return BaseGroup(identifier=identifier)


class Archivist(ABC):

    @abstractmethod
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        """
        Save meta for entity ID (must verify first)

        :param meta:       entity meta
        :param identifier: entity ID
        :return: True on success
        """
        raise NotImplemented

    @abstractmethod
    async def save_document(self, document: Document) -> bool:
        """
        Save entity document with ID (must verify first)

        :param document: entity document
        :return: True on success
        """
        raise NotImplemented

    #
    #   Public Keys
    #

    @abstractmethod
    async def get_meta_key(self, identifier: ID) -> Optional[VerifyKey]:
        """
        Get meta.key

        :param identifier: user ID
        :return: None on not found
        """
        raise NotImplemented

    @abstractmethod
    async def get_visa_key(self, identifier: ID) -> Optional[EncryptKey]:
        """
        Get visa.key

        :param identifier: user ID
        :return: None on not found
        """
        raise NotImplemented

    #
    #   Local Users
    #

    @property
    @abstractmethod
    async def local_users(self) -> List[ID]:
        """
        Get all local users (for decrypting received message)

        :return: users with private key
        """
        raise NotImplemented
