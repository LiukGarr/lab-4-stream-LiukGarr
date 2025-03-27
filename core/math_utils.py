import numpy as np


def lin2db(x):
    return 10*np.log10(x)


def db2lin(x):
    return 10**(x/10)

def snr(x,y):
    return 10*np.log10(x/y)