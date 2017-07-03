#!/usr/bin/python

from chipwhisperer.capture.api.programmers import Programmer
from chipwhisperer.common.utils import util
from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from pexpect.fdpexpect import *
import pexpect
import sys
import glob
import os
import re
import logging

#try:
#    from Crypto.Cipher import AES
#except ImportError:
#    AES = None
#

class TargetTemplate(Parameterized, Plugin):
	_name = 'Target Connection'

	def __init__(self):
		self.newInputData = util.Signal()
		self.connectStatus = util.Observable(False)
		self.getParams().register()
		self.timeout = .5
		self.expect = None
		self.expectfile = None
		self.scriptlist = {}
		self.attackvars = {}
		
		for f in glob.glob('target_scripts/serial/*.expect'):
			self.scriptlist[os.path.basename(f)] = f

	def setSomething(self):
		"""Here you would send value to the reader hardware"""
		pass

	def __del__(self):
		"""Close system if needed"""
		self.close()

	def getStatus(self):
		return self.connectStatus.value()

	def dis(self):
		"""Disconnect from target"""
		if self.expect:
			self.expect.close()
		self.close()
		self.connectStatus.setValue(False)

	def con(self, scope=None, **kwargs):
		"""Connect to target"""
		Programmer.lastFlashedFile = "unknown"
		try:
			self.connectStatus.setValue(True)
			self._con(scope, **kwargs)
			self.expect = fdspawn(self.fileno(), timeout = self.timeout)
			self.setExpectScript(self.expectfile)

		except:
			self.dis()
			raise

	def isDone(self):
		"""If encryption takes some time after 'go' called, lets user poll if done"""
		return True


	def sendTargetOutput(self, senddata):
		if self.connectStatus.value()==False:
			raise Warning("Can't write to the target while disconected. Connect to it first.")
		return 	self.expect.send(self.preProcessOutput(senddata));

	def getTargetExpect(self,expectdata):
		"""Based on key & text get expected if known, otherwise returns None"""
		return self.expect.expect(expectdata)

	def validateSettings(self):
		# return [("warn", "Target Module", "You can't use module \"" + self.getName() + "\"", "Specify other module", "57a3924d-3794-4ca6-9693-46a7b5243727")]
		return []

	def setExpectScript(self,scriptfile):
		f = open(scriptfile)
		ll = f.readlines()
		self.script_states = {}
		setname = None

		inside_state = 0
		for l in ll:
			l = l.lstrip().strip()
			if l:
				if l[0] == "#":
					continue
				(cmd,remainder) = l.split(" ",1)
				cmd=cmd.lower()
				expectstring = remainder.lstrip().strip()
				if cmd.lower() in ["send","sendline","expect","write","logging"]:
					expectstring = remainder[1:-1].decode('string_escape')
					if not setname in self.script_states:
						self.script_states[setname] = []
					self.script_states[setname].append((cmd, expectstring))
				
				elif cmd.lower() == "set":
					setargs = expectstring.split()
					if (setargs[0].lower() == "stage"):
						inside_set = 1
						setname = setargs[1].lower()

				elif cmd.lower() == "end":
					setargs = expectstring.split()
					if (setargs[0].lower() == "stage" ):
						inside_set = 1
						setname = None
		f.close()

	def run_expect_state(self, state):
		for (c,b) in self.script_states[state]:
			#logging.info(c + " " + b)
			try:
				if c == "send":
					self.expect.send(b)
				elif c == "sendline":
					self.expect.sendline(b)
				elif c == "expect":
					self.expect.expect(b)
				elif c == "write":
					self.expect.write(b)
				elif c == "logging":
					logging.info(b)
			except pexpect.TIMEOUT:
				logging.info("timeout waiting for input")
			
		if self.expect.match:
			return self.expect.match.groups()
		return ()

	def _con(self, scope=None):
		raise NotImplementedError

	def flush(self):
		"""Flush input/output buffers"""
		pass

	def close(self):
		"""Close target"""
		pass

	def initTargetDevice(self):
		"""Init Hardware"""
		pass

	def initTargetApplication(self):
		"""Init variables"""
		pass

	def fileno(self):
		raise Warning("must implement fileno()")
	
	def reinit(self):
		pass

	def preProcessOutput(self, cmdstr):
		if self.connectStatus.value()==False:
			raise Warning("Can't write to the target while disconected. Connect to it first.")

		if cmdstr is None or len(cmdstr) == 0:
			return

		varList = re.findall(r"\$(.*?)\$", cmdstr)

		newstr = cmdstr

		#Find variables to insert
		for v in self.attackvars:
			if v in self.attackvars:
				newstr = newstr.replace("$%s$" % v, self.convertVarToString(vl[v][0]))
			elif v[0] == '@': #enables dynamic functions
				newstr = newstr.replace("$%s$" % v, eval(v[1:]))

		return newstr.decode('string_escape') #fixme


	def getTimeout(self):
		return self.timeout
	
	def setTimeout(self,script, blockSignal=True):
		self.Timeout = int(script)



#    def setModeEncrypt(self):
#        """Set hardware to do encryption, if supported"""
#        pass
#
#    def setModeDecrypt(self):
#        """Set hardware to do decryption, if supported"""
#        pass
#
#    def checkEncryptionKey(self, key):
#        """System 'suggests' encryption key, and target modifies it if required because e.g. hardware has fixed key"""
#        return key
#
#    def checkPlaintext(self, text):
#        """System suggests plaintext; target modifies as required"""
#        return text
#
#    def loadEncryptionKey(self, key):
#        """Load desired encryption key"""        
#        self.key = key
#
#    def loadInput(self, inputtext):
#        """Load input plaintext"""
#        self.input = inputtext



#    def readOutput(self):        
#        """Read result"""
#        raise NotImplementedError("Target \"" + self.getName() + "\" does not implement method " + self.__class__.__name__ + ".readOutput()")
#
#    def go(self):
#        """Do Encryption"""
#        raise NotImplementedError("Target \"" + self.getName() + "\" does not implement method " + self.__class__.__name__ + ".go()")
#
#    def keyLen(self):
#        """Length of key system is using"""
#        return 16
#
#    def textLen(self):
#        """Length of the plaintext used by the system"""
#        return 16

