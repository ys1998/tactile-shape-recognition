"""
Functions for visualizing data. 
"""

import subprocess, os, sys
import seaborn as sn
from compare import load_default, compare
import numpy as np
import matplotlib.pyplot as plt

"""
Visualizing point clouds using the Point Cloud Library.
Three stage process (parameters used aren't tuned):
    - [STAGE 1] Collect raw point cloud
    - [STAGE 2] Estimate normals for data points
    - [STAGE 3] Reconstruct surface using Poisson/MarchingCubes algorithm
"""
def render3D(model_path, algo=1, stage=3):
    if not os.path.exists(model_path):
        print("Invalid path!")
        exit(1)
    else:
        if stage == 1:
            # Display raw point cloud
            subprocess.check_output([
                'pcl_viewer',
                model_path,
            ])
        else:
            # Normal estimation
            h, t = os.path.split(os.path.abspath(model_path))
            subprocess.check_output([
                                'pcl_normal_estimation', 
                                model_path, 
                                os.path.join(h, t.split('.')[0] + '_with_normals.' + t.split('.')[1]),
                                '-k', "100"
                            ])
            if stage == 2:
                subprocess.check_output([
                    'pcl_viewer',
                    os.path.join(h, t.split('.')[0] + '_with_normals.' + t.split('.')[1]),
                    '-normals', '1'
                ])
            elif stage == 3:
                # Surface reconstruction
                command = 'pcl_poisson_reconstruction' if algo is 1 else 'pcl_marching_cubes_reconstruction'
                subprocess.call([
                                    command, 
                                    os.path.join(h, t.split('.')[0] + '_with_normals.' + t.split('.')[1]), 
                                    os.path.join(h, t.split('.')[0] + '_output.vtk')
                                ])
                # View reconstructed surface
                subprocess.call(['pcl_viewer', os.path.join(h, t.split('.')[0] + '_output.vtk')])

"""
Confusion matrix for shape similarity amongst default shapes.
"""
def default_confusion_matrix():
    fv = load_default(50)
    x_labels = y_labels = list(fv.keys())
    conf_matrix = np.zeros((len(fv), len(fv)))
    for i, shape1 in enumerate(fv.keys()):
        for j, shape2 in enumerate(fv.keys()):    
            conf_matrix[i,j] = compare(fv[shape1], fv[shape2])
    
    plt.figure("Confusion Matrix")
    _ = sn.heatmap(conf_matrix, annot=True, xticklabels=x_labels, yticklabels=y_labels)
    plt.show()
