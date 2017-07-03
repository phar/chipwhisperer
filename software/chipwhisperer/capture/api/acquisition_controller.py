#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
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
import copy
from chipwhisperer.common.utils import util
from datetime import datetime, date, time


class AcquisitionController:
	def __init__(self,setid, prefix, api):
		self.sigTraceDone = util.Signal()
		self.sigNewTextResponse = util.Signal()
		self.sigPreArm = util.Signal()
		self.currentTrace = 0
		self.maxtraces = 1

		self.api = api
		self.attackvars = {"startdate":datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
		self.setid = setid
		self.prefix = prefix
		self.target = self.api.getTarget()
		self.format = self.api.getTraceFormat()
		self.scope = self.api.getScope()
		self.glitcher = self.api.getGlitcher()
		self.stage = self.api.getStage()
		self.auxList = self.api._auxList
		self.keyTextPattern = self.api.getAcqPattern()
		self.writer = self.api.getTraceFormat()
		
		if self.target != None and self.keyTextPattern != None:
			self.keyTextPattern.setTarget(self.target)

		if self.keyTextPattern != None:
			self.attackvars.update(self.keyTextPattern.initAttackVars().copy())

		if self.auxList is not None:
			for aux in self.auxList:
				if aux:
					aux.captureInit()


	def SetupNewTrace(self):
		"""Return a new trace object for the specified format."""
			#		if self.format is None:
			#			raise Warning("No trace format selected.")
		if self.format != None:
			self.writer = copy.copy(self.format)
			self.writer.clear()
			starttime = datetime.now()
			self.writer.config.setConfigFilename(self.api.getInstance().project().datadirectory + "traces/config_" + self.prefix + ".cfg") #fixme, I dont know what this does
			self.writer.config.setAttr("prefix", self.prefix)
			self.writer.config.setAttr("date", starttime.strftime('%Y-%m-%d %H:%M:%S'))


	def targetDoTrace(self):
		if self.target is None or self.target.getName() == "None":
			return []

		if "go" in self.target.script_states:
			self.target.run_expect_state("go")
		
		timeout = 50
		while self.target.isDone() is False and timeout:
			timeout -= 1
			time.sleep(0.01)

		if timeout == 0:
			logging.warning('Target timeout')

#		textout = self.target.readOutput()
		if "final" in self.target.script_states:
			textout = self.target.run_expect_state("final")
		
#		try:
#			logging.debug("PlainText: " + ''.join(format(x, '02x') for x in self.attackvars["textin"]))
#		except:
#			pass
#
#		try:
#			logging.debug("CipherText: " + ''.join(format(x, '02x') for x in self.attackvars["textout"]))
#		except:
#			pass

		return textout

	def doSingleReading(self):
		self.SetupNewTrace()
			
		# Set mode
		if self.auxList:
			for aux in self.auxList:
				if aux:
					self.sigPreArm.emit()
					aux.traceArm()

		if self.target:
			self.target.reinit()

		if self.stage:
			self.stage.enableStageMotors()
			(nx,ny) = self.stage.scanNext()
			self.stage.setCurrentCoord((nx,ny))
			self.stage.stageMovementLatencyPause()
			self.stage.disableStageMotors()
			(nx,ny) = self.stage.getCurrentCoord() #some stages may differ somewhat from the requested position
			self.attackvars["x"] = nx
			self.attackvars["y"] = ny

		if self.scope:
			self.sigPreArm.emit()
			self.scope.arm()

		if self.auxList:
			for aux in self.auxList:
				if aux:
					aux.traceArmPost()
		
		if  self.keyTextPattern != None:
			self.attackvars.update(self.keyTextPattern.nextAttackVars().copy())

		if self.target:
			# Get key / plaintext now
			if "init" in self.target.script_states:
				self.target.run_expect_state("init")

			if "configure" in self.target.script_states:
				self.target.run_expect_state("configure")
				
			# Load input, start encryption, get output
			self.attackvars["textout"] = self.targetDoTrace() #does this generate textout?
		
			self.sigNewTextResponse.emit(self.attackvars)

		logging.info(self.attackvars)

		# Get ADC reading
		if self.scope:
			try:
				ret = self.scope.capture()
				if ret:
					logging.debug('Timeout happened during acquisition.')
				return not ret
			except IOError as e:
				logging.error('IOError: %s' % str(e))
				return False

		if self.auxList:
			for aux in self.auxList:
				if aux:
					aux.traceDone()
		return True

	def setMaxtraces(self, maxtraces):
		self.maxtraces = maxtraces

	def doReadings(self, tracesDestination=None, progressBar=None):
		if self.format is None:
			raise Warning("No trace format selected.")
		
		if self.keyTextPattern:
			self.keyTextPattern.initAttackVars()

		if self.writer:
			self.writer.prepareTraceSet(self.setid)

		if self.auxList:
			for aux in self.auxList:
				if aux:
					self.sigPreArm.emit()
					aux.traceArm()

		if self.target:
			self.target.init()

		if self.stage:
			self.stage.newScan()

		self.currentTrace = 0
		while self.currentTrace < self.maxtraces:
			if self.doSingleReading():
				try:
					if self.writer:
						if self.scope != None:
							for (name,channel) in self.scope.scopechannels.items():
								if channel:
									self.writer.addTrace(channel, self.attackvars)
		
				except ValueError as e:
					logging.warning('Exception caught in adding trace %d, trace skipped.' % self.currentTrace)
					logging.debug(str(e))
				
				self.sigTraceDone.emit()
				self.currentTrace += 1
				progressBar.updateStatus(self.setid*self.maxtraces + self.currentTrace, (self.setid, self.currentTrace))
			else:
				util.updateUI()  # Check if it was aborted

			if progressBar is not None:
				if progressBar.wasAborted():
					break

		if self.auxList:
			for aux in self.auxList:
				if aux:
					aux.captureComplete()

		if self.writer != None and self.scope != None:
			# Don't clear trace as we re-use the buffer
			self.writer.config.setAttr("scopeSampleRate", self.scope.getSampleRate())
			self.writer.closeAll(clearTrace=False)
			if tracesDestination:
				tracesDestination.appendSegment(self.writer)
