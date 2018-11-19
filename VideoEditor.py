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
Create a hyperlink DONE!
Define hyperlink DONE!

Phase 3:
Save file DONE!

Phase 4:
Delete links
Status bar

*****************************************************************************'''
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QDir, Qt, QUrl, QByteArray, QTimer, QRect,QPoint
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QSound
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QLineEdit,
        QComboBox)
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
Inherits from QLabel
This LinkWidget will be used for the source image. When the link variable is
set to True, the mouse events will be enabled. The user can set up the
hyperlinks to their choosing.

When the mouse button is released, updateLink() will be called from the
VideoEditor class
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

            #if self.parent.src_image_idx in self.parent.currentLink:
            #    self.begin = QPoint( self.parent.currentLink[self.parent.src_image_idx][0],self.parent.currentLink[self.parent.src_image_idx][1])
            #    self.end = QPoint(self.parent.currentLink[self.parent.src_image_idx][0]+self.parent.currentLink[self.parent.src_image_idx][2],self.parent.currentLink[self.parent.src_image_idx][1]+self.parent.currentLink[self.parent.src_image_idx][3])
                #self.update()
                #print(self.begin.x())
                #print(self.begin.y())
                #print(self.end.x())
                #print(self.end.y())
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
        self.xLength = xLength
        self.yLength = yLength
        self.initialX = x
        self.initialY = y
        self.update()
    def getPosition(self):
        return self.initialX,self.initialY,self.xLength,self.yLength
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
        self.src_rgb_dir = ''
        self.dest_rgb_dir = ''
        self.src_image_idx = 0
        self.dest_image_idx = 0
        self.ibc = ImageByteConverter.ImageByteConverter()
        self.imageWidth = C_WIDTH
        self.imageHeight = C_LENGTH
        self.linkCreationActive = False
        self.destVideoLoaded = False
        #these are used during hyperlink creation
        # currentLink key = frame num, returns [x,y,xLength,yLength]
        # currentFrame is the main frame number to start the link
        self.currentLink = {}
        self.currentFrame = []
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
        self.defineLinkButton.clicked.connect(self.defineLinkClicked)
        self.saveButton = QPushButton('Save File', self)
        self.saveButton.clicked.connect(self.saveFileClicked)
        self.createLinkButton.setEnabled(False)
        self.defineLinkButton.setEnabled(False)
        self.saveButton.setEnabled(False)

        #combobox for links
        self.linkComboBox = QComboBox(self)
        self.deleteLinkButton = QPushButton('Delete Link', self)
        self.deleteLinkButton.clicked.connect(self.deleteLinkClicked)

        #status label
        self.statusLabel = QLabel(self)
        self.statusLabel.setText("Status:")

        #lineedit for filename
        self.filenameLabel = QLabel()
        self.filenameLabel.setText("Output Filename:")
        self.filenameLineEdit = QLineEdit(self)

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
        self.srcButtonLayout2 = QHBoxLayout()
        self.destButtonLayout2 = QHBoxLayout()

        self.srcButtonLayout2.addWidget(self.deleteLinkButton)
        self.srcButtonLayout2.addWidget(self.linkComboBox)
        self.destButtonLayout2.addWidget(self.filenameLabel)
        self.destButtonLayout2.addWidget(self.filenameLineEdit)

        self.srcButtonLayout.addWidget(self.createLinkButton)
        self.srcButtonLayout.addWidget(self.frameLengthLabel)
        self.srcButtonLayout.addWidget(self.frameLength)

        self.destButtonLayout.addWidget(self.defineLinkButton)
        self.destButtonLayout.addWidget(self.saveButton)

        self.destLayout.addWidget(self.statusLabel)
        self.destLayout.addLayout(self.destButtonLayout2)
        self.srcLayout.addLayout(self.srcButtonLayout2)

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
        #self.mainLayout.setAlignment(Qt.AlignCenter)

        self.mainLayout.addLayout(self.srcLayout)
        self.mainLayout.addLayout(self.destLayout)
        self.window.setLayout(self.mainLayout)

        self.setCentralWidget(self.window)
        self.show()

    def createLinkClicked(self):
        print("createLinkClicked() entered")
        # When create button is clicked

        #check frameLength number and make sure it is a valid int
        frameNum = self.frameLength.text()
        try:
            frameNum = int(frameNum)
        except:
            print("Invalid frame length value.")
            return

        #reset this data structure
        self.currentLink = {}
        self.currentFrame = []
        if self.linkCreationActive == False:
            #entering into link creation mode
            self.createLinkButton.setText('Exit Hyperlink Mode')
            self.frameLength.setEnabled(False)
            self.defineLinkButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.linkCreationActive = True
            #initiate the link to a default position
            self.srcImageLabel.setPosition(int((C_WIDTH/2.0)-15),int((C_LENGTH/2.0)-15),30,30)
            #the mouse events are active now
            self.srcImageLabel.setLink(True)
            #adjust the slider to desired range
            end = self.srcPositionSlider.value() + frameNum
            if(end >= len(self.src_rgb_files)):
                end = len(self.src_rgb_files) - 1
            self.srcPositionSlider.setRange(self.srcPositionSlider.value(), end)

            #make adjustments to the currentLink dict
            x,y,xLen,yLen = self.srcImageLabel.getPosition()
            for idx in range(self.srcPositionSlider.value(),end+1):
                self.currentLink[idx] = [x,y,xLen,yLen]
            self.currentFrame.append(self.srcPositionSlider.value())

        else:
            #if hyperlink mode on, reset to viewing mode
            self.createLinkButton.setText('Create Hyperlink')
            self.frameLength.setEnabled(True)
            self.defineLinkButton.setEnabled(False)
            self.saveButton.setEnabled(True)
            self.linkCreationActive = False
            #remove the rectangle link
            self.srcImageLabel.setPosition(0,0,0,0)
            self.srcImageLabel.setLink(False)
            self.srcImageLabel.clearLink()
            self.currentLink = {}
            self.currentFrame = []
            self.srcPositionSlider.setRange(0, len(self.src_rgb_files) - 1)
    def defineLinkClicked(self):
        #when the define link button is clicked
        print("defineLinkClicked() entered")
        if self.destVideoLoaded:
            #save the source video and destination vide to the metadata
            self.metadata.addVideo(self.src_rgb_dir)
            self.metadata.addVideo(self.dest_rgb_dir)
            #save linkDict to the metadata
            for mainFrameIdx in range(len(self.currentFrame)):
                if self.currentFrame[mainFrameIdx] in self.currentLink:
                    #determine the end frame #
                    if mainFrameIdx+1 >= len(self.currentFrame):
                        currentLinkList=list(self.currentLink.keys())
                        endFrameIdx = max(currentLinkList)
                    else:
                        endFrameIdx = self.currentFrame[mainFrameIdx + 1] - 1
                    idx = self.metadata.getIdx(self.src_rgb_dir)
                    destIdx = self.metadata.getIdx(self.dest_rgb_dir)
                    destFrame = self.dest_image_idx
                    startFrameIdx = self.currentFrame[mainFrameIdx]
                    #[x1,y1,xLength,yLength,start frame #, end frame #, vid_dest, vid_dest start frame#]
                    self.metadata.addLink(idx,[self.currentLink[self.currentFrame[mainFrameIdx]][0],self.currentLink[self.currentFrame[mainFrameIdx]][1],self.currentLink[self.currentFrame[mainFrameIdx]][2],self.currentLink[self.currentFrame[mainFrameIdx]][3],startFrameIdx,endFrameIdx,destIdx,destFrame])
                else:
                    print("defineLinkClicked() ERROR CANNOT LOADED A MAIN FRAME.")
            print(self.metadata.metadata)
            #this button click will also kick out of hyperlink creation mode
            self.createLinkButton.setText('Create Hyperlink')
            self.frameLength.setEnabled(True)
            self.defineLinkButton.setEnabled(False)
            self.saveButton.setEnabled(True)
            self.linkCreationActive = False
            #remove the rectangle link
            self.srcImageLabel.setPosition(0,0,0,0)
            self.srcImageLabel.setLink(False)
            self.srcImageLabel.clearLink()

            self.currentLink = {}
            self.currentFrame = []

            self.srcPositionSlider.setRange(0, len(self.src_rgb_files) - 1)
        else:
            print("Destination video not loaded.")
    def saveFileClicked(self):
        #when the save file button is clicked
        print("saveFileClicked() entered")
        #check if there are any links in here, if there is then save
        filename = self.filenameLineEdit.text()
        basedir = os.path.dirname(filename)
        #check if the filename has a directory
        if basedir != '':
            if os.path.isdir(basedir):
                self.metadata.createMetadata(basedir,os.path.basename(filename))
            else:
                print("saveFileClicked() ERROR bad directory")
        else:
            #if not just use the current working directory
            self.metadata.createMetadata(os.getcwd(),filename)
        #clear the metadata
        self.metadata.resetMetadata()
    def updateLink(self):
        # This is called by the HyperlinkLabel class
        # When the mouse is released, save the frame idx
        # save the x,y,xLength,yLength from the class
        # Update the currentLink[] dictionary
        print("updateLink() entered")
        frameIdx = self.src_image_idx
        if frameIdx not in self.currentFrame:
            self.currentFrame.append(frameIdx)
            self.currentFrame.sort()
        x,y,xLen,yLen = self.srcImageLabel.getPosition()
        #update the currentLink
        self.currentLink[frameIdx] = [x,y,xLen,yLen]
        for idx in range(frameIdx+1,len(self.src_rgb_files)):
            if idx in self.currentFrame:
                #when the idx matches up to a main frame, exit out
                break
            else:
                #update the currentLink dict to the new position
                self.currentLink[idx] = [x,y,xLen,yLen]

    def deleteLinkClicked(self):
        # When the delete link button is click
        print("deleteLinkClicked() entered")
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
            self.src_rgb_dir = os.path.abspath(file)
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
            self.dest_rgb_dir = os.path.abspath(file)
            #there are valid files in the given directory
            self.destPositionSlider.setRange(0, len(self.dest_rgb_files)-1)
            self.displayDestImage(self.dest_rgb_files[0])
            self.dest_image_idx = 0
            self.destImageIndexLabel.setText("Frame: {}".format(self.dest_image_idx+1))
            self.destVideoLoaded = True
        else:
            self.destPositionSlider.setRange(0, 0)
            self.dest_image_idx = 0
            self.destImageIndexLabel.setText("Frame:")
            self.destVideoLoaded = False
    def displaySrcImage(self,path):
        #given the path, display the image onto the label
        #qim = QImage(self.ibc.convert(path),self.imageWidth,self.imageHeight,QImage.Format_RGB888)
        #pixmap = QPixmap.fromImage(qim)
        #self.srcImageLabel.setPixmap(pixmap)
        #self.srcImageLabel.resize(self.imageWidth,self.imageHeight)
        self.srcImageLabel.setPath(path)
        if self.linkCreationActive and (self.src_image_idx in self.currentLink):
            x = self.currentLink[self.src_image_idx][0]
            y = self.currentLink[self.src_image_idx][1]
            xLength = self.currentLink[self.src_image_idx][2]
            yLength = self.currentLink[self.src_image_idx][3]
            self.srcImageLabel.setPosition(x,y,xLength,yLength)
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
