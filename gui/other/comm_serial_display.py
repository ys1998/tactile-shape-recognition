# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!
import os, sys, glob
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUiType
import numpy as np
import pyqtgraph as pg
import serial
import threading
from collections import deque

Ui_MainWindow, QMainWindow = loadUiType('interface.ui')

##### The code runs two threads 
#               i) one for receiving data from the Microcontroller
#               ii) another for updating the Interface using this data.

# Identifying the Micro Controller 
ser = serial.Serial("/dev/ttyACM0",7372800)
ser.flushInput()
ser.flushOutput()

# Stores data from the Micro Controller
dataQueue = deque([])
queueLen = 0

# Functions to send and receive data from Micro Controller 
def send(data) :
    global ser
    length = len(data)
    for i in range(length) :
        print("writing")
        ser.write((data[i]+"\r\n").encode('ascii'))
        print("wrote data :",data[i])

def receive() :
    global dataQueue,queueLen,ser
    while True :
        if ser.inWaiting() > 0 :
            queueLen = queueLen+ser.inWaiting()
            currQueue = [x for x in ser.read(ser.inWaiting())]
            for x in currQueue :
                dataQueue.append(x)
            #print(currQueue)
        

# Class for Interface
class Main(QMainWindow,Ui_MainWindow) :
    def __init__(self):
        super(Main,self).__init__()
        self.setupUi(self)
        # IntnesityData : Arrays to store data to be displayed on Interface
        self.rawData = np.zeros((4,4,4))
        self.intensityData1 = np.full((4,4,3),0)
        self.intensityData2 = np.full((4,4,3),0)
        self.intensityData3 = np.full((4,4,3),0)
        self.intensityData4 = np.full((4,4,3),0)
        self.start = 0
        self.stop = 0
        for i in range(4) :
            for j in range(4) :
                self.intensityData1[i][j][2] = 255
                self.intensityData2[i][j][2] = 255
                self.intensityData3[i][j][2] = 255
                self.intensityData4[i][j][2] = 255
        # Thread which updates the plot based on received data from Micro Controller
        self.thr = threading.Thread(target = self.processData)
        self.thr.deamon = True

        print("Intitialisation")
        self.init()
    # init() Contains other initialisations
    def init(self) :
        print("Adding ViewBoxes")
        # displays are the viewboxes (one for each patch of tactile sensors)
        self.display1 = self.patch1.addViewBox()
        self.display2 = self.patch2.addViewBox()
        self.display3 = self.patch3.addViewBox()
        self.display4 = self.patch4.addViewBox()

        # Image items to be displayed on the viewboxes
        self.currImage1 = pg.ImageItem(self.intensityData1)
        self.display1.addItem(self.currImage1)
        self.currImage2 = pg.ImageItem(self.intensityData2)
        self.display2.addItem(self.currImage2)
        self.currImage3 = pg.ImageItem(self.intensityData3)
        self.display3.addItem(self.currImage3)
        self.currImage4 = pg.ImageItem(self.intensityData4)
        self.display4.addItem(self.currImage4)

        # Functions of Start and Stop buttons
        self.startButton.clicked.connect(self.doStart)
        self.stopButton.clicked.connect(self.doStop)

    def doStart(self) :
        # starting the thread to update the Interface
        if self.start == 0 :
            self.start = 1
            self.thr.start()

    def doStop(self) :
        # stop the thread which updates the Interface
        if self.stop == 0 :
            self.stop = 1
            self.thr.join(0)

    # The function to update the Interface in real time. This function is ran in a thread.
    def processData(self) :
        global queueLen,dataQueue
        while queueLen > 1 :
            if queueLen > 1 :
            #if queueLen > 2 :

                # Read the intensity change data from the dataQueue
                pos,delta,delta2 = dataQueue.popleft(),dataQueue.popleft(),dataQueue.popleft()
                #delta = delta1*256 + delta2
                #pos,delta = dataQueue.popleft(),dataQueue.popleft()
                # Patch number as specified by the read data 
                patchNum = pos//16
                row = (pos%16)//4
                col = (pos%16)%4
                self.rawData[patchNum][row][col] = min(255,self.rawData[patchNum][row][col] + delta)
                if patchNum == 0 :
                    self.intensityData1[row][col][0] = max(0,2*self.rawData[0][row][col]-255)
                    self.intensityData1[row][col][2] = max(0,255-2*self.rawData[0][row][col])
                    self.intensityData1[row][col][1] = 255-self.intensityData1[row][col][2]-self.intensityData1[row][col][0]
                    self.currImage1.setImage(self.intensityData1,levels=(0,255))
                elif patchNum == 1 :
                    self.intensityData2[row][col][0] = max(0,2*self.rawData[1][row][col]-255)
                    self.intensityData2[row][col][2] = max(0,255-2*self.rawData[1][row][col])
                    self.intensityData2[row][col][1] = 255-self.intensityData2[row][col][2]-self.intensityData2[row][col][0]
                    self.currImage2.setImage(self.intensityData2,levels=(0,255))
                elif patchNum == 2 :
                    self.intensityData3[row][col][0] = max(0,2*self.rawData[2][row][col]-255)
                    self.intensityData3[row][col][2] = max(0,255-2*self.rawData[2][row][col])
                    self.intensityData3[row][col][1] = 255-self.intensityData3[row][col][2]-self.intensityData3[row][col][0]
                    self.currImage3.setImage(self.intensityData3,levels=(0,255))
                elif patchNum == 3 :
                    self.intensityData4[row][col][0] = max(0,2*self.rawData[3][row][col]-255)
                    self.intensityData4[row][col][2] = max(0,255-2*self.rawData[3][row][col])
                    self.intensityData4[row][col][1] = 255-self.intensityData4[row][col][2]-self.intensityData4[row][col][0]
                    self.currImage4.setImage(self.intensityData4,levels=(0,255))
                queueLen = queueLen - 3
                #queueLen = queueLen - 2
        print(self.intensityData1)

send(["1"])

# Thread to receive data
threading.Thread(target = receive).start()

# Parallely update the display based on received data. The class for interface( Main )
# itself runs another thread.
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
