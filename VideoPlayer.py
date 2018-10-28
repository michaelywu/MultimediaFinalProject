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
*****************************************************************************'''
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QDir, Qt, QUrl, QByteArray, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon, QPixmap, QImage
import sys
import os
import numpy as np
import array
import ImageByteConverter
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
        self.playbutton_active = False
        self.imageIdx = 0
        #mediaPlayer object to play the avi video
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

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

        #setup the timer
        self.updater = QTimer()
        self.updater.setSingleShot(True)
        # 30 frames a second, so delay every 33 ms
        self.updater.setInterval(33)
        self.updater.timeout.connect(self.update)

        self.show()

        '''
        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        '''
    def update(self):

        self.displayImage('{}/{}'.format(self.directory,self.rgb_files[self.imageIdx]))
        self.imageIdx += 1
        if self.imageIdx >= 9000:
            self.imageIdx = 0
        self.updater.start()
    def openDirectory(self):
        #opens a directory containing the rgb files
        #for testing purposes ONLY
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        rgb_fail = False
        wav_fail = False
        #when directory is opened
        if os.path.isdir(dir):
            rgb_fail , self.rgb_files = self.getRGBFiles(dir)
            wav_fail , self.wav_file = self.getWAVFile(dir)
            self.directory = dir

        if rgb_fail == True and wav_fail == True:
            #directory is valid
            #let the button be activated
            self.playbutton_active = True
            first_file = '{}/{}'.format(dir,self.rgb_files[0])
            self.displayImage(first_file)
            self.updater.start()
        else:
            #directory is not valid
            #leave it inactive
            self.playbutton_active = False
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
    def displayImage(self,path):
        #given the path, display the image onto the label
        qim = QImage(self.ibc.convert(path),self.imageWidth,self.imageHeight,QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qim)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.show()

    def exitCall(self):
        #exits out of the application
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

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
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())
