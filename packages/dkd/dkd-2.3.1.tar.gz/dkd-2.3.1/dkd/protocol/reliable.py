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

from .secure import SecureMessage
from .helpers import MessageExtensions


class ReliableMessage(SecureMessage, ABC):
    """ This class is used to sign the SecureMessage
        It contains a 'signature' field which signed with sender's private key

        Instant Message signed by an asymmetric key
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content data and key/keys
            data     : "...",  // base64_encode( symmetric_encrypt(content))
            key      : "...",  // base64_encode(asymmetric_encrypt(password))
            keys     : {
                "ID1": "key1", // base64_encode(asymmetric_encrypt(password))
            },
            //-- signature
            signature: "..."   // base64_encode(asymmetric_sign(data))
        }
    """

    @property
    @abstractmethod
    def signature(self) -> bytes:
        """ signature for encrypted data of message content """
        raise NotImplemented

    #
    #   Conveniences
    #

    @classmethod
    def convert(cls, array: Iterable):  # -> List[ReliableMessage]:
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
            assert isinstance(msg, ReliableMessage), 'message error: %s' % msg
            array.append(msg.dictionary)
        return array

    #
    #   Factory methods
    #

    @classmethod
    def parse(cls, msg: Any):  # -> Optional[ReliableMessage]:
        helper = reliable_helper()
        return helper.parse_reliable_message(msg=msg)

    @classmethod
    def get_factory(cls):  # -> Optional[ReliableMessageFactory]:
        helper = reliable_helper()
        return helper.get_reliable_message_factory()

    @classmethod
    def set_factory(cls, factory):
        helper = reliable_helper()
        return helper.set_reliable_message_factory(factory=factory)


def reliable_helper():
    helper = MessageExtensions.reliable_helper
    assert isinstance(helper, ReliableMessageHelper), 'message helper error: %s' % helper
    return helper


class ReliableMessageFactory(ABC):
    """ Reliable Message Factory """

    @abstractmethod
    def parse_reliable_message(self, msg: Dict[str, Any]) -> Optional[ReliableMessage]:
        """
        Parse map object to message

        :param msg: message info
        :return: ReliableMessage
        """
        raise NotImplemented


class ReliableMessageHelper(ABC):
    """ General Helper """

    @abstractmethod
    def set_reliable_message_factory(self, factory: ReliableMessageFactory):
        raise NotImplemented

    @abstractmethod
    def get_reliable_message_factory(self) -> Optional[ReliableMessageFactory]:
        raise NotImplemented

    @abstractmethod
    def parse_reliable_message(self, msg: Any) -> Optional[ReliableMessage]:
        raise NotImplemented
