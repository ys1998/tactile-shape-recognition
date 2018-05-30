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

Ui_MainWindow, QMainWindow = loadUiType('interface_vertical.ui')


##### The code runs two threads 
#               i) one for receiving data from the Microcontroller
#               ii) another for updating the Interface using this data.

# Identifying the Micro Controller 
ser = serial.Serial("/dev/ttyACM0",7372800)
ser.flushInput()
ser.flushOutput()

# Stores data from the Micro Controller
rawQueue = deque([])

# Control variable to pause or resume receiving
receiveControl = 0
# processed intensity data in scale 0 to (4096)
dataQueue = np.full((4,4,4),450)

# Control variable for updating the interface
update = 0
updateControl = 0

# Functions to scale the intensity values to color values based on required sensitivity
def scaleVal(ival,sense) :
    VCC = 3.3
    voltageMax = 2.95
    voltageHigh = 2.8
    voltageMed = 1.5
    voltageLow = 0.5
    
    Vcurrent = 0
    if sense == 2 :
        Vcurrent = voltageHigh
    if sense == 1 :
        Vcurrent = voltageMed
    if sense == 0 :
        Vcurrent = voltageLow
    Vread = 3.3*(1-ival/4096)
    colorValue =  min(255,int((voltageMax-Vread)*256/(voltageMax-Vcurrent)))
    return colorValue


# Functions to send and receive data from Micro Controller 
def send(data) :
    global ser
    length = len(data)
    for i in range(length) :
        print("writing")
        ser.write((data[i]+"\r\n").encode('ascii'))
        print("wrote data :",data[i])

def receive() :
    global ser,receiveControl,rawQueue
    while True :
        if receiveControl == 1 :
            waiting = ser.inWaiting()
            if waiting >= 0 :
                for x in ser.read(waiting) :
                    rawQueue.append(x)
                #print(rawQueue)
        time.sleep(0.001)

def updateDataQueue() :
    global dataQueue,rawQueue,update,updateControl
    while True :
        if len(rawQueue) >= 18 and updateControl == 1 :
            packet = [rawQueue.popleft() for i in range(18)][1:17]
            print(packet)
            negPacket = packet[0:8]
            posPacket = packet[8:16]
            pos = 0
            for i in range(8) :
                bitstr = "{0:b}".format(posPacket[7-i])
                bitstr = "0"*(8-len(bitstr)) + bitstr
                for j in range(8) :
                    if bitstr[7-j] == "1" :
                        patchNum = pos%4
                        row = (pos%16)//4
                        col = pos//16
                        dataQueue[patchNum][row][col] = min(4000,dataQueue[patchNum][row][col] + 100)
                    pos = pos + 1
            pos = 0
            for i in range(8) :
                bitstr = "{0:b}".format(negPacket[7-i])
                bitstr = "0"*(8-len(bitstr)) + bitstr
                for j in range(8) :
                    if bitstr[7-j] == "1" :
                        patchNum = pos%4
                        row = (pos%16)//4
                        col = pos//16
                        dataQueue[patchNum][row][col] = max(450,dataQueue[patchNum][row][col] - 100)
                    pos = pos + 1
            update = 1
        time.sleep(0.001)

# Class for Interface
class Main(QMainWindow,Ui_MainWindow) :
    def __init__(self):
        super(Main,self).__init__()
        self.setupUi(self)
        # IntnesityData : Array to store data to be displayed on Interface
        self.intensityData = []
        for k in range(3) :
            self.intensityData.append([])
            for i in range(4) :
                self.intensityData[k].append(np.full((4,4,3),0))
        # Two variables to avoid mutliple starting and stopping of thread
        self.start = 0
        self.stop = 0
        # initialise Interface to blue
        for sense in range(3) :
            for i in range(4) :
                for j in range(4) :
                    for k in range(4) :
                        self.intensityData[sense][i][j][k][2] = 255
        # Thread which updates the plot based on received data from Micro Controller
        #self.thr = ThreadHandler(self.processData)
        self.thr = threading.Thread(target = self.processData)
        print("Intitialisation")
        self.init()
    # init() Contains other initialisations
    def init(self) :
        print("Adding ViewBoxes")
        # displays are the viewboxes (one for each patch of tactile sensors)
        #self.patchHigh1.setContentsMargins(0,0,0,0)
        self.displayLow1 = self.patchLow1.addViewBox()
        self.displayLow2 = self.patchLow2.addViewBox()
        self.displayLow3 = self.patchLow3.addViewBox()
        self.displayLow4 = self.patchLow4.addViewBox()

        self.displayMed1 = self.patchMed1.addViewBox()
        self.displayMed2 = self.patchMed2.addViewBox()
        self.displayMed3 = self.patchMed3.addViewBox()
        self.displayMed4 = self.patchMed4.addViewBox()

        self.displayHigh1 = self.patchHigh1.addViewBox()
        self.displayHigh2 = self.patchHigh2.addViewBox()
        self.displayHigh3 = self.patchHigh3.addViewBox()
        self.displayHigh4 = self.patchHigh4.addViewBox() 

        #self.displayHigh1.setAspectLocked(True)
        
        self.displayHigh1.setRange(xRange = [0,4],yRange = [0,4])
        self.displayHigh2.setRange(xRange = [0,4],yRange = [0,4])
        self.displayHigh3.setRange(xRange = [0,4],yRange = [0,4])
        self.displayHigh4.setRange(xRange = [0,4],yRange = [0,4])

        self.displayLow1.setRange(xRange = [0,4],yRange = [0,4])
        self.displayLow2.setRange(xRange = [0,4],yRange = [0,4])
        self.displayLow3.setRange(xRange = [0,4],yRange = [0,4])
        self.displayLow4.setRange(xRange = [0,4],yRange = [0,4])

        self.displayMed1.setRange(xRange = [0,4],yRange = [0,4])
        self.displayMed2.setRange(xRange = [0,4],yRange = [0,4])
        self.displayMed3.setRange(xRange = [0,4],yRange = [0,4])
        self.displayMed4.setRange(xRange = [0,4],yRange = [0,4])

        #self.displayHigh1.enableAutoRange(self.displayHigh1.XYAxes)
        #print(self.displayHigh1.viewRange())

        # Image items to be displayed on the viewboxes
        self.currImageLow1 = pg.ImageItem(self.intensityData[0][0])
        self.displayLow1.addItem(self.currImageLow1)
        self.currImageLow2 = pg.ImageItem(self.intensityData[0][1])
        self.displayLow2.addItem(self.currImageLow2)
        self.currImageLow3 = pg.ImageItem(self.intensityData[0][2])
        self.displayLow3.addItem(self.currImageLow3)
        self.currImageLow4 = pg.ImageItem(self.intensityData[0][3])
        self.displayLow4.addItem(self.currImageLow4)

        self.currImageMed1 = pg.ImageItem(self.intensityData[1][0])
        self.displayMed1.addItem(self.currImageMed1)
        self.currImageMed2 = pg.ImageItem(self.intensityData[1][1])
        self.displayMed2.addItem(self.currImageMed2)
        self.currImageMed3 = pg.ImageItem(self.intensityData[1][2])
        self.displayMed3.addItem(self.currImageMed3)
        self.currImageMed4 = pg.ImageItem(self.intensityData[1][3])
        self.displayMed4.addItem(self.currImageMed4)

        self.currImageHigh1 = pg.ImageItem(self.intensityData[2][0])
        self.displayHigh1.addItem(self.currImageHigh1)
        self.currImageHigh2 = pg.ImageItem(self.intensityData[2][1])
        self.displayHigh2.addItem(self.currImageHigh2)
        self.currImageHigh3 = pg.ImageItem(self.intensityData[2][2])
        self.displayHigh3.addItem(self.currImageHigh3)
        self.currImageHigh4 = pg.ImageItem(self.intensityData[2][3])
        self.displayHigh4.addItem(self.currImageHigh4)

        #self.currImageHigh1.view.setAspectLocked(False)

        # Functions of Start and Stop buttons
        self.startButton.clicked.connect(self.doStart)
        self.stopButton.clicked.connect(self.doStop)

    def doStart(self) :
        # starting the thread to update the Interface
        global recvThread,ser,receiveControl,updateThread,updateControl
        if self.start == 0 :
            ser.flushInput()
            self.start = 1
            self.stop = 0
            self.thr.start()
            print("Started")
            recvThread.start()
            updateThread.start()
            receiveControl = 1
            updateControl = 1
        if self.stop == 1 :
            print("Started Again")
            self.stop = 0
            receiveControl = 1
            updateControl = 1

    def doStop(self) :
        # stop the thread which updates the Interface
        global recvThread,receiveControl,updateControl
        if self.stop == 0 :
            print("Stopped")
            self.stop = 1
            receiveControl = 0
            updateControl = 0
            print("Press Ctrl+C to exit")
            #sys.exit(0)

    def updateRGB(self,pos) :
        global dataQueue
        patchNum = pos//16
        row = (pos%16)//4
        col = (pos%16)%4
        for sense in range(3) :
            iVal = scaleVal(dataQueue[patchNum][col][row],sense)
            self.intensityData[sense][patchNum][row][col][0] = max(0,2*iVal-255)
            self.intensityData[sense][patchNum][row][col][2] = max(0,255-2*iVal)
            self.intensityData[sense][patchNum][row][col][1] = 255-max(0,255-2*iVal)-max(0,2*iVal-255)
        

    # The function to update the Interface in real time. This function is ran in a thread.
    def processData(self) :
        global update,dataQueue
        while True :
            #print(self.stop)
            if self.stop == 0 and update == 1 :
                #print(dataQueue)
                for pos in range(64) :
                    self.updateRGB(pos)    
                update = 0
                
                #time.sleep(0.005)
                for patchNum in range(4) :
                    if patchNum == 0 :
                        self.currImageMed1.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh1.setImage(self.intensityData[2][patchNum],levels=(0,255))
                        self.currImageLow1.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        #print("Updating color maps")
                        #print(self.intensityData[0][0],self.intensityData[1][0],self.intensityData[2][0])
                    elif patchNum == 1 :
                        self.currImageLow2.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        self.currImageMed2.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh2.setImage(self.intensityData[2][patchNum],levels=(0,255))
                        #print(self.intensityData[0][1],self.intensityData[1][1],self.intensityData[2][1])
                    elif patchNum == 2 :
                        self.currImageLow3.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        self.currImageMed3.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh3.setImage(self.intensityData[2][patchNum],levels=(0,255))
                        #print(self.intensityData[0][2],self.intensityData[1][2],self.intensityData[2][2])
                    elif patchNum == 3 :
                        self.currImageLow4.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        self.currImageMed4.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh4.setImage(self.intensityData[2][patchNum],levels=(0,255))
            time.sleep(0.01)
        #print(self.intensityData[0])


# Thread to receive data
recvThread = threading.Thread(target = receive)
updateThread = threading.Thread(target = updateDataQueue)
#recvThread = ThreadHandler(receive)

# Parallely update the display based on received data. The class for interface( Main )
# itself runs another thread.
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()

    sys.exit(app.exec_())
    recvThread.join(0)
