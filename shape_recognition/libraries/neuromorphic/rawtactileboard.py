# -*- coding: utf-8 -*-
'''
#-------------------------------------------------------------------------------
# NATIONAL UNIVERSITY OF SINGAPORE - NUS
# SINGAPORE INSTITUTE FOR NEUROTECHNOLOGY - SINAPSE
# Singapore
# URL: http://www.sinapseinstitute.org
#-------------------------------------------------------------------------------
# Neuromorphic Engineering Group
# ONR Presentation: June 13th, 2018
#-------------------------------------------------------------------------------
# Description: Library for handling serial communication with the main board
# that reads the 4x4 tactile sensors
#-------------------------------------------------------------------------------
# Notes:
# 1) Columns and Rows have been swapped for proper visualization. That is why
# rows and cols will appear weird in the code (rows first, then cols when
# accessing the taxel matrix).
# 2) The complete tactile sensor matrix have been flipped in the end also for
# visualization purposes
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
#Paths
import os, sys, glob
sys.path.append('../general') #general libraries
import numpy as np #numpy
import time #sleep
import datetime
from threading import Thread, Lock #handling concurrent threads
from collections import deque #queue for handling data
from copy import copy #copy is necessary to avoid problems
from serialhandler import SerialHandler #serial handler for communication
from threadhandler import ThreadHandler #thread handler for data acquisition
from dataprocessing import * #moving average
#-------------------------------------------------------------------------------
class RawTactileBoard():
    def __init__(self,_port='COM3',_flagSpike=False):
        self.NROWS = 4 #number of rows
        self.NCOLS = 4 #number of columns
        self.NPATCH = 5 #number of sensors
        self.port = _port #port name
        self.dataQueue = deque() #data queue
        self.thAcqLock = Lock() #lock for data acquisition
        self.thProcLock = Lock() #lock for data processing
        #serial handler for receiving data
        self.serialHandler = SerialHandler(self.port,7372800,_header=0x24,_end=0x21,_numDataBytes=160,_thLock=self.thAcqLock)
        #thread for receiving packages
        self.thAcq = ThreadHandler(self.serialHandler.readPackage)
        #thread for processing the packages
        self.thProc = ThreadHandler(self.processData)
        #moving average for all taxels of each tactile sensor patch
        self.mva = [[] for k in range(self.NPATCH*self.NROWS*self.NCOLS)]
        for k in range(len(self.mva)):
            self.mva[k] = copy(MovingAverage(_windowSize = 10)) #10 Hz cut-off frequency
        self.taxelCounter = 0 #counter for moving average across all taxels
        #matrix for storing previous values --> necessary for integrate and fire spikes
        self.prevTactile = np.zeros((self.NPATCH,self.NROWS,self.NCOLS),dtype=float)
        #threshold for spike detection
        self.threshold = 100
        #flag that determines whether spikes or raw values should be used
        self.flagSpike = _flagSpike

    #start data acquisition
    def start(self):
        self.serialHandler.open() #open the serial port
        self.thAcq.start() #start data acquisition
        self.thProc.start() #start data processing

    #stop acquisition
    def stop(self):
        self.thAcq.kill() #kill thread
        self.thProc.kill() #kill thread

    def processData(self):
        #x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.thAcqLock.acquire()
        n = len(self.serialHandler.dataQueue)
        q = copy(self.serialHandler.dataQueue)
        self.serialHandler.dataQueue.clear()
        self.thAcqLock.release()
        #y = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        #if n > 0:
        #    print(x,y,n)

        #3d array containing the 4x4 matrix of each tactile patch
        self.tactileSensors = np.zeros((self.NPATCH,self.NROWS,self.NCOLS),dtype=float)

        for k in range(n):
            data = q.popleft()
            for z in range(0,160,2):

                patchNum = int((z/2)%self.NPATCH)
                row = int((z/2)%(self.NROWS*self.NPATCH)//self.NPATCH)
                col = int((z/2)//(self.NCOLS*self.NPATCH))
                #print(z,z/2,patchNum,row,col)

                sample = data[z]<<8 | data[z+1]

                if self.flagSpike:
                    if(sample - self.prevTactile[patchNum][col][row] > self.threshold):
                        self.tactileSensors[patchNum][col][row] = 1
                        #print(sample,self.prevTactile[patchNum][col][row])
                    elif(self.prevTactile[patchNum][col][row] - sample > self.threshold):
                        self.tactileSensors[patchNum][col][row] = 0
                    else:
                        self.tactileSensors[patchNum][col][row] = 0.5
                    self.prevTactile[patchNum][col][row] = sample
                else:
                    self.tactileSensors[patchNum][col][row] = self.mva[self.taxelCounter].getSample(sample)
                    self.taxelCounter += 1
                    if self.taxelCounter >= (self.NPATCH*self.NROWS*self.NCOLS):
                        self.taxelCounter = 0

            self.thProcLock.acquire()
            for w in range(self.NPATCH):
                self.tactileSensors[w] = np.flip(self.tactileSensors[w],1)
            self.dataQueue.append(copy(self.tactileSensors))
            self.thProcLock.release()

        time.sleep(0.001) #necessary to prevent really fast thread access

    def getData(self):
        self.thProcLock.acquire()
        q = copy(self.dataQueue)
        self.dataQueue.clear()
        self.thProcLock.release()
        return q
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
if __name__=='__main__':
    def update():
        global tactileBoard
        q = tactileBoard.getData()
        n = len(q)
        for k in range(n):
            data = q.popleft()
            print(data[0])

    thMain = ThreadHandler(update)
    tactileBoard = RawTactileBoard('COM3')
    tactileBoard.start()
    thMain.start()
    a = input()
