
# -*- coding: utf-8 -*-
'''
#-------------------------------------------------------------------------------
# NATIONAL UNIVERSITY OF SINGAPORE - NUS
# SINGAPORE INSTITUTE FOR NEUROTECHNOLOGY - SINAPSE
# Singapore
# URL: http://www.sinapseinstitute.org
#-------------------------------------------------------------------------------
# Neuromorphic Engineering Group
# Author: Andrei Nakagawa-Silva, MSc
# Contact: nakagawa.andrei@gmail.com
#-------------------------------------------------------------------------------
# Description: This file contains a class for handling serial communication
# with embedded systems such as Arduino boards or ARM dev kits
#-------------------------------------------------------------------------------
'''
#-------------------------------------------------------------------------------
import serial
from serial import Serial
from threading import Timer
from ctypes import c_short
from struct import unpack
from collections import deque
from threading import Lock
import time
import sys
#-------------------------------------------------------------------------------
#method for listing all the serial ports available
def list_serial_ports():
    """ Lists serial port names

    :raises EnvironmentError:
    On unsupported or unknown platforms
    :returns:
    A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class SerialHandler():
	def __init__(self,_port='/dev/ttyACM0',_baud=115200,_timeout=0.5,_header=0x24,_end=0x21,_numDataBytes=2,_thLock=None):
		self.port =  str(_port)
		self.baud = _baud
		self.timeout = _timeout
		self.waiting = False
		self.serialPort = None
		self.dataQueue = deque()
		self.thLock = _thLock
		self.pkgHeader = _header
		self.pkgEnd = _end
		self.dataBytes = _numDataBytes

	def open(self):
		try:
			self.serialPort = Serial(self.port,self.baud,timeout=self.timeout)
			#waits for the serial port to open
			time.sleep(0.1)
			#self.serialPort = Serial('/dev/ttyUSB0',self.baud,timeout=self.timeout)
			if self.serialPort.is_open:
				self.serialPort.flushInput()
				self.serialPort.flushOutput()
				return True
			else:
				return False
		except:
			return False

	def close(self):
		try:
			self.serialPort.flushInput()
			self.serialPort.flushOutput()
			self.serialPort.close()
			if self.serialPort.is_open:
				return False
			else:
				return True
		except:
			return False

	def waitBytes(self,_numBytes):
		try:
			self.waiting = True
			t = Timer(self.timeout,self.getTimeout)
			t.start()
			numWaiting = 0
			while True:
				if(self.serialPort.is_open):
					numWaiting = self.serialPort.in_waiting
					if numWaiting < _numBytes and self.waiting is True:
						pass
					else:
						break
				else:
					break
			if numWaiting >= _numBytes:
				t.cancel()
				return True
			else:
				return False
		except:
			return False

	def getTimeout(self):
		self.waiting = False

	def waitSTByte(self,_startByte):
		receivedByte = 0
		while True:
			ret = self.waitBytes(1)
			if ret:
				receivedByte = ord(self.serialPort.read())
				if receivedByte == _startByte:
					return True
				else:
					return False
			else:
				return False

	def readPackage(self):
		header = self.waitSTByte(self.pkgHeader)
		if header:
			ret = self.waitBytes(self.dataBytes)
			if ret:
				#data = map(ord,self.serialPort.read(self.dataBytes))
				data = self.serialPort.read(self.dataBytes)
                #print(data[) #debugging
				ret = self.waitBytes(1)
				if ret:
					end = ord(self.serialPort.read())
					if end == self.pkgEnd:
						self.thLock.acquire()
						self.dataQueue.append(data)
						self.thLock.release()

	def to_int16(self,_MSB,_LSB):
		return c_short((_MSB<<8) + _LSB).value

	def to_float(self,_byteVector):
		binF = ''.join(chr(i) for i in _byteVector)
		return unpack('f',binF)[0]
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    from threading import Lock
    from threadhandler import ThreadHandler

    l = Lock()
    s = SerialHandler(_header=0x24,_end=0x21,_numDataBytes=2,_thLock=l)

    def run():
    	global s, l
    	l.acquire()
    	n = len(s.dataQueue)
    	for k in range(n):
    		data = s.dataQueue.popleft()
    		print(n, k, data[0]<<8|data[1])
    	l.release()

    s.open()
    t = ThreadHandler(s.readPackage)
    t.start()
    p = ThreadHandler(run)
    p.start()
    raw_input()
    t.kill()
    p.kill()
    s.close()
#-------------------------------------------------------------------------------
