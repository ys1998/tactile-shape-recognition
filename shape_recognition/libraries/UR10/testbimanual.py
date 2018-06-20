import os, sys
sys.path.append('../iLimb')
from UR10 import *
from iLimb import *
from copy import copy
import time

#UR10
UR10Right = UR10Controller('10.1.1.6')
UR10RightPose = URPoseManager()
UR10RightPose.load('bimanual2.urpose')
#Left
UR10Left = UR10Controller('10.1.1.4')
UR10LeftPose = URPoseManager()
UR10LeftPose.load('bimanual2.urpose')
#iLimb
iLimbRight = iLimbController('COM17')
iLimbRight.connect() #connect to iLimb
iLimbLeft = iLimbController('COM16')
iLimbLeft.connect() #connect to iLimb


#moving to open
UR10Left.read_joints_and_xyzR()
dist = 190 #pivot distance
joints = copy(UR10Left.joints)
joints[4] += 5
newXYZR = UR10Left.move_joint_with_constraints(joints,dist)
UR10Left.movej(newXYZR,3)
time.sleep(3)
