import logging
import time
import struct
from .base import ScopeTemplate
from chipwhisperer.common.utils.pluginmanager import Plugin
import numpy as np
from chipwhisperer.common.utils import util, pluginmanager
from chipwhisperer.common.utils.parameter import Parameterized, Parameter, setupSetParam
from chipwhisperer.common.utils.tracesource import TraceSource

class DummyScopeInterface_SineWave(ScopeTemplate,Plugin):
	_name = "Sine Wave"

	def __init__(self):
		super(self.__class__, self).__init__()
		self.dataUpdated = util.Signal()
		self.dataUpdated.connect(self.newDataReceived)
		self.SampSs = 42000
		self.YOffset = 0
		self.XOffset = 0
		self._channels = {"Sine":0,"Square":1}
		self._triggers = ["None"]
		self._armed = 0
		self._channel = self._channels['Sine']
		self.connected = 0
		self._samplecount = self.SampSs/8.0
		self._frequency = 2600

		self.params.addChildren([
				{'name':'Frequency', 'key':'freq', 'type':'float', 'get':self.getFrequency,'set':self.setFrequency},
				{'name':'Sample Rate', 'key':'samp', 'type':'float', 'get':self.getSampleRate,'set':self.setSampleRate},
				{'name':'Duration (samples)', 'key':'tsecs', 'type':'int', 'get':self.getSampleCount,'set':self.setSampleCount},
				{'name':'Channel', 'key':'chan', 'type':'list', 'values':self._channels, 'get':self.getChannel,'set':self.setChannel},
		])

	def getChannel(self):
		return self._channel

	def setChannel(self,chan, blockSignal=None):
		self._channel = chan

	def getSampleRate(self):
		return 	self.SampSs

	def setSampleRate(self,rate, blockSignal=None):
		self.SampSs = rate
	
	def getSampleCount(self):
		return 	self._samplecount
	
	def setSampleCount(self,count, blockSignal=None):
		self._samplecount = count
	

	def getFrequency(self):
		return 	self._frequency
	
	def setFrequency(self,freq, blockSignal=None):
		self._frequency = freq
	
	def currentSettings(self):
		pass
	
	def arm(self):
		self.armed = 1

	def _con(self):
		self.connected = 1
		return True

	def _dis(self):
		self.connected = 0
		return True
	
	
	def capture(self):
		#we're waiting on the trigger here

		x = np.arange(self._samplecount) # the points on the x axis for plotting
		y = np.sin(2 * np.pi * self._frequency * x / self.SampSs)

		self.datapoints = y
		#		logging.info(self.datapoints)
		self.dataUpdated.emit(self._channel , self.datapoints, 0, self.SampSs)
		self.armed = 0
		return False
