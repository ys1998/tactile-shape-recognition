"""
Controls UR10 and iLimb based on feedback from tactile sensors.
Once sufficient number of data points have been collected, shape
recognition module is invoked.
"""
# Configure paths
import sys
sys.path.append('libraries/iLimb')
sys.path.append('libraries/UR10')
sys.path.append('libraries/neuromorphic')
sys.path.append('libraries/general')
sys.path.append('libraries/controlsyst')
sys.path.append('../scripts')

import os, subprocess, time
import numpy as np
# import tensorflow as tf
from iLimb import *
from tactileboard import *
from UR10 import *
from threadhandler import ThreadHandler
from scripts.pcd_io import save_point_cloud

MAPPING = {'index':3, 'thumb':4}
THRESHOLD = {'index':0.08, 'thumb':0.08}

""" Abstract class for storing state variables """
class STATE:
	RADIUS = 70 # radius of object zone in mm
	NUM_POINTS = 0
	ROTATION_POS = 0 # 0,1,2,3
	ROTATION_DIR = -1 # -1/1
	CONTACT_POINTS = []

""" Function to initialize handler objects """
def init_handlers():
	# Create handlers
	global ur10, iLimb, sensors
	print('Initializing handlers ...')
	ur10 = UR10Controller('10.1.1.6')
	print('UR10 done.')
	iLimb = iLimbController('COM17')
	iLimb.connect()
	print('iLimb done.')
	sensors = TactileBoard('COM59', _sensitivity=TBCONSTS.HIGH_SENS)
	sensors.start()
	# Sleep
	time.sleep(3)
	print('TactileBoard done')

""" Function to set all handlers to default configuration """
def configure_handlers():
	global ur10, iLimb, sensors
	print('Setting UR10 to default position ...')
	UR10pose = URPoseManager()
	UR10pose.load('shape_recog_home.urpose')
	UR10pose.moveUR(ur10,'home_j',5)

	print('Setting iLimb to default pose ...')
	iLimb.setPose('openHand')
	time.sleep(3)
	iLimb.control(['thumbRotator'],['position'],[550])
	time.sleep(1)
	
	print('Calibrating tactile sensors ...')
	sensors.loadCalibration()
	time.sleep(0.5)
	sensors.useCalib = True

	time.sleep(3)
	print('Done.')

""" Function to close fingers until all fingers touch surface """
def close_hand(fingers=['index', 'thumb']):
	global iLimb, sensors
	touched = [False] * len(fingers)
	fingerArray = [[x, MAPPING[x], THRESHOLD[x]] for x in fingers]
	while not all(touched):
		time.sleep(0.005)
		q = sensors.getData()
		for _ in range(len(q)):
			tactileSample = q.popleft()
			touched = iLimb.doFeedbackPinchTouch(tactileSample, fingerArray, 1)
			if all(touched):
				break
			else:
				# update fingerArray
				fingerArray = [fingerArray[i] for i in range(len(touched)) if not touched[i]]


""" Function to calculate coordinates of points of contact """
def compute_coordinates():
	pass

""" Function to rotate hand for next reading """
def rotate_hand():
	global ur10
	ur10.read_joints()
	joints = copy(ur10.joints)

	if STATE.ROTATION_POS == 3:
		STATE.ROTATION_POS = 0
		STATE.ROTATION_DIR *= -1
	else:
		joints[4] += 45 * STATE.ROTATION_DIR
		STATE.ROTATION_POS += 1
		xyzR = ur10.move_joints_with_grasp_constraints(joints, dist_pivot=220, grasp_pivot=60, constant_axis='z')
		ur10.movej(xyzR, 10)
		time.sleep(10)

""" Function to move hand in vertical direction """
def move_vertical():
	global ur10
	# move one step up while palpating
	ur10.read_joints_and_xyzR()
	x, y, z, rx, ry, rz = copy(ur10.xyzR)
	new_joint_pos = np.array([x, y, z+10, rx, ry, rz])
	ur10.movej(new_joint_pos, 1)
	time.sleep(1)

""" Function to move hand away from the object """
def move_away(fingers=['thumb', 'index']):
	global iLimb
	iLimb.control(fingers, ['position']*len(fingers), [0]*len(fingers))
	time.sleep(1)

""" Function to move UR10 to base """
def move_to_base():
	global ur10
	ur10.read_joints_and_xyzR()
	x, y, z, rx, ry, rz = copy(ur10.xyzR)
	new_joint_pos = np.array([x, y, -100, rx, ry, rz])
	ur10.movej(new_joint_pos, 1)
	time.sleep(1)

# def move_to_rest() :
# 	global iLimb
# 	iLimb.setPose('rest')
# 	time.sleep(1)

def main():
	global ur10, iLimb, sensors
	init_handlers()
	configure_handlers()
	move_to_base()
	cntr = 0
	while cntr < 20:
		for _ in range(4):
			close_hand()
			time.sleep(0.1)
			compute_coordinates()
			iLimb.resetControl()
			time.sleep(0.5)
			move_away()
			rotate_hand()
		move_vertical()
		cntr += 1

	# Convert collected points to a PCD file
	pts = np.asarray(STATE.CONTACT_POINTS)
	save_point_cloud(pts, 'run.pcd')
	subprocess.check_call(['python', 'detect.py', '../save', 'run.pcd'])

if __name__ == '__main__':
	main()