import numpy as np
import sys
sys.path.append('libraries/UR10')
from ur10_simulation import ur10_simulator
from copy import copy
from UR10 import UR10Controller


def find_normal_orientation():
	U1 = UR10Controller('10.1.1.6')
	Sim = ur10_simulator()
	Sim2 = ur10_simulator()

	U1.read_joints()
	print("UR10 joint values", U1.joints)

	Sim2.set_joints(copy(U1.joints))
	xyzR = copy(Sim2.joints2pose())
	print("UR10 xyzR", xyzR)

	Sim.set_joints(copy(U1.joints))
	Sim.joints2pose()
	_, R1 = Sim.get_Translation_and_Rotation_Matrix()

	U1.joints[4]=copy(U1.joints[4]-90)
	Sim.set_joints(copy(U1.joints))
	Sim.joints2pose()
	_, R2= Sim.get_Translation_and_Rotation_Matrix()

	R1=np.array(R1)
	R2=np.array(R2)
	rotatedx= R1[:,2]
	rotatedy= R2[:,2]
	rotatedz= np.cross(rotatedx,rotatedy)

	print("Normal orientation (rotated z)", rotatedz)

if __name__ == '__main__':
	find_normal_orientation()