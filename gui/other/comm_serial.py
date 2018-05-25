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
		if ser.inWaiting() >= 34 :
			currQueue = [x for x in ser.read(34)]
			print(currQueue)
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

