import numpy as np
import tensorflow as tf

def concat(x, axis):
    if tf.__version__ in ['0.11.0']:
        return tf.concat(axis, x)
    if tf.__version__ in ['1.0.1']:
        return tf.concat(x, axis)

def split(x, axis, num_split):
    if tf.__version__ in ['0.11.0']:
        return tf.split(axis, num_split, x)
    if tf.__version__ in ['1.0.1']:
        return tf.split(x, num_split, axis)

def init_nn_sampler(dimX, dimH, grad_logp_func, name = 'nn_sampler'):
    # parameters
    print 'add in MLP with %d units...' % dimH
    d_in = 2
    print 'add in one hidden layer mlp...'
    W2 = tf.Variable(tf.random_normal(shape=(d_in, dimH))*0.01, name = name + '_W2')
    b2 = tf.Variable(tf.random_normal(shape=(dimH, ))*0.01, name = name + '_b2')
    W3 = tf.Variable(tf.random_normal(shape=(dimH,))*0.01, name = name + '_W3')
    b3 = tf.Variable(tf.random_normal(shape=())*0.01, name = name + '_b3')
    W4 = tf.Variable(tf.random_normal(shape=(dimH,))*0.01, name = name + '_W4')
    b4 = tf.Variable(tf.random_normal(shape=())*0.01, name = name + '_b4')         
        
    def network_transform(z, grad_z, eps = 1e-5):
        noise = tf.random_normal(z.get_shape())
        grad_z_processed = tf.expand_dims(grad_z, 2)
        
        # transformation for the output, using skip connections
        x = concat([tf.expand_dims(z, 2), grad_z_processed], 2)
        x = tf.expand_dims(x, 3)	# (K, dimX, 2, 1)
        F = tf.nn.softplus(tf.reduce_sum(x*W2, 2) + b2)
        direction = tf.reduce_sum(F*W3, 2) + b3 	# shape (K, dimX)
        # normalise to make it a vector of norm 1
        stepsize = tf.nn.relu(tf.reduce_sum(F*W4, 2) + b4)	# (K, dimX)
        delta = eps * direction + tf.sqrt(stepsize)*noise
        
        return delta
    
    def nn_sampler(z, X, y, data_N, shapes = None):
        noise = tf.random_normal(z.get_shape())
        grad_logp = grad_logp_func(X, y, z, data_N, shapes)
        delta = network_transform(z, grad_logp)
        z = z + delta
            
        return z
        
    return nn_sampler
    
