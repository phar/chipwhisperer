import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter


class StageTemplate(Parameterized, Plugin):
	_name = "None"

	def __init__(self):
		self.getParams()
		self.prefix = ""
		self.connectStatus = util.Observable(False)
	
	def con(self):
		pass

	def dis(self):
		pass


	def getStatus(self):
			return self.connectStatus.value()
