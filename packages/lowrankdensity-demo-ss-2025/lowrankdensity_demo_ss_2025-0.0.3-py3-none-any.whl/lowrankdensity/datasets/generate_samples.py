"""
Generates 2D samples from low-rank models for discrete and continuous distributions.

Author: Nassima OULD OUALI
"""

import warnings
import numpy as np 


# ===============================
# Function: generate_lowrank_discrete
# ===============================
def generate_lowrank_discrete(n_samples=5000, K=2, d1=10, d2=10):
    """
    Generate 2D discrete samples from a low-rank probability matrix.
    """
    
    # ------------------------------
    # Parameter validation
    # ------------------------------
    if type(n_samples) != int:
        raise TypeError(f"n_samples should be an int value, not {type(n_samples)}")
    
    if n_samples < 0:
        raise ValueError("n_samples can only take positive values")

    if (type(d1) != int) or (type(d2) != int):
        raise TypeError("d1 and d2 can only take int values") 

    if ((d1 > 100) or (d1 < 2)) or ((d2 > 100) or (d2 < 2)):
        raise ValueError("The number of classes d1 and d2 should be between 2 and 100")

    # Warn if rank is too high for the number of samples (low-rank approximation may be unreliable)
    if K > n_samples**(1/4):
        warnings.warn("The low rank estimator won't perform better than a classic histogram estimator for samples generated with a rank K > n_samples**(1/4)") 

    # ------------------------------
    # Low-rank matrix construction
    # ------------------------------

    # Generate two random matrices u and v of dimensions (d1 x K) and (d2 x K)
    u, v = np.random.rand(d1, K), np.random.rand(d2, K)

    # Compute the outer product approximation: P = (1/K) * u @ v.T
    res = (1/K) * (u @ v.T)

    # Normalize P so that it sums to 1 (valid probability distribution)
    P = res / np.sum(res)

    # ------------------------------
    # Sampling
    # ------------------------------

    # Flatten the probability matrix for multinomial sampling
    p = P.flatten()

    # Draw n_samples samples from the multinomial distribution defined by p
    samples = np.random.multinomial(1, p, size=n_samples).reshape((n_samples, d1, d2))

    # Find the non-zero entry in each sample (argwhere), then take the (i,j) coordinate
    samples = np.argwhere(samples == 1)[:, 1:]

    return samples


# ===============================
# Function: generate_lowrank_continuous
# ===============================
def generate_lowrank_continuous(n_samples=5000, K=2):
    """
    Generate 2D continuous samples from a mixture of K low-rank beta distributions.
    """

    # ------------------------------
    # Parameter validation
    # ------------------------------
    if type(n_samples) != int:
        raise TypeError("n_samples should be an integer")
    
    if n_samples < 0:
        raise ValueError("n_samples can only take positive values")
    
    if K <= 0:
        raise ValueError("The rank of probability matrix P used to generate data can only take positive")
    
    if type(K) != int:
        raise TypeError("The rank of probability matrix P used to generate data should be an integer")

    # Warn if rank is too high compared to the number of samples
    if K > n_samples**(1/4):
        warnings.warn("The low rank estimator won't perform better than a classic histogram estimator for samples generated with a rank K > n_samples**(1/4)") 

    # ------------------------------
    # Define K beta distribution parameters for both dimensions
    # ------------------------------

    # Parameters (a,b) for the beta distributions in dimension 1
    a1, b1 = np.linspace(1, 10, K), np.linspace(3, 10, K)

    # Parameters (a,b) for the beta distributions in dimension 2
    a2, b2 = np.linspace(2, 15, K), np.linspace(4, 25, K) 

    # ------------------------------
    # Sample from K beta distributions for both dimensions
    # f and g have shape (n_samples, K)
    # ------------------------------

    f = np.array([np.random.beta(a=a, b=b, size=n_samples) for a, b in zip(a1, b1)]).T
    g = np.array([np.random.beta(a=a, b=b, size=n_samples) for a, b in zip(a2, b2)]).T

    # ------------------------------
    # For each sample, randomly pick one of the K components to draw (low-rank mixture)
    # ------------------------------

    u = np.random.randint(low=0, high=K, size=n_samples)

    # Construct the (x, y) samples by selecting the j-th component from f and g
    samples = np.array([[f[i, j], g[i, j]] for i, j in enumerate(u)])
        
    return samples
