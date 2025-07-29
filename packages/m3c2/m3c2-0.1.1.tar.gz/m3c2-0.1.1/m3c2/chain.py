"""
samplermcmc.chain
"""
import copy
import numpy as np
import multiprocessing.managers
from sklearn.mixture import BayesianGaussianMixture as BGM
import sys
import multiprocessing
import time

from .tools import get_autocorr_len

try:
    from hyperkde import HyperKDE
except ImportError:
    pass

#pylint: disable=invalid-name
#pylint: disable=too-few-public-methods,too-many-instance-attributes
#pylint: disable=too-many-arguments


class ChainData:
    """A container for chain shared data."""

    def __init__(self, beta=1):
        """Define data containers as attributes"""
        self.beta = beta

    def to_dict(self):
        """Return a dict to be shared accros process."""
        d = {}
        for k, v in vars(self).items():
            d[k] = v
        return d


class KDETracker:
    """Monitor KDE evolution to identify a stable and good model."""

    def __init__(self, logger):
        """Create containers"""
        self.kl = []  # used by kde
        self.dKL = 1.0
        self.upkde = True
        self.count_groups = True
        self.count_dict = {}
        self.kde_groups_idx = None
        self.kde_paramlists = None
        self.logger = logger

    def counting(self, kde, ncount):
        """Count group occurence."""
        key = "_".join([".".join(pl) for pl in kde.paramlists])
        if key in [*self.count_dict]:
            self.count_dict[key] += 1
            if self.count_dict[key] == ncount:
                self.count_groups = False
                self.kde_groups_idx = kde.groups_idx
                self.kde_paramlists = kde.paramlists
        else:
            self.count_dict[key] = 1

    def set_kl(self, kde1, kde0):
        """Compute Kullback Leiber divergence between 2 KDE."""
        if self.count_groups:
            self.counting(kde1, 5)
            kl = None
        else:
            kl = kde0.get_KL(kde1) if kde0 is not None else None

        if kl is not None:
            self.kl.append(kl)
            self.logger.info(f"Adding KL={kl}")
        return kl

    def check_stability(self):
        """Check if KDE model is stable by looking at kl evolution."""
        if len(self.kl) <= 5:
            return
        akl = np.array(self.kl)
        dKL = abs(np.mean(np.diff(akl[-5:])))
        mean_kl = np.sqrt(np.mean(akl[-5:] ** 2))
        self.dKL = dKL / mean_kl
        self.logger.info(f"Updating dKL to {self.dKL}")
        self.upkde = self.dKL > 0.05


class Chain:
    """A tempered chain and its associated proposals."""

    def __init__(
        self, dim, beta, dbeta, log_l, log_p, **kwargs
    ):
        """Initialize a chain data container."""

        # self.data = ChainData(beta).to_dict()
        self.dim = dim
        self.maxL = -np.inf
        self.maxP = -np.inf
        self.chn = np.zeros((1, dim)) * np.nan
        self.logL = np.zeros((1)) * np.nan
        self.logP = np.zeros((1)) * np.nan
        self.modes = []
        self.cov = 0
        self.U = 0
        self.S = 0
        self.kde = None
        self.Px = 0
        self.Lx = 0
        self.beta = beta
        self.dbeta1 = dbeta
        self.swap_accepted = 1
        self.swap_proposed = 1

        self.props = {}
        self.anneal = 1
        self.log_l = log_l
        self.log_p = log_p
        self.logger =  kwargs.get('logger', None)
        self.profiling = kwargs.get('profiling', False)
        if self.profiling:
            self.jumps = {}
            self.ar = {}
        self.debug = kwargs.get('debug', False)
        if self.debug:
            self.full_chn = []
            self.full_win = []
            self.full_swap = []
            self.full_temp = []
            self.full_acc = []
            self.full_prop = []
            self.full_proposal = []
            self.time_cov = []
            self.time_nmodes = []
            self.time_proposal = {}
            self.time_iter = []
        self.shared = False
        self.kde_tracker = KDETracker(self.logger)
        self.offset = 0

        self.wrap_mask = kwargs.get('wrap', [])

        choose_proposal = kwargs.get('choose_proposal', None)
        if choose_proposal is None:
            choose_proposal = self._choose_proposal
        self.choose_proposal = lambda: choose_proposal(chain=self)

    @staticmethod
    def wrap(x, wrap_mask):
        """ Wraps periodic parameters """

        for _ind, a, b in wrap_mask:
            x[_ind] = (x[_ind] - a) % (b - a) + a

    def set_run_size(self, niter, nparam):
        """array allocation for a given niter run"""
        self.offset = len(self.logL) - 1
        self.chn = np.vstack([self.chn, np.zeros((niter - 1, nparam)) * np.nan])
        self.logL = np.hstack([self.logL, np.zeros((niter - 1)) * np.nan])
        self.logP = np.hstack([self.logP, np.zeros((niter - 1)) * np.nan])

    def history(self):
        S = dict()
        if self.debug:
            S["full_chn"] = self.full_chn
            S["full_win"] = self.full_win
            S["full_temp"] = self.full_temp
            S["full_swap"] = self.full_swap
            S["full_acc"] = self.full_acc
            S["full_prop"] = self.full_prop
            S["full_proposal"] = self.full_proposal
            S["time_proposal"] = self.time_proposal
            S["time_cov"] = self.time_cov
            S["time_nmodes"] = self.time_nmodes
            S["time_iter"] = self.time_iter
            for k, v in self.props.items():
                S.update(k.__self__.history())
        return S

    def init_cov(self, cov=None):
        """Initialize the covariance matrix and its SVD decomposition."""
        if cov is None:
            cov = np.diag(np.ones(len(self.Mx)) * 0.01**2)
        self.cov = cov
        self.U, self.S, v = np.linalg.svd(cov)

    # def share_data(self, manager):
    #     """Convert data container into a shared container, using
    #     multiprocessing.manager.

    #     """
    #     d = manager.dict()
    #     for k,v in self.data.items():
    #         d[k] = v
    #     self.data = d
    #     self.shared = True

    def set_current(self, y, Ly, Py):
        """Set the current point"""
        self.Mx = y
        self.Lx = Ly
        self.Px = Py

    def add_current(self, i):
        """Add current point Mx to the list of accumulated points."""
        self.chn[i + self.offset, :] = self.Mx
        self.logL[i + self.offset] = self.Lx
        self.logP[i + self.offset] = self.Px

    def add(self, i, p, lik, prior, is_max=False):
        """Add a new point and update Mx, logL, logP, Lx, Px

        if is_max is True, also update maxL and maxP.
        """
        self.chn[i + self.offset, :] = p
        self.Mx = p
        self.logL[i + self.offset] = lik
        self.Lx = lik
        self.logP[i + self.offset] = lik + prior
        self.Px = lik + prior
        if is_max:
            self.maxP = self.Px
            self.maxL = self.Lx

    def add_array(self, p, lik, prior):
        """A a series of point."""
        self.chn = p
        self.logL = lik
        self.logP = lik + prior
        self.Mx = p[-1]
        self.Lx = lik[-1]
        self.Px = lik[-1] + prior[-1]
        imax = np.argmax(lik)
        self.maxP = self.logP[imax]
        self.maxL = self.logL[imax]

    # @property
    # def Mx(self):
    #     """ Current model point.
    #     """
    #     return self.data['Mx']
    # @Mx.setter
    # def Mx(self, value):
    #    self.data['Mx'] = value

    def set_proposals(self, props):
        """Set list of proposal with their associated weights."""
        wtot = np.array(list(props.values())).sum()
        for k, v in props.items():
            props[k] = float(v) / wtot
        self.props = props
        if self.profiling:
            for k, v in self.props.items():
                kk = str(k)  # .__self__.name
                self.jumps[kk] = 0
                self.ar[kk] = 0
                if self.debug:
                    self.time_proposal[kk] = []

    @staticmethod
    def _choose_proposal(chain):
        """Randomly choose a proposal, along given weights."""
        kys = list(chain.props.keys())
        i_p = np.random.choice(len(kys), p=np.array(list(chain.props.values())))
        p = list(chain.props.keys())[i_p]
        if chain.profiling:
            # chain.jumps[p.__chain__.name] += 1
            chain.jumps[str(p)] += 1

        return p

    def get_size(self):
        """Return size of the chain."""
        i = (~np.isnan(self.logL)).sum()
        return i

    def get_sample(self, i):
        """Return sample for a given indice."""
        return self.chn[i, :]

    def get_ratio(self):
        """Return acceptance ratio"""
        return self.swap_accepted / self.swap_proposed

    def swapped(self):
        """Gather chain swap statistics."""
        self.swap_accepted += 1

    def full_step(self, ims, chains=None):
        """Update current point using a proposal."""

        # new point
        prop = self.choose_proposal()
        kprop = str(prop)  # .__self__.name
        t0 = time.time()
        y, status, Ly, qxy = prop(self.Mx, chain=self, chains=chains)
        self.wrap(y, self.wrap_mask)

        tprop = time.time() - t0
        if Ly is None:
            Ly = self.log_l(y)

        # accept or reject
        if status == 1:  # accept in any case (slice like)
            self.add(ims, y, Ly, self.log_p(y), is_max= Ly > self.maxL)
            if self.profiling:
                self.ar[kprop] += 1
        elif status == 0:
            accepted = self.MH_step(ims, y, Ly, qxy)  # accept or not
            if self.profiling and accepted:
                self.ar[kprop] += 1
        elif status == -1:
            self.add_current(ims)
            if self.profiling:  # not really considered (like below threshold)
                self.jumps[kprop] -= 1

        # extra info
        if self.debug:
            self.time_proposal[kprop].append(tprop)
            self.full_proposal.append(kprop)
            if status == 1 or (status == 0 and accepted):
                self.full_chn.append(Ly)
            else:
                self.full_chn.append(np.nan)

        return self.Mx, self.Lx, self.Px

    def MH_step(self, ims, y, Ly, qxy):
        """Performs Metropolis-Hastings selection"""

        if not np.isfinite(Ly):
            self.add_current(ims)
            return
        x = self.Mx
        pi_y = self.log_p(y)
        log_MH = (Ly - self.Lx) * self.beta + qxy + pi_y - self.log_p(x)
        log_alp = np.log(np.random.random())
        if log_MH > log_alp:
            is_max = Ly > self.maxL
            self.add(ims, y, Ly, pi_y, is_max=is_max)
            return True

        self.add_current(ims)
        return False

    def update_cov(self, ims):
        """Update covariance matrix and its SVD decomposition."""
        ims = self.get_size()
        t0 = time.time()
        al = get_autocorr_len(self.chn[0:ims, :], burn=0.25)
        istart = int(0.75 * len(self.chn[0:ims, :]))  # skip first 25% of the chain
        x_tot = np.array(self.chn)[istart : ims : int(al)]
        cov = np.cov(x_tot.T)
        self.cov = cov
        self.U, self.S, v = np.linalg.svd(cov)
        if self.debug:
            self.time_cov.append(time.time() - t0)

    def update_kde(self, ims, burn_frac=0.25, n_samples=5000):
        """Update hyperKDE."""
        # al = get_autocorr_len(self.chn, burn=burn_frac)
        ims = self.get_size()
        chn = self.chn[0:ims, :]
        burn = int(burn_frac * len(chn))
        chains = np.copy(np.array(chn))[burn:]
        down = max(len(chains) // n_samples, 1)
        chains = chains[0:-1:down]
        chains = chains[-n_samples:, :]
        self.logger.info(
            f"Build KDE with {len(chains)} samples, downsampling of {down}"
        )

        names = np.array([f"p{i}" for i in range(len(self.Mx))])
        try:
            kde = HyperKDE(
                list(names),
                chains,
                names,
                0.2,
                n_kde_max=1,
                use_kmeans=False,
                global_bw=True,
                groups_idx=self.kde_tracker.kde_groups_idx,
                paramlists=self.kde_tracker.kde_paramlists,
            )
            new, q = kde.draw_from_random_hyp_kde(chains[:, -1])
            assert np.isnan(new).sum() == 0
        except:
            self.logger.info(f"Can't build KDE on {len(chains)} samples")
            return

        kl = self.kde_tracker.set_kl(kde, self.kde)
        self.kde_tracker.check_stability()
        self.kde = kde
        return kl

    def update_modes(self, ims, tol=0.000001, reg_covar=1e-16):
        """Update modes using BayesianGaussian Mixture.

        ### FIXME: TODO: tolerance and
        ### regularization are hardcoded instead I need to do
        ### re-parametrization to make sure we do not need 1e-16
        ### FIXME: Restrict number of modes to 10
        """
        ims = self.get_size()
        t0 = time.time()
        xs = np.copy(self.chn[0:ims, :])
        SzChn = int(0.75 * np.shape(xs)[0])  ### skip first 25% of the chain
        xs = xs[SzChn::10, :]  ### and we take every 10th

        ### I use BayesianGaussian Mixture and low bound on likelihood
        ### to identify the modes
        n_comp = 1
        gmm = BGM(
            n_components=n_comp, tol=tol, reg_covar=reg_covar, covariance_type="full"
        ).fit(xs)
        ll_c = gmm.lower_bound_
        modes = []
        for ic in range(n_comp):
            modes.append(
                [gmm.means_[ic, :], gmm.covariances_[ic, :, :], gmm.weights_[ic]]
            )

        for n_comp in range(2, 11):
            gmm = BGM(
                n_components=n_comp,
                tol=tol,
                reg_covar=reg_covar,
                covariance_type="full",
            ).fit(xs)
            llmax = gmm.lower_bound_
            gm_max = copy.deepcopy(gmm)
            for ntr in range(5):
                gmm = BGM(
                    n_components=n_comp,
                    tol=tol,
                    reg_covar=reg_covar,
                    covariance_type="full",
                ).fit(xs)
                if gmm.converged_:
                    ll = gmm.lower_bound_
                    if ll > llmax:
                        llmax = ll
                        gm_max = copy.deepcopy(gmm)
            if (llmax - ll_c) / llmax > 0.02:
                modes = []
                for ic in range(n_comp):
                    modes.append(
                        [
                            gm_max.means_[ic, :],
                            gm_max.covariances_[ic, :, :],
                            gm_max.weights_[ic],
                        ]
                    )
                ll_c = llmax
            else:
                break
        self.modes = modes
        if self.debug:
            self.time_nmodes.append(time.time() - t0)

    def print_info(self):
        """Print log-likelihood info."""
        self.logger.info(
            f"current loglik: {self.Lx:.1f}, "
            f"best: {self.maxL:.1f}, "
            f"temp: {1./self.beta:.1f}, "
            f"ratio: {self.get_ratio()}"
        )

    def swap(self, chain):
        pass


class ChainParsSplitting(Chain):
    """
    Chain extension handling multitrial with fast and slow parameters.
    These are the parameters added and the main differencies

    Parameter splitting and multitrial:
    :param int ntrials: max number of fast parameters trials.
    :param int nslow: the first nslow parameters are considered as
                      "slow". This is ignored if the slow_mask/fast_mask
                      arguments are given.
    :param callable slow_mask: mask of the slow parameters.
                               By default the first nslow parameters.
    :param callable fast_mask: mask of the fast parameters.
                               By default the last dim - nslow pars.


    Likelihoods:
    :param callable slow_fun: function accepting the slow parameters as
                              argument and returning a dictionnary of "extra"
                              parameters that will be passed to proposal and
                              to the likelihood functions. This is meant to
                              encode the "slow" part of the computation.
    :param callable fast_log_l: fast log likelihood. Accepts, as argument, the
                                fast parameters and the "extra" named parameters.
                                return the fast part of the log likelihood.
    :param callable slow_log_l: (fast computation of the) slow log likelihood.
                                Accepts, as argument, the
                                wslow parameters and the "extra" named parameters.
                                return the slow part of the log likelihood.
    :param callable log_l: full log likelihood. This is the loglik argument of the
                           Sampler initialization. If None it will be computed as
                           the product of the fast_log_l and slow_log_l functions.
                           It should accept as argument the point and the "extra"
                           parameters. (Note: It will be wrapped so to be possible
                           to call it without the extra parametes.

    Note: if fast_log_l and slow_log_l arguments are not given, the Chain implements
          a standard acceptance with the full likelihood and uses the splitting
          between fast and slow parameters only for the proposals.

    Priors:
    :param callable fast_log_p: prior function for the fast parameters.
    :param callable log_p: prior function for the slow param. This is the 'logpi'
                           argument of the Sampler initialization.

    Covariance:
    :param bool full_cov: if True computes the full parameters covariance.
                          Default False.
    :param bool slow_cov: if True computes the slow parameters covariance.
                          Default True.
    :param bool fast_cov: if true computes the fast parameters covariance.
                          Default False.

    Proposals:
    The main difference with the non-MT chain is that when defining the
    proposals dictionnary, one should specify the proposal object rather than
    the method. The proposal is supposed to have fast, slow and lq methods that
    will be called by the chain. See prposal.MTProposal.
    """

    def __init__(self, *args, **kwargs):
        self.ntrials = kwargs.pop('ntrials')
        self.nslow = kwargs.pop('nslow', None)
        self.slow_mask = kwargs.pop('slow_mask', None)
        self.fast_mask = kwargs.pop('fast_mask', None)
        self.slow_fun = kwargs.pop('slow_fun')
        self.fastll = kwargs.pop('fast_log_l', None)
        self.slowll = kwargs.pop('slow_log_l', None)
        self.fast_log_p = kwargs.pop('fast_log_p')
        self.slow_cov = kwargs.pop('slow_cov', True)
        self.fast_cov = kwargs.pop('fast_cov', False)
        self.full_cov = kwargs.pop('full_cov', False)

        super().__init__(*args, **kwargs)

        if (self.nslow is None) and (self.slow_mask is None):
            raise ValueError("You need to define nslow or slow_mask/fast_mask.")

        if self.slow_mask is None:
            self.slow_mask = list(range(self.nslow))
            self.fast_mask = list(range(self.nslow, self.dim))
            # Slicing is a lot faster. Do this when we can.
            self.split = self._split_slice
            self.join = self._join_slice
        else:
            self.nslow = len(self.slow_mask)
            self.split = self._split_mask
            self.join = self._join_mask


        self.full_step = self._full_step_simple
        if self.fastll is not None:
            self.full_step = self._full_step_multitrial

        self._log_l = self.log_l

        if self._log_l is None:
            self._log_l = self._full_ll

        self.log_l = self._wrap_full_ll

        if self.slow_cov:
            self.cov_slow = None
            self.U_slow = None
            self.S_slow = None

        if self.fast_cov:
            self.cov_fast = None
            self.U_fast = None
            self.S_fast = None

        self.LPy = 1. * np.zeros(self.ntrials)
        self.Wx = 1. * np.zeros(self.ntrials)
        self.Wy = 1. * np.zeros(self.ntrials)

        self.extra = None
        self.slowlp = None
        self.fastlp = None
        self.xfastll = None
        self.xslowll = None
        self.fastlq = None

        self._fast_wrap_mask = [
            _item for _item in self.wrap_mask
            if _item[0] in self.fast_mask
        ]

        self._slow_wrap_mask = [
            _item for _item in self.wrap_mask
            if _item[0] in self.slow_mask
        ]



    def swap(self, chain):
        for _key in ['extra', 'slowlp', 'fastlp', 'xfastll', 'xslowll']:
            _dummy = self.__dict__[_key]
            self.__dict__[_key]  = chain.__dict__[_key]
            chain.__dict__[_key] = _dummy


    def init_cov(self, cov=0):
        """Initialize the covariance matrix and its SVD decomposition."""
        if self.full_cov:
            self.cov, self.U, self.S = self._init_cov(cov, list(range(self.dim)))

        if self.slow_cov:
            self.cov_slow, self.U_slow, self.S_slow = \
                self._init_cov(self.cov, self.slow_mask)

        if self.fast_cov:
            self.cov_fast, self.U_fast, self.S_fast = \
                self._init_cov(self.cov, self.fast_mask)

    def _init_cov(self, cov, mask):
        if cov == 0:
            cov = np.diag(np.ones(len(mask)) * 0.01**2)
        else:
            cov = cov[mask, mask]
        U, S, _ = np.linalg.svd(cov)
        return cov, U, S


    def update_cov(self, ims):
        """Update covariance matrix and its SVD decomposition."""
        ims = self.get_size()
        t0 = time.time()
        al = get_autocorr_len(self.chn[0:ims], burn=0.25)
        istart = int(0.75 * len(self.chn[0:ims]))
        x_tot = np.array(self.chn)[istart : ims : int(al)]

        if self.full_cov:
            self.cov, self.U, self.S = self._update_cov(0, x_tot, list(range(self.dim)))

        if self.slow_cov:
            self.cov_slow, self.U_slow, self.S_slow = \
                self._update_cov(self.cov, x_tot, self.slow_mask)

        if self.fast_cov:
            self.cov_fast, self.U_fast, self.S_fast = \
                self._update_cov(self.cov, x_tot, self.fast_mask)

        if self.debug:
            self.time_cov.append(time.time() - t0)


    def _update_cov(self, cov, x_tot, mask):
        if cov == 0:
            cov = np.cov(x_tot[:, mask].T)
        else:
            cov = cov[mask, mask]

        U, S, _ = np.linalg.svd(cov)
        return cov, U, S

    def history(self):
        S = dict()
        if self.debug:
            S["full_chn"] = self.full_chn
            S["full_win"] = self.full_win
            S["full_temp"] = self.full_temp
            S["full_swap"] = self.full_swap
            S["full_acc"] = self.full_acc
            S["full_prop"] = self.full_prop
            S["full_proposal"] = self.full_proposal
            S["time_proposal"] = self.time_proposal
            S["time_cov"] = self.time_cov
            S["time_nmodes"] = self.time_nmodes
            S["time_iter"] = self.time_iter
            for k, v in self.props.items():
                S.update(k.history())
        return S

    def _split_mask(self, x):
        return (
            [_val for _ind, _val in enumerate(x) if _ind in self.slow_mask],
            [_val for _ind, _val in enumerate(x) if _ind in self.fast_mask]
        )


    def _join_mask(self, xslow, xfast):
        ret = np.zeros(self.dim)
        ret[self.slow_mask] = xslow
        ret[self.fast_mask] = xfast
        return ret.tolist()

    def _split_slice(self, x):
        return x[:self.nslow], x[self.nslow:]


    def _join_slice(self, xslow, xfast):
        return np.concatenate([xslow, xfast])


    def _full_ll(self, xslow, xfast, **extra):

        return self.slowll(xslow, **extra) + \
               self.fastll(xfast, **extra)


    def _wrap_full_ll(self, x, **extra):

        xslow, xfast = self.split(x)

        if len(extra) == 0:
            extra = self.slow_fun(xslow)

        return self._log_l(xslow, xfast, **extra)


    def full_prior(self, x):
        """
        Full log prior function (as sum of the slow
        and fast part)

        :param array x: the point

        :return: the prior at point.
        :rtype: float
        """
        slowx, fastx = self.split(x)

        return self.log_p(slowx) + self.fast_log_p(fastx)


    def _fast_proposal_single(self, prop, xfast, extra):

        yfast = prop.fast(xfast, chain=self, **extra)[0]

        self.wrap(yfast, self._fast_wrap_mask)

        self.LPy[0] = self.fast_log_p(yfast)
        self.Wy[0] = np.exp(
            self.beta * self.fastll(yfast, **extra) + self.LPy[0] - \
            prop.lq(yfast, chain=self, **extra)
        )

        if self.fastlp is None:
            self.fastlp = self.fast_log_p(xfast)

        self.Wx[0] = np.exp(
            self.beta * self.fastll(xfast, **self.extra) + self.fastlp - \
            prop.lq(xfast, chain=self, **self.extra)
        )

        return yfast, 0


    def _fast_proposal_multi(self, prop, xfast, extra):

        yfast = prop.fast(xfast, chain=self, **extra)

        for _ind, _y in enumerate(yfast):

            self.wrap(_y, self._fast_wrap_mask)

            self.LPy[_ind] = self.fast_log_p(_y)
            self.Wy[_ind] = np.nan_to_num(np.exp(
                self.beta * self.fastll(_y, **extra) + self.LPy[_ind] - \
                prop.lq(_y, chain=self, **extra)
            ))
            self.Wx[_ind] = np.nan_to_num(np.exp(
                self.beta * self.fastll(_y, **self.extra) + self.LPy[_ind] - \
                prop.lq(_y, chain=self, **self.extra)
            ))

        _wnorm = np.sum(self.Wy[:prop.ntrials])
        if _wnorm > 0:
            _sel = np.random.choice(prop.ntrials, size=1,
                                    p=self.Wy[:prop.ntrials]/_wnorm)[0]
        else:
            _sel = 0
            
        if self.fastlp is None:
            self.fastlp = self.fast_log_p(xfast)

        self.Wx[_sel] = np.exp(
            self.beta * self.fastll(xfast, **self.extra) + self.fastlp - \
            prop.lq(xfast, chain=self, **self.extra)
        )

        return yfast[_sel], _sel


    def _slow_proposal(self, prop, xslow):

        yslow, _, _, slowlq = prop.slow(xslow, chain=self)

        self.wrap(yslow, self._slow_wrap_mask)

        _extra = self.slow_fun(yslow) # Here should be concentrated the heavy computation

        if self.extra is None:
            self.extra = self.slow_fun(xslow)

        if self.slowlp is None:
            self.slowlp = self.log_p(xslow)

        return yslow, slowlq, _extra


    def add(self, i, p, lik, prior, **kwargs):

        super().add(i, p, lik, prior, kwargs.get('is_max', False))

        self.extra = kwargs.get('extra', None)
        self.xslowll = kwargs.get('xslowll', None)
        self.xfastll = kwargs.get('xfastll', None)

        if self.extra is None:
            slow, fast = self.split(p)
            self.extra = self.slow_fun(slow)
            if self.fastll is not None:
                self.xfastll = self.fastll(fast, **self.extra)
                self.xslowll = self.slowll(slow, **self.extra)
            else:
                self.xfastll = lik
                self.xslowll = lik

        self.fastlp = kwargs.get('fastlp', None)
        self.slowlp = kwargs.get('slowlp', None)
        self.fastlq = kwargs.get('fastlq', None)


    def _full_step_simple(self, ims, chains=None):
        """
        Update the current point. It uses separate proposals for
        slow and fast parameters but it implements a global
        likelihood acceptance in the standard way.
        """
        prop = self.choose_proposal()

        xslow, xfast = self.split(self.Mx)

        if self.extra is None:
            self.extra = self.slow_fun(xslow)

        if self.slowlp is None:
            self.slowlp = self.log_p(xslow)

        if self.fastlq is None:
            self.fastlq = prop.lq(xfast, chain=self, **self.extra)

        yslow, _, _, slowlq = prop.slow(xslow, chain=self)
        if self.wrap_mask is not None:
            self.wrap(yslow, self.wrap_mask[self.slow_mask])
        slowlp = self.log_p(yslow)

        _extra = self.slow_fun(yslow)

        yfast = prop.fast(xfast, chain=self, **_extra)[0]
        if self.wrap_mask is not None:
            self.wrap(yfast, self.wrap_mask[self.fast_mask])

        fastlq = prop.lq(yfast, chain=self, **_extra)

        slowlq += fastlq - self.fastlq
        slowlp += self.fast_log_p(yfast)

        p_next = self.join(yslow, yfast)
        ll_next = self._log_l(yslow, yfast, **_extra)

        log_MH = (ll_next -  self.Lx) * self.beta + \
                 - slowlq + slowlp - self.slowlp

        log_alp = np.log(np.random.random())

        if log_MH > log_alp or ims == 0:
            self.add(
                ims, p_next,
                lik = ll_next,
                prior = slowlp,
                is_max = (ll_next > self.maxL),
                extra = _extra,
                slowlp = slowlp,
                fastlq = fastlq,
                xslowll = ll_next,
                xfastll = ll_next
            )

        else:
            self.add_current(ims)

        return self.Mx, self.Lx, self.Px


    def _full_step_multitrial(self, ims, chains=None):
        """
        Update current point using a proposal jumping once in slow
        parameters and several times in the fast ones.
        """
        prop = self.choose_proposal()

        xslow, xfast = self.split(self.Mx)

        yslow, slowlq, _extra = self._slow_proposal(prop, xslow)

        if prop.ntrials > 1:
            yfast, _sel = self._fast_proposal_multi(prop, xfast, _extra)
        else:
            yfast, _sel = self._fast_proposal_single(prop, xfast, _extra)

        slowlp = self.log_p(yslow)

        p_next = self.join(yslow, yfast)
        ll_next = self._log_l(yslow, yfast, **_extra)

        yslowll = self.slowll(yslow, **_extra)
        if self.xslowll is None:
            self.xslowll = self.slowll(xslow, **self.extra)

        log_MH = np.log(np.sum(self.Wy)/np.sum(self.Wx)) + slowlq + \
                 (yslowll - self.xslowll) * self.beta + \
                 slowlp - self.slowlp

        log_alp = np.log(np.random.random())

        if log_MH > log_alp or ims == 0:
            self.add(
                ims, p_next,
                lik = ll_next,
                prior = slowlp +  self.LPy[_sel],
                is_max = (ll_next > self.maxL),
                extra = _extra,
                xslowll = yslowll,
                xfastll = self.fastll(yfast, **_extra), # TODO: try not to re-compute this
                fastlp = self.LPy[_sel],
                slowlp = slowlp
            )

        else:
            self.add_current(ims)

        return self.Mx, self.Lx, self.Px
