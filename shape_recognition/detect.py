"""
Script for real-time shape detection using pre-trained model.
"""

import tensorflow as tf
import numpy as np
from scipy import misc
from skimage.transform import resize
import os, sys, subprocess
from vcnn import vCNN
from shutil import rmtree

from preprocess import LABELS
SHAPE = {v:k for k,v in LABELS.items()}

def detect_shape(sess, model, filepath):
	# 'filepath' is the path to the PCD file
	path = os.path.relpath(filepath, '../scripts')
	subprocess.check_call(['python', 'extract_pov.py', path, '.temp'], cwd='../scripts')
	# Walk through the data directory
	chunk = None
	cntr = 0
	for root, _, files in os.walk('../scripts/.temp'):
		for f in files:
			name, ext = os.path.splitext(f)
			# check if the file is valid
			if name.startswith('view') and ext == '.png':
				cntr += 1
				print("Processing image %d/%d" % (cntr, 6))
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
	if chunk is None:
		print('No PoV images found.')
		exit(1)
	else:
		data = np.expand_dims(chunk, axis=0) # shape (1, 6, 128, 128)
		preds = model.test(sess, data)
		print(preds)
		print("Detected shape: %s" % SHAPE[np.argmax(preds)])
	# Remove temporary directory
	rmtree('../scripts/.temp')


if __name__ == '__main__':
	if len(sys.argv) > 2:
		# Load trained model in a tf.Session and return it
		model = vCNN()
		with tf.Session(graph=model.graph) as sess:
			saver = tf.train.Saver(max_to_keep=3)
			saver.restore(sess, tf.train.latest_checkpoint(sys.argv[1]))
			detect_shape(sess, model, sys.argv[2])
	else:
		print("Usage:\npython detect.py [MODEL_LOAD_DIR] [POINT_CLOUD]")
