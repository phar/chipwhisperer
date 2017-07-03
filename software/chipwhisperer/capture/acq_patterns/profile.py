import random
from chipwhisperer.common.utils import util
from base import AcqKeyTextPattern_Base
from chipwhisperer.common.utils.parameter import setupSetParam
import struct


def static_iterator(s,e, val):
	for i in xrange(s,e):
		yield val

class AcqKeyTextPattern_Profiler(AcqKeyTextPattern_Base):
	_name = "Profiler"

	def __init__(self, target=None):
		AcqKeyTextPattern_Base.__init__(self)
		self.endians = ["Little", "Big"]
		self._endian = "Little"
		self.size = ["char", "short", "long","double"]
		self._size = "char"
		self.progression = ["Sequential-Ascending", "Sequentian-Descending", "Random", "Static"]
		self._progression = "Sequential-Ascending"
		self._range = (0,255)
		self.iterator = iter(xrange(self._range[0],self._range[1]))

		self.types = {'Random': False, 'Fixed': True}
		
		self.getParams().addChildren([
			{'name':'Endianess', 'key':'endian', 'type':'list', 'values':self.endians, 'get':self.getEndianess, 'set':self.setEndianess},
			{'name':'Size', 'key':'size', 'type':'list', 'values':self.size, 'get':self.getDataSize, 'set':self.setDataSize},
			{'name':'Range', 'key':'dorange', 'type':'range', 'get':self.getDataRange, 'set':self.setDataRange},
			{'name':'Progression', 'key':'progression', 'type':'list', 'values':self.progression, 'get':self.getProgression, 'set':self.setProgression},
		])
		self.setTarget(target)

	def getEndianess(self):
		return self._endian

	def setEndianess(self, t,blockSignal=1):
		self._endian = t

	def getDataSize(self):
		return self._size
	
	def setDataSize(self, t,blockSignal=1):
		self._size = t
	
	def getDataRange(self):
		return self._range
	
	def setDataRange(self, t,blockSignal=1):
		self._range = t
		self.setProgression(self._progression)
	
	def getProgression(self):
		return self._progression
	
	def setProgression(self, t,blockSignal=1):
		self._progression = t
		if self._progression == "Sequential-Ascending":
			self.iterator = iter(xrange(self._range[0],self._range[1],1))
		elif self._progression == "Sequentian-Descending":
			self.iterator = iter(xrange(self._range[1],self._range[0],-1))
		elif self._progression == "Random":
			d = range(self._range[0],self._range[1],1)
			random.shuffle(d)
			self.iterator = iter(d)
		elif self._progression == "Static":
			self.iterator = static_iterator(self._range[0],self._range[0]+self._range[1],self._range[0])
			
	def initAttackVars(self):
		return self.attackvars

	def nextAttackVars(self):
		if self._endian == "Little":
			e = "<"
		elif self._endian == "Big":
			e = ">"
		
		if self._size == "char":
			self.attackvars['data_value'] = struct.pack(e+"B",self.iterator.next())
		elif self._size == "short":
			self.attackvars['data_value'] = struct.pack(e+"H",self.iterator.next())
		elif self._size == "long":
			self.attackvars['data_value'] = struct.pack(e+"L",self.iterator.next())
		elif self._size == "double":
			self.attackvars['data_value'] = struct.pack(e+"Q",self.iterator.next())
		
		return  self.attackvars

	def countAttackVars(self):
		pass

	def __str__(self):
		key = "Key=" + self.findParam("Key").getValueKey()
		if self._fixedKey:
			key = key + ":" + self.findParam("initkey").getValue()
		plaintext = "Plaintext=" + self.findParam("Plaintext").getValueKey()
		if self._fixedPlain:
			plaintext = plaintext + ":" + self.findParam("inittext").getValue()

		return self.getName() + " (%s, %s)" % (key, plaintext)
