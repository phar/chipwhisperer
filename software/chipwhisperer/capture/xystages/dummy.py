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
		self._x = 0
		self._y = 0
		StageTemplate.__init__(self)
		self.params.addChildren([
								 #			{'name':'Current Position', 'key':'currpos', 'type':'range', 'get':self.getCurrentCoord, 'set':self.setCurrentCoord},
		])


	def enableStageMotors(self):
		pass

	def disableStageMotors(self):
		pass
	
	def _con(self):
		return True
	
	def _dis(self):
		return True

	def stageMovementLatencyPause(self):
		time.sleep(self._stepdelay)

	def getCurrentCoord(self):
		return self._currCoord

	def setCurrentCoord(self, coord,  blockSignal=False):
		self._currCoord = coord
