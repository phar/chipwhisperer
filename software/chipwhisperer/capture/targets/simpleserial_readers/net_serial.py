from ._base import SimpleSerialTemplate
import serial
from chipwhisperer.common.utils import serialport
import socket

class SimpleSerial_serial(SimpleSerialTemplate):
	_name = "Network Serial"

	def __init__(self):
		SimpleSerialTemplate.__init__(self)
		self.sock = None

		self.params.addChildren([
			{'name':'Host', 'key':'nethost', 'type':'str', 'value':'192.168.1.1'},
			{'name':'Port', 'key':'netport', 'type':'str', 'value':'6700'},
		])

	def debugInfo(self, lastTx=None, lastRx=None, logInfo=None):
		pass

	def write(self, string):
		if self.sock == None:
			self.con(self.scope)
		return self.sock.send(string)

	def read(self, num=0, timeout=100):
		if self.sock == None:
			self.con(self.scope)
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

	def con(self, scope = None):
		if self.sock == None:
			self.ser = serial.Serial()
			self.scope = scope
			self.sock = s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.findParam('nethost').getValue(), int(self.findParam('netport').getValue())))
