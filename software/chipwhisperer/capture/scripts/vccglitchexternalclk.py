#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
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

from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI  # Import the ChipWhisperer API
from chipwhisperer.common.scripts.base import UserScriptBase


class UserScript(UserScriptBase):
	_name = "Basic Glitching with External Clock"
	_description = "Configures basic options to enable glitching using an external oscillator"

	def __init__(self, api):
		super(UserScript, self).__init__(api)

	def run(self):
		# User commands here
		self.api.connect()

		# Example of using a list to set parameters. Slightly easier to copy/paste in this format
		lstexample = [['Results', 'Trace Output Plot', 'Point Range', (0, -1)],
					['Glitch Module', 'Output Mode', 'Glitch Only'],
					['CW Extra Settings', 'Target HS IO-Out', 'Glitch Module'],
					]

		# Download all hardware setup parameters
		#	for cmd in lstexample: self.api.setParameter(cmd)

		self.api.glitchParam.addChildren([
            #{'name':'Clock Source', 'type':'list', 'values':{'Target IO-IN':self.CLKSOURCE0_BIT, 'CLKGEN':self.CLKSOURCE1_BIT},'set':self.setGlitchClkSource, 'get':self.glitchClkSource},
            #{'name':'Glitch Width (as % of period)', 'key':'width', 'type':'float', 'limits':(0, 100), 'step':0.39062, 'readonly':True, 'value':10, 'action':self.updatePartialReconfig},
            #{'name':'Glitch Width (fine adjust)', 'key':'widthfine', 'type':'int', 'limits':(-255, 255), 'set':self.setGlitchWidthFine, 'get':self.getGlitchWidthFine},
            #{'name':'Glitch Offset (as % of period)', 'key':'offset', 'type':'float', 'limits':(0, 100), 'step':0.39062, 'readonly':True, 'value':10, 'action':self.updatePartialReconfig},
            #{'name':'Glitch Offset (fine adjust)', 'key':'offsetfine', 'type':'int', 'limits':(-255, 255), 'set':self.setGlitchOffsetFine, 'get':self.getGlitchOffsetFine},
            #{'name':'Glitch Trigger', 'type':'list', 'values':{'Ext Trigger:Continous':1, 'Manual':0, 'Continuous':2, 'Ext Trigger:Single-Shot':3}, 'set':self.setGlitchTrigger, 'get':self.glitchTrigger},
            {'name':'Single-Shot Arm', 'type':'list', 'key':'ssarm', 'values':{'Before Scope Arm':1, 'After Scope Arm':2}, 'value':2},
            #{'name':'Ext Trigger Offset', 'type':'int', 'range':(0, 50000000), 'set':self.setTriggerOffset, 'get':self.triggerOffset},
            #{'name':'Repeat', 'type':'int', 'limits':(1,255), 'set':self.setNumGlitches, 'get':self.numGlitches},
            #{'name':'Manual Trigger / Single-Shot Arm', 'type':'action', 'action': self.glitchManual},
            #{'name':'Output Mode', 'type':'list', 'values':{'Clock XORd':0, 'Clock ORd':1, 'Glitch Only':2, 'Clock Only':3, 'Enable Only':4}, 'set':self.setGlitchType, 'get':self.glitchType},
            #{'name':'Read Status', 'type':'action', 'action':self.checkLocked},
            #{'name':'Reset DCM', 'type':'action', 'action':self.actionResetDCMs},
		])

if __name__ == '__main__':
	import chipwhisperer.capture.ui.CWCaptureGUI as cwc         # Import the ChipWhispererCapture GUI
	from chipwhisperer.common.utils.parameter import Parameter  # Comment this line if you don't want to use the GUI
	Parameter.usePyQtGraph = True                               # Comment this line if you don't want to use the GUI
	api = CWCoreAPI()                                           # Instantiate the API
	app = cwc.makeApplication("Capture")                        # Change the name if you want a different settings scope
	gui = cwc.CWCaptureGUI(api)                                 # Comment this line if you don't want to use the GUI
	api.runScriptClass(UserScript)                              # Run the User Script (executes "run()" by default)
	app.exec_()                                                 # Comment this line if you don't want to use the GUI
