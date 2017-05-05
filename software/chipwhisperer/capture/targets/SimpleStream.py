import logging
from usb import USBError
from ._base import TargetTemplate
from chipwhisperer.common.utils import pluginmanager
from simpleserial_readers.cwlite import SimpleSerial_ChipWhispererLite
from chipwhisperer.common.utils.parameter import setupSetParam
import re
from itertools import *

class SimpleSerial(TargetTemplate):
	_name = "Simple Stream"

	def __init__(self):
		TargetTemplate.__init__(self)

		ser_cons = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.targets.simpleserial_readers", True, False)
		self.ser = ser_cons[SimpleSerial_ChipWhispererLite._name]
		self.keylength = 16
		self.textlength = 16
		self.outputlength = 16
		self.input = ""
		self.buff2 = '$@"this string is evaled!"$\n'
		self.params.addChildren([
			{'name':'Connection', 'type':'list', 'key':'con', 'values':ser_cons, 'get':self.getConnection, 'set':self.setConnection},
			{'name':'Maximum Input Length (Bytes)', 'key':'inputlen','type':'int', 'value':64},
			{'name':'Timeout', 'key':'timeout','type':'int', 'value':500},
			{'name':'Output 1', 'key':'buff1', 'type':'str', 'value':'./login_cmd'},
			{'name':'Output 2','key':'buff2', 'type':'str', 'get':self.getbuff2, 'set':self.setbuff2},
			{'name':'Response Regex4', 'key':'regexout', 'type':'str', 'value':'.*'},
		])
		self.setConnection(self.ser, blockSignal=True)


	def getbuff2(self):
		return self.buff2
	
	def setbuff2(self,buff2, blockSignal=True):
		self.buff2 = buff2.decode('string_escape')

	def reinit(self):
		self.ser.reinit()

	@setupSetParam("Input Length")
	def setTextLen(self, tlen):
		""" Set plaintext length. tlen given in bytes """
		self.textlength = tlen

	def textLen(self):
		""" Return plaintext length in bytes """
		return self.textlength

	@setupSetParam("Output Length")
	def setOutputLen(self, tlen):
		""" Set plaintext length in bytes """
		self.outputlength = tlen

	def outputLen(self):
		""" Return output length in bytes """
		return self.outputlength

	def getConnection(self):
		return self.ser

	@setupSetParam("Connection")
	def setConnection(self, con):
		self.ser = con
		self.params.append(self.ser.getParams())
		
		self.ser.connectStatus.connect(self.connectStatus.emit)
		self.ser.selectionChanged()

	def _con(self, scope = None):
		if not scope or not hasattr(scope, "qtadc"): Warning("You need a scope with OpenADC connected to use this Target")
		self.ser.init()
		self.ser.con(scope)
		self.ser.flush()

	def close(self):
		if self.ser != None:
			self.ser.close()

	def init(self):
		self.ser.init()
		if self.findParam('buff1').getValue():
			self.runCommand(self.findParam('buff1').getValue())

	def setModeEncrypt(self):
		pass

	def setModeDecrypt(self):
		pass

	def convertVarToString(self, var):
		if isinstance(var, str):
			return var

		sep = ""
		s = sep.join(["%02x"%b for b in var])
		return s

	def runCommand(self, cmdstr, flushInputBefore=True):
		if self.connectStatus.value()==False:
			raise Warning("Can't write to the target while disconected. Connect to it first.")

		if cmdstr is None or len(cmdstr) == 0:
			return


		vl = {} #fixme, functionize
#		vl = {"KEY":[self.key, "Hex Encryption Key"],
#			"TEXT":[self.input, "Input Plaintext"]}

		varList = re.findall(r"\$(.*?)\$", cmdstr)

		newstr = cmdstr

		#Find variables to insert
		for v in varList:
			if v in vl:
				newstr = newstr.replace("$%s$" % v, self.convertVarToString(vl[v][0]))
			elif v[0] == '@': #enables dynamic functions
				newstr = newstr.replace("$%s$" % v, eval(v[1:]))

		newstr = newstr.decode('string_escape') #fixme

		print [newstr]
		
		try:
			if flushInputBefore:
				self.ser.flushInput()
			self.ser.write(newstr)
		except USBError:
			self.dis()
			raise Warning("Error in the target. It may have been disconnected.")
		except Exception as e:
			self.dis()
			raise e


	def isDone(self):
		return True

	def readOutput(self):
		response = self.ser.read(self.findParam('inputlen').getValue(), timeout=self.findParam('timeout').getValue())
		self.newInputData.emit(response)

		print [response]

		if re.match(self.findParam('regexout').getValue(),response) == None:
			logging.warning('Response does not match response regular expresion. [%s, %s]' % (self.findParam('regexout').getValue(), response))
			return None
		return response

	def go(self):
		self.runCommand(self.buff2)

