import logging
import time
from _base import VisaScope
import struct
import numpy
#
# essentially the same as the 4000 rigol but i dont own  one of these
#
class VisaScopeInterface_RIGOLDS1000(VisaScope):
	_name = "Rigol DS1000Z,MSO1000Z"

	def __init__(self):
		super(self.__class__, self).__init__()

		self._channels = {"Channel 1":"CHANnel1","Channel 2":"CHANnel2","Channel 3":"CHANnel3","Channel 4":"CHANnel4"}
		self._triggers = {"Channel 1":"CHANnel1","Channel 2":"CHANnel2","Channel 3":"CHANnel3","Channel 4":"CHANnel4","External":"EXT","External5":"EXT5","AC Line":"ACLine"}
		self._channel = "Channel 1"


	def currentSettings(self):
		self.XScale = float(self.visaInst.query(":TIMebase:SCALe?"))
		logging.info("xscale: %.15f" % self.XScale)
		
		self.XOffset = float(self.visaInst.query(":TIMebase:MAIN:OFFSet?"))
		logging.info("xoffset: %.15f" % self.XOffset)
		
		self.YOffset = float(self.visaInst.query(":%s:OFFSet?" % (self._channel)))
		logging.info("yoffset: %.15f" % self.YOffset)
		
		self.YScale = float(self.visaInst.query(":%s:SCALe?" % (self._channel)))
		logging.info("yscale: %.15f" % self.YScale)
	
		self.SampSs = 1.0/self.XScale
		logging.info("srate %f" % self.SampSs)

	def arm(self):
		self.visaInst.write(":WAVeform:MODE NORmal")
		self.visaInst.write(":WAVeform:FORMat WORD")
		self.visaInst.write(":TRIGger:EDGe:SOURce %s"  % (self._trigger))
		self.visaInst.write(":WAVeform:SOURce %s"  % (self._channel))
		self.visaInst.write(":SINGle")

	def capture(self):
		state = str(self.visaInst.query(":TRIGger:STATus?"))
		logging.info(state)
		while str(state.strip()) not in ["TD","STOP"]:
				time.sleep(.5)
				state = str(self.visaInst.query(":TRIGger:STATus?").strip())
				logging.debug(state)

		self.visaInst.write(":WAVeform:BEGin")
		time.sleep(1)

		self.visaInst.write( ":WAVeform:DATA?")
		d =  self.visa_read_tekformat(format="h");
		self.datapoints = numpy.array(d)

		channelnum = 0
		logging.info(self.datapoints)
		self.dataUpdated.emit(channelnum, self.datapoints, 0, self.SampSs)
		return False

	def support(self):
		return ["MSO1104Z-S","MSO1104Z-S","MSO1104Z","MSO1174Z","MSO1074Z","MSO1074Z Plus","DS1104Z-S Plus","DS1104Z Plus","DS1074Z Plus","DS1054Z"]

