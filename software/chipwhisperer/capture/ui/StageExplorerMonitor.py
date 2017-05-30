from PyQt4.QtGui import *
import chipwhisperer.common.utils.qt_tweaks as QtFixes
import binascii
import sip
sip.setapi('QVariant',2)
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
from scipy.interpolate import interp1d
import random
import numpy
import logging
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

import scipy
import matplotlib.pyplot as plt

FREQ_MIN = 60
FREQ_MAX = 500

class StageExplorerMonitor(QtFixes.QDialog):
	def __init__(self, parent):
		super(StageExplorerMonitor, self).__init__(parent)

		self.capturegui = parent

		# a figure instance to plot on
		self.figure = plt.figure()

		# this is the Canvas Widget that displays the `figure`
		# it takes the `figure` instance as a parameter to __init__
		self.canvas = FigureCanvas(self.figure)

		# this is the Navigation widget
		# it takes the Canvas widget and a parent
		self.toolbar = NavigationToolbar(self.canvas, self)

		self.freqslider = QtGui.QSlider(Qt.Horizontal)
		self.freqslider.setMinimum(FREQ_MIN)
		self.freqslider.setMaximum(FREQ_MAX)
		self.freqspin = QtGui.QDoubleSpinBox()
		self.freqspin.setMinimum(FREQ_MIN)
		self.freqspin.setMaximum(FREQ_MAX)
		QObject.connect(self.freqslider, SIGNAL('valueChanged(int)'),self.updateSlider)
		self.l1 = QLabel()
	
		# Just some button connected to `plot` method
		self.button = QtGui.QPushButton('Refresh')
		self.button.clicked.connect(self.updateFreq)

		# set the layout
		layout = QtGui.QGridLayout()
		layout.addWidget(self.toolbar,0,0,1,4)
		layout.addWidget(self.canvas,1,0,1,4)
		layout.addWidget(self.freqslider,2,0,1,1)
		layout.addWidget(self.freqspin,2,2,1,1)
		layout.addWidget(self.l1,2,3,1,1)
		layout.addWidget(self.button,3,0,1,4)
		self.setLayout(layout)
		self.l1.setText("Hz")
		cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)


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

	def newData(self, key, pt, ct, expected):
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


	def onclick(self,event):
		if event:
			print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % (event.button, event.x, event.y, event.xdata, event.ydata))
	
		if self.capturegui.api.getStage():
			stage = self.capturegui.api.getStage()
			stage.enableStageMotors()
			stage.setCurrentCoord((event.x, event.y))
			stage.disableStageMotors()

	def updateBox(self):
		self.freqslider.setValue(self.freqspin.value())

	def updateSlider(self):
		self.freqspin.setValue(self.freqslider.value())
	#self.updateFreq()
	
	def updateFreq(self):
		self.plot()

	def plot(self):
		tm = self.capturegui.api.project().traceManager()
		self.data_points = []
		self.xpoints = []
		self.ypoints = []
		self.data_values = []
		xM = None
		xm = None
		yM = None
		ym = None
		s = tm.getSegment(0)
		for i in xrange(s.numTraces()):
			var = s.getWaveVars(i)
			#calculate an FFT based on the trace
			t = s.getTrace(i)
			f = numpy.fft.fft(t)
			xf = np.linspace(60.0, 1.0/(2.0*(1.0/tm.getSampleRate())), tm.numPoints()//2)
			yf = 2.0/tm.numPoints() * np.abs(f[0:tm.numPoints()//2])
			#interpolate the FFT along the frequency spectrum so that we can request
			#a quantity at arbitrary frequencies
			interp = interp1d(xf,yf)
			
			if var['x'] < xm or xm == None:
				xm = var['x']
			if var['y'] < ym or ym == None:
				ym = var['y']
			
			if var['x'] > xM or xM == None:
				xM = var['x']
			if var['y'] > yM or yM == None:
				yM = var['y']
			#store the point into a list, this list may be sparse, but is ulitmatly based on stage coordinates
			self.xpoints.append(var['x'])
			self.ypoints.append(var['y'])
			self.data_points.append((var['x'],var['y']))
			self.data_values.append(float(interp(self.freqspin.value())))
		
		#take the traces and create a 2d interpolation based on those points
		spa = self.capturegui.api.getStage().params.getChild("Samples Per Axis").getValue()
		xi, yi = np.linspace(xm, xM, spa), np.linspace(ym, yM, spa)
		f = scipy.interpolate.interp2d(self.xpoints, self.ypoints, self.data_values, kind='linear')
		ax = self.figure.add_subplot(111)
		ax.pcolormesh(xi, yi, f(xi, yi))
		self.canvas.draw()




