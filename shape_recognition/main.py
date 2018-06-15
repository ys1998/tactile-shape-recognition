import numpy as np
from vcnn import vCNN
import os, random
import tensorflow as tf

class BatchLoader(object):
    def __init__(self, data_dir, batch_size):
        self._data = np.load(os.path.join(data_dir, 'data.npy'))
        self._labels = np.load(os.path.join(data_dir, 'labels.npy'))
        self.batch_size = batch_size

        self._batch_iter = 0
        # Split data into training, validation and test splits
        n_samples = self._data.shape[0]
        tr_idx = int(n_samples * 0.8)
        val_idx = int(n_samples * 0.9)
        self._train_split = list(zip(self._data[:tr_idx], self._labels[:tr_idx]))
        self._val_split = list(zip(self._data[tr_idx:val_idx], self._labels[tr_idx:val_idx]))
        self._test_split = list(zip(self._data[val_idx:], self._labels[val_idx:]))
        del self._data, self._labels

        self.n_batches = len(self._train_split) // self.batch_size

    def get_batch(self, split):
        if split == 'train':
            if self._batch_iter == self.n_batches:
                self._batch_iter = 1
                random.shuffle(self._train_split)
                return map(np.stack, zip(*self._train_split[:self.batch_size]))
            else:
                x,y = map(np.stack, zip(*self._train_split[self._batch_iter*self.batch_size:(self._batch_iter + 1)*self.batch_size]))
                self._batch_iter += 1
                return x,y
        elif split == 'test':
            random.shuffle(self._test_split)
            return map(np.stack, zip(*self._test_split))
        elif split == 'val':
            random.shuffle(self._val_split)
            return map(np.stack, zip(*self._val_split))

def main():
    restore = False
    save_dir = './save/vcnn'

    # Create data loader
    loader = BatchLoader(data_dir='data', batch_size=50)
    # Create model
    model = vCNN()
    # Create session and restore graph, variables
    with tf.Session(graph=model.graph) as sess:
        if restore:
            saver = tf.train.Saver(max_to_keep=3)
            saver.restore(sess, tf.train.latest_checkpoint(save_dir))
        else:
            sess.run(tf.global_variables_initializer())
        model.train(sess, batch_loader=loader)
        print("Model trained.")
        x_test, y_test = loader.get_batch(split='test')
        print("Test accuracy %.4f" % model.test(sess, x_test, y_test))    

if __name__ == '__main__':
    main()
