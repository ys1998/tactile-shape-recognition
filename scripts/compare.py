"""
Functions for performing 3D shape similarity analysis of 
reconstructed object/surface with existing models.

[Normalization approach adapted from "Similarity between Three-
Dimensional Objects - An Iterative and Interactive Approach" by
Michael Elad, Ayellat Tal and Sigal Ar.]

Approach:
The 3D point cloud is first normalized into a standard form by 
the following steps
- centering
- rotation
- scaling
- 'heavier axis flip'
- x,y,z axis assignment

After normalization, feature vectors are extracted from 6 view-
points (face-centers of enclosing cube with semi-edge of 1 unit)
These vectors are compared with those of the actual model using
cosine similarity measure.
"""

import numpy as np
import os, sys
sys.path.append('..')

import pypcd.pypcd as pcd

"""
Extract shape vectors from a point cloud stored in a PCD file.
"""
def extract_shape_vectors(filepath, n_features):
	if not os.path.exists(filepath):
		print("Specified file does not exist.")
		exit(1)
	# Load point cloud (pc)
	with open(filepath, 'r') as f:
		pc = pcd.point_cloud_from_fileobj(f)
	pts = pc.pc_data
	# NOTE Hack for converting structured array to ndarray
	pts = pts.view(pts.dtype[0]).reshape(pts.shape + (-1,))
	# Normalize point cloud and get axes
	x, y, z = normalize(pts)
	# Find the points of view
	pov = np.stack([x, y, z, -x, -y, -z])
	# Find the 3D shape vectors
	fv = np.zeros([6, n_features])
	for i in range(6):
		fv[i] = find_radial_distribution(pts - pov[i], n_features)
		# TODO Try 'find_linear_distribution'
	return fv
	
"""
Bring the point cloud into standard orientation by shifting,
rotating, rescaling and flipping.
"""
def normalize(pts):
	# Find centroid
	centroid = np.mean(pts, axis=0)
	# Shift centroid to (0,0,0)
	pts -= centroid
	# Calculate covariance matrix
	c_11, c_22, c_33 = np.sum(pts**2, axis=0)
	x, y, z = pts.T
	# Find sum of pairwise products
	sum_x, sum_y, sum_z = np.sum(pts, axis=0)
	c_12 = c_21 = 0.5 * ((sum_x + sum_y)**2 - sum_x**2 - sum_y**2)
	c_13 = c_31 = 0.5 * ((sum_x + sum_z)**2 - sum_x**2 - sum_z**2)
	c_32 = c_23 = 0.5 * ((sum_z + sum_y)**2 - sum_z**2 - sum_y**2)
	# Create the covariance matrix
	covariance = np.array([c_11, c_12, c_13, c_21, c_22, c_23, c_31, c_32, c_33]).reshape([3,3])
	# Singular Value Decomposition (SVD) to get eigenvectors and 'variance'
	u, delta, _ = np.linalg.svd(covariance)
	# Rotate the point cloud using 'u'
	pts = np.matmul(pts, u.T)
	# Rescale the point cloud using 'lambda_1'
	pts /= delta[0]
	# Obtain the vectors defining axes
	ax_1, ax_2, ax_3 = np.transpose(u/np.linalg.norm(u, axis=0))
	# Find sum of projections of points on these axes
	v1 = np.sum(ax_1 * pts)
	v2 = np.sum(ax_2 * pts)
	v3 = np.sum(ax_3 * pts)
	# Flip axes so that all dot products are positive
	ax_1 = ax_1 if v1 >= 0 else -ax_1
	ax_2 = ax_2 if v2 >= 0 else -ax_2
	ax_3 = ax_3 if v3 >= 0 else -ax_3
	# Assign x, y, z axes one of ax_1, ax_2, ax_3 each
	if abs(v1) > abs(v2):
		if abs(v1) > abs(v3):
			x = ax_1
			y, z = (ax_2, ax_3) if np.dot(x, np.cross(ax_2, ax_3)) > 0 else (ax_3, ax_2) 
		else:
			x = ax_3
			y, z = (ax_1, ax_2) if np.dot(x, np.cross(ax_1, ax_2)) > 0 else (ax_2, ax_1)
	else:
		if abs(v2) > abs(v3):
			x = ax_2
			y, z = (ax_1, ax_3) if np.dot(x, np.cross(ax_1, ax_3)) > 0 else (ax_3, ax_1)
		else:
			x = ax_3
			y, z = (ax_2, ax_1) if np.dot(x, np.cross(ax_2, ax_1)) > 0 else (ax_1, ax_2)

	return x, y, z

"""
Compare two feature vectors.
Uses cosine similarity currently.
"""
def compare(fv_1, fv_2):
	product = np.sum(fv_1 * fv_2, axis=1)/(np.linalg.norm(fv_1, axis=1) * np.linalg.norm(fv_2, axis=1))
	# Combine similarities
	# TODO try ML algo for appropriate weights?
	# Weigh a particular POV more?
	weights = np.ones(6)
	return np.mean(product * weights)

"""
Find the radial distribution of given point cloud about (0,0,0).
Equi-volume shells are used as histogram bins and simple averaging 
is used for normalizing the histogram.
"""
def find_radial_distribution(pts, n_features):
	MAX_RADIUS = 2 + 1e-3 # add small margin for boundary point(s)
	distro = np.zeros(n_features)
	dist = np.linalg.norm(pts, axis=1)
	idxs = np.floor(n_features * np.power(dist/MAX_RADIUS, 1/3)).astype(int)
	distro[idxs] += 1
	return distro/np.sum(distro)