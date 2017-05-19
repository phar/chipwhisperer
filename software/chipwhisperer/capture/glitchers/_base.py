import logging

from chipwhisperer.common.utils.pluginmanager import Plugin
from chipwhisperer.common.utils.parameter import Parameterized, Parameter


class GlitcherTemplate(Parameterized, Plugin):
	_name = "None"

	def __init__(self):
		self.getParams()
		self.prefix = ""
	
	if __debug__: logging.debug('Created: ' + str(self))

	def setOpenADC(self, oa):
		pass

	def updatePartialReconfig(self, _=None):
	"""
	Reads the values set via the GUI & updates the hardware settings for partial reconfiguration. Checks that PR
	is enabled with self.prEnabled.
	"""
		pass

	def updateGlitchReadBack(self, test=False):
	"""Updates the readback register in the FPGA with glitch information, used for LCD update on CW1200 hardware."""
		pass

	@setupSetParam("Ext Trigger Offset")
	def setTriggerOffset(self, offset):
	"""Set offset between trigger event and glitch in clock cycles"""
		pass

	def triggerOffset(self):
	"""Get offset between trigger event and glitch in clock cycles"""
		pass

	@setupSetParam("Glitch Offset (fine adjust)")
	def setGlitchOffsetFine(self, fine):
	"""Set the fine glitch offset adjust, range -255 to 255"""
		pass


	@setupSetParam("Glitch Width (fine adjust)")
	def setGlitchWidthFine(self, fine):
	"""Set the fine glitch width adjust, range -255 to 255"""
		pass

	def getGlitchOffsetFine(self):
		pass

	def actionResetDCMs(self, _=None):
	"""Action for parameter class"""
		pass
	
	def resetDCMs(self, keepPhase=False):
	"""Reset the DCMs for the Glitch width & Glitch offset. Required after doing a PR operation"""
		pass
	
	def checkLocked(self, _=None):
	"""Check if the DCMs are locked and print results """
		pass
	
	@setupSetParam("Repeat")
	def setNumGlitches(self, num):
	"""Set number of glitches to occur after a trigger"""
		pass
	
	def numGlitches(self):
	"""Get number of glitches to occur after a trigger"""
		pass
	
	@setupSetParam("Glitch Trigger")
	def setGlitchTrigger(self, trigger):
	"""Set glitch trigger type (manual, continous, adc-trigger)"""
		pass
	
	def glitchTrigger(self):
	"""Get glitch trigger type"""
		pass
	
	@setupSetParam("Output Mode")
	def setGlitchType(self, t):
	"""Set glitch output type (ORd with clock, XORd with clock, clock only, glitch only)"""
		pass
	
	def glitchType(self):
		pass
	
	def glitchManual(self, _=None):
	"""
	Cause a single glitch event to occur. Depending on setting of numGlitches() this may mean
	multiple glitches in a row
	"""
		pass
	
	def glitchArm(self):
	"""If trigger is set to single-shot mode, this must be called before the selected trigger occurs"""
		pass
	
	@setupSetParam("Clock Source")
	def setGlitchClkSource(self, source):
		pass
	
	def glitchClkSource(self):
		pass
	
	def armPreScope(self):
	"""Called before scope trigger is armed"""
		pass
	
	def armPostScope(self):
	"""Called after scope trigger is armed"""
		pass
