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
from ur10_simulation import ur10_simulator

MAPPING = {'index':3, 'thumb':4}
THRESHOLD = {'index':0.08, 'thumb':0.08}

""" Abstract class for storing state variables """
class STATE:
	ROTATION_POS = 0 # 0,1,2,3
	ROTATION_DIR = -1 # -1/1
	
	CONTROL_POS = [0 for _ in range(5)]
	NUM_POINTS = 0
	CONTACT_POINTS = []

# iLimb dimensions (mm)
IDX_TO_BASE = 185
THB_TO_BASE = 105
IDX_0 = 50
IDX_1 = 35
IDX = 84
THB = 80

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
			# update control_pos for fingers that have touched a surface
			for i in range(len(fingerArray)):
				if touched[i]:
					STATE.CONTROL_POS[fingerArray[i][1]] = iLimb.controlPos

			# Self-touching condition
			if iLimb.controlPos > 500:
				return False

			if all(touched):
				return True
			else:
				# update fingerArray
				fingerArray = [fingerArray[i] for i in range(len(touched)) if not touched[i]]


""" Function to calculate coordinates of points of contact """
def compute_coordinates():
	global ur10, iLimb
	ur10.read_joints_and_xyzR()
	xyzR = copy(ur10.xyzR)
	joints = copy(ur10.joints)
	sim = ur10_simulator()
	sim.set_joints(joints)
	initial_pos = sim.joints2pose()
	tm, rm = sim.get_Translation_and_Rotation_Matrix()
	# Calculate the direction in which the end effector is pointing
	# value corresponding to z-direction is ignored
	direction = rm[:2,2] # x and y direction vector only
	direction /= np.linalg.norm(direction)
	
	# Find point of contact for index finger
	control = STATE.CONTROL_POS[MAPPING['index']]
	axis = 0; perp = 0
	if control < 210:
		# Normal circular motion
		theta = 60/210 * control
		axis = IDX_0 * np.cos(np.deg2rad(theta)) + IDX_1 * np.cos(np.deg2rad(theta + 20))
		perp = IDX_0 * np.sin(np.deg2rad(theta)) + IDX_1 * np.sin(np.deg2rad(theta + 20))
	else:
		theta = 145/500 * control
		rel_theta = 160 - 70/290 * (control - 210)
		axis = IDX_0 * np.cos(np.deg2rad(theta)) - IDX_1 * np.sin(np.deg2rad(90+theta-rel_theta))
		perp = IDX_0 * np.sin(np.deg2rad(theta)) + IDX_1 * np.cos(np.deg2rad(90+theta-rel_theta))
	axis += IDX_TO_BASE
	pt_1 = [axis * direction[0] + perp * direction[1] + xyzR[0],
			-axis * direction[1] + perp * direction[0] + xyzR[1],
			xyzR[2]]

	# Find point of contact for thumb
	control = STATE.CONTROL_POS[MAPPING['thumb']]
	theta = 90 * (1 - control/500)
	axis = THB * np.cos(np.deg2rad(theta)) + THB_TO_BASE
	perp = THB * np.sin(np.deg2rad(theta))
	pt_2 = [axis * direction[0] + perp * direction[1] + xyzR[0],
			-axis * direction[1] + perp * direction[0] + xyzR[1],
			xyzR[2]]

	STATE.NUM_POINTS += 2
	STATE.CONTACT_POINTS += [pt_1, pt_2]

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
			touched = close_hand()
			time.sleep(0.1)
			if touched:
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