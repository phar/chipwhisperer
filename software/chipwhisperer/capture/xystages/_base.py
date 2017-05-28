import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from chipwhisperer.common.utils import util
import numpy as np

class StageTemplate(Parameterized, Plugin):
	_name = "None"

	def __init__(self):
		self.getParams()
		self.prefix = ""
		self.connectStatus = util.Observable(False)
		self.sigConnectStatus = util.Signal()
		self._currCoord = (0,0)
		self._minCoord = (0,0)
		self._maxCoord = (20,20)
		self._axisSteps = 10
		self._scanpathiter = None
		self._scandone = 1
		self._stepdelay = .1
	
		self.params.addChildren([
			{'name':'Current Position', 'key':'currpos', 'type':'range', 'get':self.getCurrentCoord, 'set':self.setCurrentCoord},
			{'name':'Corner Position', 'key':'corner0', 'type':'range', 'get':self.getMinCoord, 'set':self.setMinCoord},
			{'name':'Use Current Position','key':'setminact', 'type':'action','action':self.useCurrentAsMin},
			{'name':'Opposite Corner Position','key':'corner1', 'type':'range', 'get':self.getMaxCoord, 'set':self.setMaxCoord},
			{'name':'Use Current Position ','key':'setmaxact','type':'action','action':self.useCurrentAsMax},
			{'name':'Samples Per Axis', 'key':'axis_steps', 'type':'float', 'get':self.getAxisSteps, 'set':self.setAxisSteps},
			{'name':'Stage Step Latency', 'key':'axis_delay', 'type':'float', 'get':self.getLatency, 'set':self.setLatency},
		])
	
	def con(self):
		if self._con():
			self.connectStatus.setValue(True)

	def dis(self):
		self._dis()
		self.connectStatus.setValue(False)

	def getStatus(self):
		return self.connectStatus.value()

	def getCurrentCoord(self):
		raise AttributeError("must implement")

	def setCurrentCoord(self, coord,  blockSignal=False):
		raise AttributeError("must implement")

	def enableStageMotors(self):
		"""this is only to quiet a potentially noisy RF"""
		raise AttributeError("must implement")
	
	def disableStageMotors(self):
		"""this is only to quiet a potentially noisy RF"""
		raise AttributeError("must implement")

	def stageMovementLatencyPause(self):
		"""this function is called to delay capture untill the stage is ready, this can be a static or dynamic value"""
		raise AttributeError("must implement")
	
	def updateStagePos(self):
		"""gets and updates the current stage position"""
		raise AttributeError("must implement")
	
	def _zScanPath(self):
		for x in np.linspace(self._minCoord[0],self._maxCoord[0],self._axisSteps):
			for y in np.linspace(self._minCoord[0],self._maxCoord[0],self._axisSteps):
				yield (x,y)
		self._scandone = 0

	def newScan(self):
		self._scandone = 0
		self._scanpathiter = self._zScanPath()

	def scanNext(self):
		if self._scanpathiter != None:
			return self._scanpathiter.next()
		else:
			raise ValueError("no scan iterator")

	def scanComplete(self):
		self._scanpathiter = None
		return self._scandone

	def getLatency(self):
		return self._stepdelay
	
	def setLatency(self, delay,  blockSignal=False):
		self._stepdelay = delay

	def stageMovementLatencyPause(self):
		time.sleep(self._stepdelay)

	def useCurrentAsMin(self , something):
		self._minCoord = self.getCurrentCoord()
		self.findParam('currpos').setValue(self._currCoord)
		self.findParam('corner0').setValue(self._currCoord)
	
	def useCurrentAsMax(self, something):
		self._maxCoord = self.getCurrentCoord()
		self.findParam('currpos').setValue(self._currCoord)
		self.findParam('corner1').setValue(self._currCoord)
