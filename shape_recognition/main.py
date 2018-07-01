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
from pcd_io import save_point_cloud
from ur10_simulation import ur10_simulator

MAPPING = {'index':2, 'thumb':4, 'ring':3}
THRESHOLD = {'index':0.01, 'thumb':0.01, 'ring':0.01}

""" Abstract class for storing state variables """
class STATE:
	ROTATION_ANGLE = 30
	ROTATION_POS = 0 # 0,1,2,3
	ROTATION_DIR = -1 # -1/1
	
	NUM_POINTS = 0
	CONTACT_POINTS = []
	CONTROL_POS = [0 for _ in range(5)]
	FINGER_POS = {'index':[], 'thumb':[], 'ring':[]}
	XYZR = []
	UNIT_VECTOR = []

# iLimb dimensions (mm)
IDX_TO_BASE = 185 + 40
THB_TO_BASE = 105 + 30
IDX_0 = 50
IDX_1 = 30
THB = 65

""" Function to initialize handler objects """
def init_handlers():
	# Create handlers
	global ur10, iLimb, sensors
	print('Initializing handlers ...')
	ur10 = UR10Controller('10.1.1.6')
	print('UR10 done.')
	iLimb = iLimbController('/dev/ttyACM0')
	iLimb.connect()
	print('iLimb done.')
	sensors = TactileBoard('/dev/ttyACM1', _sensitivity=TBCONSTS.DEFAULT_SENS)
	# sensors.start()
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
	iLimb.setPose('rest')
	time.sleep(3)
	
	print('Calibrating tactile sensors ...')
	sensors.start()
	sensors.startCalibration(500)
	time.sleep(2)
	sensors.stopCalibration()
	sensors.useCalib = True
	sensors.loadCalibration()
	time.sleep(1)
	print('Done.')

""" Function to close fingers until all fingers touch surface """
def close_hand(fingers=['index', 'thumb']):
	global iLimb, sensors
	touched = [False] * len(fingers)
	touched_once = False
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
					touched_once = True
					STATE.CONTROL_POS[fingerArray[i][1]] = iLimb.controlPos
					#----------------------------------------------------------
					# Collect information
					STATE.FINGER_POS[fingerArray[i][0]].append(iLimb.controlPos)
					#----------------------------------------------------------

			# Self-touching condition
			# Can be modified later
			if iLimb.controlPos > 500 and not touched_once:
				return False
			elif iLimb.controlPos > 500 and touched_once:
				for i in range(len(fingerArray)):
					if not touched[i]:
						#----------------------------------------------------------
						# Collect information
						STATE.FINGER_POS[fingerArray[i][0]].append(-1)
						#----------------------------------------------------------
				return True

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
	_ = sim.joints2pose()
	_, rm = sim.get_Translation_and_Rotation_Matrix()
	# Calculate the direction in which the end effector is pointing
	# aVlue corresponding to z-direction is ignored
	direction = rm[:2,2] # x and y direction vector only
	direction /= np.linalg.norm(direction)
	
	# Calculate unit vector direction
	dir_ang = np.arctan(abs(direction[1]/direction[0]))
	if direction[0] < 0:
		if direction[1] < 0:
			dir_ang += np.pi
		else:
			dir_ang = np.pi - dir_ang
	else:
		if direction[1] < 0:
			dir_ang = 2*np.pi - dir_ang

	# Find point of contact for index finger
	idx_control = STATE.CONTROL_POS[MAPPING['index']]
	if idx_control > 0:
		theta = 30 + 60/500 * idx_control
		if idx_control < 210:
			# Normal circular motion
			rel_theta = 30
		else:
			rel_theta = 30 + 60/290 * (idx_control - 210)
		# rel_theta = 30 + 60/500 * idx_control
		axis = IDX_0 * np.cos(np.deg2rad(theta)) + IDX_1 * np.cos(np.deg2rad(theta+rel_theta))
		perp = IDX_0 * np.sin(np.deg2rad(theta)) + IDX_1 * np.sin(np.deg2rad(theta+rel_theta))
		axis += IDX_TO_BASE
			
		pt_1 = [axis * np.cos(dir_ang) - perp * np.sin(dir_ang) + xyzR[0],
				axis * np.sin(dir_ang) + perp * np.cos(dir_ang) + xyzR[1],
				xyzR[2]]
		STATE.NUM_POINTS += 1
		STATE.CONTACT_POINTS.append(pt_1)

	# Find point of contact for thumb
	thb_control = STATE.CONTROL_POS[MAPPING['thumb']]
	if thb_control > 0:
		theta = 90 * (1 - thb_control/500)
		axis = THB * np.cos(np.deg2rad(theta)) + THB_TO_BASE
		perp = THB * np.sin(np.deg2rad(theta))

		pt_2 = [axis * np.cos(dir_ang) - perp * np.sin(dir_ang) + xyzR[0],
				axis * np.sin(dir_ang) + perp * np.cos(dir_ang) + xyzR[1],
				xyzR[2]]

		STATE.NUM_POINTS += 1
		STATE.CONTACT_POINTS.append(pt_2)

	#--------------------------------------------------
	# Collect information
	STATE.XYZR.append(xyzR)
	STATE.UNIT_VECTOR.append(direction)
	#--------------------------------------------------

""" Function to rotate hand for next reading """
def rotate_hand():
	global ur10
	ur10.read_joints()
	joints = copy(ur10.joints)

	if STATE.ROTATION_POS == 180//STATE.ROTATION_ANGLE - 1:
		STATE.ROTATION_POS = 0
		STATE.ROTATION_DIR *= -1
	else:
		joints[4] += STATE.ROTATION_ANGLE * STATE.ROTATION_DIR
		STATE.ROTATION_POS += 1
		xyzR = ur10.move_joints_with_grasp_constraints(joints, dist_pivot=220, grasp_pivot=60, constant_axis='z')
		ur10.movej(xyzR, 3)
		time.sleep(3.2)

""" Function to move hand in vertical direction """
def move_vertical():
	global ur10
	# move one step up while palpating
	ur10.read_joints_and_xyzR()
	x, y, z, rx, ry, rz = copy(ur10.xyzR)
	new_joint_pos = np.array([x, y, z+10, rx, ry, rz])
	ur10.movej(new_joint_pos, 0.5)
	time.sleep(0.7)

""" Function to move hand away from the object """
def move_away(fingers=['thumb', 'index']):
	global iLimb
	iLimb.control(fingers, ['position']*len(fingers), [0]*len(fingers))
	time.sleep(1)

""" Function to move UR10 to base """
def move_to_base(t=1):
	global ur10
	ur10.read_joints_and_xyzR()
	x, y, z, rx, ry, rz = copy(ur10.xyzR)
	new_joint_pos = np.array([x, y, -200, rx, ry, rz])
	ur10.movej(new_joint_pos, t)
	time.sleep(t+.2)

def main():
	global ur10, iLimb, sensors
	init_handlers()
	configure_handlers()

	iLimb.setPose('openHand')
	time.sleep(3)
	iLimb.control(['thumbRotator'],['position'],[700])
	time.sleep(3)
	
	move_to_base(t=5)
	height = 0
	estimated_height = 200

	for _ in range(180//STATE.ROTATION_ANGLE):
		while height < estimated_height:
			touched = close_hand(['thumb', 'index', 'ring'])
			time.sleep(0.1)
			if touched:
				compute_coordinates()
			else:
				estimated_height = height
			iLimb.resetControl()
			time.sleep(0.5)
			move_away()
			move_vertical()
			height += 10
		move_to_base()
		height = 0
		estimated_height = 200
		rotate_hand()

	# Convert collected points to a PCD file
	pts = np.asarray(STATE.CONTACT_POINTS)
	# finger_pos = np.asarray([STATE.FINGER_POS['index'], STATE.FINGER_POS['thumb']])
	# np.savetxt('controlpos.txt', finger_pos)
	# np.savetxt('xyzr.txt', np.asarray(STATE.XYZR))
	# np.savetxt('uv.txt', np.asarray(STATE.UNIT_VECTOR))
	save_point_cloud(pts, 'run.pcd')
	subprocess.check_call(['python', 'detect.py', 'save/', 'run.pcd'])

if __name__ == '__main__':
	main()
