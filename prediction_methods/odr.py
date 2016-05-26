from scipy.odr import Model, Data, ODR
from scipy.stats import linregress
import numpy as np


def ortho_regress(x, y):
    linreg = linregress(x, y)
    mod = Model(f)
    dat = Data(x, y)
    od = ODR(dat, mod, beta0=linreg[0:2])
    out = od.run()
    #print(list(out.beta))
    #return list(out.beta) + [np.nan, np.nan, np.nan]
    return(list(out.beta))


def f(p, x):
    return (p[0] * x) + p[1]
