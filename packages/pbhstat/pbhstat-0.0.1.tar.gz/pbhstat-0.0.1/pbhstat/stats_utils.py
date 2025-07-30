import numpy as np
from math import erfc
from scipy.interpolate import interp1d
from scipy.special import hyp2f1

vec_erfc = np.vectorize(erfc)

# Error function variant
def Erf(x):
    return -1 + vec_erfc(-x)

# Initialize gcf
def initialize_gcf(wmax):
    qq = np.geomspace(0.0001, wmax, 10000)

    def th(q):
        hyp = hyp2f1(1, 5 / (2 + 2 * q), 1 + 5 / (2 + 2 * q), -1 / q)
        return np.clip(2 * q / ((3 * (1 + q)) * hyp), 0, 1)

    th_vals = th(qq)
    def wq(q, th_vals):
        return q * th_vals * 4 * np.sqrt(1 - 3 / 2 * th_vals)

    wq_vals = wq(qq, th_vals)

    wqf = interp1d(qq, wq_vals, kind='cubic', bounds_error=False, fill_value="extrapolate")
    qw = interp1d(wq_vals, qq, kind='cubic', bounds_error=False, fill_value="extrapolate")

    ww = np.geomspace(0.0001, wmax, 10000)

    def gc(w, qw):
        q_vals = qw(w)
        th_vals = th(q_vals)
        y = 4/3 * (1 - np.sqrt(1 - 3/2 * th_vals))
        y2 = 4/3 - 32/9 * 1/w
        return np.where(w < 1e4, y, y2)

    gca = gc(ww, qw)
    gcf0 = interp1d(ww, np.log(gca), kind='cubic', bounds_error=False, fill_value="extrapolate")

    def gcf(w):
        return np.exp(gcf0(w))

    return gcf

# fsm and fs
def fsm(x):
    if x > 0.1:
        y = (x**3 - 3 * x)/2 * (Erf(np.sqrt(5/2) * x) + Erf(np.sqrt(5/2) * x/2)) + \
            np.sqrt(2 / (5 * np.pi)) * ((31 * x**2 / 4 + 8/5) * np.exp(-5 * x**2 / 8) + \
                                        (x**2 / 2 - 8/5) * np.exp(-5 * x**2 / 2))
    else:
        xsmall = x
        x = 0.1
        y = (x**3 - 3 * x)/2 * (Erf(np.sqrt(5/2) * x) + Erf(np.sqrt(5/2) * x/2)) + \
            np.sqrt(2 / (5 * np.pi)) * ((31 * x**2 / 4 + 8/5) * np.exp(-5 * x**2 / 8) + \
                                        (x**2 / 2 - 8/5) * np.exp(-5 * x**2 / 2))
        y = (xsmall / 0.1)**8 * y
    return y

x = np.geomspace(0.0001, 100, 1000)
fs0 = np.array([fsm(xi) for xi in x])
fs = interp1d(x, fs0, kind='cubic', bounds_error=False, fill_value="extrapolate")

# cg relations
def C(g):
    return g * (1 - 3/8 * g)

def crit(g, w, gam=0.36):
    return (C(g) - C(gcf(w)))**gam

def gamma_f(r, sigmagwf, sigmagf, sigmawf):
    return sigmagwf(r) / np.sqrt(sigmagf(r) * sigmawf(r))

def barg(r, sigmagwf, sigmawf):
    return sigmagwf(r) / sigmawf(r)

def sigmawtildef(r, sigmavf, sigmawf, sigmavwf):
    return (sigmavf(r) * sigmawf(r) - sigmavwf(r)**2) / sigmavf(r)

def bargfull(r, sigmavf, sigmagwf, sigmavwf, sigmavgf, sigmawf):
    return (sigmavf(r) * sigmagwf(r) - sigmavwf(r) * sigmavgf(r)) / (sigmavf(r) * sigmawf(r) - sigmavwf(r)**2)

def Sigmagf(r, sigmagf, sigmawf, sigmavf, sigmavgf, sigmagwf, sigmavwf):
    numerator = (sigmavf(r) * sigmagf(r) * sigmawf(r)
                 - sigmavgf(r)**2 * sigmawf(r)
                 - sigmavwf(r)**2 * sigmagf(r)
                 - sigmagwf(r)**2 * sigmavf(r)
                 + 2 * sigmagwf(r) * sigmavwf(r) * sigmavgf(r))
    denominator = sigmavf(r) * sigmawf(r) - sigmavwf(r)**2
    return numerator / denominator

def Mmax(r, alpha, A, K, gamp):
    wm1 = 2/3 * 1/np.log(alpha) * alpha**2 * r**2
    wm = (wm1 + np.sqrt(wm1**2 + 4 * 2.28 * A * 2/9 * alpha**4 * r**4)) / 2
    M = K * r**2 * (2**7 / 3**3)**gamp / wm**(2*gamp) 
    return M

def find_peak_range_indices(ps, threshold_factor=0.1):
    """
    Find indices where power spectrum is within one order of magnitude from the peak.
    
    Parameters:
        ps (array): Power spectrum values.
        threshold_factor (float): Fraction of the peak to use (default 0.1 = one order of magnitude).
        
    Returns:
        idx_min (int): First index in the peak region.
        idx_max (int): Last index in the peak region.
        peak_indices (ndarray): Array of all indices within the peak range.
    """
    ps = np.asarray(ps)
    ps_max = np.max(ps)
    mask = ps >= threshold_factor * ps_max
    peak_indices = np.where(mask)[0]
    
    if peak_indices.size == 0:
        raise ValueError("No peak region found above threshold.")
    
    idx_min = peak_indices[0]
    idx_max = peak_indices[-1]
    
    return idx_min, idx_max