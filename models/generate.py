"""
Functions for generating point clouds for 3D models.
"""

import os, sys
import numpy as np
from math import *
sys.path.append('..')

import pypcd.pypcd as pcd

"""
Point clouds for supported 3D shapes.
"""
def cylinder():
    curved_surface = np.asarray(
                        [(3*cos(theta), 3*sin(theta), z) 
                            for z in np.arange(0, 10, 0.1) 
                                for theta in np.arange(0, 2*pi, 2*pi/30)])
    upper_cover = np.asarray(
                        [(r*cos(theta), r*sin(theta), 10)
                            for r in np.arange(0, 3, 0.3)
                                for theta in np.arange(0, 2*pi, 2*pi/30)])
    lower_cover = np.asarray(
                        [(r*cos(theta), r*sin(theta), 0)
                            for r in np.arange(0, 3, 0.3)
                                for theta in np.arange(0, 2*pi, 2*pi/30)])
    return np.concatenate([lower_cover, curved_surface, upper_cover])

# def sphere(z):
#     return np.asarray([(sqrt(9-z**2)*cos(theta), sqrt(9-z**2)*sin(theta))
#                        for theta in range(0, 2*pi, 2*pi/NUM_POINTS)]).reshape(-1, 2)

# def pyramid(z):
#     return np.asarray([(3*cos(theta), 3*sin(theta))
#                        for theta in range(0, 2*pi, 2*pi/NUM_POINTS)]).reshape(-1, 2)

# def cube(z):
#     return np.asarray([(3*cos(theta), 3*sin(theta))
#                        for theta in range(0, 2*pi, 2*pi/NUM_POINTS)]).reshape(-1, 2)

# def prism_3(z):
#     return np.asarray([(3*cos(theta), 3*sin(theta)) 
#                         for theta in range(0, 2*pi, 2*pi/NUM_POINTS)]).reshape(-1,2)

# def prism_4(z):
#     return np.asarray([(3*cos(theta), 3*sin(theta))
#                        for theta in range(0, 2*pi, 2*pi/NUM_POINTS)]).reshape(-1, 2)

"""
Generate and save point clouds to PCD file.
"""
def save_point_cloud(shape, filepath):
    if shape not in globals():
        print("Shape not found.")
    else:
        # Generate point cloud
        point_cloud = globals()[shape]()
        pc = pcd.make_xyz_point_cloud(point_cloud)
        # Save point cloud to file
        pcd.save_point_cloud(pc, filepath)
