"""
Script to extract 6 PoV images from specified PCD file or folder
containing these files.
"""
import os, sys, subprocess
import numpy as np

from pcd_io import load_point_cloud, save_point_cloud
from compare import normalize
from visualize import render3D

def main():
    if len(sys.argv) != 3:
        print("Usage:\npython extract_pov.py [SOURCE FILE/FOLDER] [SAVE_DIR]")
        exit(1)
    else:
        source = sys.argv[1]
        save_dir = sys.argv[2]

        if not os.path.exists(save_dir):
            print("Creating directory %s." % save_dir)
            os.makedirs(save_dir)

        if os.path.isdir(source):
            print("Reading from directory %s." % source)
            # Walk through the directory
            for root, _, files in os.walk(source):
                for f in files:
                    name, ext = os.path.splitext(f)
                    if ext == '.pcd':
                        print("Reading from file %s." % f)
                        pts = load_point_cloud(os.path.join(root, f))
                        x, y, z = normalize(pts)

                        if not os.path.exists(os.path.join(save_dir, name)):
                            os.makedirs(os.path.join(save_dir, name))

                        save_point_cloud(pts, os.path.join(save_dir, name, name + '_normalized.pcd'))

                        # Create folder in save_dir
                        if not os.path.exists(os.path.join(save_dir, name)):
                            os.makedirs(os.path.join(save_dir, name))

                        # Generate VTK file for reconstructed surface
                        render3D(os.path.join(save_dir, name, name + '_normalized.pcd'), show=False)

                        subprocess.check_call([
                            './extract_pov',
                            os.path.join(save_dir, name, name + '_normalized_output.vtk'),
                            os.path.join(save_dir, name) + '/',
                            str(x[0]), str(x[1]), str(x[2]),
                            str(y[0]), str(y[1]), str(y[2]),
                            str(z[0]), str(z[1]), str(z[2])
                        ])
                        print('Extracted PoV images to %s' % os.path.join(save_dir, name))
        else:
            root, file = os.path.split(source)
            name, ext = os.path.splitext(file)
            if ext != '.pcd':
                print('Invalid file.')
                exit(1)
            print("Reading from file %s." % source)
            pts = load_point_cloud(source)
            x, y, z = normalize(pts)

            if not os.path.exists(os.path.join(save_dir, name)):
                os.makedirs(os.path.join(save_dir, name))

            save_point_cloud(pts, os.path.join(save_dir, name, name + '_normalized.pcd'))
            
            # Create folder in save_dir
            if not os.path.exists(os.path.join(save_dir, name)):
                os.makedirs(os.path.join(save_dir, name))

            # Generate VTK file for reconstructed surface
            render3D(os.path.join(save_dir, name, name + '_normalized.pcd'), show=False)

            subprocess.check_call([
                './extract_pov',
                os.path.join(save_dir, name, name + '_normalized_output.vtk'),
                os.path.join(save_dir, name) + '/',
                str(x[0]), str(x[1]), str(x[2]),
                str(y[0]), str(y[1]), str(y[2]),
                str(z[0]), str(z[1]), str(z[2])
            ])
            print('Extracted PoV images to %s' % os.path.join(save_dir, name))


if __name__ == '__main__':
    main()
