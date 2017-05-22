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
		self._devpath = "/dev/ttyS0"
		self._devbps = 250000
		StageTemplate.__init__(self)

		self.getParams().addChildren([
			{'name':'Stage Device', 'key':'stagedev', 'type':'str', 'get':self.getStageDev, 'set':self.setStageDev},
			{'name':'Stage Device Baud', 'key':'stagedevbps', 'type':'int', 'get':self.getStageDevBPS, 'set':self.setStageDevBPS},
			{'name':'Current Position', 'key':'datarange', 'type':'range', 'get':self.getCurrentCoord, 'set':self.setCurrentCoord},
			{'name':'Corner Position', 'key':'datarange', 'type':'range', 'get':self.getMinCoord, 'set':self.setMinCoord},
			{'name':'Use Current Position','type':'action','action':self.useCurrentAsMin},
			{'name':'Opposite Corner Position','key':'datarange', 'type':'range', 'get':self.getMaxCoord, 'set':self.setMaxCoord},
			{'name':'Use Current Position','type':'action','action':self.useCurrentAsMax},
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
	

	def getStageDev(self):
		return self._devpath
	
	def setStageDev(self, path,  blockSignal=False):
		self._devpath = path

	def getStageDevBPS(self):
		return self._devbps
	
	def setStageDevBPS(self, path,  blockSignal=False):
		self._devbps = path


	def getMinCoord(self):
		return self._minCoord
	
	def setMinCoord(self, mincoord,  blockSignal=False):
		self._minCoord = mincoord

	def getMaxCoord(self):
		return self._minCoord
	
	def setMaxCoord(self, mincoord,  blockSignal=False):
		self._minCoord = mincoord

	def useCurrentAsMin(self):
		self._minCoord = self.getCurrentCoord()

	def useCurrentAsMax(self):
		pass

	def getCurrentCoord(self):
		if self._dev == None:
			return (None,None) #fixme
		else:
			(self._x,self._y,self._z) = self._dev.getPos()
			self._currCoord = (self._x,self._y)

	def setCurrentCoord(self, coord,  blockSignal=False):
		if self._dev == None:
			return
		else:
			self._dev.gotoXYZ(coord[0],coord[1])
			self.getCurrentCoord()


	def enableStageMotors(self):
		if self._dev:
			self._dev.command("M17")


	def disableSageMotors(self):
		if self._dev:
			self._dev.command("M18")

	def con(self):
	#	self.dev()
		pass

	def dis(self):
		if self._dev != None:
			self._dev.close()
		self._dev = None

	def getStatus(self):
			pass

	def stageMovementLatencyPause(self):
		time.sleep(self._stepdelay)

#return self.connectStatus.value()
