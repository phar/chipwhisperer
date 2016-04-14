#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Authors: Colin O'Flynn
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

from chipwhisperer.common.utils.plugin import PluginTemplate


def getClass():
    return AuxiliaryTemplate


class AuxiliaryTemplate(PluginTemplate):
    name = "None"

    def __init__(self):
        PluginTemplate.__init__(self)
        self.prefix = ""

    def __del__(self):
        """Close system if needed"""
        print "Aux: Closing"
        self.close()

    def close(self):
        """Close target, disconnect if required"""
        pass

    def captureInit(self):
        """Called once before each capture grouping, do connect etc"""
        pass

    def captureComplete(self):
        """Called once complete capture is complete"""
        pass

    def traceArm(self):
        """Called before arming scope, use to arm aux system"""
        pass

    def traceArmPost(self):
        """Called after arming scope, before sending trigger to target"""
        pass

    def traceDone(self):
        """Called once capture is complete for a single trace"""
        pass

    def setPrefix(self, prefix):
        self.prefix = prefix