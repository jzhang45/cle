import numpy as np
import theano
import theano.tensor as T

from util import *


class ParamInit(object):
    """
    WRITEME

    Parameters
    ----------
    .. todo::
    """
    def __init__(self,
                 init_type='randn',
                 mean=0.,
                 stddev=0.01,
                 low=-0.1,
                 high=0.1):

        self.initializer = {
            'rand': lambda x: np.random.uniform(low=low,
                                                high=high,
                                                size=x.shape),
            'randn': lambda x: np.random.normal(loc=mean,
                                                scale=stddev,
                                                size=x.shape),
            'zeros': lambda x: np.zeros(x.shape),
            'const': lambda x: np.zeros(x.shape) + mean,
            'ortho': lambda x: scipy.linalg.orth(
                np.random.normal(loc=mean, scale=stddev, size=x.shape))
        }[init_type]

    def set(self, sharedX_var):
        numpy_var = sharedX_var.get_value()
        numpy_var = castX(self.initializer(numpy_var))
        sharedX_var.set_value(numpy_var)

    def get(self, *shape):
        return sharedX(self.initializer(np.zeros(shape)))


class NonLin(object):
    """
    WRITEME

    Parameters
    ----------
    .. todo::
    """
    def which_nonlin(self, nonlin):

        return getattr(self, nonlin)

    def linear(self, z):
        return z

    def relu(self, z):
        return z * (z > 0.)

    def sigmoid(self, z):
        return T.nnet.sigmoid(z)

    def softmax(self, z):
        return T.nnet.softmax(z)

    def tanh(self, z):
        return T.nnet.tanh(z)


class Layer(NonLin, object):
    """
    Abstract class for layers

    Parameters
    ----------
    .. todo::
    """
    def __init__(self):
        pass

    def get_params(self):
        return []

    def fprop(self, x=None):
        return x


class Input(Layer):
    """
    Abstract class for layers

    Parameters
    ----------
    .. todo::
    """
    def __init__(self, inp):
        #if not isinstance(type(inp), T.TensorVariable):
        #    raise ValueError("Input is not Theano variable.")
        self.out = inp


class FullyConnectedLayer(Layer):
    """
    Implementations of fully connected layer

    Parameters
    ----------
    .. todo::
    """
    def __init__(self,
                 name,
                 n_in,
                 n_out,
                 unit='relu',
                 init_W=ParamInit('randn'),
                 init_b=ParamInit('zeros')):

        self.nonlin = self.which_nonlin(unit)
        self.W = init_W.get(n_in, n_out)
        self.b = init_b.get(n_out)

    def get_params(self):
        return [self.W, self.b]

    def fprop(self, x):
        z = T.dot(x, self.W) + self.b
        z = self.nonlin(z)
        return z


class OnehotLayer(Layer):
    """
    Transform a scalar to one-hot vector

    Parameters
    ----------
    .. todo::
    """
    def __init__(self, max_labels):
        self.max_labels = max_labels

    def fprop(self, x):
        one_hot = T.zeros((x.shape[0], self.max_labels))
        one_hot = T.set_subtensor(
            one_hot[T.arange(x.size) % x.shape[0], x.T.flatten()], 1
        )
        return one_hot


class IdentityLayer(Layer):
    """
    Identity layer

    Parameters
    ----------
    .. todo::
    """
    def fprop(self, x):
        return x