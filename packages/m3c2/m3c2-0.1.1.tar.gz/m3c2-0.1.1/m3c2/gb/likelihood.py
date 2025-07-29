""" Galactic binary parameterization, priors and likelihood.
"""

import numpy as np
import matplotlib.pyplot as plt
try:
    from ldc.common.series import FrequencySeries
except:
    pass

import time

from .fstatistics import XYZ2AET

def is_in_prior(pp, prior):
    """prior is a npar x 2 matrix defining lower and upper bound for each
    param.

    it could also be a npar x 3 matrix, where the last column defines
    if the absolute value of the corresponding parameter should be
    used.
    """
    inPrior = True
    ppc = pp.copy()
    if prior.shape[1] == 3:  # check if abs value in range
        idx = prior[:, 2].astype(bool)
        ppc[idx] = np.abs(pp[idx])
    for i in range(len(pp)):
        if ppc[i] < prior[i, 0] or ppc[i] > prior[i, 1]:
            inPrior = False
    return inPrior


def random_point(prior):
    sz = np.shape(prior)[0]
    p = np.random.random(sz)
    for i in range(sz):
        p[i] = p[i] * (prior[i, 1] - prior[i, 0]) + prior[i, 0]
    return p


def plotAE(A, E, At, Et, SA):
    fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(16, 8))
    ax[0].plot(A.f, np.abs(At), label="data")
    ax[0].plot(A.f, np.abs(A), label="model")
    ax[0].semilogy(A.f, np.sqrt(SA) * np.ones((len(A.f))), label="noise")
    ax[1].plot(A.f, np.abs(Et), label="data")
    ax[1].plot(A.f, np.abs(E), label="model")
    ax[1].semilogy(A.f, np.sqrt(SA) * np.ones((len(A.f))), label="noise")
    for i in range(2):
        ax[i].legend()


def likelihood_flat(
    pars,
    as_gb_param,
    Npars=8,
    AET_data=None,
    GB=None,
    noise=None,
    plotIt=False,
    full_output=False,
    noise_ampl=1,
):
    """pars is Nsrc x Npars"""
    Nsrc = int(len(pars) / Npars)  ## number of sources in the model
    pars = np.reshape(pars, (Nsrc, Npars))
    df = 1 / GB.T
    fr = AET_data.f.values
    kmin0 = AET_data.A.attrs["kmin"]
    Xs = FrequencySeries(np.zeros((len(fr)), dtype=np.complex128), df=df, kmin=kmin0)
    Ys = FrequencySeries(np.zeros((len(fr)), dtype=np.complex128), df=df, kmin=kmin0)
    Zs = FrequencySeries(np.zeros((len(fr)), dtype=np.complex128), df=df, kmin=kmin0)

    for ind in range(Nsrc):
        pp = pars[ind, :]
        Xf, Yf, Zf = GB.get_fd_tdixyz(template=as_gb_param(pars[ind, :]), oversample=4)
        kmin = Xf.attrs["kmin"]
        bd, bm = (0, kmin0 - kmin) if kmin < kmin0 else (kmin - kmin0, 0)
        ed = len(fr) if len(fr) - bd < len(Xf) - bm else len(Xf) - bm + bd
        em = bm + (ed - bd)
        Xs[bd:ed] += Xf[bm:em]
        Ys[bd:ed] += Yf[bm:em]
        Zs[bd:ed] += Zf[bm:em]

    A, E, T = XYZ2AET(Xs, Ys, Zs)
    SA = noise * noise_ampl
    At = AET_data.A.values
    Et = AET_data.E.values

    if plotIt:
        plotAE(A, E, At, Et, SA)

    DA = At - A.values
    DE = Et - E.values
    loglik = -0.5 * df * np.sum(np.real(DA * np.conj(DA) + DE * np.conj(DE)) / SA)
    N = At.size
    loglik += -0.5 * N * np.log(noise_ampl)
    if full_output:
        return loglik, (At, Et), (A, E), SA
    return loglik


class FlatLogLik(object):
    """Fit for N GB source parameters as the same time.

    Noise is supposed to be known.
    """

    def __init__(self, data, GB, noise, frange, tmax, N=1, fdot_log=True, phiLR=False):
        self.data = data.sel(f=slice(frange[0], frange[1]))
        df = 1 / GB.T
        self.data.A.attrs["kmin"] = int(np.round(self.data.f[0].values / df))
        self.GB = GB
        self.N = N
        self.noise = np.mean(noise.psd(freq=self.data.f, option="A")).values
        self.fmin, self.fmax = frange
        self.t_max = tmax
        self.fdot_log = fdot_log
        self.phiLR = phiLR
        self.prior = self.make_prior()
        self.logPi = self.get_log_prior()
        name_fdot = "log10_fdot" if fdot_log else "fdot"
        name_ang = ["psi", "phi0"] if not phiLR else ["phiL", "phiR"]
        self.names = ["log10_Amp", "fr", name_fdot, "sin_bet", "lam", "cos_iota"]
        self.names += name_ang
        self.names = self.names * N

    def as_search_param(self, pp):
        """Switch from fastGB parameterizatoin to search parameterization"""
        Amp = pp["Amplitude"]
        f0 = pp["Frequency"]
        fdot = pp["FrequencyDerivative"]
        bet, lam = pp["EclipticLatitude"], pp["EclipticLongitude"]
        iota = pp["Inclination"]
        psi, phi0 = pp["Polarization"], pp["InitialPhase"]
        phiL, phiR = phi0 / 2.0 + psi, phi0 / 2.0 - psi
        fd = np.log10(fdot) if self.fdot_log else fdot
        ang = [psi, phi0] if not self.phiLR else [phiL, phiR]
        r = np.array([np.log10(Amp), f0, fd, np.sin(bet), lam, np.cos(iota)] + ang)
        return r

    def as_gb_param(self, pp):
        """switch from search parameterization to fastGB parameterization"""
        l_Amp, mf0, fdot, sin_bet, lam, cos_iota, psi, phi0 = pp
        lam = lam % (2 * np.pi)
        cos_iota = (cos_iota + 1) % 2 - 1
        iota = np.arccos(cos_iota)
        sin_bet = (sin_bet + 1) % 2 - 1
        beta = np.arcsin(sin_bet)
        amp = 10.0**l_Amp
        f0 = mf0
        if self.phiLR:
            phiL = psi
            phiR = phi0
            phi0 = phiL + phiR
            psi = phiL - phi0 / 2.0
        psi = psi % (2 * np.pi)
        phi0 = phi0 % (2 * np.pi)
        if self.fdot_log:
            fdot = 10.0**fdot
        return {
            "Frequency": f0,
            "FrequencyDerivative": fdot,
            "EclipticLatitude": beta,
            "EclipticLongitude": lam,
            "Amplitude": amp,
            "Inclination": iota,
            "Polarization": psi,
            "InitialPhase": phi0,
        }

    def make_prior(self):
        """Default GB parameters bounds"""
        Amp_bnd = [-24.0, -20.0]  ### log10 amplitude
        fr_bnd = np.array([self.fmin, self.fmax])  ### in Hz
        if self.fdot_log:
            fdot_bnd = [-18.0, -14.0]
        else:
            fdot_bnd = [
                1e-5 * self.fmax ** (15 / 3.0),
                1.25e-6 * self.fmax ** (11 / 3.0),
            ]
        sin_bet_bnd = [-1.0, 1.0]
        lam_bnd = [0, 2.0 * np.pi]
        cos_iota_bnd = [-1.0, 1.0]
        if not self.phiLR:
            psi_bnd = [-np.pi / 6.0, 2.0 * np.pi + np.pi / 6]
            phi0_bnd = [-np.pi / 6.0, 2.0 * np.pi + np.pi / 6]
        else:
            psi_bnd = [0, 4.0 * np.pi]
            phi0_bnd = [-2.0 * np.pi, 2.0 * np.pi]
        prior = [
            Amp_bnd,
            fr_bnd,
            fdot_bnd,
            sin_bet_bnd,
            lam_bnd,
            cos_iota_bnd,
            psi_bnd,
            phi0_bnd,
        ]
        prior = np.array(prior)
        if not self.fdot_log:
            vabs = np.array([0, 0, 1, 0, 0, 0, 0, 0]).reshape(8, -1)
            prior = np.hstack([prior, vabs])
        return prior

    def in_prior(self, pars, prior, Npars=8):
        """Check that GB parameters are in prior"""
        Nsrc = int(len(pars) / Npars)  ## number of sources in the model
        pars = np.reshape(pars, (Nsrc, Npars))
        for ind in range(Nsrc):
            pp = pars[ind, :]
            if not is_in_prior(pp, prior):
                return False
        return True

    def get_log_prior(self):
        """Log prior is computed once for all."""
        prior = self.make_prior()
        prior_sky_V = 4.0 * np.pi
        prior_incl = 2.0
        prior_psi = np.pi
        prior_phi = np.pi
        prior_f = int((self.fmax - self.fmin) * self.t_max)
        if self.fdot_log:
            prior_fdot = int(
                (10 ** prior[2][1] - 10 ** prior[2][0]) * self.t_max * self.t_max
            )
        else:
            prior_fdot = int((prior[2][1] - prior[2][0]) * self.t_max * self.t_max)
        prior_fdot = 1 if prior_fdot == 0 else prior_fdot
        prior_vol = [prior_sky_V, prior_incl, prior_psi, prior_phi, prior_f, prior_fdot]
        logPi = 0.0
        for pri in prior_vol:
            logPi = logPi - np.log(pri)
        return logPi

    def loglik(self, x, plotIt=False, full_output=False, **kwargs):
        if not self.in_prior(x, self.prior, Npars=8):
            return -np.inf
        return likelihood_flat(
            x,
            self.as_gb_param,
            AET_data=self.data,
            GB=self.GB,
            noise=self.noise,
            Npars=8,
            plotIt=plotIt,
            full_output=full_output,
        )

    def logprior(self, x, **kwargs):
        return self.logPi
