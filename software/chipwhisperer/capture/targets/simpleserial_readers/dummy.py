
from ._base import SimpleSerialTemplate
import serial
from chipwhisperer.common.utils import serialport
import sys

class SimpleSerial_serial(SimpleSerialTemplate):
	_name = "Dummy Comm Port"

	def __init__(self):
		SimpleSerialTemplate.__init__(self)

	#    def updateSerial(self, _=None):
	##        serialnames = serialport.scan()
	##        self.findParam('port').setLimits(serialnames)
	##        if len(serialnames) > 0:
	##            self.findParam('port').setValue(serialnames[0])

	def selectionChanged(self):
		#self.updateSerial()
		pass

	def debugInfo(self, lastTx=None, lastRx=None, logInfo=None):
		pass

	def write(self, string):
		return len(string)

	def read(self, num=0, timeout=100):
		return 0

	def flush(self):
	#self.ser.flushInput()
		pass

	def flushInput(self):
	#self.ser.flushInput()
		pass

	def close(self):
		pass

	def con(self, scope = None):
		pass

	def fileno(self):
		return sys.stdin.fileno()

