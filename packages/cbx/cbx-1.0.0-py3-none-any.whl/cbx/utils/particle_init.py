import numpy as np

def init_particles(shape=(1,1,1), x_min=-1.0, x_max = 1.0, delta=1.0, method="uniform"):
    r"""Initialize particles
    
    Parameters
    ----------
    N : int, optional
        Number of particles. The default is 100.
    d : int, optional
        Dimension of the particles. The default is 2.
    x_min : float, optional
        Lower bound for the uniform distribution. The default is 0.0.
    x_max : float, optional
        Upper bound for the uniform distribution. The default is 1.0.
    delta : float, optional
        Standard deviation for the normal distribution. The default is 1.0.
    method : str, optional
        Method for initializing the particles. The default is "uniform".
        Possible values: "uniform", "normal"
    
    Returns
    -------
    x : numpy.ndarray
        Array of particles of shape (N, d)
    """


    if method == "uniform":
        x = np.random.uniform(x_min, x_max, shape)
    elif method == "normal":
        if len(shape) == 3:
            M, N, d = shape
        elif len(shape) == 2:
            N, d = shape
            M = 1
        else:
            raise RuntimeError('Normal initialization only supported for 2D or 3D shapes!')
        
        x = np.random.multivariate_normal(np.zeros((d,)), delta * np.eye(d), (M, N))
    else:
        raise RuntimeError('Unknown method for init_particles specified!')
        
    return x