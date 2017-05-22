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

from .base import ScopeTemplate
from chipwhisperer.common.utils import pluginmanager
from chipwhisperer.common.utils.parameter import setupSetParam
from chipwhisperer.common.utils.pluginmanager import Plugin
import visa
import logging

class VisaScopeInterface(ScopeTemplate, Plugin):
	_name = "VISA Scope"

	def __init__(self):
		ScopeTemplate.__init__(self)

		self.scopes = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.scopes.visascope_interface", True, False)
		self.scopetype = None
		logging.info(self.scopes)
	
		self.params.addChildren([
			{'name':'VISA Resource String', 'key':'connStr', 'type':'str', 'value':'TCPIP::192.168.1.15::INSTR'},
			{'name':'Identified Instrument','key':'scopeid','type':'str', 'value':'None'},
			{'name':'Scope Driver','key':'scopedriver','type':'str', 'value':'None'},
			{'name':'Query Scope', 'key':'qscope', 'type':'action', 'action':self.queryscope},
			{'name':'Reset Scope', 'key':'rscope', 'type':'action', 'action':self.resetscope},
			{'name':'Sample Rate', 'key':'sampsper', 'type':'float', 'siPrefix': True, 'suffix': 'Sa/S', 'value':0},
			{'name':'X-Scale', 'key':'xscale', 'type':'float', 'value':0},
			{'name':'Y-Scale', 'key':'yscale', 'type':'float', 'value':0},
			 {'name':'Y-Offset', 'key':'yoffset', 'type':'float', 'step':1E-3, 'siPrefix': True, 'suffix': 'V', 'value':0},
			 {'name':'X-Offset', 'key':'xoffset', 'type':'float', 'step':1E-6, 'siPrefix': True, 'suffix': 'S','value':0},
								 
								 #			 {'name':'Download Offset', 'key':'xdisporigin', 'type':'int',  'limits':(0,1E9),'value':0},
								 #			 {'name':'Download Size', 'key':'xdisprange', 'type':'int', 'limits':(0,1E9),'value':0},
		])
		self.params.init()


	def queryscope(self,arg):
		vrm = visa.ResourceManager()
		self.visaInst = vrm.open_resource(self.findParam('connStr').getValue())
		self.detectedscopeid = self.visaInst.query("*IDN?").split(",")
		self.findParam('scopeid').setValue(str(self.detectedscopeid))
		logging.info(str(self.detectedscopeid))
		logging.info(self.scopes)
		self.updateScopeDriver()

	def resetscope(self,arg):
		vrm = visa.ResourceManager()
		self.visaInst = vrm.open_resource(self.findParam('connStr').getValue())
		self.visaInst.write("*RST")

	def updateScopeDriver(self):
		for s,v in self.scopes.items():
			if str(self.detectedscopeid[1]) in v.support():
				self.scopetype = self.scopes[v._name]
				self.scopetype.visaInst = self.visaInst
				self.scopetype.params = self.params
				self.scopetype.updateChannels()
				self.scopetype.updateTriggers()
				self.findParam('scopedriver').setValue(v._name)
				self.scopetype.updateCurrentSettings()
				self.scopetype.currentSettings()
				self.scopetype.dataUpdated.connect(self.newDataReceived)
				return

		self.scopetype = None
		self.findParam('scopedriver').setValue("No Support Detected")
	

	@setupSetParam("Example Strings")
	def exampleString(self, newstr):
		self.findParam('connStr').setValue(newstr)

	@setupSetParam("Scope Type")
	def setCurrentScope(self, scope, update=True):
		self.scopetype = scope


	def _con(self):
		self.queryscope("doesnt matter")
		if self.scopetype is not None:
			self.updateScopeDriver()
			self.scopetype.con(self.findParam('connStr').getValue())
			return True
		return False

	def _dis(self):
		if self.scopetype is not None:
			self.scopetype.dis()

	def arm(self):
		try:
			self.scopetype.arm()
		except Exception:
			self.dis()
			raise

	def capture(self):
		"""Raises IOError if unknown failure, returns 'False' if successful, 'True' if timeout"""
		return self.scopetype.capture()
