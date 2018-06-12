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
def cylinder(R=3, H=10):
    # x^2 + y^2 = 9
    curved_surface = np.asarray(
                        [(R*cos(theta), R*sin(theta), z) 
                            for z in np.arange(0, H, 0.1) 
                                for theta in np.arange(0, 2*pi, 2*pi/30)])
    upper_cover = np.asarray(
                        [(r*cos(theta), r*sin(theta), 10)
                            for r in np.arange(0, R, 0.3)
                                for theta in np.arange(0, 2*pi, 2*pi/30)])
    lower_cover = np.asarray(
                        [(r*cos(theta), r*sin(theta), 0)
                            for r in np.arange(0, R, 0.3)
                                for theta in np.arange(0, 2*pi, 2*pi/30)])
    return np.concatenate([lower_cover, curved_surface, upper_cover])

def sphere(R=3):
    # x^2 + y^2 + z^2 = 9
    return np.asarray([(sqrt(R**2-z**2)*cos(theta), sqrt(R**2-z**2)*sin(theta), z)
                            for z in np.arange(-R, R, 0.1)
                                for theta in np.arange(0, 2*pi, 2*pi/30)])

def pyramid(L=4, H=6):
    # Base: 4x4 (square)
    # Height: 6
    l1 = np.asarray([(x, -L/2) for x in np.arange(-L/2, L/2, 0.1)])
    l2 = np.asarray([(x, L/2) for x in np.arange(-L/2, L/2, 0.1)])
    l3 = np.asarray([(-L/2, y) for y in np.arange(-L/2, L/2, 0.1)])
    l4 = np.asarray([(L/2, y) for y in np.arange(-L/2, L/2, 0.1)])
    border = np.concatenate([l1, l2, l3, l4])

    base = np.asarray([(x, y, 0)
                            for x in np.arange(-L/2, L/2, 0.1)
                                for y in np.arange(-L/2, L/2, 0.1)])

    surface = np.concatenate([np.c_[border * (1-z/H), np.full(border.shape[0], z)]
                                for z in np.arange(0.1, H, 0.1)])
    
    return np.concatenate([base, surface])

def cube(L=4):
    # 4 x 4 x 4
    l1 = np.asarray([(x, -L/2) for x in np.arange(-L/2, L/2, 0.1)])
    l2 = np.asarray([(x, L/2) for x in np.arange(-L/2, L/2, 0.1)])
    l3 = np.asarray([(-L/2, y) for y in np.arange(-L/2, L/2, 0.1)])
    l4 = np.asarray([(L/2, y) for y in np.arange(-L/2, L/2, 0.1)])
    border = np.concatenate([l1, l2, l3, l4])

    base1 = np.asarray([(x, y, 0)
                       for x in np.arange(-L/2, L/2, 0.1)
                        for y in np.arange(-L/2, L/2, 0.1)])

    base2 = np.asarray([(x, y, 4)
                        for x in np.arange(-L/2, L/2, 0.1)
                        for y in np.arange(-L/2, L/2, 0.1)])

    surface = np.concatenate([np.c_[border, np.full(border.shape[0], z)]
                              for z in np.arange(0.1, L, 0.1)])

    return np.concatenate([base1, surface, base2])

def prism(L=4, H=6):
    # Base: equilateral triangle of side 4
    # Height: 6
    l1 = np.asarray([(x, 0) for x in np.arange(0, L, 0.1)])
    l2 = np.asarray([(L - r/2, r * sin(pi/3)) for r in np.arange(0, L, 0.1)])
    l3 = np.asarray([(r/2, r*sin(pi/3)) for r in np.arange(0, L, 0.1)])
    border = np.concatenate([l1, l2, l3])

    surface = np.concatenate([np.c_[border, np.full(border.shape[0], z)]
                              for z in np.arange(0.1, H, 0.1)])
    
    offset = np.array([L/2, (L/2)/sqrt(3)])
    base = np.concatenate([offset + (border-offset)*e/L for e in np.arange(0, L, 0.1)]) 

    return np.concatenate([np.c_[base, np.zeros(base.shape[0])], surface, np.c_[base, np.full(base.shape[0], H)]])

def cuboid(L=3, B=4, H=5):
    # 3 x 4 x 5
    l1 = np.asarray([(x, 0) for x in np.arange(0, B, 0.1)])
    l2 = np.asarray([(x, B) for x in np.arange(0, B, 0.1)])
    l3 = np.asarray([(0, y) for y in np.arange(0, B, 0.1)])
    l4 = np.asarray([(L, y) for y in np.arange(0, B, 0.1)])
    border = np.concatenate([l1, l2, l3, l4])

    base1 = np.asarray([(x, y, 0)
                        for x in np.arange(0, L, 0.1)
                        for y in np.arange(0, B, 0.1)])

    base2 = np.asarray([(x, y, H)
                        for x in np.arange(0, L, 0.1)
                        for y in np.arange(0, B, 0.1)])

    surface = np.concatenate([np.c_[border, np.full(border.shape[0], z)]
                              for z in np.arange(0.1, H, 0.1)])

    return np.concatenate([base1, surface, base2])

"""
Generate point clouds for default models.
"""
def generate_default(shape, save_dir):
    if shape not in globals():
        print("Shape not found.")
    else:
        # Generate point cloud
        point_cloud = globals()[shape]()
        save_point_cloud(point_cloud, os.path.join(save_dir, shape + '.pcd'))

"""
Generate point clouds of the default shapes for training.

Arguments:
    shape       : list of shapes to be generated
    save_dir    : directory where generated models are saved
    num_samples : number of models to be generated for each shape
    min_pts     : minimum number of points in cloud
    max_pts     : maximum number of points in cloud
"""
def generate_data(
        shapes=['cylinder', 'sphere', 'cube', 'cuboid', 'prism', 'pyramid'],
        save_dir='.', 
        num_samples=1000, 
        min_pts=200, 
        max_pts=None
    ):
    assert all([x in globals() for x in shapes]), "Invalid shape found."
    assert max_pts is None or max_pts > min_pts, "'max_pts' should be greater than 'min_pts'"

    for shape in shapes:
        pc = globals()[shape]()
        if not os.path.exists(os.path.join(save_dir, shape)):
            os.makedirs(os.path.join(save_dir, shape))
        for n in range(num_samples):
            l = min_pts; u = max_pts if max_pts is not None else pc.shape[0]
            n_pts = int(l + np.random.choice(u-l, 1, replace=False))
            idxs = np.random.choice(pc.shape[0], n_pts, replace=False)
            save_point_cloud(pc[idxs], os.path.join(save_dir, shape, "%s_%d.pcd" % (shape, n)))
