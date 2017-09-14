import os
import fnmatch
import re
import time
from BaseHTTPServer import BaseHTTPRequestHandler
from pygame import mixer
import eyed3
mixer.pre_init(44100, -16, 2, 512)
mixer.init()

directory = '.'
isLoading = False
lastFileName = ""

def getMetaDataString(filepath):
	metadata = eyed3.load(filepath)
	title = metadata.tag.title
	artist = metadata.tag.artist
	duration = metadata.info.time_secs
	return "#".join([title, artist, str(duration)])

def getNextSongs(currentSong):
	nextSongList = []
	baseName = os.path.basename(currentSong)
	currentDirectory = os.path.dirname(currentSong)

	filesInDir = os.listdir(currentDirectory)
	foundSong = False
	for i, currentFile in enumerate(filesInDir):
		if foundSong:
			filename, extension = os.path.splitext(filesInDir[i])
			if extension == ".mp3" or extension== ".MP3":
				nextSongList.append(os.path.join(currentDirectory, filesInDir[i]))
		else:
			if os.path.basename(currentFile) == baseName:
				foundSong = True
				if len(filesInDir) == i + 1:
					return []

	return nextSongList
	

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
		global isLoading
		global lastFileName

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

		elif command == "pause":
			mixer.music.pause()
			return
		elif command == "stop":
			mixer.music.stop()
		elif command == "getSongList":
			print("get files inside %s" % directory)
			files =  os.listdir(directory)
			files = [f for f in files if fnmatch.fnmatch(f, '*.mp3') or fnmatch.fnmatch(f, '*.MP3') ]
			self.wfile.write("#".join(files))
		elif command == "setSong":
			print("set song function")
			isLoading = True
			fileNameMatch = re.search("filename=(.+)+", post_data)
			if fileNameMatch:
				filename = fileNameMatch.group(1)
				lastFileName = filename
				print("set song %s" % filename)
				mixer.music.load(filename)
				print("mixer loading finished")

				print("clear the queue")
				mixer.music.clear_queue()
				nextSongList = getNextSongs(filename)

				for nextSong in nextSongList:
					mixer.music.queue(nextSong)
					print("queueing %s" % nextSong)
				
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
		elif command == "getMetaData":
			filenameMatch = re.search("filename=(.+)+", post_data)
			if filenameMatch:
				filenamePath = filenameMatch.group(1)
				metaData = getMetaDataString(filenamePath)
				self.wfile.write(metaData)
		else:
			print("unknown command")


