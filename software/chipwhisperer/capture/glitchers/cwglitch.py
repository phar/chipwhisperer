import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter
from  chipwhisperer.capture.scopes.cwhardware import ChipWhispererGlitch
from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI
from chipwhisperer.common.utils import util
from chipwhisperer.capture.scopes.openadc_interface.naeusbchip import OpenADCInterface_NAEUSBChip
import chipwhisperer.capture.scopes._qt as openadc_qt
from chipwhisperer.common.utils import util, timer, pluginmanager
from functools import partial


CODE_READ = 0x80
CODE_WRITE = 0xC0
ADDR_DATA = 33
ADDR_LEN = 34
ADDR_BAUD = 35
ADDR_EXTCLK = 38
ADDR_TRIGSRC = 39
ADDR_TRIGMOD = 40
ADDR_I2CSTATUS = 47
ADDR_I2CDATA = 48
ADDR_IOROUTE = 55


class GlitcherTemplate(Parameterized, Plugin):
	_name = "ChipWhisperer (CWLite/CW1200)"

	def __init__(self):
		self.getParams()
		self.prefix = ""
		self.enableGlitch = True
		self.connectStatus = util.Signal()
		self.connectStatus = util.Observable(False)
		self.oa = None
			#		if self.enableGlitch:
		self.getParams().addChildren([
		{'name':'HS-Glitch Out', 'type':'list', 'values':{'Enable (Low Power)':'B', 'Enable (High Power)':'A'},'set':partial(self.setGlitchOutputTarget), 'get':partial(self.getGlitchOutputTarget)},
		])

		if __debug__: logging.debug('Created: ' + str(self))

	def dummyfunc(self):
		return

	def __del__(self):
		"""Close system if needed"""
		self.close()
		if __debug__: logging.debug('Deleted: ' + str(self))


	def getStatus(self):
		return self.connectStatus.value()
	
	def dis(self):
		if not (self.cwa.getScope() != None and  "ChipWhisperer" in self.cwa.getScope().qtadc.sc.hwInfo.versions()[2]):
			self.scopetype.dis()
		self.connectStatus.setValue(False)

	def con(self,glitcher):
		self.cwa = CWCoreAPI.getInstance()
		
		if self.cwa.getScope() != None and   self.cwa.getScope().scopetype.getName() in ['NewAE USB (CWLite/CW1200)']:
			self.cwa.getScope().con()
			
			if "Lite" in self.cwa.getScope().qtadc.sc.hwInfo.versions()[2]:
				cwtype = "cwlite"
			elif "CW1200" in self.cwa.getScope().qtadc.sc.hwInfo.versions()[2]:
				cwtype = "cw1200"
			else:
				raise ValueError("this chipwhisperer does not have a glitch out")
	
			self.glitch = ChipWhispererGlitch.ChipWhispererGlitch(cwtype, self.cwa.getScope().scopetype, self.cwa.getScope().qtadc.sc)
			self.oa =  self.cwa.getScope().qtadc.sc
		else:
			self.qtadc = openadc_qt.OpenADCQt()
			scopes = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.scopes.openadc_interface", True, False, self.qtadc)
			self.scopetype = scopes[OpenADCInterface_NAEUSBChip._name]

			self.scopetype.con()

			# TODO Fix this hack .. it lives on!
			if hasattr(self.scopetype, "ser") and hasattr(self.scopetype.ser, "_usbdev"):
				self.qtadc.sc.usbcon = self.scopetype.ser._usbdev
							
			if "Lite" in self.qtadc.sc.hwInfo.versions()[2]:
				cwtype = "cwlite"
			elif "CW1200" in self.qtadc.sc.hwInfo.versions()[2]:
				cwtype = "cw1200"
			else:
				raise ValueError("this chipwhisperer does not have a glitch out")
			self.glitch = ChipWhispererGlitch.ChipWhispererGlitch(cwtype, self.scopetype, self.qtadc.sc)
			self.oa = self.qtadc.sc
	
	
		self.getParams().append(self.glitch.getParams())

		self.connectStatus.setValue(True)

	def setGlitchOutputTarget(self, out='A', enabled=False, blockSignal=None):
		if self.oa != None: #HACK
			data = self.oa.sendMessage(CODE_READ, ADDR_IOROUTE, Validate=False, maxResp=8)
			print out
			if out == 'A':
				bn = 0
			elif out == 'B':
				bn = 1
			else:
				raise ValueError("Invalid glitch output: %s" % str(out))

			if enabled:
				data[4] = data[4] | (1 << bn)
			else:
				data[4] = data[4] & ~(1 << bn)
			self.oa.sendMessage(CODE_WRITE, ADDR_IOROUTE, data)
		else:
			pass

	def getGlitchOutputTarget(self, out='A', blockSignal=None):
		if self.oa != None:
			resp = self.oa.sendMessage(CODE_READ, ADDR_IOROUTE, Validate=False, maxResp=8)
			if out == 'A':
				bn = 0
			elif out == 'B':
				bn = 1
			else:
				raise ValueError("Invalid glitch output: %s" % str(out))
			return resp[4] & (1 << bn)
		else:
			return 'A'

	def close(self):
		"""Close target, disconnect if required"""
		pass

	def glitchInit(self):
		"""Called once before each api grouping, do connect etc"""
		pass

	def glitchComplete(self):
		"""Called once complete api is complete"""
		pass

	def armPreScope(self):
		"""Called before arming scope, use to arm aux system"""
		self.glitch.armPreScope()
		pass

	def armPostScope(self):
		"""Called after arming scope, before sending trigger to target"""
		self.glitch.armPostScope()

	def glitchDone(self):
		"""Called once api is complete for a single trace"""
		pass

