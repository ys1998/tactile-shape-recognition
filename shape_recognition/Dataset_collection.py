import socket
import numpy as np
import sys
sys.path.append('libraries/UR10')
from ur10_simulation import ur10_simulator
import time
import struct
import binascii
from copy import copy
import os.path
from UR10 import UR10Controller


def movehand(ximcam,yimcam):
	print("iwebfiuweoeh")
	port = 30003
	ip1 = '10.1.1.6'
	U1 = UR10Controller(ip1)
	Sim = ur10_simulator()
	Sim2 = ur10_simulator()
	fx=130
	fy=130
	zw=-300

	# ximcam= 87
	# yimcam=78
	xim=yimcam-64
	yim=64-ximcam
	# xim=0
	# yim=0

	U1.read_joints()
	print(U1.joints)
	# U1.read_joints_and_xyzR()
	Sim2.set_joints(copy(U1.joints))
	xyzR = copy(Sim2.joints2pose())
	# xyzR[3:6] = copy(-xyzR[3:6])
	print(xyzR)
	# xyzR= copy(U1.xyzR)
	# print('ok1',xyzR)
	# print(U1.joints)
	Sim.set_joints(copy(U1.joints))
	Sim.joints2pose()
	T1,R1 = Sim.get_Translation_and_Rotation_Matrix()
	# print(R1)
	# a = input("")
	U1.joints[4]=copy(U1.joints[4]-90)
	Sim.set_joints(copy(U1.joints))
	Sim.joints2pose()
	T2,R2= Sim.get_Translation_and_Rotation_Matrix()
	# print(T1)
	# print(T2)

	R1=np.array(R1)
	R2=np.array(R2)
	rotatedx= R1[:,2]
	rotatedy= R2[:,2]
	rotatedz= np.cross(rotatedx,rotatedy)

	# print("Rotated x", rotatedx)
	# print("Rotated y",rotatedy)
	print("Rotated z", rotatedz)

	a = input("stopped")

	# print(np.sum(rotatedy*rotatedy))

	print(T1)
	rotationmatrix=np.empty((3,3))
	rotationmatrix[0,:] = rotatedz
	rotationmatrix[1,:] = rotatedy
	rotationmatrix[2,:] = rotatedx


	T1=T1+rotatedy*60
	T1=T1-rotatedz*40
	T1=T1+rotatedx*70

	print("new T1",T1)

	# print(rotatedx*rotatedy)
	print(rotationmatrix)
	transformationmatrix=np.empty((4,4))
	transformationmatrix[0:3,0:3]=rotationmatrix
	transformationmatrix[0:3,3]=-np.matmul(rotationmatrix,np.transpose(T1))
	transformationmatrix[3,:]=np.array([0,0,0,1])
	# print(transformationmatrix)
	M=np.zeros((3,4))
	M[0][0]=fx
	M[1][1]=fy
	M[2][2]=1
	# print(transformationmatrix)

	P=np.matmul(M,transformationmatrix)
	print(P)
	row1= -yim*P[2,:]+P[1,:]
	row2= -xim*P[2,:]+P[0,:]
	c1= -row1[2]*zw-row1[3]
	c2= -row2[2]*zw-row2[3]

	yw= (row1[0]*c2-row2[0]*c1)/(row1[0]*row2[1] - row2[0]*row1[1])
	xw= (row2[1]*c1-row1[1]*c2)/(row1[0]*row2[1] - row2[0]*row1[1])

	# print(rotatedx,rotatedy,rotatedz)

	# print(xw,yw)

	endeffector= np.array([xw,yw,zw+150])

	[xw,yw,zw]= endeffector-rotatedx*170

	xyzR[0]=xw
	xyzR[1]=yw
	xyzR[2]=zw
	print(xw,yw)


	print('ok',xyzR)

	# a = input('press y to continue')
	# if a == 'y':
	# 	U1.movej(xyzR,30)



	# xyzR[2]=zw+30
	# print("Translation1",T1)
	# print("Rotation1",R1)

	# print("Translation2",T2)
	# print("Rotation2",R2)

movehand(74,21)