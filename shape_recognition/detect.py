"""
Script for real-time shape detection using pre-trained model.
"""

import tensorflow as tf
import numpy as np
import os, sys
sys.path.append('..')

from scripts.compare import normalize
from scripts.pcd_io import load_point_cloud

def configure_session(load_dir):
	# Load trained model in a tf.Session and return it
	sess = tf.Session()
	saver = tf.train.Saver(max_to_keep=3)
    saver.restore(sess, tf.train.latest_checkpoint(load_dir))
    return sess

def detect_shape(sess, pts):
	# 'pts' contains loaded, raw point cloud
	# This enables the function to be used independently too
	pts = normalize(pts)


if __name__ == '__main__':
	if len(sys.argv) > 2:
		pts = load_point_cloud(sys.argv[2])
		sess = configure_session(sys.argv[1])
		detect_shape(sess, pts)