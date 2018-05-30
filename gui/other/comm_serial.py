import time
import sys
import serial
import threading
import numpy as np
from collections import deque

ser = serial.Serial("/dev/ttyACM0",117964800)
#ser.flushInput()
ser.flushOutput()

dataQueue = np.zeros((64))

def send(data) :
	global ser
	length = len(data)
	for i in range(length) :
		#print("writing")
		ser.write((data[i]+"\r\n").encode('ascii'))
		#print("wrote data :",data[i])

#st,end = [0,0]
def receive() :
	global dataQueue,ser
	#global st,end
	while True :
		waiting = ser.inWaiting()
		if waiting >= 130 :
			rawQueue = [x for x in ser.read(waiting)]
			endByte = len(rawQueue)-1
			#print(endByte,waiting)
			while rawQueue[endByte] != 2 and endByte > 0 :
				endByte = endByte-1
			if endByte < 129 :
				continue
			if rawQueue[endByte-129] == 1 :
				currQueue = rawQueue[endByte-129:endByte+1]
				newQueue = np.zeros(64)
				for i in range(64) :
					dataQueue[i] = 4096 - (currQueue[2*i+1] + currQueue[2*i+2]*256)
				for i in range(64) :
					patchNum = i//16
					row = (i%16)//4
					col = (i%16)%4
					pos = patchNum + 4*row + 16*col
					newQueue[i] = dataQueue[pos]
				#print(" START ")
				#print(newQueue[0:16])
				#print(newQueue[16:32])
				#print(newQueue[32:48])
				#print(newQueue[48:64])
				#print(" END ")
				print(rawQueue)
				time.sleep(1)
	#end = time.time()
	#sprint(end-st)
print("Started : ")
#send(["1"])
receive()
#print(dataQueue)
#print(end-st)
#threading.Thread(target = receive).start()
#threading.Thread(target = updateIntensities).start()

