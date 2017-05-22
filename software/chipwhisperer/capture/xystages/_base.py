import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from chipwhisperer.common.utils import util

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
	

	def con(self):
		pass

	def dis(self):
		pass


	def getStatus(self):
		return self.connectStatus.value()

	def getCurrentCoord(self):
		raise AttributeError("must implement")

	def setCurrentCoord(self, coord,  blockSignal=False):
		raise AttributeError("must implement")

	def enableStageMotors(self):
		"""this is only to quiet a potentially noisy RF"""
		raise AttributeError("must implement")
	
	def disableSageMotors(self):
		"""this is only to quiet a potentially noisy RF"""
		raise AttributeError("must implement")

	def stageMovementLatencyPause(self):
		"""this function is called to delay capture untill the stage is ready, this can be a static or dynamic value"""
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
		if _scanpathiter != None:
			return self._scanpathiter.next()
		else:
			raise ValueError("no scan iterator")

	def scanComplete(self):
		_scanpathiter = None
		return self._scandone
