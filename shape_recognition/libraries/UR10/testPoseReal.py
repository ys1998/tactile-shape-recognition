from UR10 import *
u = UR10Controller('10.1.1.6')
x = URPoseManager()
x.load('t1.urpose')
print(x.getPosJoint('home'))
resp = input('hit y if you want to continue')
if resp == 'y':
	x.moveUR(u,'home',30)