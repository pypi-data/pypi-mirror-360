""" Additional proposals which could be used for GB search.
"""

import numpy as np
import lisaconstants as constants
import m3c2.proposal as proposal


def harmonic_shift(x, names):
    """Shift freq of +/- N/T"""
    YRSID_SI = constants.SIDEREALYEAR_J2000DAY * 24 * 60 * 60
    df1 = 1.0 / YRSID_SI
    y = np.copy(x)
    d = np.array([n.split(":")[0] for n in names])
    ind = np.where(d == "fr")[0]
    i = np.random.choice(ind)
    fctr = int(4.0 * np.random.normal(0.0, 1.0))
    if fctr == 0:
        fctr = 1
    sgn = 1.0
    if np.random.random() < 0.5:
        sgn = -1.0
    y[i] = x[i] + sgn * fctr * df1
    return y, 0, None


class HarmonicShift(proposal.Proposal):
    """Shift freq of +/- N/T"""

    def __init__(self, names, **kwargs):
        super().__init__(names, **kwargs)
        self.name = "harmonicshift"

    def shift(self, x, chain=None, **kwargs):
        par_dict = dict(zip(self.names, x))
        y, jk, jk = harmonic_shift(x, self.names)
        y = self.sort_by(y)
        return y, 0, None, 0
