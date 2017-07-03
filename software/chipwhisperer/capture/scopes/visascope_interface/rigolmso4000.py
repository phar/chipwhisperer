import logging
import time
from _base import VisaScope, Channel
from chipwhisperer.common.utils import util
import struct
from chipwhisperer.common.utils.parameter import Parameterized, Parameter, setupSetParam
import numpy

class VisaScopeInterface_RIGOLDS4000(VisaScope):
	_name = "Rigol DS4000"

	def __init__(self):
		super(self.__class__, self).__init__()
		self._channels = {"Channel 1":"CHANnel1","Channel 2":"CHANnel2","Channel 3":"CHANnel3","Channel 4":"CHANnel4"}
		self._triggers = {"Channel 1":"CHANnel1","Channel 2":"CHANnel2","Channel 3":"CHANnel3","Channel 4":"CHANnel4","External":"EXT","External5":"EXT5","AC Line":"ACLine"}
		self.XScale = 0
		self.YScale = 0
		self.XOffset = 0
		self.YOffset = 0


	def getSampleRate(self):
		self.srate = int(float(self.visaInst.query(":ACQuire:SRATe? %s" % self._channels[self._channel])))
		return self.srate

	def forcetrigger(self):
		self.visaInst.write(":FORCetrig")

	def getCurrentSettings(self):
		self.XScale = float(self.visaInst.query(":TIMebase:SCALe?"))
		self.XOffset = float(self.visaInst.query(":TIMebase:MAIN:OFFSet?"))
		self.YScale = float(self.visaInst.query(":%s:SCALe?" % (self._channels[self._channel])))
		self.YOffset = float(self.visaInst.query(":%s:OFFSet?" % (self._channels[self._channel])))
		self.SampSs = 1.0/self.XScale
		return(self.XScale,self.XOffset,self.YScale,self.YOffset,self.SampSs)

	def arm(self):
		self.visaInst.write(":WAVeform:MODE NORmal")
		self.visaInst.write(":WAVeform:FORMat WORD")
		self.visaInst.write(":TRIGger:EDGe:SOURce %s"  % (self._triggers[self._trigger]))
		self.visaInst.write(":WAVeform:SOURce %s"  % (self._channels[self._channel]))
		self.visaInst.write(":SINGle")

	def capture(self):
		state = str(self.visaInst.query(":TRIGger:STATus?"))
		while str(state.strip()) not in ["TD","STOP"]:
				util.updateUI()
				time.sleep(.5)
				state = str(self.visaInst.query(":TRIGger:STATus?").strip())
				logging.debug(state)

		self.visaInst.write(":WAVeform:BEGin")
		time.sleep(1)

		self.visaInst.write( ":WAVeform:DATA?")
		d =  self.visa_read_tekformat(format="h");
		self.datapoints = numpy.array(d)
		return (self.datapoints, 0, self.SampSs)


	def getMagnitudeScale(self):
		self.getCurrentSettings()
		return self.YScale
	
	def setMagnitudeScale(self, scale):
		pass
	
	def getMagnitudeOffset(self):
		self.getCurrentSettings()
		return self.XScale

	def	setMagnitudeOffset(self, offset):
		pass

	def getTimeOffset(self):
		self.getCurrentSettings()
		return self.XOffset
	
	def	setTimeOffset(self, offset):
		pass

	def support(self):
		return ["DS4034","DS4054","DS4052","DS4032","DS4024","DS4022","DS4014","DS4012"]

