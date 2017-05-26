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
    # This isn't really needed, no need to bother users
    # print "umysql required: https://pypi.python.org/pypi/umysql"
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
		self.con()
		self.prepareDB()
			#	self.getParams().addChildren([{'name':'SQLite Configuration', 'type':'group', 'children':[
	#                       {'name':'Table Name', 'key':'tableName', 'type':'str', 'value':'CWTable1', 'readonly':True}
	#			  ]}])

		#Format name must agree with names from TraceContainerFormatList
		self.config.setAttr("format", "sqlite")

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

	def prepareDisk(self):
		pass
	
	def prepareDB(self):
		self.db.execute("create table IF NOT EXISTS cwtraces(trace_id integer PRIMARY KEY AUTOINCREMENT,trace   text, trace_data text,  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);" )

	def con(self):
		if self.db is not None:
			self.db.close()
		self.db = sqlite3.connect(os.path.join(self.api.project().datadirectory,"chipwhisperer.db")) #fixme.. in project directory!
		self.db.execute("PRAGMA foreign_keys = ON;")

		cx = self.db.cursor()
		cx.execute("select sqlite_version();")
		result = cx.fetchone()
		logging.info('SQLite Version: %s' % result)


	def _getTableName(self):
		return self.getParams.findParam('tableNameList').getValue()

	#    def listAllTables(self):
	#        self.con()
	#        database = self.getParams.findParam('database').getValue()
	#        results = self.db.query("SHOW TABLES IN %s"%database)
	#        tables = []
	#        for r in results.rows:
	#            tables.append(r[0])
	#        self.getParams.findParam('tableNameList').setLimits(tables)
	#

	def updatePointsTraces(self):
		res = self.db.query("SELECT COUNT(*) FROM cwtraces" )
		self._numTraces = res.rows[0][0]

		wav = self.db.query("SELECT Wave FROM cwtraces  order by trace_id LIMIT 1 OFFSET ?" , ( 0))
		self._numPoints = self.formatWave(wav, read=True).shape[0]

	def updateConfigData(self):
		self.con()
		self.tableName = self.getParams.findParam('tableName').getValue()
		res = self.db.query("SELECT COUNT(*) FROM cwtraces")
		self._numTraces = res.rows[0][0]
		self.config.setAttr('numTraces', self._numTraces)

		wav = self.db.query("SELECT Wave FROM cwtraces  order by trace_id  LIMIT 1 OFFSET ?",(0))
		self._numPoints = self.formatWave(wav, read=True).shape[0]
		self.config.setAttr('numPoints', self._numPoints)

	def numTraces(self, update=False):
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
		#		if self.findParam(["SQLite Configuration","format"]).getValue() == "NumPy JSON":
			if read == False:
				return json.dumps(wave.tolist())
			else:
				return np.array(json.loads(wave))
					#	else:
#			raise AttributeError("Invalid Format for SQLite")

	def addTrace(self, trace, attackvars, dtype=np.double,channelNum=None):
		jattackvars = json.dumps(attackvars)
		cx = self.db.cursor()
		cx.execute("INSERT INTO cwtraces (trace_data, trace) VALUES(?, ?);",( jattackvars ,self.formatWave(trace)))
		self.db.commit()

	def saveAll(self):
		#Save attributes from config settings
		for t in self.getParams.traceParams[0]['children']:
			self.config.setAttr(t["key"],  self.getParams.findParam(t["key"]).getValue() ,"sqlite")

		#Save table name/prefix too
		self.config.setAttr("tableName", self.tableName, "sqlite")
		self.config.saveTrace()

	def closeAll(self, clearTrace=True, clearText=True, clearKeys=True):
		# self.saveAllTraces(os.path.dirname(self.config.configFilename()), prefix=self.config.attr("prefix"))

		# Release memory associated with data in case this isn't deleted
	#        if clearTrace:
	#            self.traces = None
	#
	#        if clearText:
	#            self.textins = None
	#            self.textouts = None
	#
	#        if clearKeys:
	#            self.keylist = None
	#            self.knownkey = None

		if self.db is not None:
			self.db.close()
		
		self.db = None

	def getTrace(self, n):
		cx = self.db.cursor()
		cx.execute("SELECT trace FROM cwtraces order by trace_id LIMIT 1 OFFSET %d", ( n))
		wv = cx.fetchone()
		return self.formatWave(wv, read=True)

	def asc2list(self, asc):
		lst = []
		for i in range(0,len(asc),2):
			lst.append( int(asc[i:(i+2)], 16) )
		return lst

	def getWaveVars(self,n):
		cx = self.db.cursor()
		cx.execute("SELECT trace_data FROM cwtraces order by trace_id LIMIT 1 OFFSET %d",( n))
		wv = cx.fetchone()
		return json.loads()

	def getTextin(self, n): #legacy
		return self.getWaveVars()['Textin']
	
	def getTextout(self, n): #legacy
		return self.getWaveVars()['Textout']

	def getKnownKey(self, n=None):#legacy
		return self.getWaveVars()['KnownKey']