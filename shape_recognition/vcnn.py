"""
Voting Convolutional Neural Network (vCNN) implementation in Tensorflow.

vCNN consists of two components: (i) a CNN for identifying the 2D shape in each
projection/view and hence detecting the overall 3D shape, and (ii) a 'voting' 
network that collects the predictions of the CNN for each view and combines all 
6 to give a final prediction.
"""

import tensorflow as tf
import numpy as np
import time

class vCNN(object):
    def __init__(self, n_views=6, n_shapes=6):
        # Store arguments

        # Create tensor graph
        self.graph = tf.Graph()
        with self.graph.as_default():
            # Placeholders for input and output
            self._input = tf.placeholder(tf.float32, shape=[None, n_views, 128, 128], name='Input')
            self._output = tf.placeholder(tf.float32, shape=[None, n_shapes], name='Output')
            self._lr = tf.placeholder(tf.float32, name='Learning_Rate')

            # Global step counter
            self.step = tf.Variable(0, name='Global_Step', dtype=tf.int32, trainable=False)
            # List to store predictions of CNN
            self.predictions = []
            # Total loss
            self._loss = tf.Variable(0.0, dtype=tf.float32, name='Total_Loss', trainable=False)

            # CNN
            with tf.variable_scope("CNN"):
                for i in range(n_views):
                    # Convolution and Pooling layers
                    conv1 = tf.layers.conv2d(
                        inputs=tf.expand_dims(self._input[:,i,:,:], axis=-1),
                        filters=32,
                        kernel_size=(3,3),
                        strides=(1, 1),
                        padding='same',
                        kernel_initializer=tf.truncated_normal_initializer(mean=0.0, stddev=1e-3),
                        bias_initializer=tf.zeros_initializer(),
                        activation=tf.nn.leaky_relu,
                        name='ConvLayer1',
                        reuse=tf.AUTO_REUSE
                    )
                    pool1 = tf.layers.max_pooling2d(
                        inputs=conv1,
                        pool_size=(2,2),
                        strides=(2,2),
                        name='PoolLayer1'
                    )
                    conv2 = tf.layers.conv2d(
                        inputs=pool1,
                        filters=64,
                        kernel_size=(3, 3),
                        strides=(1, 1),
                        padding='same',
                        kernel_initializer=tf.truncated_normal_initializer(mean=0.0, stddev=1e-3),
                        bias_initializer=tf.zeros_initializer(),
                        activation=tf.nn.leaky_relu,
                        name='ConvLayer2',
                        reuse=tf.AUTO_REUSE
                    )
                    pool2 = tf.layers.max_pooling2d(
                        inputs=conv2,
                        pool_size=(2, 2),
                        strides=(2, 2),
                        name='PoolLayer2'
                    )
                    conv3 = tf.layers.conv2d(
                        inputs=pool2,
                        filters=32,
                        kernel_size=(3, 3),
                        strides=(1, 1),
                        padding='same',
                        kernel_initializer=tf.truncated_normal_initializer(mean=0.0, stddev=1e-3),
                        bias_initializer=tf.zeros_initializer(),
                        activation=tf.nn.leaky_relu,
                        name='ConvLayer3',
                        reuse=tf.AUTO_REUSE
                    )
                    pool3 = tf.layers.max_pooling2d(
                        inputs=conv3,
                        pool_size=(2, 2),
                        strides=(2, 2),
                        name='PoolLayer3'
                    )
                    # Fully connected layers
                    flat = tf.layers.flatten(pool3)
                    fc1 = tf.layers.dense(
                        inputs=flat,
                        units=32,
                        activation=tf.nn.leaky_relu,
                        use_bias=True,
                        kernel_initializer=tf.truncated_normal_initializer(mean=0.0, stddev=1e-2),
                        bias_initializer=tf.zeros_initializer(),
                        name='FullyConnectedLayer1',
                        reuse=tf.AUTO_REUSE
                    )
                    fc2 = tf.layers.dense(
                        inputs=fc1,
                        units=n_shapes,
                        activation=tf.nn.leaky_relu,
                        use_bias=True,
                        kernel_initializer=tf.truncated_normal_initializer(mean=0.0, stddev=1e-2),
                        bias_initializer=tf.zeros_initializer(),
                        name='FullyConnectedLayer2',
                        reuse=tf.AUTO_REUSE
                    )
                    pred = tf.nn.softmax(fc2)
                    view_loss = tf.nn.softmax_cross_entropy_with_logits(logits=fc2, labels=self._output)
                    self.predictions.append(pred)
                    self._loss = self._loss + view_loss

            # Voting network
            with tf.variable_scope("VotingNetwork"):
                combined_preds = tf.concat(self.predictions, axis=1)
                vl = tf.layers.dense(
                    inputs=combined_preds,
                    units=n_shapes,
                    activation=tf.nn.leaky_relu,
                    use_bias=True,
                    kernel_initializer=tf.truncated_normal_initializer(mean=0.0, stddev=0.1),
                    bias_initializer=tf.zeros_initializer(),
                    name='VotingLayer',
                    reuse=tf.AUTO_REUSE
                )
                # Final prediction
                self.predictions.append(tf.nn.softmax(vl))
                prediction_loss = tf.nn.softmax_cross_entropy_with_logits(logits=vl, labels=self._output)
                self._loss = self._loss + prediction_loss

            self._loss = tf.reduce_mean(self._loss)

            # Optimizers
            optim = tf.train.AdamOptimizer(learning_rate=self._lr)
            # TODO Clip gradients if 'NaN' values appear
            self.train_step = optim.minimize(self._loss)

    def train(self, sess, batch_loader, n_epochs=50, learning_rate=1e-3, save_dir='save/model', log_dir='logs'):
        """ 
        Trains the model. 
        Assumes that graph has been already loaded and initialized within 'sess'.
        """
        self.batch_loader = batch_loader
        # Create saver and summary writer
        saver = tf.train.Saver(max_to_keep=3)
        summary_writer = tf.summary.FileWriter(logdir=log_dir, graph=self.graph)
        # Monitor variables
        loss_summary = tf.summary.scalar(name='Loss', tensor=self._loss)
        pred_summary = tf.summary.tensor_summary(name='Predictions', tensor=tf.stack(self.predictions)[:,0,:])

        # Validation set
        x_val, y_val = batch_loader.get_batch(split='val')

        prev_val_acc = 0.0

        # Find starting epoch number
        st_epoch = sess.run(self.step) // batch_loader.n_batches
        prev_loss = 1000

        for n in range(st_epoch, n_epochs, 1):
            total_loss = 0.0
            for i in range(batch_loader.n_batches):
                X, Y = batch_loader.get_batch(split='train')
                st = time.time()
                loss, _, step, merged = sess.run([
                        self._loss, 
                        self.train_step,
                        tf.assign_add(self.step, 1),
                        tf.summary.merge_all()   
                    ], 
                    feed_dict={
                        self._input:X, 
                        self._output:Y,
                        self._lr:learning_rate
                    })
                print("Epoch %d/%d batch %d/%d loss %.4f time %.4f sec" % 
                        (n+1, n_epochs, i+1, batch_loader.n_batches, loss, time.time()-st))
                # Add summary
                summary_writer.add_summary(merged, global_step=step)
                total_loss += loss

            # Calculate accuracy on validation set after every epoch
            val_acc = self.test(sess, x_val, y_val)
            print("Validation accuracy: %.4f Average loss: %.4f\n" % (val_acc, total_loss/batch_loader.n_batches))
            # Save model if it has better accuracy
            if val_acc > prev_val_acc:
                saver.save(sess, save_dir, global_step=step)
                prev_val_acc = val_acc
            # Calculate average loss
            if total_loss / batch_loader.n_batches >= prev_loss:
            	learning_rate *= 0.5
            	print("Decaying learning rate to %.4f" % learning_rate)
            prev_loss = total_loss / batch_loader.n_batches

    def test(self, sess, X, Y=None):
        """ 
        Returns prediction if Y is None, otherwise returns accuracy. 
        Assumes that graph has been already loaded and initialized within 'sess'.
        """ 
        batch_size = self.batch_loader.batch_size
        n_iters = X.shape[0]//batch_size
        preds = []
        for i in range(n_iters):
        	temp = sess.run(self.predictions, feed_dict = {self._input:X[i*batch_size:(i+1)*batch_size]})
        	preds.append(temp[-1])

        temp = sess.run(self.predictions, feed_dict = {self._input:X[n_iters*batch_size:]})
        preds.append(temp[-1][:X.shape[0]%batch_size])

        preds = np.concatenate(preds)
        if Y is None:
            return preds
        else:
            return np.mean(np.argmax(preds, axis=1)==np.argmax(Y, axis=1))
