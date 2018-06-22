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


for control in range(500):
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
	x1.append(axis * direction[0] + perp * direction[1])
	y1.append(-axis * direction[1] + perp * direction[0])

	# Find point of contact for thumb
	theta = 90 * (1 - control/500)
	axis = THB * np.cos(np.deg2rad(theta)) + THB_TO_BASE
	perp = THB * np.sin(np.deg2rad(theta))
	x2.append(axis * direction[0] + perp * direction[1])
	y2.append(-axis * direction[1] + perp * direction[0])

plt.figure()
plt.plot([0, 60], [0, 80])
plt.plot(x1, y1)
plt.plot(x2, y2)
plt.show()