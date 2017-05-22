import serial

class GCODE():
	def __init__(self, port="/dev/tty.usbserial-AI03DR2E",baud=250000):
		self.port = port
		self.baud = baud
		self.ser = None
		self.feedspeed = 2000
		self.mmpos = {"X":0,"Y":0,"Z":0, "E":0}
		self.countpos = {"X":0,"Y":0,"Z":0, "E":0}
		self.connect()
		self.homeXY()
	
	
	
	def connect(self):
		self.ser = serial.Serial(self.port,self.baud)
		
		def write(self,val):
			self.ser.write(val)
		
		def setGPIOpin(self,pin, state):
			if state == True:
				self.command("M42 P%d S0" % (pin))
			else:
				self.command("M42 P%d S255" % (pin))
	
	
	def getPos(self):
		c =  self.command("M114")
		(mmpos,countpos) = c[0].split("Count ")
		for m in mmpos.split(" "):
			if m.rfind(":") > 0:
				(n,v) = m.split(":")
				self.mmpos[n] = float(v)

		countpos = countpos.replace("X: ", "X:") #hacky
		for m in countpos.split(" "):
			if m.rfind(":") > 0:
				(n,v) = m.split(":")
				self.countpos[n] = int(v)



	def homeXY(self):
		self.LCDText("homing")
		self.command("G28 Y")
		self.command("G28 X")
		self.command("G28 Z")
		self.getPos()
	
	def waitForUser(self,test):
		self.command("M1")
	
	def LCDText(self,text):
		self.command("M117 %s" % text)
	
	def gotoXYZ(self,x=None,y=None,z=None,f=None):
		args = ""
		if x != None:
			args  += "X%f " % x
		if y != None:
			args  += "Y%f " % y
		if z != None:
			args  += "Z%f " % z
		
		if f==None:
			f = self.feedspeed
		
		args += "F%f" % f
		self.command("G1 %s" % args)
		self.getPos()
	
	def waitForComplete(self):
		self.command("M400")
	
	def beep(self):
		self.command("M300")

	def close(self):
		self.ser.close()
