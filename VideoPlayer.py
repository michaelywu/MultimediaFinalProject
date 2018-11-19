'''*****************************************************************************
File: VideoPlayer.py
Written By: Michael Wu
Class: CSCI 576
Project: Hypermedia Player

Purpose: Launching this will open QT GUI. There will be several buttons.
Load button:
Play button:
Pause button:
Stop button:

Video Format (video.avi): 5 minutes long, 30 frames per second, 352x288 resolution
Frame Format (frame.rgb): Same as Assignment 2 where the resolution is 352x288 with
 each .rgb file containing 352*288 red bytes, followed by 352*288 green bytes,
 followed by 352*288 blue bytes. The frames are given in sequential order and
 there are 30 frames per second of video (9000 frames in total for each video).
Audio Format (audio.wav): 5 minutes long, 16 bits per sample, sampling rate of
 44,100 samples per second

Goals
 1. Display the images DONE!
 2. Output sound DONE!
 3. Get the play and pause button working DONE!
 4. Work on metadata parser (class that will work for both applications) DONE!
 5. Display the link DONE!
 6. Work on logic to move between videos DONE!

 TODO:
 1. Add a position slider for the video
 2. Add a sound slider for the video
*****************************************************************************'''
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QDir, Qt, QUrl, QByteArray, QTimer, QRect
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter,QPen
import sys
import os
import numpy as np
import array
import ImageByteConverter
import MetadataParser
import time
'''*****************************************************************************
Class: VideoPlayer
Inherits from QMainWindow

*****************************************************************************'''
class VideoPlayer(QMainWindow):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.setWindowTitle("CSCI 576 Interactive Video Player")
        #contains the list of RGB files
        self.rgb_files = {}
        self.image_idx = 0
        self.ibc = ImageByteConverter.ImageByteConverter()
        self.imageWidth = 352
        self.imageHeight = 288
        self.directory = ''
        #contains a name of WAV file
        self.wav_files = {}
        self.linkDict = {}
        self.videoID = []
        self.activeVideoID = 0
        # key is video ID -> frame number -> 2D list
        #[x1,y1,xLength,yLength, vid_dest, vid_dest start frame#]
        self.imageIdx = 0
        self.isPlaying = False
        self.videoLoaded = False
        #mediaPlayer object to play sound
        self.mediaPlayer = QMediaPlayer()
        self.metadata = MetadataParser.MetadataParser()
        #videoWidget = QVideoWidget()

        #Play button
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.playButtonAction)

        #Pause button
        self.pauseButton = QPushButton()
        self.pauseButton.setEnabled(False)
        self.pauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pauseButton.clicked.connect(self.pauseButtonAction)
        #self.positionSlider = QSlider(Qt.Horizontal)
        #self.positionSlider.setRange(0, 0)
        #self.positionSlider.sliderMoved.connect(self.setPosition)

        #self.errorLabel = QLabel()
        #self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
        #        QSizePolicy.Maximum)
        #self.parseJson("test.json")
        #print(self.linkDict)
        #print(self.wav_files)
        #print(self.rgb_files)
        #open video action
        #need a space in the beginning to show up in the menu bar
        openAction = QAction( ' &Open File', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open File')
        #the call back function when triggered
        openAction.triggered.connect(self.openJson)

        #exit action
        exitAction = QAction(' &Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(self.exitCall)

        #sound object
        self.sound = QSound("")

        #create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu(' &File')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        #Image label
        self.imageLabel = QLabel(self)
        self.imageLabel.mousePressEvent = self.mousePress
        self.imageLabel.setFrameShape(QFrame.Panel)
        self.imageLabel.setLineWidth(1)
        self.imageLabel.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.imageLabel.setMinimumHeight(self.imageHeight)
        self.imageLabel.setMinimumWidth(self.imageWidth)

        #setup the timer
        self.updater = QTimer()
        self.updater.setSingleShot(True)
        # 30 frames a second, so delay every 33 ms
        self.updater.setInterval(33)
        self.updater.timeout.connect(self.update)

        self.window = QWidget()

        #This will place the video source on the top
        #while placing the play and pause button on the bottom
        self.mainLayout = QVBoxLayout()
        self.controlLayout = QHBoxLayout()
        #controlLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.imageLabel)
        self.controlLayout.addWidget(self.playButton)
        self.controlLayout.addWidget(self.pauseButton)
        self.mainLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.addLayout(self.controlLayout)

        self.window.setLayout(self.mainLayout)
        #self.window.show()

        self.setCentralWidget(self.window)
        self.show()

    def update(self):
        #Check the current video's links
        #iterate through the links to determine if any of them should be written
        #updates the image
        start = time.time()
        xCoord = []
        yCoord = []
        xLength = []
        yLength = []
        #check if the fram number is in the linkDict
        if self.imageIdx in self.linkDict[self.activeVideoID]:
            #the frame has a link(s)!
            for link in self.linkDict[self.activeVideoID][self.imageIdx]:
                xCoord.append(link[0])
                yCoord.append(link[1])
                xLength.append(link[2])
                yLength.append(link[3])
        self.displayImage(self.rgb_files[self.activeVideoID][self.imageIdx],xCoord,yCoord,xLength,yLength)
        self.imageIdx += 1
        if self.imageIdx >= 9000:
            self.imageIdx = 0
        end = time.time()

        self.updater.setInterval(33-int((end-start)*1000))
        self.updater.start()

    def mousePress(self, QMouseEvent):
        # Pressing the mouse
        xClick = QMouseEvent.x()
        yClick = QMouseEvent.y()
        #print("{},{}".format(QMouseEvent.x(),QMouseEvent.y()))
        #check the metadata contents
        #if the current image index has a hyperlink
        #and the mouse event clicked is within the parameter
        #switch to the next one
        #check if the frame number is in the linkDict
        #[x1,y1,xLength,yLength, vid_dest, vid_dest start frame#]
        if self.imageWidth < xClick or self.imageHeight < yClick or xClick < 0 or yClick < 0:
            return
        if self.isPlaying and self.videoLoaded:
            if self.imageIdx in self.linkDict[self.activeVideoID]:
                for link in self.linkDict[self.activeVideoID][self.imageIdx]:
                    #check if the click is within the link
                    #make the transistion
                    x = link[0]
                    y = link[1]
                    xLen = link[2]
                    yLen = link[3]
                    if (x <= xClick) and xClick <= (x+xLen) and y <= yClick and yClick <= (y+yLen):
                        #the click was within the link
                        if str(link[4]) in self.videoID:
                            self.activeVideoID = str(link[4])
                            self.imageIdx = link[5]
                            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.wav_files[self.activeVideoID])))
                            self.mediaPlayer.setVolume(100)
                            #video is 30 fps
                            # image idx is frame+1
                            pos = int(((self.imageIdx +1) / 30.0) * 1000)
                            self.mediaPlayer.setPosition(pos)
                            self.mediaPlayer.play()
                        else:
                            print("mousePress() error! video ID is invalid.")
    def openJson(self):
        #opens the json file
        #get the file
        metadata_file = QFileDialog.getOpenFileName(self, "Select Metadata","*.json")

        #parse the json file
        parseStatus=self.parseJson(metadata_file[0])

        if parseStatus == True:
            self.imageIdx = 0
            self.activeVideoID = self.videoID[0]
            #directory is valid
            #let the button be activated
            first_file = self.rgb_files[self.activeVideoID][0]
            self.displayImage(first_file)
            self.updater.start()

            #enable the buttons
            self.pauseButton.setEnabled(True)
            self.playButton.setEnabled(True)
            #play the sound
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.wav_files[self.activeVideoID])))
            self.mediaPlayer.setVolume(100)
            self.mediaPlayer.play()

            self.isPlaying = True
            self.videoLoaded = True
        else:
            #parse did not occur properly
            self.pauseButton.setEnabled(False)
            self.playButton.setEnabled(False)
            self.isPlaying = False
            self.videoLoaded = False
    def parseJson(self,path):
        #parse the json input into more convenient data structures
        self.content = self.metadata.readMetadata(path)
        #frameDict: key : videoID->frame_number->2d list
        # returns x1,y1,xLength,yLength,Dest,destFrame#
        if 'videos' in self.content and 'links' in self.content:
            #run checks to make sure everything the input is valid
            #check 'videos' make sure all the keys are valid ints
            for key in self.content['videos'].keys():
                self.videoID.append(key)
            self.videoID.sort()
            #check 'videos' to see the return are valid directories
            for key in self.videoID:
                if not os.path.isdir(self.content['videos'][key]):
                    print("VideoPlayer.py: parseJson() Invalid path in videos.")
                    return False
                #load the rgb files and wav files
                rgb_fail , self.rgb_files[key] = self.getRGBFiles(self.content['videos'][key])
                wav_fail , self.wav_files[key] = self.getWAVFile(self.content['videos'][key])
                if rgb_fail == False or wav_fail == False:
                    print("VideoPlayer.py: parseJson() unable to retrieve rgv or wav files")
                    return False
                self.linkDict[key] = {}

            for key in self.content['links'].keys():
                links = self.content['links'][key]
                #2d list
                #[x1,y1,xLength,yLength,start frame #, end frame #, vid_dest, vid_dest start frame#]
                for link in links:
                    if len(link) != 8:
                        print("VideoPlayer.py: parseJson() link list is not compliant.")
                        return False
                    startFrame = link[4]
                    endFrame = link[5]
                    for frameNum in range(startFrame,endFrame+1):
                        if frameNum not in self.linkDict[key]:
                            self.linkDict[key][frameNum] = []
                        self.linkDict[key][frameNum].append([link[0],link[1],link[2],link[3],str(link[6]),link[7]])
        else:
            print("VideoPlayer.py: parseJson() INVALID JSON FILE.")
            return False
        return True
    def getRGBFiles(self, path):
        #given the path it will get the list of RGB files in order
        # return bool, list
        files = []
        pass_fail = False
        for file in os.listdir(path):
            if file.endswith(".rgb") or file.endswith(".RGB"):
                files.append("{}/{}".format(path,file))
        if len(files) > 0:
            pass_fail = True
        else:
            print("There are no RGB files in the given diretory.")
        files.sort()
        return pass_fail,files
    def getWAVFile(self, path):
        #given the path it will get the list of wav files in order
        # return bool, list
        wav_file = ''
        pass_fail = False
        for file in os.listdir(path):
            if file.endswith(".wav") or file.endswith(".WAV"):
                wav_file = "{}/{}".format(path,file)
        if wav_file != '':
            pass_fail = True
        else:
            print("The given input directory does not have just one wav file.")

        return pass_fail,wav_file

    def displayImage(self,path,x1=None,y1=None,xLength=None,yLength=None):
        #given the path, display the image onto the label
        qim = QImage(self.ibc.convert(path),self.imageWidth,self.imageHeight,QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qim)
        if(x1 != None or y1 != None or xLength != None or yLength != None):
            for idx in range(len(x1)):
                # create painter instance with pixmap
                painterInstance = QPainter(pixmap)
                # set rectangle color and thickness
                penRectangle = QPen(Qt.white)
                # draw rectangle on painter
                painterInstance.setPen(penRectangle)
                painterInstance.drawRect(x1[idx],y1[idx],xLength[idx],yLength[idx])
                painterInstance.end()
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.resize(self.imageWidth,self.imageHeight)
        self.imageLabel.show()

    def exitCall(self):
        #exits out of the application
        sys.exit(app.exec_())

    def playButtonAction(self):
        #will only play if the video is paused
        if self.isPlaying == False and self.videoLoaded == True:
            self.updater.start()
            self.mediaPlayer.play()
            self.isPlaying = True

    def pauseButtonAction(self):
        #will only pause if the video is still playing
        if self.isPlaying == True and self.videoLoaded == True:
            self.updater.stop()
            self.mediaPlayer.pause()
            self.isPlaying = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(400, 400)
    player.setFixedSize(player.size())
    player.show()
    sys.exit(app.exec_())
