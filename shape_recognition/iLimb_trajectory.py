import matplotlib.pyplot as plt
import numpy as np

IDX_TO_BASE = 185 + 40
THB_TO_BASE = 105 + 30
IDX_0 = 50
IDX_1 = 30
THB = 65

def get_coords(idx, thb, xyzr, uv):

	x1 = []; y1 = []
	x2 = []; y2 = []
	z = []
	helper_x = []
	helper_y = []


	for idx_control, thb_control, xyzR, direction in zip(idx, thb, xyzr, uv):
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
		x1.append(axis * np.cos(dir_ang) - perp * np.sin(dir_ang) + xyzR[0])
		y1.append(axis * np.sin(dir_ang) + perp * np.cos(dir_ang) + xyzR[1])

		# Find point of contact for thumb
		theta = 90 * (1 - thb_control/500)
		axis = THB * np.cos(np.deg2rad(theta)) + THB_TO_BASE
		perp = THB * np.sin(np.deg2rad(theta))
		x2.append(axis * np.cos(dir_ang) - perp * np.sin(dir_ang) + xyzR[0])
		y2.append(axis * np.sin(dir_ang) + perp * np.cos(dir_ang) + xyzR[1])

		helper_x.extend([xyzR[0], xyzR[0]+50*direction[0]])
		helper_y.extend([xyzR[1], xyzR[1]+50*direction[1]])
		# print(direction, axis, perp)
		z.append(xyzR[2])

	return x1, y1, z, x2, y2, z
	

if __name__ == '__main__':
	pts = np.loadtxt('controlpos.txt')
	idx = pts[0]; thb = pts[1]
	xyzr = np.loadtxt('xyzr.txt')
	uv = np.loadtxt('uv.txt')
	# get_coords(idx[:len(idx)//3], thb[:len(thb)//3], xyzr[:len(xyzr)//3], uv[:len(uv)//3])
	x1, y1, _, x2, y2, _ = get_coords(idx, thb, xyzr, uv)
	# Plot trajectory/points
	plt.figure()
	# plt.plot(helper_x, helper_y)
	plt.scatter(x1, y1)
	plt.scatter(x2, y2)
	plt.axes().set_aspect('equal', 'datalim')
	plt.show()