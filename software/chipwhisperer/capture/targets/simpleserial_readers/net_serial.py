from ._base import SimpleSerialTemplate
import serial
from chipwhisperer.common.utils import serialport
import socket
from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI

class SimpleSerial_serial(SimpleSerialTemplate):
	_name = "Network Serial"

	def __init__(self):
		SimpleSerialTemplate.__init__(self)
		self.sock = None
		
		#	self.api.sigNewCapture.connect(self.reconnect)

		self.params.addChildren([
			{'name':'Host', 'key':'nethost', 'type':'str', 'value':'127.0.0.1'},
			{'name':'Port', 'key':'netport', 'type':'str', 'value':'3137'},
		])

	def debugInfo(self, lastTx=None, lastRx=None, logInfo=None):
		pass

	def write(self, string):
		return self.sock.send(string)

	def read(self, num=0, timeout=100):
		return self.sock.recv(num)
	
	def flush(self):
	#        self.ser.flushInput()
		pass

	def flushInput(self):
	#        self.ser.flushInput()
		pass

	def close(self):
		if self.sock is not None:
			self.sock.close()
			self.sock = None

	def init(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.findParam('nethost').getValue(), int(self.findParam('netport').getValue())))

	def reinit(self):
		if self.sock is not None:
			self.sock.close()
		self.init()

	def con(self,scope):
		self.reinit()
