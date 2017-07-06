import logging
from usb import USBError
from base import TargetTemplate
from chipwhisperer.common.utils import pluginmanager
from simpleserial_readers.cwlite import SimpleSerial_ChipWhispererLite
from simpleserial_readers.sys_serial import SimpleSerial_serial
from chipwhisperer.common.utils.parameter import setupSetParam
import re
from itertools import *

class SimpleSerial(TargetTemplate):
	_name = "Simple Stream (depre)"

	def __init__(self):
		self.timeout = 5
		
		TargetTemplate.__init__(self)

		ser_cons = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.targets.simpleserial_readers", True, False)
		self.ser = ser_cons[SimpleSerial_serial._name]
		self.expectfile = self.scriptlist.items()[0][1]
		self.params.addChildren([
			{'name':'Connection', 'type':'list', 'key':'con', 'values':ser_cons, 'get':self.getConnection, 'set':self.setConnection},
			{'name':'Timeout', 'key':'timeout','type':'int', 'get':self.getTimeout, 'set':self.setTimeout},
			{'name':'Communication Script', 'key':'expectscript', 'type':'list', 'values':self.scriptlist,'get':self.getScript, 'set':self.setScript}
		])
		
		self.setConnection(self.ser, blockSignal=True)


	def getTimeout(self):
		return self.timeout * 1000.0
	
	@setupSetParam("Timeout")
	def setTimeout(self, timeout):
		self.timeout = int(timeout)/1000.0

	def getScript(self):
		return self.expectfile
	
	@setupSetParam("Communication Script")
	def setScript(self,script):
		self.expectfile = script
		self.setExpectScript(self.expectfile)

	def reinit(self):
		if self.ser:
			self.ser.reinit()

	def getConnection(self):
		return self.ser

	@setupSetParam("Connection")
	def setConnection(self, con):
		self.ser = con
		self.params.append(self.ser.getParams())
		
		self.ser.connectStatus.connect(self.connectStatus.emit)
		self.ser.selectionChanged()

	def _con(self, scope = None):
		if not scope or not hasattr(scope, "qtadc"):
			Warning("You need a scope with OpenADC connected to use this Target")
		self.ser.init()
		self.ser.con(scope)
		self.ser.flush()

	def close(self):
		if self.ser != None:
			self.ser.close()

	def fileno(self):
		return self.ser.fileno()

	def init(self):
		"""Init Hardware"""
		self.ser.init()

	def isDone(self):
		return True

	def init(self):
		pass

	def reinit(self):
		pass

