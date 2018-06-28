import time
import sys
import serial
import threading
import numpy as np
from collections import deque

rawQueue = deque([])

def receive() :
	ser = serial.Serial("/dev/ttyACM0", 117964800)
	ser.flushInput()
	ser.flushOutput()
	global rawQueue
	while True :
		waiting = ser.inWaiting()
		if waiting >= 18 :
			rawQueue.extend(ser.read(waiting))
			print(rawQueue)

def update():
	global rawQueue
	while True:
		while len(rawQueue) > 0 and rawQueue[0] != 1:
			rawQueue.popleft()
		if len(rawQueue) > 18:
			for _ in range(18):
				print(rawQueue.popleft(), end=' ')
			print("")	

def main():
	recvThread = threading.Thread(target = receive)
	updtThread = threading.Thread(target = update)
	recvThread.start()
	# updtThread.start()

if __name__ == '__main__':
	main()
