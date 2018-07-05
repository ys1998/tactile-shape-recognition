"""
Functions for visualizing data. 
"""

import subprocess, os, sys
import seaborn as sn
sys.path.append('..')
from scripts.compare import load_default, compare
import numpy as np
import matplotlib.pyplot as plt

"""
Visualizing point clouds using the Point Cloud Library.
Three stage process (parameters used aren't tuned):
    - [STAGE 1] Collect raw point cloud
    - [STAGE 2] Estimate normals for data points
    - [STAGE 3] Reconstruct surface using Poisson/MarchingCubes algorithm

NOTE: Changed the reconstruction algorithm to ConcaveHull for dealing with
lower number of data points better.
"""
def render3D(model_path, stage=2, show=True):
    if not os.path.exists(model_path):
        print("Invalid path!")
        exit(1)
    else:
        if stage == 1 and show:
            # Display raw point cloud
            subprocess.check_output([
                'pcl_viewer',
                model_path,
            ])
        else:
            h, t = os.path.split(os.path.abspath(model_path))
            if not os.path.exists(os.path.join(h, t.split('.')[0] + '_output.vtk')):
                print('Surface information not found, generating new file.')
                # Surface reconstruction using Concave Hull
                subprocess.check_call([
                    'pcl_compute_hull',
                    model_path,
                    os.path.join(h, t.split('.')[0] + '_output.vtk')
                ])
            # View reconstructed surface
            if show:
                subprocess.check_call(
                    ['pcl_viewer', os.path.join(h, t.split('.')[0] + '_output.vtk')])

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

"""
View PoV images from data array.
"""
def view_pov(data):
    for i in range(data.shape[0]):
        f, ax = plt.subplots(2, 3, True, True, True)
        ax[0,0].imshow(data[i][0])
        ax[0,1].imshow(data[i][1])
        ax[0,2].imshow(data[i][2])
        ax[1, 0].imshow(data[i][3])
        ax[1, 1].imshow(data[i][4])
        ax[1, 2].imshow(data[i][5])
        plt.show()
