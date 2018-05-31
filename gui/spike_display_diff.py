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

"""
The code runs on three threads 
    i) for continuously receiving data from the microcontroller 
    ii) for processing the received data
    ii) for updating the interface using this data
"""

# Identifying the Micro Controller 
ser = serial.Serial("/dev/ttyACM0",7372800)
ser.flushInput()
ser.flushOutput()

"""
Stores data from the microcontroller as a 'deque' of bytes.
Packet format:
    [1 (start byte)]
    [8 bytes for negative spike information]
    [8 bytes for positive spike information]
    [2 (end byte)]
"""
rawQueue = deque([])

# Control variable to pause or resume receiving
receiveControl = 0
# Spike activity (1 - positive, -1 - negative, 0 - none)
spikeEvent = np.full((4,4,4), 0)
# Control variable for updating the interface
update = 0
updateControl = 0

# Variable to store timestep count
TIME = 0

# File writing variables
FILENAME = None
FILE = None
WRITE = False

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
    Vread = VCC*(1-ival/4096)
    colorValue =  min(255,int((voltageMax-Vread)*256/(voltageMax-Vcurrent)))
    return colorValue


# Functions to send and receive data from microcontroller 
def send(data) :
    global ser
    length = len(data)
    print("writing")
    for i in range(length) :
        ser.write((data[i]+"\r\n").encode('ascii'))
        print("wrote data :",data[i])

def receive() :
    global ser,receiveControl,rawQueue
    while True :
        if receiveControl == 1 :
            waiting = ser.inWaiting()
            if waiting >= 0 :
                rawQueue.extend(ser.read(waiting))
        time.sleep(0.0001)

def updateDataQueue() :
    global rawQueue, update, updateControl, TIME
    global WRITE, FILE
    while True:
        if len(rawQueue) >= 18 and updateControl == 1 :
            TIME += 1
            packet = [rawQueue.popleft() for i in range(18)][1:17]
            negPacket = packet[0:8]
            posPacket = packet[8:16]

            # Convert 8 bytes to one 64 bit number
            positive_spikes = posPacket[0]
            negative_spikes = negPacket[0]
            for i in range(1, 8):
                positive_spikes = positive_spikes << 8 | posPacket[i]
                negative_spikes = negative_spikes << 8 | negPacket[i]
            
            # Iterate over the 64 positions
            for i in range(64):
                posVal = (positive_spikes & 1<<i) >> i
                negVal = (negative_spikes & 1<<i) >> i

                patchNum = i % 4
                row = (i % 16)//4
                col = i//16

                if posVal == 1:
                    # Positive Spike
                    spikeEvent[patchNum][row][col] = 1                    
                    if WRITE and FILE is not None:
                        # write spike data to the file
                        FILE.write("{0} {1} {2} {3} {4}\n".format(patchNum, row, col, 1, TIME))
                else :
                    if negVal == 1:
                        # Negative Spike
                        spikeEvent[patchNum][row][col] = -1                        
                        if WRITE and FILE is not None:
                            # write spike data to the file
                            FILE.write("{0} {1} {2} {3} {4}\n".format(patchNum, row, col, -1, TIME))
                    else :
                        # No Spike
                        spikeEvent[patchNum][row][col] = 0
                        # Nothing written in case of no spike event               
            update = 1
        time.sleep(0.001)

# Class for Interface
class Main(QMainWindow,Ui_MainWindow) :
    def __init__(self):
        super(Main,self).__init__()
        self.setupUi(self)

        """
        Array to store data to be displayed on the interface.
        Three levels of sensitivity are displayed for each patch
            (1) High sensitivity (2.5V - 3V)
            (2) Medium sensitivity (2V - 3V)
            (3) Low sensitivity (1.5V - 3V)
        """
        self.intensityData = []
        for k in range(3) :
            self.intensityData.append([])
            for i in range(4) :
                # Interface initialized to black
                self.intensityData[k].append(np.full((4,4,3),0))
        
        # Two variables to avoid multiple starting and stopping of thread
        self.start = 0
        self.stop = 0

        # Thread which updates the plot based on data received from microcontroller
        self.thr = threading.Thread(target = self.processData)

        print("Intitialising ... ", end='')
        self.init()
        print("Done.")

    # Function for initialising interface and callbacks
    def init(self) :
        print("Adding view-boxes ... ", end='')
        # displays are the viewboxes (one for each patch of tactile sensors)
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

        # Callback functions for Start, Pause, File and Read buttons
        self.startButton.clicked.connect(self.doStart)
        self.stopButton.clicked.connect(self.doStop)
        self.readButton.clicked.connect(self.doRead)
        self.chooseButton.clicked.connect(self.chooseFile)

        print("Done.")

    def doStart(self) :
        # starting the thread to update the interface
        global recvThread, ser, receiveControl, updateThread, updateControl
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
            print("Resumed")
            self.stop = 0
            receiveControl = 1
            updateControl = 1

    def doStop(self) :
        # stop the thread which updates the interface
        global receiveControl, updateControl
        if self.stop == 0 :
            print("Paused")
            self.stop = 1
            receiveControl = 0
            updateControl = 0
            print("Press Ctrl+C to exit")
    
    def chooseFile(self):
        global FILE, FILENAME
        FILENAME = QtWidgets.QFileDialog.getSaveFileName()[0]
        if FILENAME != None and FILENAME != "":
            print("Saving data to \"{0}\"".format(FILENAME))
        
        if FILE is None:
            try:
                FILE = open(FILENAME, 'a')
            except Exception as _:
                print("Unable to open file!")
                FILENAME = None
        else:
            FILE.close()
            try:
                FILE = open(FILENAME, 'a')
            except Exception as _:
                print("Unable to open file!")
                FILENAME = None

    def doRead(self):
        global WRITE
        if WRITE:
            WRITE = False
            self.readButton.setText("Resume")
        else:
            WRITE = True
            self.readButton.setText("Pause")

    def updateRGB(self,pos):
        global spikeEvent
        patchNum = pos % 4
        row = (pos % 16)//4
        col = pos//16
        for sense in range(3) :
            if spikeEvent[patchNum][row][col] == 1:
                self.intensityData[sense][patchNum][row][col] = np.array([255, 0, 0])
            elif spikeEvent[patchNum][row][col] == -1:
                self.intensityData[sense][patchNum][row][col] = np.array([0, 0, 255])
            else:
                self.intensityData[sense][patchNum][row][col] = np.array([0, 0, 0])
        

    # Function to update the interface in real time.
    # It runs in a separate thread.
    def processData(self) :
        global update
        while True :
            if self.stop == 0 and update == 1 :
                for pos in range(64) :
                    self.updateRGB(pos)    
                update = 0
                
                for patchNum in range(4) :
                    if patchNum == 0 :
                        self.currImageMed1.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh1.setImage(self.intensityData[2][patchNum],levels=(0,255))
                        self.currImageLow1.setImage(self.intensityData[0][patchNum],levels=(0,255))
                    elif patchNum == 1 :
                        self.currImageLow2.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        self.currImageMed2.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh2.setImage(self.intensityData[2][patchNum],levels=(0,255))
                    elif patchNum == 2 :
                        self.currImageLow3.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        self.currImageMed3.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh3.setImage(self.intensityData[2][patchNum],levels=(0,255))
                    elif patchNum == 3 :
                        self.currImageLow4.setImage(self.intensityData[0][patchNum],levels=(0,255))
                        self.currImageMed4.setImage(self.intensityData[1][patchNum],levels=(0,255))
                        self.currImageHigh4.setImage(self.intensityData[2][patchNum],levels=(0,255))
            time.sleep(0.001)

# Thread to receive data
recvThread = threading.Thread(target = receive)
# Thread to process the received data
updateThread = threading.Thread(target = updateDataQueue)
 
if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        main = Main()
        main.show()
        app.exec_()
        recvThread.join(0)
    except Exception as _:
        pass
    sys.exit(0)
