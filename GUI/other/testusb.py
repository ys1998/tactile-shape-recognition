import usb
import sys
import threading
from collections import deque
import time

dataQueue = deque([])
queueLen = 0

dev = usb.core.find(bDeviceClass = 2)
if dev is None:
	raise ValueError('Device not found')

if dev.is_kernel_driver_active(0):
	dev.detach_kernel_driver(0)

usb.util.claim_interface(dev,1)
print("Claimed Interface")

endpoint_out = dev[0][(1,0)][0]
endpoint_in = dev[0][(1,0)][1]
print(endpoint_out.bEndpointAddress,endpoint_in.bEndpointAddress)

def send(data) :
	global dev
	length = len(data)
	for i in range(length) :
		dev.write(endpoint_out.bEndpointAddress,(data[i]+"\r\n").encode('ascii'))
		print("Written Data :",data[i])

st,end = [0,0]

def receive() :
	global dataQueue,queueLen,st,end,dev
	while queueLen < 2000:
		if queueLen == 0 :
			st = time.time()
		currQueue = [x for x in dev.read(endpoint_in.bEndpointAddress,2000)]
		queueLen = queueLen+len(currQueue)
		#print("Read Data: ",currQueue)
		for x in currQueue :
			dataQueue.append(x)
	end = time.time()

send(["1"])

receive()
print(queueLen,dataQueue)
print(end-st)