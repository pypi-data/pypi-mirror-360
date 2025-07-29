"""
samplermcmc.proposal
"""

import numpy as np
import sys
from .tools import get_autocorr_len, gauss_ll

try:
    from hyperkde import HyperKDE
except ImportError:
    HyperKDE = None


def init_logger():
    """Default logger is stdout."""
    from importlib import reload  # Not needed in Python 2
    import logging

    reload(logging)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    return logging.getLogger()

class Proposal:
    """A proposal function. We use a class to stored meta-data and ease
    the customization.
    """

    def __init__(self, names, logger=None, sort_name=None, sort_range=None, **kwargs):
        """Default initialization.

        Number of parameters and their names are set here.
        sort_range: (1st index use to reshape, first axis size)
        """
        self.names = np.array(names)
        self.dim = len(names)
        self.name = "default"
        self.sort_name = sort_name
        if sort_name is not None:
            self.sort_sel = np.where(self.names == sort_name)[0]
            self.sort_range = sort_range
        if logger is None:
            logger = init_logger()
        self.logger = logger
        self.ps_slow = kwargs.get("ps_slow", False)
        self.ps_fast = kwargs.get("ps_fast", False)
        if self.ps_slow and self.ps_fast:
            raise ValueError('Only one of ps_slow and ps_fast can be set to True')

    def chn_mask(self, chain):
        if self.ps_slow:
            return chain.slow_mask
        if self.ps_fast:
            return chain.fast_mask
        return list(range(self.dim))

    def get_cov(self, chain):
        """Return covariance SVD decomposition."""
        if self.ps_slow:
            return chain.cov_slow, chain.U_slow, chain.S_slow
        if self.ps_fast:
            return chain.cov_fast, chain.U_fast, chain.S_fast
        return chain.cov, chain.U, chain.S

    def sort_by(self, x):
        if self.sort_name is None:
            return x
        short_a = np.argsort(x[self.sort_sel])
        reshaped = x[self.sort_range[0] :].reshape(-1, self.sort_range[1])
        reshaped = reshaped[short_a, :]
        x = np.hstack([x[0 : self.sort_range[0]], reshaped.flatten()])
        return x

    def history(self):
        return dict()

    def Lx(self, chain):
        if self.ps_slow:
            return chain.xslowll

        if self.ps_fast:
            return chain.xfastll

        return chain.Lx

    def log_l(self, chain, x):
        x = x.copy()

        if self.ps_slow: 
            # We return the full loglike at a different slow point so 
            # this can get really slow.
            return chain._log_l(x, chain.split(chain.Mx)[1],
                                **chain.slow_fun(x))

        if self.ps_fast:
            return chain._log_l(chain.split(chain.Mx)[0], x,
                                **chain.extra)

        #chain.wrap(x, chain.wrap_mask)        
        return chain.log_l(x)

    def get_sample(self, chain, ind):
        smpl = chain.get_sample(ind)
        if self.ps_slow:
            return chain.split(smpl)[0]

        if self.ps_fast:
            return chain.split(smpl)[1]

        return smpl
        

class Slice(Proposal):
    """A slice sampler.

    Any proposed points is accepted here.
    """

    def __init__(self, names, get_cov=None, get_dir=None, **kwargs):
        """Set scaling probability and factor."""
        super().__init__(names, **kwargs)
        self.p1 = [0.95, 10.0]
        self.p2 = [0.9, 0.2]
        self.jump = [0.2, 3]  # prob, sigma
        self.max_cnt = 200
        self.name = "slice"
        self.cnt = []
        self.get_cov = super().get_cov if get_cov is None else get_cov
        self.get_direction = self.get_direction_ if get_dir is None else get_dir

    def get_direction_(self, x, U, S):
        """Design the direction in which we move."""
        prob = np.random.rand()
        if prob > self.p1[0]:
            scale = self.p1[1]
        elif prob > self.p2[0]:
            scale = self.p2[1]
        else:
            scale = 1.0

        d = len(x)
        cd = scale * 2.38 / np.sqrt(d)
        # dx = np.dot(U, np.random.randn(d) * cd * np.sqrt(S))
        dx = cd * np.dot(np.random.randn(d)*np.sqrt(S), U.T)

        if prob <= self.jump[0]:  ### jump in the coordinate direction
            ix = np.random.choice(d)  ### choosing the coordinate
            del_x = (
                self.jump[1] * dx[ix]
            )  ### choose 3 sigma jump in that coord. direction
            dx = np.zeros(d)
            dx[ix] = del_x
        return dx

    def slice(self, x, chain=None, **kwargs):
        """Return actual sample.

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        _, U, S = self.get_cov(chain)
        dx = self.get_direction(x, U, S)
        logLxT = self.Lx(chain) * chain.beta
        logu = logLxT - np.random.exponential(1.0)

        xr = np.copy(x)
        for i in range(self.max_cnt):  # going "right"
            xr = xr + dx
            loglik = self.log_l(chain, xr) * chain.beta
            if loglik <= logu:
                break
        self.nl_cnt = i

        xl = np.copy(x)
        for i in range(self.nl_cnt, self.max_cnt):  # going "left"
            xl = xl - dx
            loglik = self.log_l(chain, xl) * chain.beta
            if loglik <= logu:
                break
        self.nl_cnt = i

        for i in range(
            self.nl_cnt, self.max_cnt
        ):  # choosing a point along that direction
            al1 = np.random.random()
            xp = xl + al1*(xr-xl)
            loglik = self.log_l(chain, xp) * chain.beta
            if loglik > logu:
                    pars = xp
                    break
            else:
                sgn = np.dot((xp-x), (xr-xl))
                if sgn<0:
                    xl = xp
                else:
                    xr = xp

        self.nl_cnt = i
        self.cnt.append(i)
        if self.nl_cnt >= self.max_cnt - 1 or not np.isfinite(loglik):
            return x, 0, self.Lx(chain), 0
        pars = self.sort_by(pars)
        return pars, 1, loglik / chain.beta, 0

    def history(self):
        return dict({"slice_cnt": self.cnt})


class SCAM(Proposal):
    """A Single Component Adaptive Metropolis sampler."""

    def __init__(self, names, get_cov=None, **kwargs):
        """Set scaling probability and factor."""
        super().__init__(names, **kwargs)
        self.p1 = (0.97, 10.0)
        self.p2 = (0.90, 0.2)
        self.addNoise = False
        self.name = "SCAM"
        self.get_cov = super().get_cov if get_cov is None else get_cov
        self.extra_fact = kwargs.get("extra_fact", 1.)

    def SCAM(self, x, chain=None, **kwargs):
        """Return actual sample by jumping in one component direction.

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        prob = np.random.rand()
        if prob > self.p1[0]:  # ocasional large/small jump:
            scale = self.p1[1]
        elif prob > self.p2[0]:
            scale = self.p2[1]
        else:
            scale = 1.0

        d = len(x)
        _, U, S = self.get_cov(chain)
        cd = 2.38 * scale / np.sqrt(d)
        ind = np.unique(np.random.randint(0, self.dim, 1))
        x_new = x + np.random.randn() * cd * np.sqrt(S[ind]) * U[:, ind].flatten()
        x_new = self.sort_by(x_new)
        if self.addNoise:
            dx = 0.05 * np.random.normal(0.0, 1.0e-6 / self.dim, self.dim)
            x_new = 0.95 * x_new + dx

        return x_new, 0, None, 0


class ReMHA(Proposal):
    """A Regional Metropolis Hastings Algorithm sampler."""

    def __init__(self, names, **kwargs):
        """Set scaling probability and factor."""
        super().__init__(names, **kwargs)
        self.name = "ReMHA"

    def ReMHA(self, x, chain=None, **kwargs):
        """Return actual sample by jumping in one component direction.

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        d = len(x)
        if not chain.modes:
            chain.update_modes()
        Nm = len(chain.modes)
        means = np.array([md[0] for md in chain.modes])
        covs = np.array([md[1] for md in chain.modes])
        weights = np.array([md[2] for md in chain.modes])

        ## draw randomly from iy mode
        iy = np.random.choice(len(weights), p=weights)
        mn_y = np.array(means[iy, :])
        cv_y = 2.38**2 * np.array(covs[iy, :, :]) / d
        y = np.random.multivariate_normal(mn_y, cv_y)
        y = self.sort_by(y)
        return y, 0, None, 0


class DE(Proposal):
    """A differential evolution sampler."""

    def __init__(self, names, DE_skip=1000, **kwargs):
        """Set scaling probability and factor."""
        super().__init__(names, **kwargs)
        self.DE_skip = DE_skip
        self.p = (0.5, 1.0)
        self.pc = 0.7
        self.name = "DE"

    def DE(self, x, chain=None, **kwargs):
        """Return actual sample using differential evolution of a given chain.

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        burn = self.DE_skip
        chain_size = chain.get_size()
        if chain_size <= burn + 5:
            return x, -1, None, 0

        mm = np.random.randint(burn, chain_size)
        nn = np.random.randint(burn, chain_size)
        while mm == nn:
            nn = np.random.randint(burn, chain_size)

        scale = self.get_scale(chain)
        dx = self.get_sample(chain, mm) - self.get_sample(chain, nn)
        x_new = x + dx * scale
        x_new = self.sort_by(x_new)
        return x_new, 0, None, 0

    def get_scale(self, chain):
        """ """
        prob = np.random.rand()
        ## choose scale of the jump
        if prob > self.p[0]:
            scale = self.p[1]
        else:
            scale = (
                np.random.rand()
                * 2.4
                / np.sqrt(self.dim)
                * np.sqrt(chain.anneal / chain.beta)
            )
        return scale

    def DE_all(self, x, chains=None, chain=None, **kwargs):
        """Return actual sample using differential evolution of all chains.

        Args:
        x: the current position
        chains, chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        burn = self.DE_skip
        ci1, ci2 = np.random.randint(0, len(chains), size=2)  ## mixing all chains
        chain_size1 = chains[ci1].get_size()
        chain_size2 = chains[ci2].get_size()
        if chain_size1 <= burn + 5 or chain_size2 <= burn + 5:
            return x, -1, None, 0

        # we will use last 30% of each chain
        imin1 = max(burn, int(chain_size1 * self.pc))
        imin2 = max(burn, int(chain_size2 * self.pc))
        mm = np.random.randint(imin1, chain_size1)
        nn = np.random.randint(imin2, chain_size2)
        scale = self.get_scale(chain)

        dx = chains[ci1].get_sample(mm) - chains[ci2].get_sample(nn)
        x_new = x + dx * scale
        x_new = self.sort_by(x_new)
        return x_new, 0, None, 0


class AdaptiveKDE(Proposal):
    """Adaptive KDE proposal base on hypKDE library"""

    def __init__(self, names, **kwargs):
        """Check that hyperkde is installed."""
        if HyperKDE is None:
            print("ImportError: hyperkde is not installed.")

        super().__init__(names, **kwargs)
        self.name = "adaptKDE"

    def kde_jump(self, x, chain, ims=0, **kwargs):
        """Return new sample draw from KDE distribution."""
        if chain.kde is None:
            return x, -1, None, 0

        x_new, qxy = chain.kde.draw_from_random_hyp_kde(x)
        return x_new, 0, None, qxy


class Prior(Proposal):
    """A simple sampler based on priors."""

    def __init__(self, names, prior, **kwargs):
        """Set prior range."""
        super().__init__(names, **kwargs)
        self.prior = np.array(prior)
        self.name = "prior"

    def sample_prior(self, x, chain=None, **kwargs):
        """Return actual sample.

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        sz = np.shape(self.prior)[0]
        y = np.random.random(sz)
        for i in range(sz):
            y[i] = y[i] * (self.prior[i, 1] - self.prior[i, 0]) + self.prior[i, 0]
        y = self.sort_by(y)
        return y, 0, None, 0


class Gibbs(Proposal):
    """
    Proposal with jump in a subset of parameters only
    """

    def __init__(self, names, subset_names=[], cov=None, **kwargs):
        """
        subset_names: list of parameters used for the jump
        """
        super().__init__(names, **kwargs)

        # array of indices for params we want to vary
        self.ipars = [list(names).index(p) for p in subset_names]
        if not self.ipars:
            return
        if cov is None:
            self.cov = np.diag(np.ones(len(subset_names)) * 0.01**2)
        assert len(subset_names) == self.cov.shape[0]
        U, S, v = np.linalg.svd(self.cov)
        self.U = U
        self.S = S
        self._scam = SCAM(subset_names, get_cov=self.get_cov)
        self._slice = Slice(
            subset_names, get_dir=self.get_direction, get_cov=self.get_cov
        )
        self._slice.max_cnt = 20

    def update_cov(self, sub_chain):
        """Updates covariance of a subset of chain"""
        if not self.ipars:
            return
        sub_chain = sub_chain[:, self.ipars]
        al = get_autocorr_len(sub_chain, burn=0.25)
        istart = int(0.5 * len(sub_chain))  # skip 50% of the chain
        x_tot = np.array(sub_chain)[istart :: int(al)]
        cov = np.cov(x_tot.T)
        U, S, v = np.linalg.svd(cov)
        self.U = U
        self.S = S

    def get_cov(self, chain=None):
        """Return covariance SVD decomposition."""
        return self.cov, self.U, self.S

    def SCAM(self, x):
        """A Single Component Adaptive Metropolis sampler."""
        y = x.copy()
        if not self.ipars:
            return y, 0, None, 0

        x_new, status, logy, qxy = self._scam.SCAM(x[self.ipars])
        y[self.ipars] = x_new
        return y, status, logy, qxy

    def get_direction(self, x, U, S):
        """Design the direction in which we move."""
        prob = np.random.rand()
        if prob > self._slice.p1[0]:
            scale = self._slice.p1[1]
        elif prob > self._slice.p2[0]:
            scale = self._slice.p2[1]
        else:
            scale = 1.0

        d = len(x[self.ipars])
        cd = scale * 2.38 / np.sqrt(d)
        dx = np.dot(U, np.random.randn(d) * cd * np.sqrt(S))

        if prob <= self._slice.jump[0]:  # jump in the coordinate direction
            ix = np.random.choice(d)  # choosing the coordinate
            del_x = (
                self._slice.jump[1] * dx[ix]
            )  # choose 3 sigma jump in that coord. dir
            dx = np.zeros(d)
            dx[ix] = del_x

        DX = np.zeros(len(x))
        DX[self.ipars] = dx
        return DX

    def slice(self, x, chain=None):
        """Return actual sample."""
        if not self.ipars:
            return x, 0, None, 0
        x_new, status, logy, qxy = self._slice.slice(x, chain=chain)
        return x_new, status, logy, qxy


class HyperModelWhat(Proposal):
    """A proposal handling hyper models, where one parameter controls
    model selection.

    """

    def __init__(
        self,
        names,
        nindex=0,
        bins=[0, 0.5, 1],
        model_names=[],
        update_step=1000,
        choose_model=np.random.random,
        **kwargs,
    ):
        """Set scaling probability and factor.

        nindex:  index for models jumps (int)
        bins: model selection range, [0, 0.5, 1] gives two models [0-0.5][0.5,1]
        model_names: list of parameter names for each model
        covs:  initial covariance matrix for each model
        update_step: when to update cov
        """
        self.name = "HM"

        assert nindex < len(names) - 1 and nindex >= 0
        self.kk = nindex
        assert bins[0] == 0 and bins[-1] == 1
        assert np.all(bins[:-1] <= bins[1:])  # check sorted
        self.bins = bins
        self.nmodel = len(bins) - 1
        assert len(model_names) == self.nmodel
        self.adapt = update_step
        self.choose_model = choose_model

        # initialize GibbsSCAM fro each model
        self.gibbsc = [Gibbs(names, subset_names=mnames) for mnames in model_names]
        self.cnt = 1
        self.scam_jump = kwargs.get("scam_jump", True)
        self.slice_jump = kwargs.get("slice_jump", True)

    def check_update(self, chain, force=False):
        """Check if update of cov is needed, and do it."""
        if self.cnt % self.adapt == 0 or force:
            for j in range(len(self.gibbsc)):
                if force:
                    self.gibbsc[j].update_cov(chain.chn)
                else:
                    limits = [self.bins[j], self.bins[j + 1]]  # limits of kappa
                    ind_sub = (chain.chn[:, self.kk] > limits[0]) & (
                        chain.chn[:, self.kk] <= limits[1]
                    )
                    if ind_sub.sum() > 100:
                        self.gibbsc[j].update_cov(chain.chn[ind_sub, :])

    def model_selection(self, kappa, jump=True):
        """Random model selection"""
        ## making jump in model: always uniform
        if jump:
            kappa = self.choose_model()

        ### which model?
        # i = int(np.ceil(kappa*self.nmodel)) # model index
        i = np.searchsorted(self.bins, kappa)
        return i - 1, kappa

    def HMJump(self, x, chain=None, **kwargs):
        """Jump from one model to another (uniform).

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        self.cnt += 1
        y = x.copy()
        _, y[self.kk] = self.model_selection(x[self.kk], jump=True)
        return y, 0, None, 0

    def HMSCAM(self, x, chain=None, **kwargs):
        """Return actual sample by jumping in one component direction.

        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        self.cnt += 1
        self.check_update(chain)
        i, kappa = self.model_selection(x[self.kk], jump=self.scam_jump)
        y, stat, logy, qxy = self.gibbsc[i].SCAM(x)
        y[self.kk] = kappa
        return y, stat, None, qxy

    def HMslice(self, x, chain=None, **kwargs):
        """Return actual sample by jumping in one component direction.
        Args:
        x: the current position
        chain: all additional runtime data needed to propose a new point.

        Returns:
        y: the new position
        status: 0 (do MH decision), 1 (accept) or -1 (reject)
        logy: the log-likelihood at y position if already computed.
        qxy: 0 for symmetric proposal distribution
        """
        self.cnt += 1
        self.check_update(chain)
        i, kappa = self.model_selection(x[self.kk], jump=self.slice_jump)
        y = x.copy()
        y[self.kk] = kappa
        y, stat, logy, qxy = self.gibbsc[i].slice(y, chain=chain)
        return y, stat, None, qxy


class CovProposal(Proposal):
    """
    Propose jumps out of the gaussian distibution defined by the
    covariance matrix and mode built from chain.
    Besides the standard arguments of the :attr:`Proposal`: class
    it accepts the following parameters:

    :param int adapt: frequency (in steps) of the covariance update.
    :param np.array ini_mode: initial mode of the proposal distribution.
                              Default: null vector.
    :param np.array ini_cov: initial covariance of the proposal dist.
                             Default: diagonal 0.1 matrix.
    :param bool get_qxy: return the ration of the proposal
                         probabilities. Default: True.

    :return: propsed point, O, None, qxy
    :rtype: list
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cnt = 0
        self.adapt = kwargs.get('adapt', 1000)
        self.dim = len(self.names)

        self.mean = kwargs.get('ini_mode', np.zeros(self.dim))[:self.dim]
        self.cov = np.diag(
            np.ones(self.dim) * kwargs.get('ini_cov', .1)
        )
        self.get_qxy = kwargs.get('get_qxy', True)
        self.lp = gauss_ll(self.mean, self.cov)


    def update_cov(self, chain):
        """
        Update the covariance matrix
        """

        if chain is None:
            return

        ims = chain.get_size()
        if ims > self.adapt:
            self.cov, _, _ =  self.get_cov(chain)
        istart = int(0.75 * len(chain.chn[0:ims, :]))  # skip first 25% of the chain
        # TODO: using the mask is likey not very effcient.
        self.mean = np.mean(chain.chn[istart:ims, self.chn_mask(chain)], axis=0)
        self.lp = gauss_ll(self.mean, self.cov)


    def get_proposal(self, y, chain=None, chains=None):
        """ use update_cov=True in sampler options"""
        self.cnt += 1

        if (self.cnt % self.adapt == 0) or (self.cnt == 1):
            self.update_cov(chain)

        x = np.random.multivariate_normal(
            self.mean,
            self.cov
        )

        _qxy =  self.lp(y) - self.lp(x) if self.get_qxy else 0

        return x, 0, None, _qxy


class ParSplitProposal(Proposal):
    """
    Parameter splitting (and multi trial) proposal.

    :params int ntrials: number of fast trials. Default 1000.

    :param function slowp: proposition for slow pars. Signature
                           slowp(old_slow, chain=None, chains=None)

                           returns: new_point, <ignored>, <ignored>, proposal_prob

                           it will be accessible via the proposal
                           `slow` method call.

    :param function fastp: proposition for fast pars. Signature
                           fastp(old_fast, chain=None, chains=None, **extra)

                           returns: new_point, <ignored>, <ignored>, <ignored>


                           where extra are the parameters returned by the
                           `slow_fun` in ChainMultiTrial.
                           it is wrapped by  the proposal `fast` method
                           to generate `ntrial` fast points.

    :param function fastlq: proposition probability for fast pars. Signature
                           fastlq(old_fast, chain=None, chains=None, **extra)

                           returns the proposal probability (float)

                           where extra are the parameters returned by the
                           `slow_fun` in ChainMultiTrial.
                           it will be accessible via the proposal
                           `lq` method call.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ntrials = kwargs.get('ntrials', 1000)
        self.slow = kwargs['slowp']
        self._fast = kwargs['fastp']
        self.lq = kwargs['fastlq']

    def fast(self, x, chain=None, chains=None, **extra):
        """
        Returns `ntrial` fast points.
        """
        return [self._fast(x, chain=chain, chains=chains, **extra)[0]
                for _ in range(self.ntrials)]
