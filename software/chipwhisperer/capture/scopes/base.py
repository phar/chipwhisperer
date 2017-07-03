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
import logging

from chipwhisperer.common.utils import util
from chipwhisperer.common.utils.tracesource import TraceSource
from chipwhisperer.common.utils.parameter import Parameterized


class ScopeTemplate(Parameterized):
	_name = "None"

	def __init__(self):
		self.dataUpdated = util.Signal()
		self.connectStatus = util.Observable(False)
		self.getParams().register()
		self.scopechannels = {}
		self.chanobj = Channel(self._name)
		self.scopechannels[self._name] = self.chanobj
		self._trigger = None
		self._channel = None
		self._yscale = 1.0
		self._xscale = 1.0
		self._xoffset = 0
		self._yoffset = 0

		self.params.addChildren([
			{'name':'Sample Rate', 'key':'sampsper', 'type':'float', 'siPrefix': True, 'suffix': 'Sa/S', 'get':self.getSampleRate,'set':self.setSampleRate},
			{'name':'Y-Scale', 'key':'yscale', 'type':'float', 'get':self.getMagnitudeScale,'set':self.setMagnitudeScale},
			{'name':'Y-Offset', 'key':'yoffset', 'type':'float', 'step':1E-3, 'siPrefix': True, 'suffix': 'V', 'get':self.getMagnitudeOffset,'set':self.setMagnitudeOffset},
			{'name':'X-Offset', 'key':'xoffset', 'type':'float', 'step':1E-6, 'siPrefix': True, 'suffix': 'S','get':self.getTimeOffset,'set':self.setTimeOffset},
		])
	

	def updateScopeDriver(self):
		self.scopetype = self.scopes[v._name]
		self.scopetype.visaInst = self.visaInst
		self.scopetype.params = self.params
		self.findParam('scopedriver').setValue(v._name)
		self.scopetype.updateCurrentSettings()
		self.scopetype.currentSettings()
		self.scopetype.dataUpdated.connect(self.newDataReceived)

	def setSampleRate(self, scale,blockSignal=False):
		raise AttributeError("must implement setSampleRate")
	
	def getSampleRate(self):
		raise AttributeError("must implement getSampleRate")

	def setTimeScale(self, scale):
		raise AttributeError("must implement setTimeScale")
	
	def getMagnitudeScale(self):
		raise AttributeError("must implement getMagnitudeScale")

	def setMagnitudeScale(self, scale,  blockSignal=False):
		raise AttributeError("must implement setMagnitudeScale")
	
	def getMagnitudeOffset(self):
		raise AttributeError("must implement getMagnitudeOffset")

	def	setMagnitudeOffset(self, offset,  blockSignal=False):
		raise AttributeError("must implement setMagnitudeOffset")
	
	def getTimeOffset(self):
		raise AttributeError("must implementgetTimeOffset")

	def setTimeOffset(self, offset,  blockSignal=False):
		raise AttributeError("must implement setTimeOffset")

	def getTrigger(self):
		raise Warning("must implement getTrigger")
	
	def setTrigger(self,trig, blockSignal=None):
		raise Warning("must implement setTrigger")
	
	def getChannel(self):
		raise Warning("must implement getChannel")
	
	def setChannel(self,trig, blockSignal=None):
		raise Warning("must implement setChannel")
	
	def dcmTimeout(self):
		pass

	def setAutorefreshDCM(self, enabled):
		pass

	def setCurrentScope(self, scope):
		pass

	def newDataReceived(self, channel, data=None, offset=0, sampleRate=0):
		self.scopechannels[channel].newScopeData(data, offset, sampleRate) #fixme

	def getStatus(self):
		return self.connectStatus.value()

	def con(self):
		for (cn,channel) in self.scopechannels.items():
			channel.register()
		if self._con():
			self.connectStatus.setValue(True)

	def _con(self):
		raise Warning("Scope \"" + self.getName() + "\" does not implement method " + self.__class__.__name__ + ".con()")

	def dis(self):
		if self._dis():
			for (cn,channel) in self.scopechannels.items():
				channel.deregister()
		self.connectStatus.setValue(False)

	def _dis(self):
		raise Warning("Scope \"" + self.getName() + "\" does not implement method " + self.__class__.__name__ + ".dis()")

	def arm(self):
		"""Prepare the scope for capturing"""
		# NOTE - if reimplementing this, should always check for connection first
		# if self.connectStatus.value() is False:
		#     raise Exception("Scope \"" + self.getName() + "\" is not connected. Connect it first...")
		# raise NotImplementedError("Scope \"" + self.getName() + "\" does not implement method " + self.__class__.__name__ + ".arm()")
		pass

	def capture(self):
		"""Capture one trace and returns True if timeout has happened."""

		# NOTE: If you have a waiting loop (waiting for arm), call the function util.updateUI() inside that loop to keep
		#       the UI responsive:
		#
		# while self.done() == False:
		#     time.sleep(0.05)
		#     util.updateUI()
		pass
	


class Channel(TraceSource):
	"""Save the traces emited by the scopes and notify the TraceSourceObservers."""

	def __init__(self, name="Unknown Channel"):
		TraceSource.__init__(self, name)
		self._lastData = []
		self._lastOffset = 0
		self._sampleRate = 0

	def newScopeData(self, data=None, offset=0, sampleRate=0):
		"""Capture the received trace and emit a signal to inform the observers"""
		self._lastData = data
		self._lastOffset = offset
		self._sampleRate = sampleRate
		if len(data) > 0:
			self.sigTracesChanged.emit()
		else:
			logging.warning('Captured trace in "%s" has len=0' % self.name)

	def getTrace(self, n=0):
		if n != 0:
			raise ValueError("Live trace source has no buffer, so it only supports trace 0.")
		return self._lastData

	def numPoints(self):
		return len(self._lastData)

	def numTraces(self):
		return 1

	def offset(self):
		return self._lastOffset

	def getSampleRate(self):
		return self._sampleRate

	def __str__(self):
		return self.name
