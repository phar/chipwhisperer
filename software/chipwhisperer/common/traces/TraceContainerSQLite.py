import logging
import pickle
import numpy as np
from _base import TraceContainer
from _cfgfile import makeAttrDict
import json
import sqlite3
import os
from chipwhisperer.common.api.CWCoreAPI import CWCoreAPI

try:
	import sqlite3 as sql
except ImportError, e:
	print "sqlite3 is required if you would like to use sqlite trace containers"
	raise ImportError(e)

class TraceContainerSQLite(TraceContainer):
	_name = "SQLite"

	def __init__(self, openMode = False):
		super(TraceContainerSQLite, self).__init__()
		self.db = None
		self.idOffset = 0
		self.lastId = 0
		self.openMode = openMode
		self.fmt = None
		self.setid = None
			#	self.getParams().addChildren([{'name':'SQLite Configuration', 'type':'group', 'children':[
	#                       {'name':'Table Name', 'key':'tableName', 'type':'str', 'value':'CWTable1', 'readonly':True}
	#			  ]}])

		#Format name must agree with names from TraceContainerFormatList
		self.config.setAttr("format", "sqlite")
		

	def setDirectory(self, directory):
		self.dir = directory
		os.mkdir(directory)
	
	def makePrefix(self, mode='prefix'):
		if mode == 'prefix':
			prefix = self.config.attr('prefix')
			if prefix == "" or prefix is None:
				raise AttributeError("Prefix attribute not set in trace config")

			#Drop everything but underscore (_) for table name
			prefix = "tracedb_" + prefix
			prefix = prefix.replace("-","_")
			prefix = ''.join(c for c in prefix if c.isalnum() or c in("_"))
			return prefix
		raise ValueError("Invalid mode: %s"%mode)

	def prepareTraceSet(self,setid):
		self.setid = setid
		self.con()
	
	def prepareDB(self):
		self.db.execute("create table IF NOT EXISTS cwtraces_%d (trace_id integer PRIMARY KEY AUTOINCREMENT,trace   text, trace_data text,  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);" % self.setid )

	def con(self):
		logging.info(dir(self))
		logging.info(dir(self.config))
		logging.info(self.configfile)
		self.dbfile = CWCoreAPI.getInstance().project().getDataFilepath("traces.sqlite3")["abs"]
		logging.info(CWCoreAPI.getInstance().project())


		logging.info("waveform database %s" % self.dbfile)
		self.db = sqlite3.connect(self.dbfile) #fixme.. in project directory!
		self.prepareDB()
		self.db.execute("PRAGMA foreign_keys = ON;")

		cx = self.db.cursor()
		cx.execute("select sqlite_version();")
		result = cx.fetchone()[0]
		logging.info('SQLite Version: %s' % result)


	def updatePointsTraces(self):
		cx = self.db.cursor()
		cx.execute("SELECT COUNT(*) FROM cwtraces_%d"  % self.setid )
		self._numTraces = cx.fetchone()[0]

		cx = self.db.cursor()
		cx.execute("SELECT trace FROM cwtraces_%d  order by trace_id LIMIT 1"  % self.setid)
		wav = cx.fetchone()[0]
		self._numPoints = self.formatWave(wav, read=True).shape[0]

	def updateConfigData(self):
		if self.db != None:
			cx = self.db.cursor()
			cx.execute("SELECT COUNT(*) FROM cwtraces_%d" % self.setid )
			self._numTraces = cx.fetchone()[0]
			self.config.setAttr('numTraces', self._numTraces)

			cx = self.db.cursor()
			cx.execute("SELECT trace FROM cwtraces_%d  order by trace_id  LIMIT 1" % self.setid)
			wav = cx.fetchone()[0]
			self._numPoints = self.formatWave(wav, read=True).shape[0]
			self.config.setAttr('numPoints', self._numPoints)

	def numTraces(self, update=True):
		if update:
			self.updateConfigData()
		return self._numTraces

	def numPoints(self, update=False):
		if update:
			self.updateConfigData()
		return self._numPoints

	def loadAllConfig(self):
		for p in self.getParams.traceParams[0]['children']:
			try:
				val = self.config.attr(p["key"], "sqlite")
				self.getParams.findParam(p["key"]).setValue(val)
			except ValueError:
				pass
			#print "%s to %s=%s"%(p["key"], val, self.getParams.findParam(p["key"]).getValue())

	def loadAllTraces(self, path=None, prefix=None):
		self.updateConfigData()

	def formatWave(self, wave, read=False):
		
		if read == False:
			return json.dumps(wave.tolist())
		else:
			return np.array(json.loads(wave))

	def addTrace(self, trace, attackvars, dtype=np.double,channelNum=None):
		jattackvars = json.dumps(attackvars)
		cx = self.db.cursor()
		cx.execute("INSERT INTO cwtraces_%d (trace_data, trace) VALUES(?, ?);"  % self.setid ,( jattackvars ,self.formatWave(trace)))
		self.db.commit()

	def saveAll(self):
		#Save attributes from config settings
		for t in self.getParams.traceParams[0]['children']:
			self.config.setAttr(t["key"],  self.getParams.findParam(t["key"]).getValue() ,"sqlite")

		#Save table name/prefix too
		self.config.setAttr("tableName", self.tableName, "sqlite")
		self.config.saveTrace()

	def closeAll(self, clearTrace=True, clearText=True, clearKeys=True):
		if self.db is not None:
			self.db.close()
		
		self.db = None

	def getTrace(self, n):
		if self.db == None:
			self.con()
		
		cx = self.db.cursor()
		cx.execute("SELECT trace FROM cwtraces_%d order by trace_id LIMIT 1 OFFSET ?" % self.setid , (n,))
		wv = cx.fetchone()[0]
		return self.formatWave(wv, read=True)

	def asc2list(self, asc):
		lst = []
		for i in range(0,len(asc),2):
			lst.append( int(asc[i:(i+2)], 16) )
		return lst

	def getWaveVars(self,n):
		if self.db == None:
			self.con()
		cx = self.db.cursor()
		cx.execute("SELECT trace_data FROM cwtraces_%d order by trace_id LIMIT 1 OFFSET ?" % self.setid ,( n,))
		wv = cx.fetchone()[0]
		return json.loads(wv)

	def getTextin(self, n): #legacy
		return self.getWaveVars()['Textin']
	
	def getTextout(self, n): #legacy
		return self.getWaveVars()['Textout']

	def getKnownKey(self, n=None):#legacy
		return self.getWaveVars()['KnownKey']
