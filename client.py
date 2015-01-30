from threading import Thread
import socket
import os
import sys
import readline
import thread
import time
class IrcClient():
	def connect(self, s, nick, channel):
		global messages
		packets = ["NICK %s\r\n" % (nick), "USER %s %s %s: %s\r\n" % (nick, nick, nick, nick)]
		for packet in packets:
			s.send(packet)
		connected = True
		clear = False
		messages = []
		terminal_size = os.popen("stty size").read()
		terminal_size = int(terminal_size.split(" ")[0].strip())
		for n in range(terminal_size):
			messages.append("")
		while connected:
			data = s.recv(1024).strip()
			if "PRIVMSG " in data:
				channel = data.split("PRIVMSG ")
				channel = channel[1].split(" :")
				channel = channel[0].strip()
				name = data.split("!", 1)[0]
				message = "[%s]%s - %s" % (channel, name[1:], data.split(":", 2)[2].strip())
				print message
				if len(messages) <= terminal_size:
					messages.append(message)
				else:
					messages.pop(0)
					messages.append(message)			
			else:
				print data.partition(":")[2]
			if clear == True:
				os.system("clear")
				for message in messages:
					print message
				
			if "PING " in data:
				hashbit = data.split("PING ")[1]
				send(s,"PONG %s\r\n" % (hashbit))
			if " 376 " in data:
				send(s, "JOIN %s\r\n" % (channel))
			if "End of /NAMES list" in data:
				if 'ready' in vars():
					pass
				else:
					ready = True
					#Thread(target=self.readInput, args = (s,)).start()
					clear = True
	
	def readInput(self, s):
		global channel
		while True:
			message = raw_input("[%s]>" % (channel))
			if message.startswith("/"):
				self.parse_command(s, message)
			else:
				sendmsg(s, channel, message)
			
	def parse_command(self, s, message):
		global channel
		try:
			command = message[1:].split(" ", 1)[0].strip()
			if command == "join":
				chan = message.split(" ")[1].strip()
				channel = chan
				send(s, "JOIN %s\r\n" % (channel))
			if command == "part":
				chan = message.split(" ")[1].strip()
				channel = chan
				send(s, "PART %s\r\n" % (channel))
			if command == "quit":
				send(s, "QUIT :Exiting Irc Client\r\n")
				s.close()
				os._exit(1)
			if command == "chan":
				channel = message.split(" ")[1].strip()
				print "Current channel is " + channel
			if command == "nick":
				nick = message.split(" ")[1].strip()
				send(s, "NICK %s\r\n" % (nick))
		except Exception as e:
			print e
			print "Incorrect command usage"

def send(s, message):
	s.send(message)
	os.system("clear")
	for message in messages:
		print message

def sendmsg(s, channel, message):
	s.send("PRIVMSG %s :%s\r\n" % (channel, message))
	global messages
	messages.append("["+channel+"][You]:" + message)
	os.system("clear")
	for message in messages:
		print message	
def inputLine():
	while True:
		time.sleep(3)
		sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())+2)+'\r')
		global channel
		sys.stdout.write('['+channel+']>' + readline.get_line_buffer())
		sys.stdout.flush()
global channel 
channel = "#k"
client = IrcClient()
name = raw_input("[Choose a nick]>")
host = raw_input("[Host to connect to]>")
port = raw_input("[Port to connect to]>")
channel = raw_input("[Channel to join]>")
s = socket.socket()
s.connect((host, int(port)))
Thread(target=client.connect, args = (s, name, channel,)).start()
thread.start_new_thread(inputLine, ())
client.readInput(s)
