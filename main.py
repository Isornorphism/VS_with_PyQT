# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication
from game import *
import sys

    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Game()
    w.show()
    
    sys.exit(app.exec_())
    #app.exec_()
    #app.quit()
    