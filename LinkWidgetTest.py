import VideoEditor
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter,QPen, QBrush, QColor
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
import ImageByteConverter
if __name__ == '__main__':
    app = QApplication(sys.argv)
    path = '/Users/michaelwu/Documents/CSCI576/NewYorkCity/NYOne/NYOne0001.rgb'
    window = VideoEditor.HyperlinkLabel()
    window.setPath(path)
    window.resize(352, 288)
    #window.drawRect()
    #ibc = ImageByteConverter.ImageByteConverter()
    #qim = QImage(ibc.convert(path),352,288,QImage.Format_RGB888)
    #pixmap = QPixmap.fromImage(qim)
    #window.setPixmap(pixmap)
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
