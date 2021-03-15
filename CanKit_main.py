'''
Created on 2021-3-12

@author: C7278PT
'''
#coding=utf-8
import sys
from UI2 import Ui_Form
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import *
import time

#from PyQt5.QtWidgets import QApplication,QWidget,QMessageBox,QPushButton

class CanKitMain(QWidget,Ui_Form):
    def __init__(self):
        super(CanKitMain, self).__init__()
        self.setupUi(self)  
        self.init_ui()  

    def init_ui(self):
        self.pushButton.clicked.connect(self.show1)
        self.lineEdit.setText("0")
        self.thread= None
        
    def show1(self):
        if self.thread == None:
            self.thread = TH1()     #instance of thread
            self.thread.running = True
            self.thread.signal.connect(self.callback)   #connect to callback
            print("tread set!")
            self.thread.start( )    #start thread
        else:
            self.thread.running = False
            self.thread.quit()
            self.thread = None
            
    def callback(self): #callback
        #print("enter Callback...")
        iIn = self.lineEdit.text()
        i = int(iIn)
        i += 10;
        self.lineEdit.setText(str(i))
        self.lcdNumber.display(str(i))
        
            
    pass        
        


class TH1(QThread):
    signal = pyqtSignal(int) #fill in para
    def __init__(self):
        super().__init__()
        
    def __del__(self):
        self.wait()
        
    def run(self):
        print("Thread run")
        i = 1;
        for i in range(1000):
            if self.running == False: break
            self.signal.emit(i) #emit signal
            print("signal emitted!"+ str(i))
            time.sleep(0.2)







if __name__ == "__main__":
    app = QApplication(sys.argv[1:])

    window = CanKitMain()
    window.show()

    sys.exit(app.exec_())