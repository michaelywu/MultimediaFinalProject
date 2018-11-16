'''*****************************************************************************
File: VideoEditor.py
Written By: Michael Wu
Class: CSCI 576
Project: Hypermedia Player

Purpose: Launching this will open QT GUI. There will be several widgets.

2 frames, one on the left and one on the right. The left is the source video,
the right is the destination video.
The bottom of the frames must have sliders so the user can look through the frames.
Action:
-Import source video: filedialog will pop up looking to give a directory. The
corresponding slider will be active when loaded correctly.
-Import destination video: filedialog will pop up looking to give a directory.
The corressponding slider will be active when loaded correctly.
-Create a hyperlink:
    -At the source frame, a default bounding box is created. Where the user
    can move around the box or change the size
    -Frame length number
-Define link:
    -Will only be active when a link is selected. This will attach the link
    to a destination video.
-Save file: Save it into a json file
Status:
-List the links created.

Phase 1:
Create all the widgets
Load the videos
Make slider work

Phase 2:
Create a hyperlink
Define hyperlink

Phase 3:
Save file

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
'''*****************************************************************************
Class: VideoEditor
Inherits from QMainWindow

*****************************************************************************'''
class VideoEditor(QMainWindow):

    def __init__(self, parent=None):
        super(VideoEditor, self).__init__(parent)
        self.setWindowTitle("CSCI 576 Video Editor")
        #contains the list of RGB files
        self.src_rgb_files = []
        self.dest_rgb_files = []
        self.src_image_idx = 0
        self.dest_image_idx = 0
        self.ibc = ImageByteConverter.ImageByteConverter()
        self.imageWidth = 352
        self.imageHeight = 288
        self.directory = ''
        #contains a name of WAV file
        self.linkDict = {}
        self.videoID = []
        self.activeVideoID = 0
        # key is video ID -> frame number -> 2D list
        #[x1,y1,xLength,yLength, vid_dest, vid_dest start frame#]
        self.imageIdx = 0
        self.isPlaying = False
        self.videoLoaded = False

        self.metadata = MetadataParser.MetadataParser()

        self.srcPositionSlider = QSlider(Qt.Horizontal)
        self.srcPositionSlider.setRange(0, 0) #leave it disabled
        #self.srcPositionSlider.sliderMoved.connect(self.setSrcPosition)
        self.srcPositionSlider.valueChanged.connect(self.setSrcPosition)

        self.destPositionSlider = QSlider(Qt.Horizontal)
        self.destPositionSlider.setRange(0, 0)
        self.destPositionSlider.sliderMoved.connect(self.setDestPosition)


        #need a space in the beginning to show up in the menu bar
        srcAction = QAction( ' &Open Source Video', self)
        srcAction.setShortcut('Ctrl+S')
        srcAction.setStatusTip('Open Source Video')
        #the call back function when triggered
        srcAction.triggered.connect(self.openSourceVideo)

        destAction = QAction( ' &Open Destination Video', self)
        destAction.setShortcut('Ctrl+D')
        destAction.setStatusTip('Open Destination Video')
        #the call back function when triggered
        destAction.triggered.connect(self.openDestinationVideo)

        #exit action
        exitAction = QAction(' &Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(self.exitCall)

        #create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu(' &File')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(srcAction)
        fileMenu.addAction(destAction)
        fileMenu.addAction(exitAction)

        #Source image label
        self.srcImageLabel = QLabel(self)
        #self.srcImageLabel.mousePressEvent = self.mousePress
        self.srcImageLabel.setFrameShape(QFrame.Panel)
        self.srcImageLabel.setLineWidth(1)
        self.srcImageLabel.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.srcImageLabel.setMinimumHeight(self.imageHeight)
        self.srcImageLabel.setMinimumWidth(self.imageWidth)

        #Destination image label
        self.destImageLabel = QLabel(self)
        #self.destImageLabel.mousePressEvent = self.mousePress
        self.destImageLabel.setFrameShape(QFrame.Panel)
        self.destImageLabel.setLineWidth(1)
        self.destImageLabel.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.destImageLabel.setMinimumHeight(self.imageHeight)
        self.destImageLabel.setMinimumWidth(self.imageWidth)

        self.window = QWidget()

        #This will place the video source on the top
        #while placing the play and pause button on the bottom
        self.mainLayout = QVBoxLayout()
        self.displayLayout = QHBoxLayout()
        self.sliderLayout = QHBoxLayout()
        #self.controlLayout = QHBoxLayout()
        #controlLayout.setContentsMargins(0, 0, 0, 0)
        self.displayLayout.addWidget(self.srcImageLabel)
        self.displayLayout.addWidget(self.destImageLabel)
        self.displayLayout.setAlignment(Qt.AlignCenter)
        self.sliderLayout.addWidget(self.srcPositionSlider)
        self.sliderLayout.addWidget(self.destPositionSlider)
        #self.controlLayout.addWidget(self.playButton)
        #self.controlLayout.addWidget(self.pauseButton)
        self.mainLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.addLayout(self.displayLayout)
        self.mainLayout.addLayout(self.sliderLayout)
        self.window.setLayout(self.mainLayout)
        #self.window.show()

        self.setCentralWidget(self.window)
        self.show()


    def setSrcPosition(self):
        #print("setSrcPosition() called")
        #print(self.srcPositionSlider.value())
        self.src_image_idx = self.srcPositionSlider.value()
        if (self.src_image_idx <len(self.src_rgb_files)):
            self.displaySrcImage(self.src_rgb_files[self.src_image_idx])

    def setDestPosition(self):
        #print("setDestPosition() called")
        self.dest_image_idx = self.destPositionSlider.value()
        if (self.dest_image_idx <len(self.dest_rgb_files)):
            self.displayDestImage(self.dest_rgb_files[self.dest_image_idx])

    def openSourceVideo(self):
        #print("openSourceVideo() called")
        file = str(QFileDialog.getExistingDirectory(self, "Select Source Video Directory"))
        pass_fail, self.src_rgb_files = self.getRGBFiles(os.path.abspath(file))
        if pass_fail:
            #there are valid files in the given directory
            self.srcPositionSlider.setRange(0, len(self.src_rgb_files)-1)
            #load the first image
            self.displaySrcImage(self.src_rgb_files[0])
            self.src_image_idx = 0
        else:
            self.src_image_idx = 0
            self.srcPositionSlider.setRange(0, 0)

    def openDestinationVideo(self):
        #print("openDestinationVideo() called")
        file = str(QFileDialog.getExistingDirectory(self, "Select Destination Video Directory"))
        pass_fail, self.dest_rgb_files = self.getRGBFiles(os.path.abspath(file))
        if pass_fail:
            #there are valid files in the given directory
            self.destPositionSlider.setRange(0, len(self.dest_rgb_files)-1)
            self.displayDestImage(self.dest_rgb_files[0])
            self.dest_image_idx = 0
        else:
            self.destPositionSlider.setRange(0, 0)
            self.dest_image_idx = 0

    def displaySrcImage(self,path):
        #given the path, display the image onto the label
        qim = QImage(self.ibc.convert(path),self.imageWidth,self.imageHeight,QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qim)
        self.srcImageLabel.setPixmap(pixmap)
        #self.srcImageLabel.resize(self.imageWidth,self.imageHeight)
        self.srcImageLabel.show()

    def displayDestImage(self,path):
        #given the path, display the image onto the label
        qim = QImage(self.ibc.convert(path),self.imageWidth,self.imageHeight,QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qim)
        self.destImageLabel.setPixmap(pixmap)
        #self.imageLabel.resize(self.imageWidth,self.imageHeight)
        self.destImageLabel.show()

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

    def exitCall(self):
        #exits out of the application
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoEditor()
    player.resize(1000, 400)
    player.setFixedSize(player.size())
    player.show()
    sys.exit(app.exec_())
