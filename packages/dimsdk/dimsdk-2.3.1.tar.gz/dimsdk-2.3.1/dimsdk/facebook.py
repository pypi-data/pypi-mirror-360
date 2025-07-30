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

"""
    Facebook
    ~~~~~~~~

    Barrack for cache entities
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from dimp import EncryptKey, VerifyKey
from dimp import ID

from .core import Barrack, Archivist
from .mkm import EntityDelegate, User, Group
from .mkm import UserDataSource, GroupDataSource


class Facebook(EntityDelegate, UserDataSource, GroupDataSource, ABC):

    @property
    @abstractmethod
    def barrack(self) -> Optional[Barrack]:
        raise NotImplemented

    @property
    @abstractmethod
    def archivist(self) -> Optional[Archivist]:
        raise NotImplemented

    async def select_local_user(self, receiver: ID) -> Optional[ID]:
        """
        Select local user for receiver

        :param receiver: user/group ID
        :return: local user
        """
        archivist = self.archivist
        assert archivist is not None, 'archivist not ready'
        users = await archivist.local_users
        #
        #  1.
        #
        if users is None or len(users) == 0:
            assert False, 'local users should not be empty'
            # return None
        elif receiver.is_broadcast:
            # broadcast message can decrypt by anyone, so
            # just return current user
            return users[0]
        #
        #  2.
        #
        if receiver.is_user:
            # personal message
            for item in users:
                if receiver == item:
                    # DISCUSS: set this item to be current user?
                    return item
        elif receiver.is_group:
            # split group message
            #
            # the messenger will check group info before decrypting message,
            # so we can trust that the group's meta & members MUST exist here.
            members = await self.get_members(identifier=receiver)
            if members is None or len(members) == 0:
                # assert False, 'members not found: %s' % receiver
                return None
            for item in users:
                if item in members:
                    # DISCUSS: set this item to be current user?
                    return item
        else:
            assert False, 'receiver error: %s' % receiver
        # not me?
        return None

    #
    #   Entity Delegate
    #

    # Override
    async def get_user(self, identifier: ID) -> Optional[User]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        barrack = self.barrack
        assert barrack is not None, 'barrack not ready'
        #
        #  1. get from user cache
        #
        user = barrack.get_user(identifier=identifier)
        if user is not None:
            return user
        #
        #  2. check visa key
        #
        if not identifier.is_broadcast:
            visa_key = await self.public_key_for_encryption(identifier=identifier)
            if visa_key is None:
                # assert False, 'visa.key not found: %s' % identifier
                return None
            # NOTICE: if visa.key exists, then visa & meta must exist too.
        #
        #  3. create user and cache it
        #
        user = barrack.create_user(identifier=identifier)
        if user is not None:
            barrack.cache_user(user=user)
        return user

    # Override
    async def get_group(self, identifier: ID) -> Optional[Group]:
        assert identifier.is_group, 'group ID error: %s' % identifier
        barrack = self.barrack
        assert barrack is not None, 'barrack not ready'
        #
        #  1. get from group cache
        #
        group = barrack.get_group(identifier=identifier)
        if group is not None:
            return group
        #
        #  2. check members
        #
        if not identifier.is_broadcast:
            members = await self.get_members(identifier=identifier)
            if members is None or len(members) == 0:
                # assert False, 'group members not found: %s' % identifier
                return None
            # NOTICE: if members exist, then owner (founder) must exist,
            #         and bulletin & meta must exist too.
        #
        #  3. create group and cache it
        #
        group = barrack.create_group(identifier=identifier)
        if group is not None:
            barrack.cache_group(group=group)
        return group

    #
    #   User DataSource
    #

    # Override
    async def public_key_for_encryption(self, identifier: ID) -> Optional[EncryptKey]:
        assert identifier.is_user, 'user ID error: %s' % identifier
        archivist = self.archivist
        assert archivist is not None, 'archivist not ready'
        #
        #  1. get key from visa
        #
        visa_key = await archivist.get_visa_key(identifier=identifier)
        if visa_key is not None:
            # if visa.key exists, use it for encryption
            return visa_key
        #
        #  2. get key from meta
        #
        meta_key = await archivist.get_meta_key(identifier=identifier)
        if isinstance(meta_key, EncryptKey):
            # if visa.key not exists and meta.key is encrypt key,
            # use it for encryption
            return meta_key

    # Override
    async def public_keys_for_verification(self, identifier: ID) -> List[VerifyKey]:
        # assert identifier.is_user, 'user ID error: %s' % identifier
        archivist = self.archivist
        assert archivist is not None, 'archivist not ready'
        keys: List[VerifyKey] = []
        #
        #  1. get key from visa
        #
        visa_key = await archivist.get_visa_key(identifier=identifier)
        if isinstance(visa_key, VerifyKey):
            # the sender may use communication key to sign message.data,
            # so try to verify it with visa.key first
            keys.append(visa_key)
        #
        #  2. get key from meta
        #
        meta_key = await archivist.get_meta_key(identifier=identifier)
        if meta_key is not None:
            # the sender may use identity key to sign message.data,
            # try to verify it with meta.key too
            keys.append(meta_key)
        assert len(keys) > 0, 'failed to get verify key for user: %s' % identifier
        return keys
