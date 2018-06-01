"""
Functions for preprocessing spike data from files and preparing
input batches for training.
Also has functions for loading preprocessed data.
"""

import numpy as np
import sys, os
import argparse

# Commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, default='', help='Path to data-file to be preprocessed')
parser.add_argument('--folder', type=str, default='', help='Path to folder containing data-files')
parser.add_argument('--save_dir', type=str, default='data', help='Path to directory where preprocessed data is saved')

""" Function for processing a single file """
def process_file(path, shape, save_dir):
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Create data placeholder
    data = np.full(shape, 0, dtype=np.float)
    with open(path, 'r') as f:
        # Skip the header
        f.readline()
        # Iterate over lines in the file
        for line in f:
            patchNum, row, col, pol, t = [int(x) for x in line.split()]
            data[0][t][row][col + 4*patchNum] = pol



def main():
    args = parser.parse_args()
    assert args.file is not '' and args.folder is not '', "Enter valid file/folder name."

    if args.folder:
        # Process all valid .txt files inside specified folder
        for root, _, files in os.walk(args.folder):
            for fl in files:
                path = os.path.join(root, fl)
                if os.path.splitext(path)[1] == '.txt':
                    with open(path, 'r') as f:
                        flag, t = f.readline().split()
                        if flag == 'TACTILE_DATA_FILE':
                            # Input tensor shape: [batch_size, depth, height, width]
                            shape = [1, int(t), 4, 16]
                            # File is valid, read data 
                            process_file(path, shape, args.save_dir)
    elif args.file:
        with open(args.file, 'r') as f:
            flag, t = f.readline().split()
            if flag == 'TACTILE_DATA_FILE':
                # Input tensor shape: [batch_size, depth, height, width]
                shape = [1, int(t), 4, 16]
                # File is valid, read data
                process_file(args.file, shape, args.save_dir)


if __name__ == '__main__':
    main()
