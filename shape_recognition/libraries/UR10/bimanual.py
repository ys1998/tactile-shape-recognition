import os, sys
sys.path.append('../iLimb')
from UR10 import *
from iLimb import *
from copy import copy
import time

#UR10
UR10Right = UR10Controller('10.1.1.6')
UR10RightPose = URPoseManager()
UR10RightPose.load('bimanual.urpose')
#iLimb
iLimbRight = iLimbController('COM17')
iLimbRight.connect() #connect to iLimb

f=['thumb','index','middle','ring','little']
a=['open']*len(f)
p=[290]*len(f)
iLimbRight.control(f,a,p)
time.sleep(2)

#iLimbRight.setPose('openHand') #open the fingers

#first, go to home position
UR10RightPose.moveUR(UR10Right,'homej',5)
time.sleep(5)

#go down to prepare grasping
UR10RightPose.moveUR(UR10Right,'grasp1p',5)
time.sleep(5)
#rotate the thumb
iLimbRight.control('thumbRotator','close',290)

#read the joints 
UR10Right.read_joints_and_xyzR()
auxpos = copy(UR10Right.xyzR)
auxjoints = copy(UR10Right.joints)

#rotate the wrist a little bit
auxjoints[4] -= 10
UR10Right.movejoint(np.deg2rad(auxjoints),5)
time.sleep(5)

#read the joints 
UR10Right.read_joints_and_xyzR()
auxpos = copy(UR10Right.xyzR)
auxjoints = copy(UR10Right.joints)

#move towards the object
auxpos[1] = -268
UR10Right.movej(auxpos,5)
time.sleep(5)

#grasp
f = ['index','middle','ring','little']
a = ['position'] * len(f)
p = [420] * len(f)
iLimbRight.control(f,a,p)
time.sleep(1)
iLimbRight.control('thumb','position',320)
time.sleep(1)

#lift
#UR10Right.read_joints_and_xyzR()
#auxpos = copy(UR10Right.xyzR)
#auxjoints = copy(UR10Right.joints)