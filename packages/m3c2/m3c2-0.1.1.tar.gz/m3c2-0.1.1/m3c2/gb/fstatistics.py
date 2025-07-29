import numpy as np

def XYZ2AET(X, Y, Z):
    A,E,T = ((Z - X)/np.sqrt(2.0),
            (X - 2.0*Y + Z)/np.sqrt(6.0),
            (X + Y + Z)/np.sqrt(3.0))
    if hasattr(X, "attrs"):
        A.attrs = X.attrs
    return A,E,T

class Fstat:
    def __init__(self, data, GB, noise):
        """Init a Fstat container with fastGB approximation, noise and TDI
        data.
        """
        self.data = data
        self.GB = GB
        self.fdot = 1e-17
        self.amp = 1.0e-21
        self.df = 1 / GB.T
        self.noise = noise

    def f_stats(self, X1, X2, fr_i, E1=None, E2=None):
        """Compute F-statistics for a pair of TDI vectors."""
        kmin = X1.attrs["kmin"]
        X1 = X1.values
        X2 = X2.values

        if E1 is None:
            U = np.sum(np.abs(X1[:]) ** 2)
            V = np.sum(np.abs(X2[:]) ** 2)
            W = np.sum(X1[:] * np.conjugate(X2[:]))
            SX = self.noise.psd(freq=np.array([fr_i]), option="X")[0]

            Xt = self.data.X.values[kmin : kmin + len(X1)]
            Nu = np.sum(Xt * np.conj(X1[:]))
            Nv = np.sum(Xt * np.conj(X2[:]))
        else:
            U = np.sum(np.abs(X1[:]) ** 2 + np.abs(E1[:]) ** 2)
            V = np.sum(np.abs(X2[:]) ** 2 + np.abs(E2[:]) ** 2)
            W = np.sum(X1[:] * np.conjugate(X2[:]) + E1[:] * np.conjugate(E2[:]))
            SX = self.noise.psd(freq=np.array([fr_i]), option="A")[0]

            At = self.data.A.values[kmin : kmin + len(X1)]
            Et = self.data.E.values[kmin : kmin + len(X1)]
            Nu = np.sum(At * np.conj(X1[:]) + Et * np.conj(E1[:]))
            Nv = np.sum(At * np.conj(X2[:]) + Et * np.conj(E2[:]))

        De = U * V - np.absolute(W) ** 2
        Fstat = (
            V * np.absolute(Nu) ** 2
            + U * np.absolute(Nv) ** 2
            - 2.0 * np.real(W * Nu * np.conjugate(Nv))
        )
        Fstat /= De * SX
        Fstat *= 2 * self.df
        a1c = (V * Nu - np.conj(W) * Nv) / De
        a2c = (U * Nv - W * Nu) / De
        return Fstat, a1c, a2c

    def get_coeff(self, fr_i, bet_i, lam_i, option="X"):
        """ """
        X1, Y1, Z1 = self.GB.get_fd_tdixyz(
            f0=fr_i,
            fdot=self.fdot,
            ampl=self.amp,
            theta=0.5 * np.pi - bet_i,
            phi=lam_i,
            incl=0.5 * np.pi,
            psi=0,
            phi0=0,
        )
        X2, Y2, Z2 = self.GB.get_fd_tdixyz(
            f0=fr_i,
            fdot=self.fdot,
            ampl=self.amp,
            theta=0.5 * np.pi - bet_i,
            phi=lam_i,
            incl=0.5 * np.pi,
            psi=0.25 * np.pi,
            phi0=0,
        )
        if option == "X":
            Fstat, a1c, a2c = self.f_stats(X1, X2, fr_i)
        else:
            A1, E1, T1 = XYZ2AET(X1, Y1, Z1)
            A1.attrs = X1.attrs
            A2, E2, T2 = XYZ2AET(X2, Y2, Z2)
            Fstat, a1c, a2c = self.f_stats(A1, A2, fr_i, E1=E1, E2=E2)

        ### reconstruct the signal
        a1 = np.real(a1c)
        a3 = np.imag(a1c)
        a2 = np.real(a2c)
        a4 = np.imag(a2c)
        return Fstat, a1, a2, a3, a4

    def compute(self, fr_i, bet_i, lam_i, option="X"):
        """Compute F-statistics for a given freq and sky position."""
        lAmp = np.log10(self.amp)
        Fstat, a1, a2, a3, a4 = self.get_coeff(fr_i, bet_i, lam_i, option=option)
        A = a1**2 + a2**2 + a3**2 + a4**2
        D = a1 * a4 - a2 * a3
        Ap = 0.5 * (np.sqrt(A + 2.0 * D) + np.sqrt(A - 2.0 * D))
        Ac = 0.5 * (np.sqrt(A - 2.0 * D) - np.sqrt(A + 2.0 * D))
        Amp = 0.5 * (Ap + np.sqrt(Ap * Ap - Ac * Ac))
        cos_i = 0.5 * Ac / Amp
        phi0 = 0.5 * np.arctan2(
            2.0 * (a1 * a3 + a2 * a4), (a1 * a1 + a2 * a2 - a3 * a3 - a4 * a4)
        )
        psi = 0.25 * np.arctan2(
            2.0 * (a1 * a2 + a3 * a4), (a1 * a1 + a3 * a3 - a2 * a2 - a4 * a4)
        )
        phi0 = np.pi - phi0
        psi = psi + np.pi
        l_Amp = np.log10(Amp) + lAmp
        return (
            np.float(Fstat),
            l_Amp,
            fr_i,
            np.log10(self.fdot),
            np.sin(bet_i),
            lam_i,
            cos_i,
            psi,
            phi0,
        )

    def check_coeff(self, Ap, Ac, phi_, psi_):
        """Compute coeff for a given phi, psi variation."""
        a1_ = Ap * np.cos(phi_) * np.cos(2 * psi_) + Ac * np.sin(phi_) * np.sin(
            2.0 * psi_
        )
        a2_ = Ap * np.sin(2.0 * psi_) * np.cos(phi_) - Ac * np.cos(2.0 * psi_) * np.sin(
            phi_
        )
        a3_ = -Ap * np.cos(2 * psi_) * np.sin(phi_) + Ac * np.sin(2.0 * psi_) * np.cos(
            phi_
        )
        a4_ = -Ap * np.sin(phi_) * np.sin(2 * psi_) - Ac * np.cos(phi_) * np.cos(
            2.0 * psi_
        )
        coeff = np.array([float(a1_), float(a2_), float(a3_), float(a4_)])
        return coeff

    def fixangle(self, fr_i, bet_i, lam_i, phi0, psi, option="X"):
        """Get angle which gives correct a1,a2,a3,a4.

        Avoid extra degeneracies.
        """
        lAmp = np.log10(self.amp)
        Fstat, a1, a2, a3, a4 = self.get_coeff(fr_i, bet_i, lam_i, option=option)
        C0 = np.array([float(a1), float(a2), float(a3), float(a4)])

        A = a1**2 + a2**2 + a3**2 + a4**2
        D = a1 * a4 - a2 * a3
        Ap = 0.5 * (np.sqrt(A + 2.0 * D) + np.sqrt(A - 2.0 * D))
        Ac = 0.5 * (np.sqrt(A - 2.0 * D) - np.sqrt(A + 2.0 * D))
        C1 = self.check_coeff(Ap, Ac, phi0, psi)
        C2 = self.check_coeff(Ap, Ac, phi0, psi + np.pi / 2)

        if np.sum(np.isclose(C1, C0, atol=2e-2)) == 4:
            return phi0, psi
        elif np.sum(np.isclose(C2, C0, atol=2e-2)) == 4:
            return phi0, psi + np.pi / 2
        else:
            print(
                f"Warning: inconsistent phi0, psi {C0}, {C1}, {C2}"
            )  # one of the 2 above has to be True
            return phi0, psi
