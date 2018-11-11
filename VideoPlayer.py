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
 5. Display the link
 6. Work on logic to move between videos
*****************************************************************************'''
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QDir, Qt, QUrl, QByteArray, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter,QPen
import sys
import os
import numpy as np
import array
import ImageByteConverter
import MetadataParser
'''*****************************************************************************
Class: VideoPlayer
Inherits from QMainWindow

*****************************************************************************'''
class VideoPlayer(QMainWindow):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.setWindowTitle("CSCI 576 Interactive Video Player")
        #contains the list of RGB files
        self.rgb_files = []
        self.image_idx = 0
        self.ibc = ImageByteConverter.ImageByteConverter()
        self.imageWidth = 352
        self.imageHeight = 288
        self.directory = ''
        #contains a name of WAV file
        self.wav_file = ''
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

        #open video action
        #need a space in the beginning to show up in the menu bar
        openAction = QAction( ' &Open Directory', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Directory')
        #the call back function when triggered
        openAction.triggered.connect(self.openDirectory)

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

        self.imageLabel = QLabel(self)
        #self.imagePixmap = QPixmap()
        #label.setPixmap(pixmap)
        self.imageLabel.resize(self.imageWidth,self.imageHeight)
        self.imageLabel.mousePressEvent = self.mousePress
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

        self.mainLayout.addLayout(self.controlLayout)

        self.window.setLayout(self.mainLayout)
        #self.window.show()

        self.setCentralWidget(self.window)
        self.show()

    def update(self):
        #Check the current video's links
        #iterate through the links to determine if any of them should be written
        #updates the image
        self.displayImage('{}/{}'.format(self.directory,self.rgb_files[self.imageIdx]),0,0,50,50)
        self.imageIdx += 1
        if self.imageIdx >= 9000:
            self.imageIdx = 0
        self.updater.start()

    def mousePress(self, QMouseEvent):
        # Pressing the mouse
        print("{},{}".format(QMouseEvent.x(),QMouseEvent.y()))
        #check the metadata contents
        #if the current image index has a hyperlink
        #and the mouse event clicked is within the parameter
        #switch to the next one
    def openDirectory(self):
        #opens a directory containing the rgb files
        #for testing purposes ONLY
        metadata_file = QFileDialog.getOpenFileName(self, "Select Metadata","*.json")
        #print(metadata_file[0])
        rgb_fail = False
        wav_fail = False

        self.content = self.metadata.readMetadata(metadata_file[0])
        dir = self.content['videos']["0"]
        if os.path.isdir(dir):
            rgb_fail , self.rgb_files = self.getRGBFiles(dir)
            wav_fail , self.wav_file = self.getWAVFile(dir)
            self.directory = dir
            #the wave file is now the full absolute path
            self.wav_file = os.path.abspath('{}/{}'.format(dir,self.wav_file))
        if rgb_fail == True and wav_fail == True:
            self.imageIdx = 0
            #directory is valid
            #let the button be activated
            first_file = '{}/{}'.format(dir,self.rgb_files[0])
            self.displayImage(first_file)
            self.updater.start()

            #enable the buttons
            self.pauseButton.setEnabled(True)
            self.playButton.setEnabled(True)
            #play the sound
            #self.sound.play(self.wav_file)
            #QSound.play(self.wav_file)
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.wav_file)))
            self.mediaPlayer.setVolume(100)
            self.mediaPlayer.play()

            self.isPlaying = True
            self.videoLoaded = True
        else:
            #directory is not valid
            #leave it inactive
            #disable the buttons
            self.pauseButton.setEnabled(False)
            self.playButton.setEnabled(False)
            self.isPlaying = False
            self.videoLoaded = False
    def getRGBFiles(self, path):
        #given the path it will get the list of RGB files in order
        # return bool, list
        files = []
        pass_fail = False
        for file in os.listdir(path):
            if file.endswith(".rgb") or file.endswith(".RGB"):
                files.append(file)
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
                wav_file = file
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
            # create painter instance with pixmap
            painterInstance = QPainter(pixmap)

            # set rectangle color and thickness
            penRectangle = QPen(Qt.white)
            #penRedBorder.setWidth(3)

            # draw rectangle on painter
            painterInstance.setPen(penRectangle)
            painterInstance.drawRect(x1,y1,xLength,yLength)
            painterInstance.end()
        self.imageLabel.setPixmap(pixmap)
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

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.resize(400, 400)
    player.show()
    sys.exit(app.exec_())
