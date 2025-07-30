# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
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
from typing import Optional, Iterable, Any, List, Dict

from mkm.types import DateTime
from mkm.types import Mapper
from mkm import ID

from .helpers import MessageExtensions


class Content(Mapper, ABC):
    """This class is for creating message content

        Message Content
        ~~~~~~~~~~~~~~~

        data format: {
            'type'    : i2s(0),         // message type
            'sn'      : 0,              // serial number

            'time'    : 123,            // message time
            'group'   : 'Group ID',     // for group message

            //-- message info
            'text'    : 'text',         // for text message
            'command' : 'Command Name'  // for system command
            //...
        }
    """

    @property
    @abstractmethod
    def type(self) -> str:
        """ content type """
        raise NotImplemented

    @property
    @abstractmethod
    def sn(self) -> int:
        """ serial number as message id """
        raise NotImplemented

    @property
    @abstractmethod
    def time(self) -> Optional[DateTime]:
        """ message time """
        raise NotImplemented

    @property
    @abstractmethod
    def group(self) -> Optional[ID]:
        """
            Group ID/string for group message
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if field 'group' exists, it means this is a group message
        """
        raise NotImplemented

    @group.setter
    @abstractmethod
    def group(self, value: ID):
        raise NotImplemented

    #
    #   Conveniences
    #

    @classmethod
    def convert(cls, array: Iterable):  # -> List[Content]:
        contents = []
        for item in array:
            msg = cls.parse(content=item)
            if msg is None:
                # content error
                continue
            contents.append(msg)
        return contents

    @classmethod
    def revert(cls, contents: Iterable) -> List[Dict]:
        array = []
        for msg in contents:
            assert isinstance(msg, Content), 'content error: %s' % msg
            array.append(msg.dictionary)
        return array

    #
    #   Factory method
    #

    @classmethod
    def parse(cls, content: Any):  # -> Optional[Content]:
        helper = content_helper()
        return helper.parse_content(content=content)

    @classmethod
    def get_factory(cls, msg_type: str):  # -> Optional[ContentFactory]:
        helper = content_helper()
        return helper.get_content_factory(msg_type)

    @classmethod
    def set_factory(cls, msg_type: str, factory):
        helper = content_helper()
        helper.set_content_factory(msg_type, factory=factory)


def content_helper():
    helper = MessageExtensions.content_helper
    assert isinstance(helper, ContentHelper), 'content helper error: %s' % helper
    return helper


class ContentFactory(ABC):
    """ Content Factory """

    @abstractmethod
    def parse_content(self, content: Dict[str, Any]) -> Optional[Content]:
        """
        Parse map object to content

        :param content: content info
        :return: Content
        """
        raise NotImplemented


class ContentHelper(ABC):
    """ General Helper """

    @abstractmethod
    def set_content_factory(self, msg_type: str, factory: ContentFactory):
        raise NotImplemented

    @abstractmethod
    def get_content_factory(self, msg_type: str) -> Optional[ContentFactory]:
        raise NotImplemented

    @abstractmethod
    def parse_content(self, content: Any) -> Optional[Content]:
        raise NotImplemented
