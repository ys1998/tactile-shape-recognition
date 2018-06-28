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
import time
import importlib
from collections import deque
from threadhandler import ThreadHandler

Ui_MainWindow, QMainWindow = loadUiType('interface.ui')


##### The code runs two threads 
#               i) one for receiving data from the Microcontroller
#               ii) another for updating the Interface using this data.

# Identifying the Micro Controller 
ser = serial.Serial("/dev/ttyACM0",7372800)
ser.flushInput()
ser.flushOutput()

# Stores data from the Micro Controller
dataQueue = np.zeros((4,4,4))
update = 0

def getPos(pos) :
    patchNum = pos//16
    row = (pos%16)//4
    col = (pos%16)%4
    return patchNum + 4*row + 16*col

def getPos2(pos) :
    patchNum = pos//16
    row = (pos%16)//4
    col = (pos%16)%4
    return 4*patchNum + row + 16*col

# Functions to send and receive data from Micro Controller 
def send(data) :
    global ser
    length = len(data)
    for i in range(length) :
        #print("writing")
        ser.write((data[i]+"\r\n").encode('ascii'))
        #print("wrote data :",data[i])

def receive() :
    global dataQueue,ser,update
    while True :
        waiting = ser.inWaiting()
        maxlength = 34
        if waiting >= maxlength :
            rawQueue = [x for x in ser.read(waiting)]
            endByte = len(rawQueue)-1
            #print(endByte,waiting)
            while rawQueue[endByte] != 2 and endByte > 0 :
                endByte = endByte-1
            #print(endByte)
            if endByte < maxlength-1 :
                continue
            if rawQueue[endByte-maxlength+1] == 1 :
                for row in range(4) :
                    for col in range(4) :
                        pos = 2*(4*col+row)+endByte-maxlength+2
                        dataQueue[0][row][col] = 4096-(rawQueue[pos]+rawQueue[pos+1]*256)
                update = 1
                print("Received packet : ",dataQueue[0])
        

# Class for Interface
class Main(QMainWindow,Ui_MainWindow) :
    def __init__(self):
        super(Main,self).__init__()
        self.setupUi(self)
        # IntnesityData : Array to store data to be displayed on Interface
        self.intensityData = []
        for i in range(4) :
            self.intensityData.append(np.full((4,4,3),0))
        # Two variables to avoid mutliple starting and stopping of thread
        self.start = 0
        self.stop = 0
        # initialise Interface to blue
        for i in range(4) :
            for j in range(4) :
                for k in range(4) :
                    self.intensityData[i][j][k][2] = 255
        # Thread which updates the plot based on received data from Micro Controller
        self.thr = ThreadHandler(self.processData)

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
        self.currImage1 = pg.ImageItem(self.intensityData[0])
        self.display1.addItem(self.currImage1)
        self.currImage2 = pg.ImageItem(self.intensityData[1])
        self.display2.addItem(self.currImage2)
        self.currImage3 = pg.ImageItem(self.intensityData[2])
        self.display3.addItem(self.currImage3)
        self.currImage4 = pg.ImageItem(self.intensityData[3])
        self.display4.addItem(self.currImage4)

        # Functions of Start and Stop buttons
        self.startButton.clicked.connect(self.doStart)
        self.stopButton.clicked.connect(self.doStop)

    def doStart(self) :
        # starting the thread to update the Interface
        global recvThread,ser
        if self.start == 0 :
            ser.flushInput()
            self.start = 1
            self.thr.start()
            recvThread.start()

    def doStop(self) :
        # stop the thread which updates the Interface
        global recvThread
        if self.stop == 0 :
            print("Stopped")
            self.stop = 1
            self.thr.pause()
            recvThread.pause()
            self.thr.kill()
            recvThread.kill()

    # The function to update the Interface in real time. This function is ran in a thread.
    def processData(self) :
        global update,dataQueue
        while True :
            #print(update)
            if update == 1 : 
                #print("First update")
                for pos in range(64) :
                    patchNum = pos//16
                    row = (pos%16)//4
                    col = (pos%16)%4
                    if patchNum == 0 :
                        self.intensityData[0][row][col][0] = max(0,2*int(dataQueue[patchNum][col][row]/16)-255)
                        self.intensityData[0][row][col][2] = max(0,255-2*int(dataQueue[patchNum][col][row]/16))
                        self.intensityData[0][row][col][1] = 255-self.intensityData[0][row][col][2]-self.intensityData[0][row][col][0]
                        self.currImage1.setImage(self.intensityData[0],levels=(0,255))
                    elif patchNum == 1 :
                        self.intensityData[1][row][col][0] = max(0,2*int(dataQueue[patchNum][col][row]/16)-255)
                        self.intensityData[1][row][col][2] = max(0,255-2*int(dataQueue[patchNum][col][row]/16))
                        self.intensityData[1][row][col][1] = 255-self.intensityData[1][row][col][2]-self.intensityData[1][row][col][0]
                        self.currImage2.setImage(self.intensityData[1],levels=(0,255))
                    elif patchNum == 2 :
                        self.intensityData[2][row][col][0] = max(0,2*int(dataQueue[patchNum][col][row]/16)-255)
                        self.intensityData[2][row][col][2] = max(0,255-2*int(dataQueue[patchNum][col][row]/16))
                        self.intensityData[2][row][col][1] = 255-self.intensityData[2][row][col][2]-self.intensityData[2][row][col][0]
                        self.currImage3.setImage(self.intensityData[2],levels=(0,255))
                    elif patchNum == 3 :
                        self.intensityData[3][row][col][0] = max(0,2*int(dataQueue[patchNum][col][row]/16)-255)
                        self.intensityData[3][row][col][2] = max(0,255-2*int(dataQueue[patchNum][col][row]/16))
                        self.intensityData[3][row][col][1] = 255-self.intensityData[3][row][col][2]-self.intensityData[3][row][col][0]
                        self.currImage4.setImage(self.intensityData[3],levels=(0,255))
                update = 0
        #print(self.intensityData[0])


# Thread to receive data
#recvThread = threading.Thread(target = receive)
recvThread = ThreadHandler(receive)
# Parallely update the display based on received data. The class for interface( Main )
# itself runs another thread.
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())
