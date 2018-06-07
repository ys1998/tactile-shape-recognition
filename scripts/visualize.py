"""
Script for visualizing point clouds using the Point Cloud Library.
Three step process:
    - Estimate normals for data points
    - Reconstruct surface using Poisson/MarchingCubes algorithm
    - Display reconstructed surface

(parameters used aren't tuned)
"""

import subprocess, os, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, required=True, help="Path to point cloud file")
parser.add_argument('--algo', type=int, choices=[1,2], default=1, help="Reconstruction algorithm [Poisson (1) / MarchingCubes (2)]")
parser.add_argument('--stage', type=int, choices=[1,2,3], default=3, help="Processing level [1] raw [2] with normals [3] reconstructed surface")

def main(args):
    model_path = args.model
    if not os.path.exists(model_path):
        print("Invalid path!")
        exit(1)
    else:
        # Normal estimation
        h, t = os.path.split(os.path.abspath(model_path))
        subprocess.check_output([
                            'pcl_normal_estimation', 
                            model_path, 
                            os.path.join(h, t.split('.')[0] + '_with_normals.' + t.split('.')[1]),
                            '-k', "100"
                        ])
        # Surface reconstruction
        command = 'pcl_poisson_reconstruction' if args.algo is 1 else 'pcl_marching_cubes_reconstruction'
        subprocess.call([
                            command, 
                            os.path.join(h, t.split('.')[0] + '_with_normals.' + t.split('.')[1]), 
                            os.path.join(h, t.split('.')[0] + '_output.vtk')
                        ])
        # View reconstructed surface
        subprocess.call(['pcl_viewer', os.path.join(h, t.split('.')[0] + '_output.vtk')])

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
