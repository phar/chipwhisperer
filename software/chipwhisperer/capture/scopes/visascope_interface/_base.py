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


class VisaScope(Parameterized,Plugin):
	_name= 'Scope Settings'

	header = ""
	
	_channels = ["None"]
	_triggers = ["None"]
	_channel = None
	
	def __init__(self):
		
		self.dataUpdated = util.Signal()
		self.getParams().addChildren([
			{'name':'Channel','key':'chan','type':'list', 'values':self._channels, 'get':self.getChannel, 'set':self.setChannel},
		])
	
		self.newScan()

	def getChannel(self):
		return self._channel
	
	def setChannel(self,channel,blockSignal=None):
		self._channel = channel

	def con(self, constr):
		logging.info(self.visaInst.ask("*IDN?"))
		
		for cmd in self.header:
			self.visaInst.write(cmd)
			logging.info('VISA: %s' % cmd)
			time.sleep(0.1)
		self.updateCurrentSettings()
		
	def dis(self):
		pass
	
	def updateCurrentSettings(self):
		self.currentSettings()
		self.findParam('xscale').setValue(self.XScale)
		self.findParam('yscale').setValue(self.YScale)
		self.findParam('xoffset').setValue(self.XOffset)
		self.findParam('yoffset').setValue(self.YOffset)
		self.findParam('sampsper').setValue(self.SampSs)
		pass

	def currentSettings(self):
		"""You MUST implement this"""
		pass

	def arm(self):
		"""Example arm implementation works on most"""
		#self.visaInst.write(":DIGitize")

	def capture(self):
		"""You MUST implement this"""
		self.dataUpdated.emit(self.datapoints, 0)

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

	def updateChannels(self):
		return self._channels
	
	def updateTriggers(self):
		return self._triggers

