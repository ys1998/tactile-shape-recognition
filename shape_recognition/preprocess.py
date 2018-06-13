"""
Script for preparing input data for training.

It scans the specified directory for PoV images and converts
them into 128x128 numpy arrays by cropping the central square,
rescaling and converting to grayscale.

Output:
(i) data
    a numpy array of dimension (N, 6, 128, 128) 

(ii) labels
    a numpy array of dimension (N, M) with labels as below
        0 - cube
        1 - cuboid
        2 - cylinder
        3 - prism
        4 - pyramid
        5 - sphere

    where   N = number of 3D models
            M = number of shapes/classes
"""

import numpy as np
from scipy import misc
from skimage.transform import resize
import matplotlib.pyplot as plt
import os, sys

LABELS = {
    'cube':0,
    'cuboid':1,
    'cylinder':2,
    'prism':3,
    'pyramid':4,
    'sphere':5
}

def make_label(idx):
    val = np.zeros(len(LABELS))
    val[idx] = 1.0
    return val

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage:\npython preprocess.py [DATA_DIR] [SAVE_DIR]")
        exit(1)
    data_dir = sys.argv[1]
    if not os.path.exists(data_dir):
        print("Invalid data directory. Aborting.")
        exit(1)
    if len(sys.argv) == 2:
        save_dir = 'data'
    else:
        save_dir = sys.argv[2]
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Placeholders for output
    data = []
    labels = []

    total_imgs = 6006*6
    img_cntr = 0

    # Walk through the data directory
    for root, _, files in os.walk(data_dir):
        chunk = None; cntr=0
        for f in files:
            name, ext = os.path.splitext(f)
            # check if the file is valid
            if name.startswith('view') and ext == '.png':
                print("Processing image %d/%d" % (img_cntr, total_imgs))
                img_cntr += 1
                cntr += 1
                if chunk is None:
                    chunk = np.empty([6, 128, 128])
                # Load file
                img = misc.imread(os.path.join(root, f),flatten=True)
                # Crop central square
                side = min(img.shape)
                x = img.shape[0]//2 - side//2
                y = img.shape[1]//2 - side//2
                img = img[x:x+side, y:y+side]
                # Rescale image to 128x128
                img = resize(img, (128, 128), anti_aliasing=True, preserve_range=True)
                chunk[int(name.split('_')[1])] = img
        if chunk is not None and cntr == 6:
            data.append(chunk)
            labels.append(make_label(LABELS[os.path.split(root)[1].split('_')[0]]))
    
    # Convert output into a single array
    data = np.stack(data).astype(np.int8)
    labels = np.stack(labels).astype(np.int8)

    # Save to disk
    np.save(os.path.join(save_dir, 'data.npy'), data)
    np.save(os.path.join(save_dir, 'labels.npy'), labels)
    print("Preprocessing done.")

if __name__ == '__main__':
    main()
