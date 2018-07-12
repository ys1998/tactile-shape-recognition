# Configure paths
import os, sys, subprocess
sys.path.append('../scripts')
sys.path.append('../shape_recognition')
sys.path.append('../shape_recognition/libraries/general')
sys.path.append('../shape_recognition/libraries/iLimb')
sys.path.append('../shape_recognition/libraries/UR10')
sys.path.append('../shape_recognition/libraries/neuromorphic')

# Import libraries

# PyQt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
# Standard
import numpy as np
import tensorflow as tf
import pyqtgraph as pg
# from threading import Thread
from collections import deque
import serial
# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Custom
from iLimb import *
from UR10 import *
from threadhandler import ThreadHandler
from serialhandler import list_serial_ports
from pcd_io import save_point_cloud
from ur10_simulation import ur10_simulator
from iLimb_trajectory import get_coords
from visualize import render3D
from detect import detect_shape
from vcnn import vCNN
from dataprocessing import MovingAverage

# Load UI file
Ui_MainWindow, QMainWindow = loadUiType('formMain_gui.ui')

# Constants
MAPPING = {'index':0, 'thumb':1}
THRESHOLD = {'index':0.01, 'thumb':0.01}
# iLimb dimensions (mm)
IDX_TO_BASE = 185 + 40
THB_TO_BASE = 105 + 30
IDX_0 = 50
IDX_1 = 30
THB = 65

""" Abstract class for storing state variables """
class STATE:
	ROTATION_ANGLE = 30
	ROTATION_POS = 0 # 0,1,2,3
	ROTATION_DIR = -1 # -1/1
	
	NUM_POINTS = 0
	CONTACT_POINTS = []
	CONTROL_POS = [0 for _ in range(5)]
	FINGER_POS = {'index':[], 'thumb':[]}
	XYZR = []
	UNIT_VECTOR = []

	STOP = False
	HEIGHT = 0
	ESTIMATED_HEIGHT = 200
	STARTED = False

class port:
	def __init__(self, widget):
		self.view = widget
	def write(self, *args):
		self.view.append(*args)
	def flush(self, *args):
		pass

""" Main class for controlling the GUI """
class FormMain(QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		# Constructor
		super(FormMain, self).__init__()
		self.setupUi(self)
		
		# Handlers
		self.ur10 = None
		self.iLimb = None

		# Set available ports
		self.port_ur10.setText("10.1.1.6")
		self.port_iLimb.addItems(list_serial_ports())
		self.port_tactile.addItems(list_serial_ports())

		# For tactile values
		self.ser = None
		self.dataQueue = deque([], maxlen=1000)
		self.receiveThread = ThreadHandler(_worker=self.receive)
		self.MIN = np.array([0,0])
		self.MAX = np.array([4096, 4096])
		self.mvaFilt = [MovingAverage(_windowSize = 1000), MovingAverage(_windowSize=1000)]

		# Connect buttons to callback functions
		self.initialize.clicked.connect(self.init_handlers)
		self.configure.clicked.connect(self.configure_handlers)
		self.init_main.clicked.connect(self.start_main)
		self.stop_main.clicked.connect(self.break_main)
		self.toHome.clicked.connect(self.move_to_home)
		self.toBase.clicked.connect(lambda: self.move_to_base(t=5))
		self.moveUp.clicked.connect(lambda: self.move_vertical(_dir=1))
		self.moveDown.clicked.connect(lambda: self.move_vertical(_dir=-1))
		self.cw.clicked.connect(self.rotate_hand_CW)
		self.ccw.clicked.connect(self.rotate_hand_CCW)
		self.toPose.clicked.connect(self.move_iLimb_to_pose)
		self.pinch.clicked.connect(lambda: self.close_hand())
		self.moveAway.clicked.connect(lambda: self.move_away())
		self.startSensors.clicked.connect(lambda: [	self.sensors_timer.start(0), self.receiveThread.start() ])
		self.stopSensors.clicked.connect(lambda: [ self.sensors_timer.stop(), self.receiveThread.pause()])
		self.calibrate.clicked.connect(self.calibrate_sensors)
		self.visualize.clicked.connect(lambda: [self.save_points(), render3D('run.pcd', stage=1)])
		self.convexHull.clicked.connect(lambda: [self.save_points(), render3D('run.pcd', stage=2)])
		self.detectShape.clicked.connect(self.recognize_shape)
		self.clear.clicked.connect(self.reset_stored_values)

		# Initialize PoV graphs
		views = [self.view0, self.view1, self.view2, self.view3, self.view4, self.view5]
		self.povBoxes = []
		self.povPlots = []
		for view in views:
			view.ci.layout.setContentsMargins(0,0,0,0)
			view.ci.layout.setSpacing(0)
			self.povBoxes.append(view.addPlot())
			self.povPlots.append(pg.ScatterPlotItem())
			self.povBoxes[-1].addItem(self.povPlots[-1])

		# Initialize tactile sensor graphs
		self.timestep = [0]
		self.sensorData = [[], []]
		self.sensorBoxes = []
		self.sensorPlots = []
		for view in [self.sensor_index, self.sensor_thumb]:
			view.ci.layout.setContentsMargins(0,0,0,0)
			view.ci.layout.setSpacing(0)
			self.sensorBoxes.append(view.addPlot())
			self.sensorPlots.append(pg.PlotCurveItem(pen=pg.mkPen('b',width=1)))
			self.sensorBoxes[-1].addItem(self.sensorPlots[-1])
			self.sensorBoxes[-1].setXRange(min=0, max=20, padding=0.1)
			# self.sensorBoxes[-1].setYRange(min=0, max=1, padding=0.1)

		self.pov_timer = QtCore.QTimer()
		self.pov_timer.timeout.connect(self.update_pov)
		self.sensors_timer = QtCore.QTimer()
		self.sensors_timer.timeout.connect(self.update_sensor_readings)

		self.main_thread  = Thread(target=self._palpation_routine)
		self.main_thread.daemon = True

		# Redirect console output to textBrowser
		sys.stdout = port(self.textBrowser)

		# Create TensorFlow session and load pretrained model
		self.load_session()

	""" Function to initialize handler objects """
	def init_handlers(self):
		# Create handlers
		print('Initializing handlers ...')
		self.ur10 = UR10Controller(self.port_ur10.text())
		print('UR10 done.')
		self.iLimb = iLimbController(self.port_iLimb.currentText())
		self.iLimb.connect()
		print('iLimb done.')
		self.ser = serial.Serial(self.port_tactile.currentText(),117964800)
		self.ser.flushInput()
		self.ser.flushOutput()
		print('TactileBoard done')

	""" Functions to set all handlers to default configuration """
	def move_to_home(self):
		print('Setting UR10 to default position ...')
		UR10pose = URPoseManager()
		UR10pose.load('shape_recog_home.urpose')
		UR10pose.moveUR(self.ur10,'home_j',5)
		time.sleep(5.2)
			
	def move_iLimb_to_pose(self):
		print('Setting iLimb to default pose ...')
		self.iLimb.setPose('openHand')
		time.sleep(3)
		self.iLimb.control(['thumbRotator'], ['position'], [700])
		time.sleep(3)	

	def calibrate_sensors(self):
		self.receiveThread.start()
		print('Calibrating tactile sensors ...')
		# Clear data queue
		self.dataQueue.clear()
		# Wait till queue has sufficient readings
		while len(self.dataQueue) < 500:
			pass
		# Calculate lower and upper bounds
		samples = np.asarray(copy(self.dataQueue))
		self.MIN = np.mean(samples, axis=0)
		self.MAX = self.MIN + 500 
		self.dataQueue.clear()
		# Set Y-range
		for box in self.sensorBoxes:
			box.setYRange(min=0, max=1, padding=0.1)
		print("Done")

	def configure_handlers(self):
		self.move_to_home()
		self.move_iLimb_to_pose()
		self.calibrate_sensors()
		print('Done.')

	""" Function to create and load pretrained model """
	def load_session(self):
		self.model = vCNN()
		self.session = tf.Session(graph=self.model.graph)
		with self.session.as_default():
			with self.session.graph.as_default():
				saver = tf.train.Saver(max_to_keep=3)
				saver.restore(self.session, tf.train.latest_checkpoint('../shape_recognition/save'))

	""" Function to clear all collected values """
	def reset_stored_values(self):
		STATE.NUM_POINTS = 0
		STATE.CONTACT_POINTS = []
		STATE.CONTROL_POS = [0 for _ in range(5)]
		STATE.FINGER_POS = {'index':[], 'thumb':[]}
		STATE.XYZR = []
		STATE.UNIT_VECTOR = []

	""" Function to close fingers until all fingers touch surface """
	def close_hand(self, fingers=['index', 'thumb']):
		touched = [False] * len(fingers)
		touched_once = False
		fingerArray = [[x, MAPPING[x], THRESHOLD[x]] for x in fingers]
		while not all(touched):
			time.sleep(0.005)
			q = self.get_sensor_data()
			for _ in range(len(q)):
				tactileSample = q.popleft()
				touched = self.iLimb.doFeedbackPinchTouch(tactileSample, fingerArray, 1)
				# update control_pos for fingers that have touched a surface
				for i in range(len(fingerArray)):
					if touched[i]:
						touched_once = True
						STATE.CONTROL_POS[fingerArray[i][1]] = self.iLimb.controlPos
						#----------------------------------------------------------
						# Collect information
						STATE.FINGER_POS[fingerArray[i][0]].append(self.iLimb.controlPos)
						#----------------------------------------------------------

				# Self-touching condition
				# Can be modified later
				if self.iLimb.controlPos > 200 and not touched_once:
					return False
				elif self.iLimb.controlPos > 200 and touched_once:
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
	def compute_coordinates(self):
		self.ur10.read_joints_and_xyzR()
		xyzR = copy(self.ur10.xyzR)
		joints = copy(self.ur10.joints)
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

	""" Functions to rotate hand for next reading """
	def rotate_hand_CCW(self):
		self.ur10.read_joints()
		joints = copy(self.ur10.joints)

		if STATE.ROTATION_POS < 180//STATE.ROTATION_ANGLE - 1:
			STATE.ROTATION_POS += 1
			joints[4] += STATE.ROTATION_ANGLE * -1
			xyzR = self.ur10.move_joints_with_grasp_constraints(joints, dist_pivot=220, grasp_pivot=60, constant_axis='z')
			self.ur10.movej(xyzR, 3)
			time.sleep(3.2)
			
	def rotate_hand_CW(self):
		self.ur10.read_joints()
		joints = copy(self.ur10.joints)

		if STATE.ROTATION_POS > 0:
			STATE.ROTATION_POS -= 1
			joints[4] += STATE.ROTATION_ANGLE * 1
			xyzR = self.ur10.move_joints_with_grasp_constraints(joints, dist_pivot=220, grasp_pivot=60, constant_axis='z')
			self.ur10.movej(xyzR, 3)
			time.sleep(3.2)

	def rotate_hand(self):
		# Boundary checks
		if STATE.ROTATION_POS == 0 and STATE.ROTATION_DIR == -1:
			STATE.ROTATION_DIR = 1
		if STATE.ROTATION_POS == 180//STATE.ROTATION_ANGLE - 1 and STATE.ROTATION_DIR == 1:
			STATE.ROTATION_DIR = -1
		# Rotate the hand according to direction
		if STATE.ROTATION_DIR == 1:
			self.rotate_hand_CCW()
		else:
			self.rotate_hand_CW()

	""" Function to move hand in vertical direction """
	def move_vertical(self, _dir=1):
		# move one step up while palpating
		self.ur10.read_joints_and_xyzR()
		x, y, z, rx, ry, rz = copy(self.ur10.xyzR)
		new_joint_pos = np.array([x, y, z+10*_dir, rx, ry, rz])
		self.ur10.movej(new_joint_pos, 0.5)
		time.sleep(0.7)
		STATE.HEIGHT += 10*_dir

	""" Function to move hand away from the object """
	def move_away(self, fingers=['thumb', 'index']):
		self.iLimb.control(fingers, ['position']*len(fingers), [0]*len(fingers))
		time.sleep(1)

	""" Function to move UR10 to base """
	def move_to_base(self, t=1):
		self.ur10.read_joints_and_xyzR()
		x, y, z, rx, ry, rz = copy(self.ur10.xyzR)
		new_joint_pos = np.array([x, y, -200, rx, ry, rz])
		self.ur10.movej(new_joint_pos, t)
		time.sleep(t+.2)
		STATE.HEIGHT = 0
		STATE.ESTIMATED_HEIGHT = 200

	""" Function to pause of main loop """
	def break_main(self):
		STATE.STOP = True

	""" Function to resume/start standard palpation """
	def start_main(self):	
		if STATE.STARTED:
			STATE.STOP = False
		else:
			self.main_thread.start()
			STATE.STARTED = True
			self.pov_timer.start(0)		

	""" Main routine """
	def _palpation_routine(self):	
		print("Starting standard palpation routine ...")	
		for i in range(180//STATE.ROTATION_ANGLE):
			print("Rotation pos : %d"%(i+1))
			while STATE.HEIGHT < STATE.ESTIMATED_HEIGHT:
				# Pause condition
				print("Height : %d"%STATE.HEIGHT)
				while STATE.STOP is True:
					time.sleep(0.05)
				touched = self.close_hand(['thumb', 'index'])
				time.sleep(0.1)
				if touched:
					self.compute_coordinates()
				else:
					STATE.ESTIMATED_HEIGHT = STATE.HEIGHT
				self.iLimb.resetControl()
				time.sleep(0.5)
				self.move_away()
				self.move_vertical()
			self.move_to_base()
			self.rotate_hand()
		self.recognize_shape()

	""" Function to detect shape """
	def recognize_shape(self):
		self.save_points()
		detect_shape(self.session, self.model, 'run.pcd')

	""" Function to save point cloud """
	def save_points(self):
		# Convert collected points to a PCD file
		pts = np.asarray(STATE.CONTACT_POINTS)
		finger_pos = np.asarray([STATE.FINGER_POS['index'], STATE.FINGER_POS['thumb']])
		np.savetxt('controlpos.txt', finger_pos)
		np.savetxt('xyzr.txt', np.asarray(STATE.XYZR))
		np.savetxt('uv.txt', np.asarray(STATE.UNIT_VECTOR))
		save_point_cloud(pts, 'run.pcd')

	""" Function to update the 6 PoV images """
	def update_pov(self):
		idx = STATE.FINGER_POS['index']
		if len(idx) > 0:
			thb = STATE.FINGER_POS['thumb']
			xyzr = STATE.XYZR
			uv = STATE.UNIT_VECTOR
			# Get lists of coordinates
			x1, y1, z1, x2, y2, z2 = get_coords(idx, thb, xyzr, uv)
			x = x1+x2; y = y1+y2; z = z1+z2
			# Store projections
			pts = np.empty((6, 2, len(x)))
			pts[0][0] = x; pts[0][1] = y
			pts[1][0] = x; pts[1][1] = z
			pts[2][0] = y; pts[2][1] = z
			pts[3][0] = 2*np.mean(x) - x; pts[3][1] = y
			pts[4][0] = 2*np.mean(x) - x; pts[4][1] = z
			pts[5][0] = 2*np.mean(y) - y; pts[5][1] = z

			for i, plot in enumerate(self.povPlots):
				plot.clear()
				plot.addPoints(pts[i][0], pts[i][1])

	""" Function to update the tactile sensor readings """
	def update_sensor_readings(self):
		if len(self.dataQueue)>0:
			data = self.dataQueue[-1] # take the latest reading
			val_1 = (data[0] - self.MIN[0])/(self.MAX[0] - self.MIN[0]) # reading of first sensor (index)
			val_2 = (data[1] - self.MIN[1])/(self.MAX[1] - self.MIN[1]) # reading of second sensor (thumb)
			val_1, val_2 = np.clip([val_1, val_2], 0, 1)
			t = self.timestep[-1] + 0.005
			self.sensorData[0].append(val_1)
			self.sensorData[1].append(val_2)
			self.timestep.append(t)
			
			for i, plot in enumerate(self.sensorPlots):
				plot.setData(self.timestep[1:], self.sensorData[i])

			if t>20:
				self.timestep = [0]
				self.sensorData = [[], []]

	""" Function to populate the data queue with raw values """
	def receive(self):
		recvLength = 6
		waiting = self.ser.inWaiting()
		if waiting >= recvLength :
			rawQueue = [x for x in self.ser.read(recvLength)]
			reading_0 = rawQueue[1] * 256 + rawQueue[2]
			reading_1 = rawQueue[3] * 256 + rawQueue[4]
			self.dataQueue.append([self.mvaFilt[0].getSample(reading_0), self.mvaFilt[1].getSample(reading_1)])

	""" Function to procure data from data queue """
	def get_sensor_data(self):
		# Select last (atmost) 50 readings
		data = np.asarray(copy(self.dataQueue))[-20:]
		self.dataQueue.clear()
		# Normalize data
		data = (data - self.MIN)/(self.MAX - self.MIN)
		data = np.clip(data, 0, 1)
		# Convert data to standard format (list of [patchno][col][row] values)
		processed_data = deque([x.reshape(2,1,1) for x in data])
		return processed_data

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	main = FormMain()
	main.show()
	sys.exit(app.exec_())