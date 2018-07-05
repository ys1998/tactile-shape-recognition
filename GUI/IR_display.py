import os, sys, glob
sys.path.append('../shape_recognition/libraries/general')
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUiType
import numpy as np
import pyqtgraph as pg
import serial
import threading
import time
import importlib
from dataprocessing import MovingAverage
from collections import deque

Ui_MainWindow, QMainWindow = loadUiType('IR_interface.ui')

ser = serial.Serial("/dev/ttyACM0",117964800)
ser.flushInput()
ser.flushOutput()
file_object = open("IR_sensor_data.txt",'w')
startTime = 0


dataQueue = deque([])
receiveControl = 0

def receive() :
	global dataQueue,ser
	recvLength = 6
	mvaFilt = MovingAverage(_windowSize = 1000)
	while True :
		if receiveControl == 1 :
			waiting = ser.inWaiting()
			if waiting >= recvLength :
				rawQueue = [x for x in ser.read(recvLength)]
				reading = rawQueue[recvLength-3]*256+rawQueue[recvLength-2]
				dataQueue.append(mvaFilt.getSample(reading))

class Main(QMainWindow,Ui_MainWindow) :
	def __init__(self):
		super(Main,self).__init__()
		self.setupUi(self)
		#button start
		self.btnStart.clicked.connect(self.doStart)
		#button stop
		self.btnStop.clicked.connect(self.doStop)

		#variables
		self.maxTime = 20
		self.sampfreq = 100
		self.dt = 1.0 / self.sampfreq
		self.freq = 0.5
		self.maxSamples = (1.0/self.dt)*self.maxTime


		self.curveFSR = self.graphicsViewForce.plot(pen=pg.mkPen('b',width=1))
		# self.graphicsViewForce.setXRange(min=0,max=self.maxTime,padding=0.01)
		self.curveVelocity = self.graphicsViewVelocity.plot(pen=pg.mkPen('b',width=1))
		# self.graphicsViewVelocity.setXRange(min=0,max=self.maxTime,padding=0.01)

		self.start = 0
		self.firstStart = 0
		#self.thr = threading.Thread(target = self.update)
		self.updateControl = 0

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		#self.timer.setInterval(100)

		self.fsr = []
		self.velcoity = []
		self.tv = []
		self.sampleCount = 0
		self.timestep = 0

	def doStart(self) :
		global receiveControl,recvThread,file_object,startTime,dataQueue
		if self.start == 0 :
			if self.firstStart == 0 :
				#self.thr.start()
				recvThread.start()
				self.firstStart = 1
				startTime = time.clock()
				file_object = open("IR_sensor_data.txt",'w')
			else :
				file_object = open("IR_sensor_data.txt",'a')
			dataQueue = deque([])
			self.timer.start(0)
			receiveControl = 1
			self.updateControl = 1
			self.start = 1
	def doStop(self) :
		global receiveControl,file_object
		if self.start == 1 :
			self.timer.stop()
			receiveControl = 0
			self.updateControl = 0
			self.start = 0
			file_object.close()

	def update(self) :
		#while True :
		global dataQueue,file_object,startTime
		if self.updateControl == 1 and len(dataQueue) > 0:
			#print(dataQueue)
			for i in range(len(dataQueue)-1) :
				sampleData = dataQueue.popleft()
			sampleData = dataQueue.popleft()
			if sampleData != 0 : 
				file_object.write(str(time.clock()-startTime)+" "+str(sampleData)+"\n")
				self.fsr.append(sampleData)
				self.tv.append(self.timestep)
				self.timestep+=self.dt
				self.sampleCount+=1

				if self.sampleCount >= self.maxSamples:
					self.fsr = []
					self.tv = []
					self.velocity = []
					self.timestep = 0
					self.sampleCount = 0
				self.curveFSR.setData(self.tv,self.fsr)
			#time.sleep(0.005)

recvThread = threading.Thread(target = receive)

if __name__ == '__main__':
	import sys
	from PyQt5 import QtGui
	app = QtGui.QApplication(sys.argv)
	main = Main()
	main.show()
	sys.exit(app.exec_())