import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from chipwhisperer.common.utils.gcode_helper import GCODE
from _base import StageTemplate
from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI

import numpy as np
import time



class DummyStageTemplate(StageTemplate, Plugin):
	_name = "Dummy Stage"

	def __init__(self):
		self.getParams()
		self.prefix = ""
		StageTemplate.__init__(self)
		self._x = 0
		self._y = 0
		self.params.addChildren([
			{'name':'Current Position', 'key':'currpos', 'type':'range', 'get':self.getCurrentCoord, 'set':self.setCurrentCoord},
			{'name':'Corner Position', 'key':'corner0', 'type':'range', 'get':self.getMinCoord, 'set':self.setMinCoord},
			{'name':'Opposite Corner Position','key':'corner1', 'type':'range', 'get':self.getMaxCoord, 'set':self.setMaxCoord},
			{'name':'Samples Per Axis', 'key':'axis_steps', 'type':'float', 'get':self.getAxisSteps, 'set':self.setAxisSteps},
			{'name':'Stage Step Latency', 'key':'axis_delay', 'type':'float', 'get':self.getLatency, 'set':self.setLatency},
		])

	def getLatency(self):
		return self._stepdelay
	
	def setLatency(self, delay,  blockSignal=False):
		self._stepdelay = delay
	
	def getAxisSteps(self):
		return self._axisSteps
	
	def setAxisSteps(self, steps,  blockSignal=False):
		self._axisSteps = steps
	
	def getMinCoord(self):
		return self._minCoord
	
	def setMinCoord(self, mincoord,  blockSignal=False):
		self._minCoord = mincoord

	def getMaxCoord(self):
		return self._minCoord
	
	def setMaxCoord(self, mincoord,  blockSignal=False):
		self._minCoord = mincoord

	def getCurrentCoord(self):
		return self._currCoord

	def setCurrentCoord(self, coord,  blockSignal=False):
		self._currCoord = (coord[0],coord[1])
		pass
	
	def enableStageMotors(self):
		pass

	def disableSageMotors(self):
		pass
	
	def _con(self):
		pass
	
	def _dis(self):
		pass

	def getStatus(self):
		pass

	def stageMovementLatencyPause(self):
		time.sleep(self._stepdelay)

#return self.connectStatus.value()
