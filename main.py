from gpiozero import Button
import subprocess
from os import listdir, path
from time import sleep
from signal import pause

ROOTDIR = "/home/pi/Music"

folders = [folder for folder in listdir(ROOTDIR) if path.isdir("%s/%s" % (ROOTDIR, folder))]
folders.sort()

print(folders)
nFolders = len(folders)
print(nFolders)

curFolder = 0
curTrack = 0
playProcess = None

def getFolderTracks(indexFolder):
	if (indexFolder >= nFolders or indexFolder < 0):
		return []
	folder = folders[indexFolder]
	tracks = [track for track in listdir("%s/%s" % (ROOTDIR, folder)) if (track[-4:] == ".mp3" or track[-4:] == ".wma" or track[-4:] == ".aac" or track[-4:] == ".ogg" or track[-5:] == ".flac")]
	tracks.sort()
	return tracks

def play(indexFolder, indexTrack):
	global playProcess
	path = "%s/%s/%s" % (ROOTDIR, folders[indexFolder], getFolderTracks(indexFolder)[indexTrack])
	print("play %s" % path)
	if playProcess is not None:
		try:
			playProcess.kill()
		except:
			pass
	playProcess = subprocess.Popen(['cvlc', path, '--play-and-exit'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#returnValue = playProcess.wait()
	#print("after wait. ret=%s" % returnValue)

def onStop():
	global playProcess
	print("stop")
	if playProcess is not None:
		try:
			playProcess.kill()
		finally:
			pass
		playProcess = None

def onNextTrack():
	global curTrack
	print("next track")
	# only go to next track if not currently playing
	if playProcess is not None:
		tracks = getFolderTracks(curFolder)
		curTrack = (curTrack + 1) % len(tracks)

	play(curFolder, curTrack)

def onNextFolder():
	global curTrack, curFolder
	print("next folder")
	curFolder = (curFolder + 1) % nFolders
	curTrack = 0
	play(curFolder, curTrack)

def onPreviousFolder():
	global curTrack, curFolder
	print("previous folder")
	curFolder = (curFolder - 1) % nFolders
	curTrack = 0
	play(curFolder, curTrack)


# GPIO bindings. I did a custom header for Raspberry Pi 1, with four buttons
# header pinout: https://www.megaleecher.net/sites/default/files/images/raspberry-pi-rev2-gpio-pinout.jpg
bounce_time = 0.1
button1 = Button(14, pull_up=True, bounce_time=bounce_time)
button1.when_released = onNextTrack

button2 = Button(23, pull_up=True, bounce_time=bounce_time)
button2.when_released = onStop

button3 = Button(8, pull_up=True, bounce_time=bounce_time)
button3.when_released = onNextFolder

button4 = Button(7, pull_up=True, bounce_time=bounce_time)
button4.when_released = onPreviousFolder

subprocess.Popen(["cvlc", "/home/pi/startup.ogg", "--play-and-exit"])

#pause()
while True:
	# detect finished track
	if playProcess is not None and playProcess.poll() is not None:
		onNextTrack()
	sleep(0.1)
