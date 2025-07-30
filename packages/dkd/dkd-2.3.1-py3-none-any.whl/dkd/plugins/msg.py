# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
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

from abc import ABC, abstractmethod
from typing import Optional, Dict

from mkm.types import Singleton

from ..protocol.content import ContentHelper
from ..protocol.envelope import EnvelopeHelper
from ..protocol.instant import InstantMessageHelper
from ..protocol.secure import SecureMessageHelper
from ..protocol.reliable import ReliableMessageHelper
from ..protocol.helpers import MessageExtensions


# class GeneralMessageHelper(ContentHelper, EnvelopeHelper,
#                            InstantMessageHelper, SecureMessageHelper, ReliableMessageHelper,
#                            ABC):
class GeneralMessageHelper(ABC):
    """ Message GeneralFactory """

    #
    #   Message Type
    #

    @abstractmethod
    def get_content_type(self, content: Dict, default: Optional[str]) -> Optional[str]:
        raise NotImplemented


@Singleton
class SharedMessageExtensions:
    """ Message FactoryManager """

    def __init__(self):
        super().__init__()
        self.__helper: Optional[GeneralMessageHelper] = None

    @property
    def helper(self) -> Optional[GeneralMessageHelper]:
        return self.__helper

    @helper.setter
    def helper(self, helper: GeneralMessageHelper):
        self.__helper = helper

    #
    #   Content
    #

    @property
    def content_helper(self) -> Optional[ContentHelper]:
        return MessageExtensions.content_helper

    @content_helper.setter
    def content_helper(self, helper: ContentHelper):
        MessageExtensions.content_helper = helper

    #
    #   Envelope
    #

    @property
    def envelope_helper(self) -> Optional[EnvelopeHelper]:
        return MessageExtensions.envelope_helper

    @envelope_helper.setter
    def envelope_helper(self, helper: EnvelopeHelper):
        MessageExtensions.envelope_helper = helper

    #
    #   InstantMessage
    #

    @property
    def instant_helper(self) -> Optional[InstantMessageHelper]:
        return MessageExtensions.instant_helper

    @instant_helper.setter
    def instant_helper(self, helper: InstantMessageHelper):
        MessageExtensions.instant_helper = helper

    #
    #   SecureMessage
    #

    @property
    def secure_helper(self) -> Optional[SecureMessageHelper]:
        return MessageExtensions.secure_helper

    @secure_helper.setter
    def secure_helper(self, helper: SecureMessageHelper):
        MessageExtensions.secure_helper = helper

    #
    #   ReliableMessage
    #

    @property
    def reliable_helper(self) -> Optional[ReliableMessageHelper]:
        return MessageExtensions.reliable_helper

    @reliable_helper.setter
    def reliable_helper(self, helper: ReliableMessageHelper):
        MessageExtensions.reliable_helper = helper
