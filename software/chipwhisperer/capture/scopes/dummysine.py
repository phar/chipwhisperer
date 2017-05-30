import logging
import time
import struct
from .base import ScopeTemplate
from chipwhisperer.common.utils.pluginmanager import Plugin
import numpy as np
from chipwhisperer.common.utils import util, pluginmanager
from chipwhisperer.common.utils.parameter import Parameterized, Parameter, setupSetParam
from chipwhisperer.common.utils.tracesource import TraceSource
from scipy import signal

class DummyScopeInterface_SineWave(ScopeTemplate,Plugin):
	_name = "Waveform Generator"

	def __init__(self):
		self.dataUpdated = util.Signal()
		self.dataUpdated.connect(self.newDataReceived)
		self.SampSs = 42000
		self._channels = ["Sine","Square","Noise"]
		self._triggers = ["None"]
		self._armed = 0
		self._channel = self._channels[0]
		self.connected = 0
		self._samplecount = self.SampSs/8.0
		self._frequency = 2600
		self._yscale = 1.0
		self._yoffset = 0.0
		self._xoffset = 0.0
		super(self.__class__, self).__init__()

		self.params.addChildren([
				{'name':'Frequency', 'key':'freq', 'type':'float', 'siPrefix': True, 'suffix': 'Hz', 'get':self.getFrequency,'set':self.setFrequency},
				{'name':'Sample Rate', 'key':'samp', 'type':'float', 'siPrefix': True, 'suffix': 'Sa/S','get':self.getSampleRate,'set':self.setSampleRate},
				{'name':'Duration (samples)', 'key':'tsecs', 'type':'int', 'get':self.getSampleCount,'set':self.setSampleCount},
		])
	
	
	def getMagnitudeScale(self):
		return self._yscale
	
	def setMagnitudeScale(self, scale,  blockSignal=False):
		self._yscale = scale
	
	def getMagnitudeOffset(self):
		return self._yoffset
	
	def	setMagnitudeOffset(self, offset,  blockSignal=False):
		self._yoffset = offset
	
	def getTimeOffset(self):
		return self._xoffset
	
	def setTimeOffset(self, offset,  blockSignal=False):
		self._xoffset = offset
	
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
		x = np.arange(self._samplecount) # the points on the x axis for plotting
		if self._channel == "Sine":
			self.datapoints = (np.sin(2 * np.pi * self._frequency * x / self.SampSs) * self._yscale) + self._yoffset
		elif self._channel == "Square":
			self.datapoints = (signal.square(2 * np.pi * self._frequency * x / self.SampSs) * self._yscale)  + self._yoffset
		elif self._channel == "Noise":
			self.datapoints = (np.random.rand(self._samplecount) - .5) + self._yoffset
		else:
			self.datapoints = [0]

		self.dataUpdated.emit(0, self.datapoints, 0, self.SampSs)
		self.armed = 0
		return False
