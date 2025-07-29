"""
From emcee:
https://emcee.readthedocs.io/en/stable/tutorials/autocorr/#autocorr
"""

import numpy as np
import os
import pickle

try:
    import acor._acor as acor
except ImportError:
    acor = None


def next_pow_two(n):
    """Returns the next power of two greater than or equal to `n`"""
    i = 1
    while i < n:
        i = i << 1
    return i


# Automated windowing procedure following Sokal (1989)
def auto_window(taus, c):
    m = np.arange(len(taus)) < c * taus
    if np.any(m):
        return np.argmin(m)
    return len(taus) - 1


def autocorr_func_1d(x):
    """Estimate the normalized autocorrelation function of a 1-D series
    Args:
        x: The series as a 1-D numpy array.
    Returns:
        array: The autocorrelation function of the time series.
    """
    x = np.atleast_1d(x)
    if len(x.shape) != 1:
        raise ValueError("invalid dimensions for 1D autocorrelation function")
    n = next_pow_two(len(x))

    # Compute the FFT and then (from that) the auto-correlation function
    f = np.fft.fft(x - np.mean(x), n=2 * n)
    acf = np.fft.ifft(f * np.conjugate(f))[: len(x)].real
    acf /= acf[0]
    return acf


def autocorr_time(y, c=5.0):
    f = autocorr_func_1d(y)
    taus = 2.0 * np.cumsum(f) - 1.0
    window = auto_window(taus, c)
    return taus[window]


def lagged_auto_cov(xi_minus_xs, t):
    """
    from stackoverflow
    for series of values x_i, length N, compute empirical auto-cov with lag t
    defined: 1/(N-1) * \sum_{i=0}^{N-t} ( x_i - x_s ) * ( x_{i+t} - x_s )

    """
    N = len(xi_minus_xs)
    auto_cov = 1.0 / (N - t) * np.sum(xi_minus_xs[0 : N - t] * xi_minus_xs[t:N])
    return auto_cov


def python_acor(X, lag=10, winmult=5):
    """re-factored version of code by Jonathan Goodman & Dan
    Foreman-Mackey
    """
    X = X.copy()
    L = len(X)
    if L < 5 * lag:
        return np.nan, np.nan
    X -= np.mean(X)
    C = np.array([lagged_auto_cov(X, l) for l in range(lag)])
    D = C[0] + 2 * (C[1:].sum())
    sigma = np.sqrt(D / L)
    tau = D / C[0]
    if tau * winmult < lag:
        return sigma, tau
    X = X[0:-2:2] + X[1:-1:2]
    sigma_, tau_ = python_acor(X, lag=lag, winmult=winmult)
    if np.isfinite(sigma_):
        sigma = sigma_
        tau = tau_
    D = 0.25 * sigma * sigma * L
    tau = D / C[0]
    sigma = np.sqrt(D / L)
    return sigma, tau


def get_autocorr_len(chn, burn=0.25, lag=10, opt="acor-c"):
    """Compute slim factor to retain un-correlated samples."""
    istart = int(chn.shape[0] * burn)
    xs = chn[istart:, :]
    opt = "acor-p" if opt == "acor-c" and acor is None else opt

    if opt == "acor-c":
        try:
            als = [acor.acor(xs[:, i], lag)[0] for i in range(xs.shape[1])]
        except:
            opt = "acor-p"
    if opt == "acor-p":
        als = [python_acor(xs[:, i], lag=lag)[1] for i in range(xs.shape[1])]
    elif opt == "emcee":
        als = [autocorr_time(xs[:, i]) for i in range(xs.shape[1])]

    al = np.nanmin(als)
    al = np.random.uniform(10.0, 100.0) if al > 100 else al
    al = max(al, 1)
    return int(al)


def get_mcmc_stats(dirname, proposals):
    """Gather MCMC stats from all chain in containers

    Returns:
    jumps_t: a nchains x nprop array, number of jumps per proposals
    ar_t: a nchains x nprop array, number of accepted jumps per proposals
    nswap: a nchains x 2 array, number of accepted and proposed swaps (pt sampling)
    """
    nchains = len(proposals)
    short_name = lambda n: n.split(" of ")[0].split(" method ")[-1]
    prop_names = [[short_name(str(k)) for k, v in p.items()] for p in proposals]
    full_names = list(set([n for i in range(nchains) for n in prop_names[i]]))
    jumps_t = np.rec.fromarrays(
        [np.zeros((nchains))] * len(full_names), names=full_names
    )
    ar_t = np.rec.fromarrays([np.zeros((nchains))] * len(full_names), names=full_names)
    nswap = np.zeros((nchains, 2))
    for i in range(nchains):
        s = pickle.load(open(os.path.join(dirname, f"stats_{i}.pkl"), "rb"))
        for n in full_names:
            skeys = [short_name(k) for k in s.keys()]
            if n in skeys:
                ni = skeys.index(n)
                ki = list(s.keys())[ni]
                jumps_t[n][i] = s[ki]["njump"]
                if jumps_t[n][i] == 0:
                    jumps_t[n][i] = 1
                ar_t[n][i] = s[ki]["ar"]
        if "nswap_accepted" in s.keys():
            nswap[i, 0] = s["nswap_accepted"]
            nswap[i, 1] = s["nswap_proposed"]

    return jumps_t, ar_t, nswap


def gauss_lnorm(cov):
    """
    Compute the normalization of a gaussian distribution.
    
    :param array cov: covariance matrix.
    
    :return: log of the norm
    :rtype: float
    """
    _dim = cov.shape[0]
    _norm = np.sqrt(np.pi)**_dim
    _norm *= np.sqrt(np.linalg.det(cov).real)
    if _norm <= 0:
        _norm = 1
    return np.log(_norm)    


def gauss_ll(mode, cov, norm=True):
    """
    Builds a gaussian log likelihood function

    :param float mode: mode of the gaussian distribution.
    :param float cov: covariance matrix.

    :return: the gaussian distribution function for the
             given parameters
    :rtype: function
    """
    _icov = np.linalg.pinv(cov, rcond=1e-15, hermitian=True)
    _ln = gauss_lnorm(cov) if norm else 0
    def _func(_par):
        return - _ln - .5 * np.dot(np.dot((_par - mode).T, _icov), (_par - mode))
    return _func
