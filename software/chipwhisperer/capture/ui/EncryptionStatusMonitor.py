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

from PyQt4.QtGui import *
import chipwhisperer.common.utils.qt_tweaks as QtFixes
import binascii


class EncryptionStatusMonitor(QtFixes.QDialog):
	def __init__(self, parent):
		super(EncryptionStatusMonitor, self).__init__(parent)
		self.oldattackvars = None

	#
	#        self.dLayout = QVBoxLayout()
	#
	#        self.textResultsLayout = QGridLayout()
	#		
	#        self.textInLine = QtFixes.QLineEdit()
	#        self.textOutLine = QtFixes.QLineEdit()
	#        self.textResultsLayout.addWidget(QLabel("Text In "), 0, 0)
	#        self.textInLine.setReadOnly(True)
	#        self.textResultsLayout.addWidget(self.textInLine, 0, 1)
	#        self.textResultsLayout.addWidget(QLabel("Text Out"), 1, 0)
	#        self.textOutLine.setReadOnly(True)
	#        self.textResultsLayout.addWidget(self.textOutLine, 1, 1)
	#        self.textResultsLayout.addWidget(QLabel("Expected"), 2, 0)
	#        self.textOutExpected = QtFixes.QLineEdit()
	#        self.textOutExpected.setReadOnly(True)
	#        self.textResultsLayout.addWidget(self.textOutExpected, 2, 1)
	#        self.textResultsLayout.addWidget(QLabel("Enc. Key"), 3, 0)
	#        self.textEncKey = QtFixes.QLineEdit()
	#        self.textEncKey.setReadOnly(True)
	#        self.textResultsLayout.addWidget(self.textEncKey, 3, 1)
	#        self.dLayout.addLayout(self.textResultsLayout)
	#
	#        # Count of OK passes
	#        cntLayout = QHBoxLayout()
	#
	#        self.totalOps = QLabel("0")
	#        self.totalOK = QLabel("?")
	#        self.totalFail = QLabel("?")
	#        self.clearPB = QPushButton("Clear")
	#        self.clearPB.clicked.connect(self.clrCnt)
	#
	#        cntLayout.addWidget(QLabel("Total Ops: "))
	#        cntLayout.addWidget(self.totalOps)
	#        cntLayout.addStretch()
	#        cntLayout.addWidget(QLabel("Total OK: "))
	#        cntLayout.addWidget(self.totalOK)
	#        cntLayout.addStretch()
	#        cntLayout.addWidget(QLabel("Total Failed: "))
	#        cntLayout.addWidget(self.totalFail)
	#        cntLayout.addStretch()
	#        cntLayout.addWidget(self.clearPB)
	#        self.clrCnt()
	#
	#        self.dLayout.addLayout(cntLayout)
	#
	#        self.setLayout(self.dLayout)
		self.hide()

	def clrCnt(self, ignored=False):
		self._cntops = 0
		self._okops = 0
		self._failops = 0
		self.totalOps.setText("%d" % self._cntops)
		self.totalOK.setText("%d" % self._okops)
		self.totalFail.setText("%d" % self._failops)

	def setHexText(self, lineedit, data):
		if data is not None:
			lineedit.setText(binascii.hexlify(data))
		else:
			lineedit.setText("?")

	def redraw_gui(self):
		i = 0
		self.dLayout = QVBoxLayout()
		for i in xrange(5):
			self.textResultsLayout = QGridLayout()
			self.textInLine = QtFixes.QLineEdit()
			self.textResultsLayout.addWidget(self.textInLine, 0, i)
		self.setLayout(self.dLayout)

	def newData(self, attackvars):
		
		if self.oldattackvars != attackvars:
			self.redraw_gui()
			self.oldattackvars= attackvars
		
		if 'key' in attackvars: #fixme!
			key = attackvars['key']
			pt = attackvars['plaintext']
			ct = attackvars['cyphertext']
			expected = attackvars['expected']
			
			self.setHexText(self.textOutLine, ct)
			self.setHexText(self.textInLine, pt)
			self.setHexText(self.textEncKey, key)
			self.setHexText(self.textOutExpected, expected)

			self._cntops += 1

			if ct and expected and list(ct) == list(expected):
				self._okops += 1
			else:
				self._failops += 1

			self.totalOps.setText("%d" % self._cntops)
			self.totalOK.setText("%d" % self._okops)
			self.totalFail.setText("%d" % self._failops)
