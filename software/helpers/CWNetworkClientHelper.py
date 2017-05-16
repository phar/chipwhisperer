import SocketServer
import subprocess
import struct
import time

class MyTCPHandler(SocketServer.BaseRequestHandler):
	def readline(self, timeout=2):
		buf = ""
		ok = 1
		while ok ==	1:
			b = self.request.recv(1)
			buf += b
			if b == '':
				time.sleep(1)
			if b in ['\n']:
				ok = 0
		return buf

	def handle(self):
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024)
		print [self.data]
		
		print "wrote: %s" % str([self.client_address[0]])
		#r = self.readline()
		#r = ""
		#print self.data
		#print r
		self.data = ""
		proc = subprocess.Popen(self.server.runcommand,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
		(retdata,rc) = proc.communicate()
		#		print retdata
		res = retdata.split("\r\n")
		self.request.sendall(res[-3])

if __name__ == "__main__":
	HOST, PORT = "0.0.0.0", 3137
	SocketServer.TCPServer.allow_reuse_address = True
	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler,bind_and_activate=True)
	server.command_flag = ""
	#	server.runcommand = ["echo", "hello world"]
	server.runcommand = ["C:\\Program Files (x86)\\STMicroelectronics\\STM32 ST-LINK Utility\\ST-LINK Utility\\st-link_cli","-HardRst", "-Dump","0x8000000","1000","foo.bin"]
	
	server.allow_reuse_address=True
	server.server_activate()
	server.serve_forever()




