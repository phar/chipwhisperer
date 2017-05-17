#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Find this and more at newae.com - this file is part of the chipwhisperer
# project, http://www.assembla.com/spaces/chipwhisperer
#
#    This file is part of chipwhisperer.
#
#    chipwhisperer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    chipwhisperer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with chipwhisperer.  If not, see <http://www.gnu.org/licenses/>.
#=================================================

import random
from chipwhisperer.common.utils import util
from _base import AcqKeyTextPattern_Base
from chipwhisperer.common.utils.parameter import setupSetParam


class AcqKeyTextPattern_None(AcqKeyTextPattern_Base):
    _name = "None"

    def __init__(self, target=None):
        AcqKeyTextPattern_Base.__init__(self)

    @setupSetParam("Key")
    def setKeyType(self, t):
        self._fixedKey = t

    def getPlainType(self):
        return self._fixedPlain

    @setupSetParam("Plaintext")
    def setPlainType(self, t):
        self._fixedPlain = t

    def getInitialKey(self):
        return " ".join(["%02X"%b for b in self._key])

    @setupSetParam("Fixed Encryption Key")
    def setInitialKey(self, initialKey, binaryKey=False):
		pass

    def getInitialText(self):
        return ""

    @setupSetParam("Fixed Plaintext")
    def setInitialText(self, initialText, binaryText=False):
       pass
	
    def initPair(self):
        pass
