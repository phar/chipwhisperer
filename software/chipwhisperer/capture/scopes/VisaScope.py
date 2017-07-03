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

from .base import ScopeTemplate
from .base import Channel
from chipwhisperer.common.utils import pluginmanager
from chipwhisperer.common.utils.parameter import setupSetParam
from chipwhisperer.common.utils.pluginmanager import Plugin
import logging

try:
	import visa
except ImportError, e:
	print "************************************************************"
	print "NI-Visa and Pyvisa are required for VISA instrument support"
	print "https://www.ni.com/visa/"
	print "https://pyvisa.readthedocs.io/en/stable/"
	print "************************************************************"
	raise ImportError(e)

class VisaScopeInterface(ScopeTemplate, Plugin):
	_name = "VISA Scope"

	def __init__(self):
		self.scopetype = None
		self._channels = ["Channel 1","Channel 2","Channel 3","Channel 4"]
		self._triggers = ["Channel 1","Channel 2","Channel 3","Channel 4","EXT","EXT5","ACLine"]

		super(self.__class__, self).__init__()

		self.chanobj = Channel(self._name)
		self.scopechannels[self._name] = self.chanobj
		
		self.scopes = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.scopes.visascope_interface", True, False)

		self.params.addChildren([
			{'name':'Channel', 'key':'chan', 'type':'list', 'values':self._channels, 'get':self.getChannel,'set':self.setChannel},
			{'name':'Trigger', 'key':'trigger', 'type':'list', 'values':self._triggers, 'get':self.getTrigger,'set':self.setTrigger},
			{'name':'VISA Resource String', 'key':'connStr', 'type':'str', 'value':'TCPIP::192.168.1.15::INSTR'},
			{'name':'Identified Instrument','key':'scopeid','type':'str', 'value':'None'},
			{'name':'Scope Driver','key':'scopedriver','type':'str', 'value':'None'},
			{'name':'Query Scope', 'key':'qscope', 'type':'action', 'action':self.queryscope},
			{'name':'Force Trigger', 'key':'trig', 'type':'action', 'action':self.forcetrigger},
			{'name':'Reset Scope', 'key':'rscope', 'type':'action', 'action':self.resetscope},
		])
#		self.getChannels()
		self.params.init()
	
	def forcetrigger(self,trig):
		if self.scopetype:
			self.scopetype.forcetrigger()
		else:
			raise Warning("must implement force trigger")

	def setSampleRate(self, scale,  blockSignal=False):
		pass
	
	def getChannel(self):
		if self.scopetype:
			return self.scopetype.getChannel()
		return None
	
	@setupSetParam("Channel")
	def setChannel(self, chan, blockSignal=1):
		if self.scopetype:
			self.scopetype.setChannel(chan)
		pass

	def getTrigger(self):
		if self.scopetype:
			return self.scopetype.getTrigger()
		return None

	@setupSetParam("Trigger")
	def setTrigger(self,trig):
		if self.scopetype:
			self.scopetype.setTrigger(trig)
	
	def getSampleRate(self):
		if self.scopetype:
			return self.scopetype.getSampleRate()
	
	def setTimeScale(self, scale):
		pass
	
	def getMagnitudeScale(self):
		if self.scopetype:
			return self.scopetype.getMagnitudeScale()
	
	@setupSetParam("Y-Scale")
	def setMagnitudeScale(self, scale):
		if self.scopetype:
			self.scopetype.setMagnitudeScale(scale)
	
	def getMagnitudeOffset(self):
		if self.scopetype:
			return self.scopetype.getMagnitudeOffset()
	
	@setupSetParam("Y-Offset")
	def	setMagnitudeOffset(self, offset):
		if self.scopetype:
			return self.scopetype.setMagnitudeOffset(offset)
	
	def getTimeOffset(self):
		if self.scopetype:
			return self.scopetype.getTimeOffset()

	@setupSetParam("X-Offset")
	def setTimeOffset(self, offset):
		if self.scopetype:
			self.scopetype.setTimeOffset(offset)

	def updateCurrentSettings(self):
		if self.scopetype:
			self.scopetype.getCurrentSettings(offset)
			self.setCurrentSettings()

	def setCurrentSettings(self):
		(self.XScale,self.XOffset,self.YScale,self.YOffset,self.SampSs) = self.getcurrentSettings()
		self.findParam('yscale').setValue(self.YScale)
		self.findParam('xoffset').setValue(self.XOffset)
		self.findParam('yoffset').setValue(self.YOffset)
		self.findParam('sampsper').setValue(self.SampSs)

	def queryscope(self,arg):
		vrm = visa.ResourceManager()
		self.visaInst = vrm.open_resource(self.findParam('connStr').getValue())
		self.detectedscopeid = self.visaInst.query("*IDN?").strip().split(",")
		self.findParam('scopeid').setValue(str(self.detectedscopeid))
		self.updateScopeDriver()

	def resetscope(self,arg):
		vrm = visa.ResourceManager()
		self.visaInst = vrm.open_resource(self.findParam('connStr').getValue())
		self.visaInst.write("*RST")

	def updateScopeDriver(self):
		for s,v in self.scopes.items():
			if str(self.detectedscopeid[1]) in v.support():
				logging.info("found scope driver: %s" % v._name)
				self.scopetype = self.scopes[v._name]
				self.scopetype.visaInst = self.visaInst
				self.scopetype.params = self.params
				#				self.params.append(self.scopetype.params)
				self.findParam('scopedriver').setValue(v._name)
				self.scopetype.updateCurrentSettings()
				self.scopetype.currentSettings()
				self.dataUpdated.connect(self.newDataReceived)
				self.params.init()

				return

		self.scopetype = None
		self.findParam('scopedriver').setValue("No Support Detected")
	
	@setupSetParam("Scope Type")
	def setCurrentScope(self, scope, update=True):
		self.scopetype = scope

	def _con(self):
		self.queryscope("doesnt matter")
		if self.scopetype is not None:
			self.updateScopeDriver()
			self.scopetype.con(self.findParam('connStr').getValue())
			return True
		return False

	def _dis(self):
		if self.scopetype is not None:
			self.scopetype.dis()

	def arm(self):
		try:
			if self.scopetype is not None:
				self.scopetype.arm()
		except Exception:
			self.dis()
			raise

	def capture(self):
		if self.scopetype is not None:
			(dp,do,ss) = self.scopetype.capture()
			self.dataUpdated.emit(self._name, dp,do,ss)
		else:
			pass #fixme warning
