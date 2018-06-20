from UR10 import *
from copy import copy
import time

UR10Cont = UR10Controller('10.1.1.6')

#read the current position
UR10Cont.read_joints_and_xyzR()

origin = copy(UR10Cont.xyzR)

delayt = 0.8
dist = 100
height = 0.1
repet = 25
aux = copy(origin)

print(origin)
for k in range(repet):

	print('repetition: ', k)

	
	aux[0] += dist
	#UR10Cont.movej
	aux[2] -= height

	UR10Cont.movej(aux,delayt)

	time.sleep(delayt+0.1)

	aux[0] -= dist
	aux[2] -= height

	UR10Cont.movej(aux,delayt)
	time.sleep(delayt+0.1)

