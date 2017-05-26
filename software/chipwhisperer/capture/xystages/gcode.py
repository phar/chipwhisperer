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

		self.params.addChildren([
			{'name':'Stage Device', 'key':'stagedev', 'type':'str', 'get':self.getStageDev, 'set':self.setStageDev},
			{'name':'Stage Device Baud', 'key':'stagedevbps', 'type':'int', 'get':self.getStageDevBPS, 'set':self.setStageDevBPS},
			{'name':'Current Position', 'key':'currpos', 'type':'range', 'get':self.getCurrentCoord, 'set':self.setCurrentCoord},
			{'name':'Corner Position', 'key':'corner0', 'type':'range', 'get':self.getMinCoord, 'set':self.setMinCoord},
			{'name':'Use Current Position','key':'setminact', 'type':'action','action':self.useCurrentAsMin},
			{'name':'Opposite Corner Position','key':'corner1', 'type':'range', 'get':self.getMaxCoord, 'set':self.setMaxCoord},
			{'name':'Use Current Position ','key':'setmaxact','type':'action','action':self.useCurrentAsMax},
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

	def useCurrentAsMin(self , something):
		self.updateStagePos()
		self._minCoord = self.getCurrentCoord()
		self.findParam('corner0').setValue(self._currCoord)

	def useCurrentAsMax(self, something):
		self.updateStagePos()
		self._maxCoord = self.getCurrentCoord()
		self.findParam('corner1').setValue(self._currCoord)

	def getCurrentCoord(self):
		if self._dev == None:
			return (None,None) #fixme
		else:
			return self._currCoord

	def updateStagePos(self):
		self._dev.getPos()
		self._currCoord = (self._dev.mmpos["X"],self._dev.mmpos["Y"])
		self.findParam('currpos').setValue(self._currCoord)

	def setCurrentCoord(self, coord,  blockSignal=False):
		if self._dev == None:
			return
		else:
			self._dev.gotoXYZ(coord[0],coord[1])
			self.getCurrentCoord()


	def enableStageMotors(self):
		if self._dev:
			self._dev.command("M17")
			self.updateStagePos()


	def disableStageMotors(self):
		if self._dev:
			self._dev.command("M18")
			self.updateStagePos()

	def con(self):
		if self._dev:
			self._dev.close()
		self._dev = GCODE(self._devpath, self._devbps)
		self.updateStagePos()
		
	def dis(self):
		if self._dev != None:
			self._dev.close()
		self._dev = None

	def getStatus(self):
			pass

	def stageMovementLatencyPause(self):
		time.sleep(self._stepdelay)

#return self.connectStatus.value()
