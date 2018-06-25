import matplotlib.pyplot as plt
import numpy as np

x1 = []; y1 = []
x2 = []; y2 = []

direction = [0.6, -0.8]
IDX_TO_BASE = 185
THB_TO_BASE = 105
IDX_0 = 50
IDX_1 = 35
IDX = 84
THB = 80


def get_coords(idx, thb, xyzr, uv):

	for idx_control, thb_control, xyzR, direction in zip(idx, thb, xyzr, uv):
		# Find point of contact for index finger
		theta = 30 + 60/500 * idx_control
		if idx_control < 210:
			# Normal circular motion
			rel_theta = 30
		else:
			rel_theta = 30 + 60/290 * (idx_control - 210)

		axis = IDX_0 * np.cos(np.deg2rad(theta)) + IDX_1 * np.cos(np.deg2rad(theta+rel_theta))
		perp = IDX_0 * np.sin(np.deg2rad(theta)) + IDX_1 * np.sin(np.deg2rad(theta+rel_theta))
		axis += IDX_TO_BASE
		x1.append(axis * direction[0] + perp * direction[1] + xyzR[0])
		y1.append(-axis * direction[1] + perp * direction[0] + xyzR[1])

		# Find point of contact for thumb
		theta = 90 * (1 - thb_control/500)
		axis = THB * np.cos(np.deg2rad(theta)) + THB_TO_BASE
		perp = THB * np.sin(np.deg2rad(theta))
		x2.append(axis * direction[0] + perp * direction[1] + xyzR[0])
		y2.append(-axis * direction[1] + perp * direction[0] + xyzR[1])

	# Plot trajectory/points
	plt.figure()
	plt.scatter(x1, y1)
	plt.scatter(x2, y2)
	plt.show()

if __name__ == '__main__':
	get_coords(
				idx=list(range(500)), 
				thb=list(range(500)),
				xyzr=[],
				uv=[]
				)