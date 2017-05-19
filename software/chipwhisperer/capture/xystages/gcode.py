import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from chipwhisperer.common.utils.gcode_helper import GCODE
from _base import StageTemplate

import numpy as np
import time



class GCodeStageTemplate(StageTemplate, Plugin):
	_name = "GCODE Stage"

	def __init__(self):
		StageTemplate.__init__(self)
		self.getParams()
		self.prefix = ""

		self.getParams().addChildren([
			{'name':'Corner Location', 'key':'datarange', 'type':'range', 'get':self.getRange, 'set':self.setRange},
			{'name':'Use Current Location', 'key':'datarange', 'type':'action','action':self.foo},
			{'name':'Opposite Corner Location', 'key':'datarange', 'type':'range', 'get':self.getRange, 'set':self.setRange},
			{'name':'Use Current Location', 'key':'datarange', 'type':'action','action':self.foo},
			{'name':'Glitch Power', 'key':'datarange', 'type':'action','action':self.foo},
			{'name':'Glitch Count', 'key':'datarange', 'type':'action','action':self.foo},

		])
	
	def foo(self):
		pass

	def con(self):
		pass

	def dis(self):
		pass

	def getStatus(self):
		return self.connectStatus.value()
