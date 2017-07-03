#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2016, NewAE Technology Inc
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

import copy
import os
import traceback
import sys
import logging
from chipwhisperer.capture.api.acquisition_controller import AcquisitionController
from chipwhisperer.capture.api.programmers import Programmer
from chipwhisperer.common.api.ProjectFormat import ProjectFormat
from chipwhisperer.common.results.base import ResultsBase
from chipwhisperer.common.ui.ProgressBar import *
from chipwhisperer.common.utils import util, pluginmanager
from chipwhisperer.common.utils.parameter import Parameterized, Parameter, setupSetParam
from chipwhisperer.common.utils.tracesource import TraceSource
from chipwhisperer.common.api.settings import Settings


class CWCoreAPI(Parameterized):
    """
    ChipWisperer API Class.
    Provides access to the most important parts of the tool.
    It has a singleton method called CWCoreAPI.getInstance() that returns a reference to the API instance.
    """

    __name__ = "ChipWhisperer-IOAdev"
    __organization__ = "NewAE Technology Inc."
    __version__ = "V3.3.0"
    _name = 'Generic Settings'
    instance = None

    def __init__(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        CWCoreAPI.instance = self
        self.sigNewProject = util.Signal()
        self.sigConfigurationChange = util.Signal() #change in the scope, target or glitcher, not settings
        self.sigConnectStatus = util.Signal()
        self.sigAttackChanged = util.Signal()
        self.sigNewInputData = util.Signal()
        self.sigNewTextResponse = util.Signal()
        self.sigNewCapture = util.Signal()
        self.sigPreArm = util.Signal()
        self.sigTraceDone = util.Signal()
        self.sigCampaignStart = util.Signal()
        self.sigCampaignDone = util.Signal()
        self.executingScripts = util.Observable(False)

        self.valid_glitchers = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.glitchers", True, True)
        self.valid_scopes = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.scopes", True, True)
        self.valid_targets =  pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.targets", True, True)
        self.valid_traces = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.common.traces", True, True)
        self.valid_aux = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.auxiliary", True, True)
        self.valid_acqPatterns =  pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.acq_patterns", True, True)
        self.valid_attacks = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.analyzer.attacks", True, False)
        self.valid_preprocessingModules = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.analyzer.preprocessing", False, True)
        self.valid_stages = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.xystages", True, True)
        self.settings = Settings()

        # Initialize default values
        self._project = self._stage =  self._traceFormat = self._scope = self._target = self._attack = self._acqPattern = self._glitcher = None
		
		##set sqlite as our new default
		# self._traceFormat = self.valid_traces['SQLite']
		
        self._attack = self.valid_attacks.get("CPA", None)
		# self._acqPattern = self.valid_acqPatterns["None"]
        self._auxList = [None]  # TODO: implement it as a list in the whole class
        self._numTraces = 50
        self._numTraceSets = 1

        self.params = Parameter(name='Generic Settings', type='group', addLoadSave=True).register()
        self.params.addChildren([
            {'name':'Scope Module', 'key':'scopeMod', 'type':'list', 'values':self.valid_scopes, 'get':self.getScope, 'set':self.setScope},
			{'name':'Glitcher Module', 'key':'glitchMod', 'type':'list', 'values':self.valid_glitchers, 'get':self.getGlitcher, 'set':self.setGlitcher},
			{'name':'Stage Module', 'key':'stageMod', 'type':'list', 'values':self.valid_stages, 'get':self.getStage, 'set':self.setStage},
			{'name':'Target Module', 'key':'targetMod', 'type':'list', 'values':self.valid_targets, 'get':self.getTarget, 'set':self.setTarget},
            {'name':'Trace Format', 'type':'list', 'values':self.valid_traces, 'get':self.getTraceFormat, 'set':self.setTraceFormat},
            {'name':'Auxiliary Module', 'type':'list', 'values':self.valid_aux, 'get':self.getAuxModule, 'set':self.setAux, 'visible':self.scopeIsChipwhisperer},
			{'name':'Key/Text Pattern Generator', 'type':'list', 'values':self.valid_acqPatterns, 'get':self.getAcqPattern, 'set':self.setAcqPattern},
            {'name':'Acquisition Settings', 'type':'group', 'children':[
                    {'name':'Number of Traces', 'type':'int', 'limits':(1, 1E9), 'get':self.getNumTraces, 'set':self.setNumTraces, 'linked':['Traces per Set']},
                    {'name':'Number of Sets', 'type':'int', 'limits':(1, 1E6), 'get':self.getNumTraceSets, 'set':self.setNumTraceSets, 'linked':['Traces per Set'], 'tip': 'Break acquisition into N sets, '
                     'which may cause data to be saved more frequently. The default capture driver requires that NTraces/NSets is small enough to avoid running out of system memory '
                     'as each segment is buffered into RAM before being written to disk.'},
                    {'name':'Traces per Set', 'type':'int', 'readonly':True, 'get':self.tracesPerSet},
            ]},
        ])


        self.glitchParam = Parameter(name="Glitcher Settings", type='group', addLoadSave=True).register()
        self.params.getChild('Glitcher Module').stealDynamicParameters(self.glitchParam)

        self.scopeParam = Parameter(name="Scope Settings", type='group', addLoadSave=True).register()
        self.params.getChild('Scope Module').stealDynamicParameters(self.scopeParam)

        self.targetParam = Parameter(name="Target Settings", type='group', addLoadSave=True).register()
        self.params.getChild('Target Module').stealDynamicParameters(self.targetParam)

        self.traceParam = Parameter(name="Trace Settings", type='group', addLoadSave=True).register()
        self.params.getChild('Trace Format').stealDynamicParameters(self.traceParam)

        self.auxParam = Parameter(name="Aux Settings", type='group', addLoadSave=True).register()
        self.params.getChild('Auxiliary Module').stealDynamicParameters(self.auxParam)

        self.stageParam = Parameter(name="Stage Settings", type='group', addLoadSave=True).register()
        self.params.getChild('Stage Module').stealDynamicParameters(self.stageParam)

        # self.attackParam = Parameter(name="Attack Settings", type='group')
        # self.params.getChild('Attack Module').getDynamicParameters(self.attackParam)

        self.newProject()

    def scopeIsChipwhisperer(self):
		if self._scope in ["ChipWhisperer/OpenADC"]:
			return True
		return False

    def getResults(self, name):
        """Return the requested result widget. It should be registered."""
        return ResultsBase.registeredObjects[name]


    def getStage(self):
        """Return the current stage module object."""
        return self._stage
	
    @setupSetParam("Stage Module")
    def setStage(self, driver):
        """Set the current stage module object."""
        if self.getStage():
            self.getStage().dis()
		
        if self._stage != driver:
            self._stage = driver
            self.sigConfigurationChange.emit()
		
        if self.getStage():
            self.getStage().connectStatus.connect(self.sigConnectStatus.emit)

    def getGlitcher(self):
        """Return the current glitcher module object."""
        return self._glitcher

    @setupSetParam("Glitcher Module")
    def setGlitcher(self, driver):
        """Set the current glitcher module object."""
        if self.getGlitcher():
            self.getGlitcher().dis()
        if self._glitcher != driver:
            self._glitcher = driver
            self.sigConfigurationChange.emit()
	
        if self.getGlitcher():
            self.getGlitcher().connectStatus.connect(self.sigConnectStatus.emit)

    def getScope(self):
        """Return the current scope module object."""
        return self._scope

    @setupSetParam("Scope Module")
    def setScope(self, driver):
        """Set the current scope module object."""
        if self.getScope():
            self.getScope().dis()
		
        if self._scope != driver:
            self._scope = driver
            self.sigConfigurationChange.emit()

        if self.getScope():
            self.getScope().connectStatus.connect(self.sigConnectStatus.emit)

    def getTarget(self):
        """Return the current target module object."""
        return self._target

    @setupSetParam("Target Module")
    def setTarget(self, driver):
        """Set the current target module object."""
        if self.getTarget():
			self.getTarget().dis()
		
        if self._target != driver:
            self._target = driver
            self.sigConfigurationChange.emit()
	
        if self.getTarget():
            self.getTarget().newInputData.connect(self.sigNewInputData.emit)
            self.getTarget().connectStatus.connect(self.sigConnectStatus.emit)

    def getAuxModule(self):
        """Return a list with the auxiliary modules."""
        return self._auxList[0]

    def getAuxList(self):
        """Return a list with the auxiliary modules."""
        return self._auxList

    @setupSetParam("Auxiliary Module")
    def setAux(self, aux):
        """Set the first aux module. Will be updated to support more modules."""
        self._auxList = [aux]

    def getAcqPattern(self):
        """Return the selected acquisition pattern."""
        return self._acqPattern

    @setupSetParam("Key/Text Pattern")
    def setAcqPattern(self, pat):
        """Set the current acquisition pattern."""
        self._acqPattern = pat
        if self._acqPattern is not None:
            self._acqPattern.getParams().remove()
            self.getParams().append(self._acqPattern.getParams())

    def getTraceFormat(self):
        """Return the selected trace format."""
        return self._traceFormat

    @setupSetParam("Trace Format")
    def setTraceFormat(self, format):
        """Set the current trace format for acquisition."""
        self._traceFormat = format

    def getAttack(self):
        """Return the current attack module. NOT BEING USED AT THE MOMENT"""
        return self._attack

    def setAttack(self, attack):
        """Set the current attack module. NOT BEING USED AT THE MOMENT"""
        self._attack = attack
        if self.getAttack():
            self.getAttack().setTraceLimits(self.project().traceManager().numTraces(), self.project().traceManager().numPoints())
        self.sigAttackChanged.emit()

    def project(self):
        """Return the current opened project"""
        return self._project

    def setProject(self, proj):
        """Set the current opened project"""
        self._project = proj
        self.sigNewProject.emit()

    def newProject(self):
        """Create a new project"""
        self.setProject(ProjectFormat())
        self.project().setProgramName(self.__name__)
        self.project().setProgramVersion(self.__version__)
        print self.project().datadirectory
        #self.params.load(os.path.join(self.project().datadirectory, "settings.cwset"))

    def openProject(self, fname):
        """Open project file"""
        self.newProject()
        self.project().load(fname)
        logging.info(dir(self.project()))
        logging.info(TraceSource.registeredObjects["Trace Management"])
        logging.info(dir(TraceSource.registeredObjects["Trace Management"]))
        TraceSource.registeredObjects["Trace Management"].getTrace(0)
				
        try:
            ResultsBase.registeredObjects["Trace Output Plot"].setTraceSource(TraceSource.registeredObjects["Trace Management"])
        except KeyError:
            pass

    def saveProject(self, fname=None):
        """Save the current opened project to file"""
        if fname is not None:
            self.project().setFilename(fname)
				
        self.project().save()

    def connectStage(self):
        """Connect to the selected stage"""
        try:
            if self.getStage():
                self.getStage().con()
        except Warning:
            sys.excepthook(*sys.exc_info())
            return False
        return True

    def disconnectStage(self):
        """Disconnect the current stage"""
        self.getStage().dis()
	
	
	
    def connectScope(self):
        """Connect to the selected scope"""
        try:
            if self.getScope():
                self.getScope().con()
                try:
                    # Sets the Plot Widget input (if it exists) to the last added TraceSource
                    ResultsBase.registeredObjects["Trace Output Plot"].setTraceSource(
                        TraceSource.registeredObjects[next(reversed(TraceSource.registeredObjects))])
                except KeyError:
                    pass

        except Warning:
            sys.excepthook(*sys.exc_info())
            return False
        return True

    def disconnectScope(self):
        """Disconnect the current scope"""
        self.getScope().dis()

    def connectTarget(self):
        """Connect to the selected target"""
        try:
            if self.getTarget():
                self.getTarget().con(scope=self.getScope())
        except Warning:
            sys.excepthook(*sys.exc_info())
            return False
        return True

    def disconnectTarget(self):
        """Disconnect the current target"""
        self.getTarget().dis()

    def connectGlitcher(self):
        """Connect to the selected glitcher"""
        try:
            if self.getGlitcher():
                self.getGlitcher().con(glitcher=self.getGlitcher())
        except Warning:
            sys.excepthook(*sys.exc_info())
            return False
        return True

    def disconnectTrigger(self):
        """Disconnect the current target"""
        self.getGlitcher().dis()

    def doConDis(self):
        """DEPRECATED: It is here just for compatibility reasons"""
        logging.warning('Method doConDis() is deprecated... use connect() or disconnect() instead')
        return self.connect()

    def connect(self):
        """Connect both: scope and target"""
        return self.connectScope() and self.connectTarget()

    def disconnect(self):
        """Disconnect both: scope and target"""
        self.disconnectScope()
        self.disconnectTarget()

    def getNumTraces(self):
        """Return the total number or traces for acquisition purposes"""
        return self._numTraces

    @setupSetParam("Number of Traces")
    def setNumTraces(self, n):
        """Set the total number or traces for acquisition purposes"""
        self._numTraces = int(float(n))

    def getNumTraceSets(self):
        """Return the number of sets/segments"""
        return self._numTraceSets

    @setupSetParam("Number of Sets")
    def setNumTraceSets(self, s):
        """Set the number of sets/segments"""
        self._numTraceSets = s

    def tracesPerSet(self):
        """Return the number of traces in each set/segment"""
        return int(self._numTraces / self._numTraceSets)

    def capture1(self):
        """Capture one trace"""
        starttime = datetime.now()
        try:
            self.sigNewCapture.emit()
            prefix = starttime.strftime('%Y.%m.%d-%H.%M.%S') + "_"
            ac = AcquisitionController(0, prefix, self)
            ac.sigPreArm.connect(self.sigPreArm.emit)
            ac.sigNewTextResponse.connect(self.sigNewTextResponse.emit)
            if self.getTarget():
                self.getTarget().init()
            return ac.doSingleReading()
        except Warning:
            sys.excepthook(*sys.exc_info())
            return False

    def captureM(self, progressBar=None):
        """Capture multiple traces and save its result"""
        if not progressBar: progressBar = ProgressBarText()

        with progressBar:
            progressBar.setStatusMask("Current Segment = %d Current Trace = %d", (0,0))
            progressBar.setMaximum(self._numTraces)

            waveBuffer = None
            tcnt = 0
            setSize = self.tracesPerSet()
            for i in range(0, self._numTraceSets):
                if progressBar.wasAborted(): break
                starttime = datetime.now()
                prefix = starttime.strftime('%Y.%m.%d-%H.%M.%S') + "_"

                for aux in self._auxList:
                    if aux:
                        aux.setPrefix(prefix)

                self.sigNewCapture.emit()

                ac = AcquisitionController(i, prefix, self)

                ac.sigPreArm.connect(self.sigPreArm.emit)
                ac.setMaxtraces(setSize)
				
                ac.sigNewTextResponse.connect(self.sigNewTextResponse.emit)
                ac.sigTraceDone.connect(self.sigTraceDone.emit)
				
                self.sigCampaignStart.emit(prefix)
				
                ac.doReadings(tracesDestination=self.project().traceManager(), progressBar=progressBar)

                self.sigCampaignDone.emit()
                tcnt += setSize

                if progressBar.wasAborted():
                    break

        return True

    def runScriptModule(self, mod, funcName="run"):
        """Execute the function in the Plugin classes of the specified module"""
        try:
            classes = pluginmanager.getPluginClassesFromModules([mod])
            if len(classes) == 0:
                raise Warning("No UserScriptBase class found")
            for c in classes:
                self.runScriptClass(c, funcName)
        except Exception as e:
            sys.excepthook(Warning, "Could not execute Script Module %s: '%s:%s'" %
                             (str(mod),
                              "".join(traceback.format_exception_only(sys.exc_info()[0], e.message)).rstrip("\n "),
                              str(e).rstrip("\n ")
                              ), sys.exc_info()[2])

    def runScriptClass(self, scriptClass, funcName="run"):
        """Execute the funcName function in the specified class."""
        try:
            self.executingScripts.setValue(True)
            m = scriptClass(self)
            if funcName is not None:
                eval('m.%s()' % funcName)
        except Exception as e:
                sys.excepthook(Warning, "Could not execute method %s in script class %s: '%s:%s'" %
                               (funcName,
                                scriptClass.__name__,
                                "".join(traceback.format_exception_only(sys.exc_info()[0], e.message)).rstrip("\n "),
                                str(e).rstrip("\n ")
                                ), sys.exc_info()[2])
        finally:
            self.executingScripts.setValue(False)

    def getParameter(self, path):
        """Return the value of a registered parameter"""
        return Parameter.getParameter(path)

    def setParameter(self, pathAndValue):
        """Set the parameter value, given its path. It should be registered in Parameter.registeredParameters"""
        Parameter.setParameter(pathAndValue)

    @staticmethod
    def getInstance():
        """Implements the singleton pattern/anti-pattern. Returns a reference to the API instance."""
        return CWCoreAPI.instance
