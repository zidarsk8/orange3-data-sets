import math
import signal
import sys
import logging
from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import *

logger = logging.getLogger(__name__)


class Overlay(QWidget):

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.dot_count = 6

    def _draw_eclipse(self, painter, color, dot_number):
        painter.setBrush(QBrush(color))
        radiants = 2 * math.pi * dot_number / self.dot_count
        painter.drawEllipse(
            self.width() / 2 + 30 * math.cos(radiants) - 10,
            self.height() / 2 + 30 * math.sin(radiants) - 10,
            20, 20)

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(6):
            c = 127 + ((self.counter - i*3) % 18) * 7
            color = QColor(c, c, c)
            self._draw_eclipse(painter, color, i)

        painter.end()

    def showEvent(self, event):

        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):
        logger.info("counter %s", self.counter)

        self.counter += 1
        self.update()
        if self.counter == 70:
            self.killTimer(self.timer)
            self.hide()


class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        QMainWindow.__init__(self, parent)

        widget = QWidget(self)
        self.editor = QTextEdit()
        self.editor.setPlainText("0123456789" * 100)
        button = QPushButton("Wait", autoDefault=True)

        layout = QGridLayout(widget)
        layout.addWidget(button, 1, 1, 1, 1)
        layout.addWidget(self.editor, 0, 0, 1, 3)

        self.setCentralWidget(widget)
        self.overlay = Overlay(self.editor)
        self.overlay.hide()
        button.clicked.connect(self.press)

    def press(self):
        logger.info("pressed")
        self.overlay.counter = 0
        self.overlay.show()

    def resizeEvent(self, event):

        self.overlay.resize(event.size())
        event.accept()


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
