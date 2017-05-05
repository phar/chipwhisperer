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

		proc = subprocess.Popen(self.server.runcommand  + [server.command_flag] + [self.data],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
		(retdata,rc) = proc.communicate()

		self.request.sendall("r"+("%02x"%len(retdata))+retdata+"\n")

if __name__ == "__main__":
	HOST, PORT = "0.0.0.0", 3137
	SocketServer.TCPServer.allow_reuse_address = True
	server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler,bind_and_activate=True)
	server.command_flag = ""
	server.runcommand = ["echo", "hello world"]
	server.allow_reuse_address=True
	server.server_activate()
	server.serve_forever()




