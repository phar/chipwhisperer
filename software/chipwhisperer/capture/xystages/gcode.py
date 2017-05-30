import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from chipwhisperer.common.utils.gcode_helper import GCODE
from _base import StageTemplate
from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI
import numpy as np
import time



class GCodeStageTemplate(StageTemplate, Plugin):
	_name = "GCODE Stage"

	def __init__(self):
		self.getParams()
		self.prefix = ""
		self._dev = None
		self._devpath = "/dev/tty.usbserial-AI03DR2E"
		self._devbps = 250000
		StageTemplate.__init__(self)
		self._feedrate = 10

		self.params.addChildren([
			{'name':'Stage Device', 'key':'stagedev', 'type':'str', 'get':self.getStageDev, 'set':self.setStageDev},
			{'name':'Stage Device Baud', 'key':'stagedevbps', 'type':'int', 'get':self.getStageDevBPS, 'set':self.setStageDevBPS},
			{'name':'X-Y FeedRate', 'key':'feedrate', 'type':'int', 'get':self.getFeedRate, 'set':self.setFeedRate},
								 #			{'name':'Current Position', 'key':'currpos', 'type':'range', 'get':self.getCurrentCoord, 'set':self.setCurrentCoord},

		])

	def getFeedRate(self):
		return self._feedrate
	
	def setFeedRate(self, rate,  blockSignal=False):
		self._feedrate = rate
	

	def getStageDev(self):
		return self._devpath
	
	def setStageDev(self, path,  blockSignal=False):
		self._devpath = path

	def getStageDevBPS(self):
		return self._devbps
	
	def setStageDevBPS(self, path,  blockSignal=False):
		self._devbps = path
	

	def updateStagePos(self):
		self.getCurrentCoord()

	def setCurrentCoord(self, coord,  blockSignal=False):
		if self._dev == None:
			return
		else:
			self._dev.gotoXYZ(coord[0],coord[1],f=self._feedrate)
			self.getCurrentCoord()

	def enableStageMotors(self):
		if self._dev:
			self._dev.command("M17")
			self.updateStagePos()

	def disableStageMotors(self):
		if self._dev:
			self._dev.command("M18")
			self.updateStagePos()

	def _con(self):
		self._dev = GCODE(self._devpath, self._devbps)
		self.updateStagePos()
		return True
		
	def _dis(self):
		if self._dev != None:
			self._dev.close()
		self._dev = None


	def getCurrentCoord(self): #fixme
		if self._dev != None:
			self._currCoord = (self._dev.mmpos["X"],self._dev.mmpos["Y"])
			return self._currCoord
		else:
			return (None,None)

