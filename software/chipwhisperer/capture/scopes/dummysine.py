import logging
import time
import struct
from .base import ScopeTemplate
from .base import Channel
from chipwhisperer.common.utils.pluginmanager import Plugin
import numpy as np
from chipwhisperer.common.utils import util, pluginmanager
from chipwhisperer.common.utils.parameter import Parameterized, Parameter, setupSetParam
from chipwhisperer.common.utils.tracesource import TraceSource
from scipy import signal

class DummyScopeInterface_SineWave(ScopeTemplate,Plugin):
	_name = "Waveform Generator"

	def __init__(self):
		self.SampSs = 42000
		self._channels = ["Square","Sine","Noise"]
		self._triggers = {"None":None}
		self._armed = 0
		self.connected = 0
		self._samplecount = self.SampSs/8.0
		self._frequency = 2600
		self._channel = self._channels[0]

		super(self.__class__, self).__init__()
	
		self.dataUpdated = util.Signal()
		self.dataUpdated.connect(self.newDataReceived)
		self.chanobj = Channel(self._name)
		self.scopechannels[self._name] = self.chanobj
		
		self.params.addChildren([
				{'name':'Frequency', 'key':'freq', 'type':'float', 'siPrefix': True, 'suffix': 'Hz', 'get':self.getFrequency,'set':self.setFrequency},
				{'name':'Sample Rate', 'key':'samp', 'type':'float', 'siPrefix': True, 'suffix': 'Sa/S','get':self.getSampleRate,'set':self.setSampleRate},
				{'name':'Duration (samples)', 'key':'tsecs', 'type':'int', 'get':self.getSampleCount,'set':self.setSampleCount},
				{'name':'Channel', 'key':'chan', 'type':'list', 'values':self._channels, 'get':self.getChannel,'set':self.setChannel},
				{'name':'Trigger', 'key':'trigger', 'type':'list', 'values':self._triggers, 'get':self.getTrigger,'set':self.setTrigger}
		])
		self.params.init()

	def getChannel(self):
		return self._channel
	
	@setupSetParam("Channel")
	def setChannel(self,chan):
		self._channel = str(chan)
	
	def getTrigger(self):
		return self._trigger
	
	@setupSetParam("Trigger")
	def setTrigger(self,trig):
		self._trigger = trig
	
	def getMagnitudeScale(self):
		return self._yscale
	
	@setupSetParam("Y-Scale")
	def setMagnitudeScale(self, scale):
		self._yscale = scale
	
	def getMagnitudeOffset(self):
		return self._yoffset
	
	@setupSetParam("Y-Offset")
	def	setMagnitudeOffset(self, offset):
		self._yoffset = offset
	
	def getTimeOffset(self):
		return self._xoffset
	
	def setTimeOffset(self, offset,  blockSignal=False):
		self._xoffset = offset

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
	
	@setupSetParam("Frequency")
	def setFrequency(self,freq):
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
		
		if str(self._channel) == "Sine":
			self.datapoints =        (np.sin(2 * np.pi * self._frequency * x / self.SampSs) * self._yscale) + self._yoffset
		elif str(self._channel) == "Noise":
			self.datapoints = (np.random.rand(int(self._samplecount)) - .5) + self._yoffset
		elif str(self._channel) == "Square":
			self.datapoints = (signal.square(2 * np.pi * self._frequency * x / self.SampSs) * self._yscale) + self._yoffset
		else:
			self.datapoints = (np.random.rand(int(self._samplecount)) - .5) + self._yoffset

		#logging.info((self._channel, self.datapoints, 0, self.SampSs))
		self.dataUpdated.emit(self._channel, self.datapoints, 0, self.SampSs) #fixme
			#self.dataUpdated.emit("Noise", self.datapoints, 0, self.SampSs)
		self.armed = 0
		return False
