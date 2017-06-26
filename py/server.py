import os
import fnmatch
import re
import time
from BaseHTTPServer import BaseHTTPRequestHandler
from pygame import mixer
mixer.pre_init(44100, -16, 2, 512)
mixer.init()

directory = '.'
isLoading = False

class Player(object):
	def __init__(self, filename=""):
		#self.filename = filename
		#self.isInit = True
		mixer.init()
		print("mixer init")

	def getIsInit(self):
		if self.isInit:
			return True
		return False

	def setFilename(self, filename):

		mixer.music.load(filename)
		"""
		if not os.path.exists(filename):
			self.isInit = False
			raise IOError("%s doesn't exist - abort" % (filename))

		self.filename = filename
		self.isInit = True
		print("load %s" % self.filename)
		"""
	
	def play(self):
		"""
		if not self.isInit:
			raise ValueError("Player is not initialize can't play song")
		print("playing song %s" % self.filename)
		print("is init? %d" % self.isInit)
		"""
		mixer.music.play()
		print("should play music")
	
	def stop(self):
		mixer.music.stop()


player = Player()
#This class will handles any incoming request from
#the browser 
class MyHandler(BaseHTTPRequestHandler):
	def __init__(self, request, client_address, server):
		BaseHTTPRequestHandler.__init__(self, request, client_address, server)
			
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		# define some custom data to test
		f = open("index.html")
		self.wfile.write(f.read())
		f.close()
		return

	def do_POST(self):
		global directory
		global player
		global isLoading

		print ("is busy %d " % mixer.get_busy())
		if not mixer.get_init():
			mixer.init()
		
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

		content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        	post_data = self.rfile.read(content_length) # <--- Gets the data itself
		commandMatch = re.search("command=(\w+)", post_data)
		if commandMatch is None:
			self.send_response(200)
			self.end_headers()
			return
		
		command = commandMatch.group(1)
		if command == "play":
			print("play")

			if mixer.get_busy():
				mixer.stop()			
			mixer.music.play()
			time.sleep(1)
			print ("audio")
		elif command == "pause":
			mixer.music.pause()
			return
		elif command == "stop":
			mixer.music.stop()
		elif command == "getSongList":
			print("get files inside %s" % directory)
			files =  os.listdir(directory)
			files = [f for f in files if fnmatch.fnmatch(f, '*.mp3')]
			self.wfile.write("#".join(files))
		elif command == "setSong":
			print("set song function")
			isLoading = True
			fileNameMatch = re.search("filename=(.+)+", post_data)
			if fileNameMatch:
				filename = fileNameMatch.group(1)
				print("set song %s" % filename)
					
				mixer.music.load(filename)
				print("mixer loading finished")
				
		elif command == "setDirectory":
			directoryMatch = re.search("directory=(.+)+", post_data)
			if directoryMatch:
				directoryPath = directoryMatch.group(1)
				# todo: add check if directory makes sense
				directory = directoryPath
				print("directory changed to %s" % directory)
		elif command == "getDirectory":
			print("getDirectory %s" % directory)
			self.wfile.write(directory)
		elif command == "getSubDirectories":
			print("getSubDirectories")
			dirs = []
			contentInDir = os.listdir(directory)
			for currentItem in contentInDir:
				if os.path.isdir(os.path.join(directory, currentItem)):
					dirs.append(currentItem)
			self.wfile.write("#".join(dirs))
		elif command == "gotoParent":
			# get current directory first
			print("goto parent");
			parentDir = os.path.abspath(os.path.join(directory, os.path.pardir))
			directory = parentDir
			print "new parent set"
		else:
			print("unknown command")


