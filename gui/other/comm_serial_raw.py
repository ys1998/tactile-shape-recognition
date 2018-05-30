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
		if waiting >= 18 :
			rawQueue = [x for x in ser.read(waiting)]
			print(rawQueue)
			#time.sleep(1)
	#end = time.time()
	#sprint(end-st)
print("Started : ")
#send(["1"])
receive()
#print(dataQueue)
#print(end-st)
#threading.Thread(target = receive).start()
#threading.Thread(target = updateIntensities).start()

