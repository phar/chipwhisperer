import logging
import time
from _base import VisaScope
import struct

class VisaScopeInterface_TEK3000(VisaScope):
	_name = "Tektronix MSO/DPO 3000"

	def __init__(self):

		self.xScales = {"500 mS":500E-3, "200 mS":200E-3, "100 mS":100E-3, "50 mS":50E-3,
				   "20 mS":20E-3, "10 mS":10E-3, "5 mS":5E-3, "2 mS":2E-3, "1 mS":1E-3,
				   "500 uS":500E-6, "200 uS":200E-6, "100 uS":100E-6, "50 uS":50E-6,
				   "20 uS":20E-6, "10 uS":10E-6, "5 uS":5E-6, "2uS":2E-6, "1 uS":1E-6}

		self.yScales = {"10 V":10, "5 V":5, "2 V":2, "500 mV":500E-3, "200 mV":200E-3, "100 mV":100E-3,
				   "50 mV":50E-3, "20 mV":20E-3, "10 mV":10E-3, "5 mV":5E-3}

		self.SampSs = 0
		self.YOffset = 0
		self.XOffset = 0
		self.header = []
		self.XScale = 1.0
		self.YScale = 1.0
		self.YOffset = 0
		self.XOffset = 0
		
		self._channels = {"CHANnel1":"CH1","CHANnel2":"CH2","CHANnel3":"CH3","CHANnel4":"CH4"}
		self._triggers = ["CHANnel1","CHANnel2","CHANnel3","CHANnel4","EXT","EXT5","ACLine"]

		super(self.__class__, self).__init__()


	def currentSettings(self):
		self.XScale = float(self.visaInst.query("HORizontal:SCAle?"))
		logging.info("xscale: %.15f" % self.XScale)
		
		self.XOffset = float(self.visaInst.query("HORizontal:SCAle?"))
		logging.info("xoffset: %.15f" % self.XOffset)
		
		self.YOffset = float(self.visaInst.query("CH1:OFFSet?"))
		logging.info("yoffset: %.15f" % self.YOffset)
		
		self.YScale = float(self.visaInst.query("CH1:SCAle?"))
		logging.info("yscale: %.15f" % self.YScale)
	
		self.SampSs = 1.0/self.XScale
		logging.info("srate %f" % self.SampSs)

	def arm(self):
		self.visaInst.write(":WAVeform:MODE NORmal")
		self.visaInst.write(":WAVeform:FORMat WORD")
		self.visaInst.write(":SINGle")


	def capture(self):
		self.visaInst.write("DATa:SOUrce CH1")
		self.visaInst.write( "CURVe?")
		d =  self.visa_read_tekformat(format="h");
		self.datapoints = d

#		self.visaInst.write( ":WAVeform:DATA?")
#		d =  self.visa_read_tekformat(format="h");
#		self.datapoints += d

		channelnum = 0
		
		self.dataUpdated.emit(channelnum, self.datapoints, 0, self.SampSs)
		return False

	def support(self):
		return ["MSO3012","DPO3012","MSO3014","DPO3014","MSO3032","DPO3032","MSO3034","DPO3034","DPO3052","MOS3053", "DPO3054"]
