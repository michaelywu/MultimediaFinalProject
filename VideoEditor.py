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
    -Frame length number
-Define link:
    -Check if there is a valid frame length
    -Check if there is a source video and dest video
    -Load into data structure
    -
-Save file: Save it into a json file
Status:
-List the links created.

Phase 1:
Create all the widgets DONE!
Load the videos DONE!
Make slider work DONE!

Phase 2:
Create a hyperlink
Define hyperlink

Phase 3:
Save file

*****************************************************************************'''
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QDir, Qt, QUrl, QByteArray, QTimer, QRect,QPoint
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QLineEdit)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter,QPen, QBrush, QColor
import sys
import os
import numpy as np
import array
import ImageByteConverter
import MetadataParser

C_WIDTH = 352
C_LENGTH = 288
'''*****************************************************************************
Class: LinkWidget
Inherits from QWidget

*****************************************************************************'''
class HyperlinkLabel(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
        #self.setGeometry(int((C_WIDTH/2.0)-15),int((C_LENGTH/2.0)-15),30,30)
        self.begin = QPoint()
        self.end = QPoint()
        self.link = False
        self.parent = parent
        self.initialX = 0
        self.initialY = 0
        self.xLength = 0
        self.yLength = 0
        self.path = None
        self.ibc = ImageByteConverter.ImageByteConverter()
        self.drawRect = False
        #self.qp = QPainter(self)
    def setPath(self,path):
        self.path = path
    def setLink(self,link = True):
        self.link = link

    def paintEvent(self, event):
        if self.path != None:
            #qim = QImage(self.ibc.convert(self.path),352,288,QImage.Format_RGB888)
            qim = QImage(self.ibc.convert(self.path),self.parent.imageWidth,self.parent.imageHeight,QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qim)

            #qp = QPainter(self)
            qp = QPainter(self)
            qp.drawPixmap(self.rect(), pixmap)
            br = QBrush(QColor(255, 255, 255, 40))
            qp.setBrush(br)
            qp.drawRect(QRect(self.begin, self.end))

    def clearLink(self):
        self.begin = QPoint()
        self.end = QPoint()

    def mousePressEvent(self, event):
        if self.link:
            self.begin = event.pos()
            self.end = event.pos()
            #save the initial click coord
            self.initialX = event.x()
            self.initialY = event.y()
            print("X {} Y {}".format(self.initialX,self.initialY))
            self.update()

    def mouseMoveEvent(self, event):
        if self.link:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.link:
            #self.begin = event.pos()
            self.end = event.pos()
            #save the release click coord. Calculate the coord
            self.xLength = event.x() - self.initialX
            self.yLength = event.y() - self.initialY
            print("Release X {} Y {}".format(self.xLength,self.yLength))
            self.parent.updateLink()
            self.update()
    def setPosition(self,x,y,xLength,yLength):
        self.begin = QPoint(x,y)
        self.end = QPoint(x+xLength,y+yLength)
        self.update()
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
        self.imageWidth = C_WIDTH
        self.imageHeight = C_LENGTH
        self.linkCreationActive = False

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

        #frame number labels
        self.srcImageIndexLabel = QLabel()
        self.destImageIndexLabel = QLabel()
        self.srcImageIndexLabel.setText("Frame:")
        self.destImageIndexLabel.setText("Frame:")
        #Source image label
        #self.srcImageLabel = QLabel(self)
        self.srcImageLabel = HyperlinkLabel(self)
        #self.srcImageLabel.mousePressEvent = self.mousePress
        self.srcImageLabel.setFrameShape(QFrame.Panel)
        self.srcImageLabel.setLineWidth(1)
        self.srcImageLabel.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.srcImageLabel.setMinimumHeight(self.imageHeight)
        self.srcImageLabel.setMinimumWidth(self.imageWidth)

        #Destination image label
        self.destImageLabel = QLabel(self)
        self.destImageLabel.setFrameShape(QFrame.Panel)
        self.destImageLabel.setLineWidth(1)
        self.destImageLabel.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        self.destImageLabel.setMinimumHeight(self.imageHeight)
        self.destImageLabel.setMinimumWidth(self.imageWidth)

        #button objects
        self.createLinkButton = QPushButton('Create Hyperlink', self)
        self.createLinkButton.clicked.connect(self.createLinkClicked)
        self.defineLinkButton = QPushButton('Set Hyperlink', self)
        self.saveButton = QPushButton('Save File', self)
        self.createLinkButton.setEnabled(False)
        self.defineLinkButton.setEnabled(False)
        self.saveButton.setEnabled(False)

        #frame length length
        self.frameLengthLabel = QLabel()
        self.frameLengthLabel.setText("Frame Length:")
        self.frameLength = QLineEdit(self)

        self.window = QWidget()

        self.mainLayout = QHBoxLayout()
        self.srcLayout = QVBoxLayout()
        self.destLayout = QVBoxLayout()
        self.srcButtonLayout = QHBoxLayout()
        self.destButtonLayout = QHBoxLayout()

        self.srcButtonLayout.addWidget(self.createLinkButton)
        self.srcButtonLayout.addWidget(self.frameLengthLabel)
        self.srcButtonLayout.addWidget(self.frameLength)

        self.destButtonLayout.addWidget(self.defineLinkButton)
        self.destButtonLayout.addWidget(self.saveButton)

        self.destLayout.addLayout(self.destButtonLayout)
        self.srcLayout.addLayout(self.srcButtonLayout)

        self.srcLayout.addWidget(self.srcImageLabel)
        self.destLayout.addWidget(self.destImageLabel)

        self.srcLayout.addWidget(self.srcPositionSlider)
        self.destLayout.addWidget(self.destPositionSlider)

        self.srcLayout.addWidget(self.srcImageIndexLabel)
        self.destLayout.addWidget(self.destImageIndexLabel)

        self.srcLayout.setAlignment(Qt.AlignCenter)
        self.destLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.setAlignment(Qt.AlignCenter)

        self.mainLayout.addLayout(self.srcLayout)
        self.mainLayout.addLayout(self.destLayout)
        self.window.setLayout(self.mainLayout)

        self.setCentralWidget(self.window)
        self.show()

    def createLinkClicked(self):
        print("createLinkClicked() entered")
        # When create button is clicked
        # Disable other widgets
        # Read frame length
        # Update positional slider
        # Create a dictionary key = frameIdx returns (x,y,xLength,yLength)
        #
        #
        # Change link button to turn off link creator mode

        #check frameLength number and make sure it is a valid int
        frameNum = self.frameLength.text()
        try:
            frameNum = int(frameNum)
        except:
            print("Invalid frame length value.")
            return
        if self.linkCreationActive == False:
            self.createLinkButton.setText('Exit Hyperlink Mode')
            self.frameLength.setEnabled(False)
            self.linkCreationActive = True
            self.srcImageLabel.setPosition(int((C_WIDTH/2.0)-15),int((C_LENGTH/2.0)-15),30,30)
            self.srcImageLabel.setLink(True)
        else:
            #if hyperlink mode on,
            self.createLinkButton.setText('Create Hyperlink')
            self.frameLength.setEnabled(True)
            self.linkCreationActive = False
            self.srcImageLabel.setPosition(0,0,0,0)
            self.srcImageLabel.setLink(False)
            self.srcImageLabel.clearLink()
    def updateLink(self):
        # This is called by the HyperlinkLabel class
        # When the mouse is released, save the frame idx
        # save the x,y,xLength,yLength from the class
        # Update the link dictionary
        #
        print("updateLink() entered")
    def setSrcPosition(self):
        #print("setSrcPosition() called")
        #print(self.srcPositionSlider.value())
        self.src_image_idx = self.srcPositionSlider.value()
        if (self.src_image_idx <len(self.src_rgb_files)):
            self.displaySrcImage(self.src_rgb_files[self.src_image_idx])
            self.srcImageIndexLabel.setText("Frame: {}".format(self.src_image_idx+1))

    def setDestPosition(self):
        #print("setDestPosition() called")
        self.dest_image_idx = self.destPositionSlider.value()
        if (self.dest_image_idx <len(self.dest_rgb_files)):
            self.displayDestImage(self.dest_rgb_files[self.dest_image_idx])
            self.destImageIndexLabel.setText("Frame: {}".format(self.dest_image_idx+1))

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
            self.srcImageIndexLabel.setText("Frame: {}".format(self.src_image_idx+1))
            self.createLinkButton.setEnabled(True)
        else:
            self.src_image_idx = 0
            self.srcPositionSlider.setRange(0, 0)
            self.srcImageIndexLabel.setText("Frame:")
            self.createLinkButton.setEnabled(False)
    def openDestinationVideo(self):
        #print("openDestinationVideo() called")
        file = str(QFileDialog.getExistingDirectory(self, "Select Destination Video Directory"))
        pass_fail, self.dest_rgb_files = self.getRGBFiles(os.path.abspath(file))
        if pass_fail:
            #there are valid files in the given directory
            self.destPositionSlider.setRange(0, len(self.dest_rgb_files)-1)
            self.displayDestImage(self.dest_rgb_files[0])
            self.dest_image_idx = 0
            self.destImageIndexLabel.setText("Frame: {}".format(self.dest_image_idx+1))
        else:
            self.destPositionSlider.setRange(0, 0)
            self.dest_image_idx = 0
            self.destImageIndexLabel.setText("Frame:")

    def displaySrcImage(self,path):
        #given the path, display the image onto the label
        #qim = QImage(self.ibc.convert(path),self.imageWidth,self.imageHeight,QImage.Format_RGB888)
        #pixmap = QPixmap.fromImage(qim)
        #self.srcImageLabel.setPixmap(pixmap)
        #self.srcImageLabel.resize(self.imageWidth,self.imageHeight)
        self.srcImageLabel.setPath(path)
        self.srcImageLabel.update()
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
