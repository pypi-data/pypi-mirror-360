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

from .content import Content
from .envelope import Envelope
from .message import Message
from .helpers import MessageExtensions


class InstantMessage(Message, ABC):
    """
        Instant Message
        ~~~~~~~~~~~~~~~

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content
            content  : {...}
        }
    """

    @property
    @abstractmethod
    def content(self) -> Content:
        """ message content """
        raise NotImplemented

    # @content.setter
    # def content(self, value: Content):
    #     """ only for rebuild content """
    #     raise NotImplemented

    #
    #   Conveniences
    #

    @classmethod
    def convert(cls, array: Iterable):  # -> List[InstantMessage]:
        messages = []
        for item in array:
            msg = cls.parse(msg=item)
            if msg is None:
                # message error
                continue
            messages.append(msg)
        return messages

    @classmethod
    def revert(cls, messages: Iterable) -> List[Dict]:
        array = []
        for msg in messages:
            assert isinstance(msg, InstantMessage), 'message error: %s' % msg
            array.append(msg.dictionary)
        return array

    #
    #   Factory methods
    #

    @classmethod
    def create(cls, head: Envelope, body: Content):  # -> InstantMessage:
        helper = instant_helper()
        return helper.create_instant_message(head=head, body=body)

    @classmethod
    def parse(cls, msg: Any):  # -> Optional[InstantMessage]:
        helper = instant_helper()
        return helper.parse_instant_message(msg=msg)

    @classmethod
    def generate_serial_number(cls, msg_type: Optional[str], now: Optional[DateTime]) -> int:
        helper = instant_helper()
        return helper.generate_serial_number(msg_type, now)

    @classmethod
    def get_factory(cls):  # -> Optional[InstantMessageFactory]:
        helper = instant_helper()
        return helper.get_instant_message_factory()

    @classmethod
    def set_factory(cls, factory):
        helper = instant_helper()
        return helper.set_instant_message_factory(factory=factory)


def instant_helper():
    helper = MessageExtensions.instant_helper
    assert isinstance(helper, InstantMessageHelper), 'message helper error: %s' % helper
    return helper


class InstantMessageFactory(ABC):
    """ Instant Message Factory """

    @abstractmethod
    def generate_serial_number(self, msg_type: Optional[str], now: Optional[DateTime]) -> int:
        """
        Generate SN for message content

        :param msg_type: content type
        :param now:      message time
        :return: SN (uint64, serial number as msg id)
        """
        raise NotImplemented

    @abstractmethod
    def create_instant_message(self, head: Envelope, body: Content) -> InstantMessage:
        """
        Create instant message with envelope & content

        :param head: message envelope
        :param body: message content
        :return: InstantMessage
        """
        raise NotImplemented

    @abstractmethod
    def parse_instant_message(self, msg: Dict[str, Any]) -> Optional[InstantMessage]:
        """
        Parse map object to message

        :param msg: message info
        :return: InstantMessage
        """
        raise NotImplemented


class InstantMessageHelper(ABC):
    """ General Helper """

    @abstractmethod
    def set_instant_message_factory(self, factory: InstantMessageFactory):
        raise NotImplemented

    @abstractmethod
    def get_instant_message_factory(self) -> Optional[InstantMessageFactory]:
        raise NotImplemented

    @abstractmethod
    def generate_serial_number(self, msg_type: Optional[str], now: Optional[DateTime]) -> int:
        raise NotImplemented

    @abstractmethod
    def create_instant_message(self, head: Envelope, body: Content) -> InstantMessage:
        raise NotImplemented

    @abstractmethod
    def parse_instant_message(self, msg: Any) -> Optional[InstantMessage]:
        raise NotImplemented
