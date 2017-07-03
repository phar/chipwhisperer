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
import time
import visa
import struct
from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from chipwhisperer.common.utils import util
from chipwhisperer.common.utils.tracesource import TraceSource


class VisaScope(Parameterized,Plugin):
	_name= 'Scope Settings'
	
	def __init__(self):
	#		self.getParams().register()
		self.header = []
		self._channels = ["Channel 1"]
		self._triggers = ["Channel 1"]
	
		self._channel = self._channels[0]
		self._trigger = self._triggers[0]


	def con(self, constr):
		logging.info(self.visaInst.ask("*IDN?"))
		
		for cmd in self.header:
			self.visaInst.write(cmd)
			logging.info('VISA: %s' % cmd)
			time.sleep(0.1)

	def dis(self):
		pass
	
	def updateCurrentSettings(self):
		#		raise Warning("must implement updateCurrentSettings")
		pass  #fixme

	def currentSettings(self):
		#raise Warning("You MUST implement this")
		pass #fixme

	def arm(self):
		"""Example arm implementation works on most"""
		#self.visaInst.write(":DIGitize")

	def capture(self):
		raise Warning("You MUST implement capture")
	

	def support(self):
		return []

	def visa_read_tekformat(self, format="h"):
		data = self.visaInst.read_raw()
		
		#Find '#' which is start of frame
		start = data.find('#')

		if start < 0:
			raise IOError('Error in header')

		start += 1
		hdrlen = data[start]
		hdrlen = int(hdrlen)

		start += 1
		datalen = data[start:(start+hdrlen)]
		datalen = int(datalen)

		start += hdrlen

		#Each is two bytes
		wavdata = bytearray(data[start:(start + datalen)])
		datapoints =  list(struct.unpack(("<%d%c" % (datalen / struct.calcsize(format), format)),wavdata))

		return datapoints

	def getChannel(self):
		return self._channel
	
	def setChannel(self,chan, blockSignal=None):
		self._channel = chan

	def getTrigger(self):
		return self._trigger
	
	def setTrigger(self,trig, blockSignal=None):
		self._trigger = trig



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
