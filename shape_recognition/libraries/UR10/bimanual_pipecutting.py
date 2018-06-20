from UR10 import *
from copy import copy
import time

UR10Left = UR10Controller('10.1.1.4')
UR10Right = UR10Controller('10.1.1.6')

#read the current position
UR10Right.read_joints_and_xyzR()
UR10Left.read_joints_and_xyzR()

originRight = copy(UR10Right.xyzR)
originLeft = copy(UR10Left.xyzR)

delayt = 1
dist = 100
height = 0.3
repet = 25

auxLeft = copy(originLeft)
auxRight = copy(originRight)

print(originRight)
for k in range(repet):

	print('repetition: ', k)

	#left arm
	auxLeft[0] -= dist
	auxLeft[2] -= height

	auxRight[0] += dist
	auxRight[2] -= height

	UR10Right.movej(auxLeft,delayt)
	UR10Right.movej(auxRight,delayt)

	time.sleep(delayt+0.1)

	auxRight[0] -= dist
	auxRight[2] -= height

	UR10Right.movej(auxRight,delayt)
	time.sleep(delayt+0.1)

