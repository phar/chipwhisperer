	# Authors: Colin O'Flynn
#
# Find this and more at newae.com - this file is part of the chipwhisperer
# project, http://www.assembla.com/spaces/chipwhisperer
#
#    This file is part of chipwhisperer.
#
#    chipwhisperer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    chipwhisperer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with chipwhisperer.  If not, see <http://www.gnu.org/licenses/>.
#=================================================
import logging
import time
from _base import VisaScope


class VisaScopeInterface_MSO54831D(VisaScope):
	def __init__(self):
		self._name = "Agilent MSO 54831D"

		self._channels = {"Channel 1":"CHANnel1","Channel 2":"CHANnel2","Channel 3":"CHANnel3","Channel 4":"CHANnel4"}
		self._triggers = {"Channel 1":"CHANnel1","Channel 2":"CHANnel2","Channel 3":"CHANnel3","Channel 4":"CHANnel4","External":"EXT","External5":"EXT5","AC Line":"ACLine"}
		self._channel = "Channel 1"

		super(VisaScope, self).__init__()
			
    def currentSettings(self):
        self.visaInst.write(":TRIG:SWE AUTO")
        self.visaInst.write(":RUN")
        time.sleep(0.5)
        test = self.visaInst.ask_for_values(":WAVeform:PREamble?")
        self.visaInst.write(":TRIG:SWE TRIG")

        if test[4] != 0.0:
            self.XDisplayedOrigin = (test[12] - test[5]) / test[4]
            srange = test[11] / test[4]
        else:
            self.XDisplayedOrigin = 0.0
            srange = 0.0

        spoints = test[2]

        if srange < spoints:
            self.XDisplayedRange = srange
        else:
            self.XDisplayedRange = spoints

        self.XScale = self.visaInst.ask_for_values(":TIMebase:SCALe?")
        self.XScale = self.XScale[0]
        self.XOffset = self.visaInst.ask_for_values(":TIMebase:POSition?")
        self.XOffset = self.XOffset[0]
        self.YOffset = self.visaInst.ask_for_values(":%s:OFFSet?" % (self._channel))
        self.YOffset = self.YOffset[0]
        self.YScale = self.visaInst.ask_for_values(":%s:SCALe?" % (self._channel))
        self.YScale = self.YScale[0]

    def arm(self):
        self.visaInst.write(":DIGitize")

    def capture(self):
        xdstart = self.findParam("xdisporigin").getValue()
        xdrange = self.findParam("xdisprange").getValue()

        command = ":WAVeform:DATA?"

        if (xdstart != 0) or (xdrange != 0):
            command += " %d" % xdstart

            if xdrange != 0:
                command += ",%d" % xdrange

        #print command
        self.visaInst.write(command)
        data = self.visaInst.read_raw()

        #Find '#' which is start of frame
        start = data.find('#')

        if start < 0:
            raise IOError('Error in header')

        start += 1
        hdrlen = data[start]
        hdrlen = int(hdrlen)

        #print hdrlen

        start += 1
        datalen = data[start:(start+hdrlen)]
        datalen = int(datalen)
        #print datalen

        start += hdrlen

        #Each is two bytes
        wavdata = bytearray(data[start:(start + datalen)])

        self.datapoints = []

        for j in range(0, datalen, 2):
            data = wavdata[j] | (wavdata[j+1] << 8)

            if (data & 0x8000):
                data = -65536 + data

            self.datapoints.append(data)

        self.dataUpdated.emit(self.datapoints, 0)
        return False

    def support(self):
        return ["MSO54831D"]
