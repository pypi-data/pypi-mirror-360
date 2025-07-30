import sys
import warnings

from spiceitup.run import Main
from spiceitup.settings.const import Const
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def main():
    warnings.filterwarnings("ignore")
    # Used to prevent to show All-NaN RuntimeWarning
    # Slices in the data cube can be filled with NaN
    # Of course, comment this line while you are developing

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    win = Main()
    win.applyStyle(app)
    win.resize(Const.window_width, Const.window_height)
    win.setWindowIcon(QIcon('images/icon.png'))
    win.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
