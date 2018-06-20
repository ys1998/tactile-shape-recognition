import socket
import time
import struct

HOST = "10.1.1.4" # The remote host
PORT_30003 = 30003

print "Starting Program"

count = 0
home_status = 0
program_run = 0
	
while (True):
 if program_run == 0:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(10)
		s.connect((HOST, PORT_30003))
		time.sleep(1.00)
		print ""
		packet_1 = s.recv(4)
		packet_2 = s.recv(8)
		packet_3 = s.recv(48)
		packet_4 = s.recv(48)
		packet_5 = s.recv(48)
		packet_6 = s.recv(48)
		packet_7 = s.recv(48)
		packet_8 = s.recv(48)
		packet_9 = s.recv(48)
		packet_10 = s.recv(48)
		packet_11 = s.recv(48)

		print packet_8[0:8]
		x = packet_8[0:8].encode("hex")
		base = str(x)
		base = struct.unpack('!d', base.decode('hex'))[0]
		print "base = ", base * (180.0/3.1419)

		x = packet_8[8:16].encode("hex")
		shoulder = str(x)
		shoulder = struct.unpack('!d', shoulder.decode('hex'))[0]
		print "shoulder = ", shoulder * (180.0/3.1419)

		x = packet_8[16:24].encode("hex")
		elbow = str(x)
		elbow = struct.unpack('!d', elbow.decode('hex'))[0]
		print "elbow = ", elbow * (180.0/3.1419)

		x = packet_8[24:32].encode("hex")
		wrist1 = str(x)
		wrist1 = struct.unpack('!d', wrist1.decode('hex'))[0]
		print "wrist1 = ", wrist1 * (180.0/3.1419)

		x = packet_8[32:40].encode("hex")
		wrist2 = str(x)
		wrist2 = struct.unpack('!d', wrist2.decode('hex'))[0]
		print "wrist2 = ", wrist2 * (180.0/3.1419)

		x = packet_8[40:48].encode("hex")
		wrist3 = str(x)
		wrist3 = struct.unpack('!d', wrist3.decode('hex'))[0]
		print "wrist3 = ", wrist3 * (180.0/3.1419)

		packet_12 = s.recv(8)
		packet_12 = packet_12.encode("hex") #convert the data from \x hex notation to plain hex
		x = str(packet_12)
		x = struct.unpack('!d', x.decode('hex'))[0]
		print "X = ", x * 1000

		packet_13 = s.recv(8)
		packet_13 = packet_13.encode("hex") #convert the data from \x hex notation to plain hex
		y = str(packet_13)
		y = struct.unpack('!d', y.decode('hex'))[0]
		print "Y = ", y * 1000

		packet_14 = s.recv(8)
		packet_14 = packet_14.encode("hex") #convert the data from \x hex notation to plain hex
		z = str(packet_14)
		z = struct.unpack('!d', z.decode('hex'))[0]
		print "Z = ", z * 1000

		packet_15 = s.recv(8)
		packet_15 = packet_15.encode("hex") #convert the data from \x hex notation to plain hex
		Rx = str(packet_15)
		Rx = struct.unpack('!d', packet_15.decode('hex'))[0]
		print "Rx = ", Rx

		packet_16 = s.recv(8)
		packet_16 = packet_16.encode("hex") #convert the data from \x hex notation to plain hex
		Ry = str(packet_16)
		Ry = struct.unpack('!d', packet_16.decode('hex'))[0]
		print "Ry = ", Ry

		packet_17 = s.recv(8)
		packet_17 = packet_17.encode("hex") #convert the data from \x hex notation to plain hex
		Rz = str(packet_17)
		Rz = struct.unpack('!d', packet_17.decode('hex'))[0]
		print "Rz = ", Rz

		packet_18 = s.recv(48)
		packet_19 = s.recv(48)
		packet_20 = s.recv(48)

		x = packet_20[0:8]
		x = x.encode("hex") #convert the data from \x hex notation to plain hex
		xx = str(x)
		xx = struct.unpack('!d', xx.decode('hex'))[0]
		print "XX = ", xx * 1000
		x = packet_20[8:16]
		x = x.encode("hex") #convert the data from \x hex notation to plain hex
		xx = str(x)
		yy = struct.unpack('!d', xx.decode('hex'))[0]
		print "YY = ", yy * 1000
		x = packet_20[16:24]
		x = x.encode("hex") #convert the data from \x hex notation to plain hex
		xx = str(x)
		zz = struct.unpack('!d', xx.decode('hex'))[0]
		print "ZZ = ", zz * 1000
		x = packet_20[24:32]
		x = x.encode("hex") #convert the data from \x hex notation to plain hex
		xx = str(x)
		zz = struct.unpack('!d', xx.decode('hex'))[0]
		print "ZZ = ", zz 
		
		home_status = 1
		program_run = 0

		valdeg = (0.0*3.1419) / 180.0
		strjoints = 'movej([' + str(base) + ',' + str(shoulder) + ',' + str(elbow) + ',' + str(wrist1) + ',' + str(wrist2+valdeg) + ',' + str(wrist3) + '], t=5.0) \n'
		s.send(strjoints)
		print strjoints
		s.close()
		break
	except socket.error as socketerror:
		print("Error: ", socketerror)
	print "Program finish"