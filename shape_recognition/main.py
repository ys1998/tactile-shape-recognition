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

import os, subprocess, time
from iLimb import *
from tactileboard import *
from UR10 import *

""" Function to initialize handler objects """
def init_handlers():
	# Create handlers
	global ur10, hand, sensors
	print('Initializing handlers ...')
	ur10 = UR10Controller('10.1.1.6')
	hand = iLimbController()
	hand.connect()
	sensors = TactileBoard(_sensitivity=TBCONSTS.HIGH_SENS)
	sensors.start()
	# Sleep
	time.sleep(3)
	print('Done')

""" Function to set all handlers to default configuration """
def configure_handlers():
	global ur10, hand, sensors
	print('Setting UR10 to default position ...')

	print('Setting iLimb to default pose ...')

	print('Calibrating tactile sensors ...')

""" Function to close fingers until all fingers touch surface """
def close_hand():


""" Function to rotate hand for next reading """
def rotate_hand():


""" Function to move hand in vertical direction """
def move_vertical():
