"""
Functions for generating point clouds for 3D models.
"""

import os, sys
import numpy as np
from math import *
sys.path.append('..')

import pypcd.pypcd as pcd
from scripts.pcd_io import load_point_cloud, save_point_cloud

"""
Point clouds for supported 3D shapes.
"""
def cylinder():
    # x^2 + y^2 = 9
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

def sphere():
    # x^2 + y^2 + z^2 = 9
    return np.asarray([(sqrt(9-z**2)*cos(theta), sqrt(9-z**2)*sin(theta), z)
                            for z in np.arange(-3, 3, 0.1)
                                for theta in np.arange(0, 2*pi, 2*pi/30)])

def pyramid():
    # Base: 4x4 (square)
    # Height: 6
    l1 = np.asarray([(x, -2) for x in np.arange(-2, 2, 0.1)])
    l2 = np.asarray([(x, 2) for x in np.arange(-2, 2, 0.1)])
    l3 = np.asarray([(-2, y) for y in np.arange(-2, 2, 0.1)])
    l4 = np.asarray([(2, y) for y in np.arange(-2, 2, 0.1)])
    border = np.concatenate([l1, l2, l3, l4])

    base = np.asarray([(x, y, 0)
                            for x in np.arange(-2, 2, 0.1)
                                for y in np.arange(-2, 2, 0.1)])

    surface = np.concatenate([np.c_[border * (1-z/6), np.full(border.shape[0], z)]
                                for z in np.arange(0.1, 6, 0.1)])
    
    return np.concatenate([base, surface])

def cube():
    # 4 x 4 x 4
    l1 = np.asarray([(x, -2) for x in np.arange(-2, 2, 0.1)])
    l2 = np.asarray([(x, 2) for x in np.arange(-2, 2, 0.1)])
    l3 = np.asarray([(-2, y) for y in np.arange(-2, 2, 0.1)])
    l4 = np.asarray([(2, y) for y in np.arange(-2, 2, 0.1)])
    border = np.concatenate([l1, l2, l3, l4])

    base1 = np.asarray([(x, y, 0)
                       for x in np.arange(-2, 2, 0.1)
                       for y in np.arange(-2, 2, 0.1)])

    base2 = np.asarray([(x, y, 4)
                       for x in np.arange(-2, 2, 0.1)
                       for y in np.arange(-2, 2, 0.1)])

    surface = np.concatenate([np.c_[border, np.full(border.shape[0], z)]
                              for z in np.arange(0.1, 4, 0.1)])

    return np.concatenate([base1, surface, base2])

def prism():
    # Base: equilateral triangle of side 4
    # Height: 6
    l1 = np.asarray([(x, 0) for x in np.arange(0, 4, 0.1)])
    l2 = np.asarray([(4 - r/2, r * sin(pi/3)) for r in np.arange(0, 4, 0.1)])
    l3 = np.asarray([(r/2, r*sin(pi/3)) for r in np.arange(0, 4, 0.1)])
    border = np.concatenate([l1, l2, l3])

    surface = np.concatenate([np.c_[border, np.full(border.shape[0], z)]
                              for z in np.arange(0.1, 6, 0.1)])
    
    offset = np.array([2, 2/sqrt(3)])
    base = np.concatenate([offset + (border-offset)*e/4 for e in np.arange(0, 4, 0.1)]) 

    return np.concatenate([np.c_[base, np.zeros(base.shape[0])], surface, np.c_[base, np.full(base.shape[0], 6)]])

def cuboid():
    # 3 x 4 x 5
    l1 = np.asarray([(x, 0) for x in np.arange(0, 4, 0.1)])
    l2 = np.asarray([(x, 3) for x in np.arange(0, 4, 0.1)])
    l3 = np.asarray([(0, y) for y in np.arange(0, 3, 0.1)])
    l4 = np.asarray([(4, y) for y in np.arange(0, 3, 0.1)])
    border = np.concatenate([l1, l2, l3, l4])

    base1 = np.asarray([(x, y, 0)
                        for x in np.arange(0, 4, 0.1)
                        for y in np.arange(0, 3, 0.1)])

    base2 = np.asarray([(x, y, 5)
                        for x in np.arange(0, 4, 0.1)
                        for y in np.arange(0, 3, 0.1)])

    surface = np.concatenate([np.c_[border, np.full(border.shape[0], z)]
                              for z in np.arange(0.1, 5, 0.1)])

    return np.concatenate([base1, surface, base2])

"""
Generate point clouds for default models.
"""
def generate_shape_pc(shape, save_dir):
    if shape not in globals():
        print("Shape not found.")
    else:
        # Generate point cloud
        point_cloud = globals()[shape]()
        save_point_cloud(point_cloud, os.path.join(save_dir, shape + '.pcd'))