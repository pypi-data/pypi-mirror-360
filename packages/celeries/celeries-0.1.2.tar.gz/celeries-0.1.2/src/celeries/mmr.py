# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later
from dataclasses import dataclass

import numpy as np

from . import laplace, prime
from . import mpfrac as mf
from . import series as se
from .birkhoff import NormalForm
from .perham import LazyPerHam


class MMR:
  r"""
  Model of mean-motion resonances and resonant chains in the planar case.

  The Hamiltonian is computed following Delisle (2017).
  The Hamiltonian variables are v = (y, phi, x, dL), with
  :math:`y_i = \sqrt{2 D_i} \sin(\sigma_i)`,
  :math:`x_i = \sqrt{2 D_i} \cos(\sigma_i)`,
  where :math:`D_i` is the angular momentum deficit (AMD) of planet i.
  phi and dL are the three planet angles and associated actions (:math:`\Delta L`),
  as defined in Delisle (2017).
  The two first integrals are delta and Gamma.
  We consider the renormalized (by Gamma) problem,
  so Gamma = 1 by definition, and delta as well as all other actions
  are normalized by Gamma.

  Parameters
  ----------
  m0 : float
    Mass of the star.
  m : (npla,) ndarray
    Masses of the planets (from the inner to the outer).
  k : (npla-1, 2) ndarray
    Coefficients of the resonances between consecutive planets.
    A chain of 3 planets with a 3/2 resonance between the two inner planet,
    and 4/3 resonance between the two outer ones would have:
    k = np.array([[2,3], [3,4]]).
  degree : int
    Degree of the development in eccentricity.
  G : float
    Gravitational constant.

  Attributes
  ----------
  H : Series
    Hamiltonian.
  grad_H : (4*npla-4,) ndarray
    Array of Series giving the gradient of the Hamiltonian
    with respect to the variables v (y, phi, x, dL).
  J : Series
    Symplectic matrix.
  dv : (4*npla-4,) ndarray
    Array of Series giving the temporal derivatives of the variables v.
  grad_dv : (4*npla-4, 4*npla-4) ndarray
    Matrix of series giving the gradient of dv (aka Jacobian matrix).
  """

  def __init__(self, m0, m, k, degree, G=39.4769264088976328):
    self.G = G
    self.m0 = m0
    self.m = m
    self.k = k.reshape((-1, 2))
    self.degree = degree
    self.mass_ratio = np.sum(self.m) / self.m0
    self.npla = len(self.m)
    self.ndof = 2 * self.npla - 2
    self.ndim = 2 * self.ndof
    assert self.k.shape[0] == self.npla - 1
    self.q = self.k[:, 1] - self.k[:, 0]
    self.km_max = np.max(self.k[:, 0] + self.k[:, 1]) * self.degree
    self.mu = self.G * (self.m0 + self.m)
    self.beta = self.m0 * self.m / (self.m0 + self.m)

    # Change of variables
    self.M = _chg_MMR_2d(self.k, self.degree)
    self.iM = np.linalg.inv(self.M)

    # Rescaling by Gamma
    rP = self.k[:, 1] / self.k[:, 0]
    self.n0 = np.array([1 * rP[j:].prod() for j in range(self.npla)])
    self.La0 = self.beta * self.mu ** (2 / 3) * self.n0 ** (-1 / 3)
    Gamma = self.iM[self.npla :, -1] @ self.La0
    self.La0 /= Gamma
    self.n0 *= Gamma**3
    self.sumLa0 = np.sum(self.La0)

    # Init variables
    self.dL = np.array([se.Var(f'dL_{j}') for j in range(self.npla - 2)])
    self.phi = np.array([se.Angle(f'phi_{j}') for j in range(self.npla - 2)])
    self.sqA = np.array([se.Var(f'sqA(phi)_{j}') for j in range(self.npla - 2)])
    self.x = np.array([se.Var(f'x_{j}') for j in range(self.npla)])
    self.y = np.array([se.Var(f'y_{j}') for j in range(self.npla)])
    self.epsilon = se.Var('epsilon')
    phaseq = se.Var('phaseq')

    # Keplerian part
    dLa = np.array(
      [
        sum(self.M[self.npla : -2, self.npla + i] * self.dL)
        + self.M[-2, self.npla + i] * self.epsilon
        for i in range(self.npla)
      ]
    )
    self.H = -3 / 2 * np.sum(self.n0 / self.La0 * dLa**2)

    # Perturbative part
    ph = LazyPerHam(self.degree, self.km_max, spatial=False)
    self._alpha0_coorbs = np.zeros(
      self.npla - 2
    )  # a1/a2 values for coorbital couples, 0 otherwise
    for j in range(self.npla):
      for l in range(j):
        rap = mf.Fraction(self.k[l:j, 0].prod(), self.k[l:j, 1].prod())
        kl = int(rap.numerator)
        kj = int(rap.denominator)
        qjl = kj - kl
        alpha0 = (self.mu[l] / self.mu[j] * (self.n0[j] / self.n0[l]) ** 2) ** (1 / 3)
        values = {ph.alpha: alpha0}
        CoefDir = (
          -self.m[l] / self.m0 * self.mu[j] ** 2 * self.beta[j] ** 3 / self.La0[j] ** 2
        )
        CoefInd = (
          1
          / self.m0
          * self.mu[l]
          * self.beta[l] ** 2
          / self.La0[l]
          * self.mu[j]
          * self.beta[j] ** 2
          / self.La0[j]
        )
        coefsphi = (kj * self.iM[self.npla + j] - kl * self.iM[self.npla + l])[
          self.npla : -2
        ].round()
        phase = 1
        for p in range(self.npla - 2):
          phase *= self.phi[p].expi() ** int(coefsphi[p])
        if qjl == 0:
          # Coorbitals
          kphi = np.argmax(abs(coefsphi))
          self._alpha0_coorbs[kphi] = alpha0
          Hjl = (
            CoefDir * ph.coorbital_direct() + CoefInd * ph.coorbital_indirect()
          ).evalnum(values)
          Hjl = Hjl.subst(
            ph.XXb[0], np.sqrt(1 / self.La0[l]) * (self.x[l] - mf.i * self.y[l])
          )
          Hjl = Hjl.subst(
            ph.XXb[2], np.sqrt(1 / self.La0[l]) * (self.x[l] + mf.i * self.y[l])
          )
          Hjl = Hjl.subst(
            ph.XXb[1], np.sqrt(1 / self.La0[j]) * (self.x[j] - mf.i * self.y[j])
          )
          Hjl = Hjl.subst(
            ph.XXb[3], np.sqrt(1 / self.La0[j]) * (self.x[j] + mf.i * self.y[j])
          )
          Hjl = Hjl.substvars({ph.theta: self.phi[kphi], ph.sqA: self.sqA[kphi]})
        else:
          # Other resonances
          for s in range((degree - 1) // 2 + 2):
            values[se.Var(f'b_{2 * s + 1:d}_0')] = laplace.b(s + 1 / 2, 0, alpha0)
            values[se.Var(f'b_{2 * s + 1:d}_1')] = laplace.b(s + 1 / 2, 1, alpha0)
          Hjl = se.Series()
          for d in range(-(degree // qjl), degree // qjl + 1):
            Hjl += (
              CoefDir * ph.direct([-d * kl, d * kj])
              + CoefInd * ph.indirect([-d * kl, d * kj])
            ).evalnum(values)
          Hjl = Hjl.subst(
            ph.XXb[0],
            np.sqrt(1 / self.La0[l]) * (self.x[l] - mf.i * self.y[l]) / phaseq,
          )
          Hjl = Hjl.subst(
            ph.XXb[2],
            np.sqrt(1 / self.La0[l]) * (self.x[l] + mf.i * self.y[l]) * phaseq,
          )
          Hjl = Hjl.subst(
            ph.XXb[1],
            np.sqrt(1 / self.La0[j]) * (self.x[j] - mf.i * self.y[j]) / phaseq,
          )
          Hjl = Hjl.subst(
            ph.XXb[3],
            np.sqrt(1 / self.La0[j]) * (self.x[j] + mf.i * self.y[j]) * phaseq,
          )
          Hjl = Hjl.subst(phaseq, phase, qjl, True)
        self.H += Hjl

    # Ordered Hamiltonian variables (positions/angles first)
    self.v = np.concatenate((self.y, self.phi, self.x, self.dL))

    # Gradient of H
    self.grad_H = self.grad(self.H)

    # Symplectic matrix
    self.J = np.zeros((self.ndim, self.ndim), dtype=int)
    self.J[: self.ndof, self.ndof :] = np.identity(self.ndof, dtype=int)
    self.J[self.ndof :, : self.ndof] = -np.identity(self.ndof, dtype=int)

    # Temporal derivatives
    self.dv = self.J @ self.grad_H

    # Jacobian matrix (= J @ Hessian)
    self.grad_dv = np.array([self.grad(dvi) for dvi in self.dv])

    self._W = {}
    self._Wv = {}
    self._dLa = np.array([se.Var(f'dLa_{p}') for p in range(self.npla)])
    self._la = np.array([se.Angle(f'la_{p}') for p in range(self.npla)])
    self._v_nr = np.concatenate((self.y, self._la, self.x, self._dLa))

  def grad(self, f):
    r"""
    Compute the gradient of f with respect to the Hamiltonian variables:
    y, phi, x, dL.

    Parameters
    ----------
    f : Series
      Series for which to compute the gradient.

    Returns
    -------
    grad : (4*npla-4,) ndarray
      Gradient.
    """
    dfdeps = f.deriv(self.epsilon)
    dfdy = [f.deriv(self.y[i]) + dfdeps * self.y[i] for i in range(self.npla)]
    dfdphi = [
      f.deriv(self.phi[i])
      + self._alpha0_coorbs[i] * self.phi[i].sin() / self.sqA[i] * f.deriv(self.sqA[i])
      for i in range(self.npla - 2)
    ]
    dfdx = [f.deriv(self.x[i]) + dfdeps * self.x[i] for i in range(self.npla)]
    dfdL = [f.deriv(self.dL[i]) for i in range(self.npla - 2)]
    return np.array(dfdy + dfdphi + dfdx + dfdL)

  def eval_array(self, a, v, delta):
    r"""
    Evaluate an array (of arbitrary dimension) with the provided values of
    the Hamiltonian variables v (y, phi, x, dL) and delta.

    Parameters
    ----------
    a : ndarray
      Array of Series to be evaluated.
    v : (4*npla-4,) ndarray
      Values of the Hamiltonian variables (y, phi, x, dL).
    delta : float
      Value of delta.

    Returns
    -------
    a_num : ndarray
      Array of values.
    """
    values = {vi: vinum for vi, vinum in zip(self.v, v)}

    y = v[: self.npla]
    x = v[self.ndof : self.ndof + self.npla]
    Dtot = np.sum(x * x + y * y) / 2
    values[self.epsilon] = Dtot - delta

    values.update(
      {
        sqAi: np.sqrt(1 + aci**2 - 2 * aci * np.cos(phii))
        for sqAi, aci, phii in zip(
          self.sqA, self._alpha0_coorbs, v[self.npla : self.ndof]
        )
      }
    )

    a_num = np.array([ak.evalnum(values).toConst().real for ak in a.flat])
    a_num.shape = a.shape

    return a_num

  def eval_dv(self, v, delta):
    r"""
    Evaluate the temporal derivatives dv/dt of
    the Hamiltonian variables v (y, phi, x, dL).

    Parameters
    ----------
    v : (4*npla-4,) ndarray
      Values of the Hamiltonian variables (y, phi, x, dL).
    delta : float
      Value of delta.

    Returns
    -------
    dv_num : (4*npla-4,) ndarray
      Values of the derivatives.
    """
    return self.eval_array(self.dv, v, delta)

  def eval_grad_dv(self, v, delta):
    r"""
    Evaluate the Jacobian matrix
    (matrix of the gradients of the derivatives dv/dt).

    Parameters
    ----------
    v : (4*npla-4,) ndarray
      Values of the Hamiltonian variables (y, phi, x, dL).
    delta : float
      Value of delta.

    Returns
    -------
    Jac_num : (4*npla-4, 4*npla-4) ndarray
      Jacobian matrix (d (dv_i/dt) / d vj).
    """
    return self.eval_array(self.grad_dv, v, delta)

  def solve_fp(self, v0, delta, **kwargs):
    r"""
    Local root-finding of the derivatives (dv/dt) to find
    a fixed point of the averaged problem.

    The root-finding is performed using :func:`newton`
    and try to find a root of :func:`eval_dv`
    while making use of the Jacobian matrix (:func:`eval_grad_dv`).

    Parameters
    ----------
    v0 : (4*npla-4,) ndarray
      Initial values of the Hamiltonian variables (y, phi, x, dL).
    delta : float
      Value of delta.
    **kwargs :
      Optional arguments to pass to :func:`newton`.

    Returns
    -------
    sol : NewtonResult
      The solution represented as a :class:`NewtonResult` object.
    """

    if 'fscale' not in kwargs:
      kwargs['fscale'] = 1 / self.mass_ratio

    return newton(
      self.eval_dv,
      v0,
      jac=self.eval_grad_dv,
      args=(delta,),
      **kwargs,
    )

  def _calc_W(self, km_max):
    ph = LazyPerHam(self.degree, km_max, spatial=False)

    self._W[km_max] = se.Series()

    se.settrunc(self._dLa, 1)
    La = self.La0 + self._dLa
    a = (La / self.beta) ** 2 / self.mu
    n = np.sqrt(self.mu / a**3)

    for j in range(self.npla):
      for l in range(j):
        rap = mf.Fraction(self.k[l:j, 0].prod(), self.k[l:j, 1].prod())
        kl = int(rap.numerator)
        kj = int(rap.denominator)
        alpha0 = (self.mu[l] / self.mu[j] * (self.n0[j] / self.n0[l]) ** 2) ** (1 / 3)
        alpha = a[l] / a[j]
        dalpha = alpha - alpha0
        values = {ph.alpha: alpha}
        for s in range((self.degree) // 2 + 2):
          values[se.Var(f'b_{2 * s + 1:d}_0')] = (
            laplace.b(s + 1 / 2, 0, alpha0)
            + laplace.deriv_b(s + 1 / 2, 0, alpha0) * dalpha
          )
          values[se.Var(f'b_{2 * s + 1:d}_1')] = (
            laplace.b(s + 1 / 2, 1, alpha0)
            + laplace.deriv_b(s + 1 / 2, 1, alpha0) * dalpha
          )
        CoefDir = (
          -self.m[l] / self.m0 * self.mu[j] ** 2 * self.beta[j] ** 3 / La[j] ** 2
        )
        CoefInd = (
          1
          / self.m0
          * self.mu[l]
          * self.beta[l] ** 2
          / La[l]
          * self.mu[j]
          * self.beta[j] ** 2
          / La[j]
        )
        for kjj in range(-km_max, km_max + 1):
          for kll in range(-km_max + abs(kjj), km_max - abs(kjj) + 1):
            if kjj * kl == kll * kj or abs(kjj - kll) > self.degree:
              continue
            Wjl = CoefDir * ph.direct([-kll, kjj]) + CoefInd * ph.indirect([-kll, kjj])
            for vark, valk in values.items():
              Wjl = Wjl.subst(vark, valk)
            Wjl = Wjl.subst(
              ph.XXb[0],
              np.sqrt(1 / La[l]) * (self.x[l] - mf.i * self.y[l]),
            )
            Wjl = Wjl.subst(
              ph.XXb[2],
              np.sqrt(1 / La[l]) * (self.x[l] + mf.i * self.y[l]),
            )
            Wjl = Wjl.subst(
              ph.XXb[1],
              np.sqrt(1 / La[j]) * (self.x[j] - mf.i * self.y[j]),
            )
            Wjl = Wjl.subst(
              ph.XXb[3],
              np.sqrt(1 / La[j]) * (self.x[j] + mf.i * self.y[j]),
            )
            self._W[km_max] += (
              Wjl
              * self._la[j].expi() ** kjj
              * self._la[l].expi() ** (-kll)
              / (mf.i * (kjj * n[j] - kll * n[l]))
            )
    dWdv = np.array([self._W[km_max].deriv(vk) for vk in self._v_nr])
    self._Wv[km_max] = np.concatenate((-dWdv[2 * self.npla :], dWdv[: 2 * self.npla]))

  def ell2v(self, ell, km_max=None):
    r"""
    Convert elliptical coordinates
    to the coordinates of the average problem v = (y, phi, x, dL).

    Parameters
    ----------
    ell : (npla, 4,) ndarray
      Astrocentric coordinates: a (semi-major axis), e (eccentricity),
      :math:`\lambda_0` (mean longitude),
      and :math:`\varpi` (longitude of periastron) of the planets.
    km_max : int or None
      If provided, the change of variables due to averaging
      is peformed, including terms up to km_max.

    Returns
    -------
    v : (4*npla-4,) ndarray
      Normalized coordinates (y, phi, x, dL).
    delta : float
      Value of delta (normalized by Gamma).
    Gamma : float
      Value of Gamma, setting the scale of the system.
    """
    a, e, la0, w = ell.T
    La = self.beta * np.sqrt(self.mu * a)
    Gamma = self.iM[self.npla :, -1] @ La
    La /= Gamma
    G = La * np.sqrt(1 - e**2)
    D = La - G
    dLa = La - self.La0

    if km_max is not None:
      if km_max not in self._Wv:
        self._calc_W(km_max)
      v_nr = np.concatenate(
        (np.sqrt(2 * D) * np.sin(-w), la0, np.sqrt(2 * D) * np.cos(-w), dLa)
      )
      values = {vark: valk for vark, valk in zip(self._v_nr, v_nr)}
      v_nr += np.array([Wvk.evalnum(values).toConst().real for Wvk in self._Wv[km_max]])
      y = v_nr[: self.npla]
      la0 = v_nr[self.npla : 2 * self.npla]
      x = v_nr[2 * self.npla : 3 * self.npla]
      dLa = v_nr[3 * self.npla :]
      w = -np.arctan2(y, x)
      D = (x * x + y * y) / 2

    delta = self.sumLa0 - np.sum(G)
    sig_phi = self.M @ np.concatenate((-w, la0))
    x = np.sqrt(2 * D) * np.cos(sig_phi[: self.npla])
    y = np.sqrt(2 * D) * np.sin(sig_phi[: self.npla])
    dL = self.iM.T[self.npla :, self.npla :] @ dLa
    v = np.concatenate((y, sig_phi[self.npla : -2] % (2 * np.pi), x, dL[:-2]))
    return (v, delta, Gamma)

  def v2ell(self, v, delta, Gamma=1, phiG=0, phiGamma=0, km_max=None):
    r"""
    Convert the coordinates of the average problem v = (y, phi, x, dL)
    to elliptical coordinates.

    Parameters
    ----------
    v : (4*npla-4,) ndarray
      Normalized coordinates (y, phi, x, dL).
    delta : float
      Value of delta (normalized by Gamma).
    Gamma : float
      Value of Gamma, setting the scale of the system.
    phiG, phiGamma : float
      Values of the angles associated to G and Gamma
      (which do not appear in the Hamiltonian).
    km_max : int or None
      If provided, the change of variables due to averaging
      is peformed, including terms up to km_max.

    Returns
    -------
    ell : (npla, 4,) ndarray
      Astrocentric coordinates: a (semi-major axis), e (eccentricity),
      :math:`\lambda_0` (mean longitude),
      and :math:`\varpi` (longitude of periastron) of the planets.
    """

    y = v[: self.npla]
    phi = v[self.npla : self.ndof]
    x = v[self.ndof : self.ndof + self.npla]
    dL = v[self.ndof + self.npla :]

    D = (x * x + y * y) / 2
    Dtot = np.sum(D)
    eps = Dtot - delta
    dLa = self.M.T[self.npla :, self.npla : -1] @ np.concatenate((dL, [eps]))

    sig = np.arctan2(y, x)
    sigphi = np.concatenate((sig, phi, [phiG, phiGamma]))
    mwla0 = self.iM @ sigphi
    w = -mwla0[: self.npla]
    la0 = mwla0[self.npla :]

    if km_max is not None:
      if km_max not in self._Wv:
        self._calc_W(km_max)
      v_nr = np.concatenate(
        (
          np.sqrt(2 * D) * np.sin(-w),
          la0,
          np.sqrt(2 * D) * np.cos(-w),
          dLa,
        )
      )
      values = {vark: valk for vark, valk in zip(self._v_nr, v_nr)}
      dv = np.array([Wvk.evalnum(values).toConst().real for Wvk in self._Wv[km_max]])
      v_nr -= dv
      y = v_nr[: self.npla]
      la0 = v_nr[self.npla : 2 * self.npla]
      x = v_nr[2 * self.npla : 3 * self.npla]
      dLa = v_nr[3 * self.npla :]
      w = -np.arctan2(y, x)
      D = (x * x + y * y) / 2

    La = self.La0 + dLa
    a = (La * Gamma / self.beta) ** 2 / self.mu
    e = np.sqrt(1 - (1 - D / La) ** 2)

    return np.column_stack((a, e, la0 % (2 * np.pi), w % (2 * np.pi)))

  def v2couple(self, v, i, j):
    r"""
    Compute the two resonance angles of a couple of planet from the
    coordinates v = (y, phi, x, dL).

    Parameters
    ----------
    v : (..., 4*npla-4) ndarray
      Normalized coordinates (y, phi, x, dL).

    Returns
    -------
    sigi, sigj : (...) ndarrays
      The two resonance angles.
    """
    rap = mf.Fraction(self.k[i:j, 0].prod(), self.k[i:j, 1].prod())
    ki = int(rap.numerator)
    kj = int(rap.denominator)
    qd = kj - ki
    ci = (
      kj * self.iM[self.npla + j, :]
      - ki * self.iM[self.npla + i, :]
      + qd * self.iM[i, :]
    ).astype(int)
    cj = (
      kj * self.iM[self.npla + j, :]
      - ki * self.iM[self.npla + i, :]
      + qd * self.iM[j, :]
    ).astype(int)
    sig = np.arctan2(v[..., : self.npla], v[..., self.ndof : self.ndof + self.npla])
    phi = v[..., self.npla : self.ndof]

    sigi = np.einsum('i,...i->...', ci[: self.npla], sig) + np.einsum(
      'i,...i->...', ci[self.npla : self.ndof], phi
    )
    sigj = np.einsum('i,...i->...', cj[: self.npla], sig) + np.einsum(
      'i,...i->...', cj[self.npla : self.ndof], phi
    )
    return (sigi, sigj)

  def random_v0(self, delta, nsample=1, factor=1):
    r"""
    Generate random coordinates v0 to use as initial values for
    :func:`solve_fp`.

    Parameters
    ----------
    delta : float
      Value of delta (normalized by Gamma).
    nsample : int
      Number of samples to generate.
    factor : float
      Factor for the scaling of the actions.

    Returns
    -------
    v0 : (4*npla-4,) if nsample=1 or (nsample, 4*npla-4) ndarray
      Random coordinates.
    """
    mins = np.empty(self.ndim)
    maxs = np.empty(self.ndim)

    ax = np.sqrt(factor * (self.mass_ratio + max(0, delta)))
    aL = factor * (self.mass_ratio + np.abs(delta))

    # y
    mins[: self.npla] = -ax
    maxs[: self.npla] = ax
    # phi
    mins[self.npla : self.ndof] = 0
    maxs[self.npla : self.ndof] = 2 * np.pi
    # x
    mins[self.ndof : self.ndof + self.npla] = -ax
    maxs[self.ndof : self.ndof + self.npla] = ax
    # dL
    mins[self.ndof + self.npla :] = -aL
    maxs[self.ndof + self.npla :] = aL

    return np.random.uniform(mins, maxs, None if nsample == 1 else (nsample, self.ndim))

  def merge_fp(
    self,
    sols_fp,
    min_rep_merge=1,
    max_dist_merge=1e-5,
    max_dist_link=np.inf,
    max_age_link=1,
    min_len_keep=1,
  ):
    r"""
    Merge and link the fixed points found by :func:`solve_fp`
    after several tries for a grid of values of delta.

    This method allows to clean out the results of calling many times
    :func:`solve_fp` with different initialization (v0)
    to try and find all the fixed points.

    Parameters
    ----------
    sols_fp : (ndelta, ntry) ndarray
      Matrix of ``OptimizeResult`` object as provided by :func:`solve_fp`
      for ndelta values of delta, and ntry calls per value of delta.
    min_rep_merge : int
      Minimum number of repetition of a fixed point,
      for a given value of delta to consider it as valid.
      By default min_rep_merge=1 means that all fixed points are kept.
    max_dist_merge : float
      Maximum distance to consider two solutions as the same fixed point
      for a given value of delta.
    max_dist_link : float
      Maximum distance to consider that two fixed points
      at two different values of delta belong to the same family.
    max_age_link : int
      Maximum age (it terms of delta index) at which to try to link fixed points
      (to be considered as the same family).
      By default max_age_link=1 means that we only try to link with fixed points
      from the previous value of delta (do not allow gaps).
    min_len_keep : int
      Minimum length (in terms of delta index)
      to consider a family of fixed points as valid.
      By default min_len_keep=1 means that all families are kept.

    Returns
    -------
    vs : (ndelta, nfamily, 4*npla-4) ndarray
      Array of the merged and linked (by family) fixed points.
    """
    raw_vs = [[skl.x for skl in sk if skl.success] for sk in sols_fp]
    scaled_vs = []
    refs = []
    refages = []

    for k, vk in enumerate(raw_vs):
      svk = np.array(
        [
          np.concatenate(
            (
              vkl[: self.npla] / np.sqrt(self.mass_ratio),
              np.exp(1j * vkl[self.npla : self.ndof]),
              vkl[self.ndof : self.ndof + self.npla] / np.sqrt(self.mass_ratio),
              vkl[self.ndof + self.npla :] / self.mass_ratio,
            )
          )
          for vkl in vk
        ]
      )
      mvk = _merge_points(svk, min_rep_merge, max_dist_merge)
      scaled_vs.append(_link_points(mvk, refs, refages, max_dist_link, max_age_link))
      _clean_points(
        scaled_vs,
        refs,
        refages,
        len(raw_vs) - k - 1,
        max_age_link,
        min_len_keep,
      )
    nv = len(scaled_vs[-1])
    for j in range(len(scaled_vs)):
      scaled_vs[j] += [np.full(self.ndim, np.nan)] * (nv - len(scaled_vs[j]))
    vs = np.array(scaled_vs)
    vs[:, :, : self.npla] *= np.sqrt(self.mass_ratio)
    vs[:, :, self.npla : self.ndof] = np.angle(vs[:, :, self.npla : self.ndof])
    vs[:, :, self.ndof : self.ndof + self.npla] *= np.sqrt(self.mass_ratio)
    vs[:, :, self.ndof + self.npla :] *= self.mass_ratio

    return vs.real

  def fp_modes(self, v_fp, delta):
    r"""
    Compute the eigenvalues and eigenmodes around a fixed point.

    This method allows to perform a symplectic change of coordinates
    from the variables v = (y, phi, x, dL)
    to new variables :math:`\mathbf{u} = (u, \tilde{u})`:
    :math:`v = Q \mathbf{u}`.

    The eigenmodes are provided with all "angles" :math:`u` first
    and then all associated "actions" :math:`\tilde{u}`.
    The eigenvalues (and corresponding eigenmodes) are sorted from the larger to the
    smaller absolute value.
    For elliptical fixed points, the change of variables is such that:
    :math:`\tilde{u} = -i \bar{u}`.
    The frequency (imaginary part of the eignevalue) corresponding to :math:`u_i`
    can be positive or negative depending on the fixed point being a local
    minimum or maximum of the Hamiltonian
    in the direction of the corresponding eigenmode.

    Parameters
    ----------
    v_fp : (4*npla-4,) ndarray
      Coordinates of the fixed point.
    delta : float
      Value of delta (normalized by Gamma).

    Returns
    -------
    eig_val : (4*npla-4,) ndarray
      Eigenvalues.
    eig_vec : (4*npla-4, 4*npla-4) ndarray
      Matrix Q of the symplectic change of variables.
    """
    Jac = self.eval_grad_dv(v_fp, delta)
    eig_val, eig_vec = np.linalg.eig(Jac)

    # Sort all negative then all positive in decreasing absolute values
    ksort = np.argsort(eig_val.real + eig_val.imag)
    ksort = np.concatenate((ksort[: self.ndof], ksort[self.ndof :][::-1]))
    eig_val, eig_vec = eig_val[ksort], eig_vec[:, ksort]

    # Make sure to have a symplectic change of variable
    # with u, -i conj(u) for imaginary eigen values
    eig_vec[:, np.abs(eig_val.imag) > np.abs(eig_val.real)] *= np.sqrt(1j)
    norm = np.diag(eig_vec.T[: self.ndof] @ self.J @ eig_vec[:, self.ndof :]).real
    fact = np.sqrt(np.abs(norm))
    eig_vec[:, : self.ndof] /= fact
    eig_vec[:, self.ndof :] /= fact
    ksort = np.arange(self.ndof)
    ksort[norm < 0] += self.ndof
    ksort = np.concatenate((ksort, (ksort + self.ndof) % self.ndim))

    return (eig_val[ksort], eig_vec[:, ksort])

  def fp_normalform(self, v_fp, delta, order, resonances=None, clean_epsilon=None):
    r"""
    Compute the Birkhoff normal form (:class:`birkhoff.NormalForm`)
    around a fixed point.

    Parameters
    ----------
    v_fp : (4*npla-4,) ndarray
      Coordinates of the fixed point.
    delta : float
      Value of delta (normalized by Gamma).
    order : int
      Order of the expansion of the normal form (see :class:`birkhoff.NormalForm`).
    resonances : (nr, ndof) ndarray or None
      Resonances to keep in the normal form (as well as any combination).
    clean_epsilon : float or None
      Threshold to delete small coefficients from the Hamiltonian (if provided),
      before computing the normal form.

    Returns
    -------
    nf : NormalForm
      Normal form of the Hamiltonian around the fixed point.
    eig_val : (4*npla-4,) ndarray
      Eigenvalues of the quadratic part.
    eig_vec : (4*npla-4, 4*npla-4) ndarray
      Matrix Q of the symplectic change of variables
      applied before computing the normal form.
    """
    eig_val, eig_vec = self.fp_modes(v_fp, delta)
    u = [se.Var(f'u_{k}') for k in range(self.ndof)]
    ut = [se.Var(f'ũ_{k}') for k in range(self.ndof)]
    uut = np.concatenate((u, ut))

    se.savetrunc()
    se.settrunc(uut, order)
    v = v_fp + eig_vec @ uut
    Dtot = np.sum(v[: self.npla] ** 2 + v[self.ndof : self.ndof + self.npla] ** 2) / 2
    epsilon = Dtot - delta

    H_fp = self.H.subst(self.epsilon, epsilon)
    for vark, valk in zip(self.v, v):
      H_fp = H_fp.subst(vark, valk)
      if isinstance(vark, se.Angle):
        H_fp = H_fp.subst(vark.expi(), (mf.i * valk).exp())

    if clean_epsilon:
      H_fp = H_fp.clean(clean_epsilon)

    se.resttrunc()
    nf = NormalForm(H_fp, uut, order, resonances)
    return nf, eig_val, eig_vec

  def laplace_latex_label(self, i):
    r"""
    Latex string of the definition of the i-th Laplace angle (phi_i).

    Parameters
    ----------
    i : int
      Index of the Laplace angle (phi_i).

    Returns
    -------
    latex_label : str
      Definition of the angle as a function of mean longitudes (lambda),
      in latex format.
    """
    label = ''
    for p in range(self.npla):
      if self.M[self.npla + i, self.npla + p] != 0:
        if self.M[self.npla + i, self.npla + p] < 0:
          label += '-'
        elif label != '':
          label += '+'
        if abs(self.M[self.npla + i, self.npla + p]) != 1:
          frac = mf.Fraction(
            abs(self.M[self.npla + i, self.npla + p])
          ).limit_denominator(40)
          num = frac.numerator
          den = frac.denominator
          label += f'{num:d}'
          if den != 1:
            label += f'/{den:d}'
        label += f'\\lambda_{{{p + 1}}}'
    return label

  def couple_latex_labels(self, i, j):
    r"""
    Latex string of the definition of the two resonance angles
    sigi, sigj, for the couple of planets i, j
    (as computed by :func:`v2couple`).

    Parameters
    ----------
    i, j : int
      Indices of the planets.

    Returns
    -------
    labeli, labelj : str
      Definitions of the two angles, in latex format.
    """
    rap = mf.Fraction(self.k[i:j, 0].prod(), self.k[i:j, 1].prod())
    ki = int(rap.numerator)
    kj = int(rap.denominator)
    qd = kj - ki
    label = ''
    if kj != 1:
      label += str(kj)
    label += f'\\lambda_{{{j + 1:d}}} - '
    if ki != 1:
      label += str(ki)
    label += f'\\lambda_{{{i + 1:d}}}'
    if qd > 0:
      label += '-'
      if qd != 1:
        label += str(qd)
      labeli = label + f'\\varpi_{{{i + 1:d}}}'
      labelj = label + f'\\varpi_{{{j + 1:d}}}'
    return (labeli, labelj)


def _chg_MMR_2d(k, degree):
  q = k[:, 1] - k[:, 0]
  npla = q.size + 1
  ref = -1
  while q[ref] < 1:
    ref -= 1
  M = np.zeros((2 * npla, 2 * npla))
  for i in range(npla):
    M[i, i] = 1
    M[i, ref - 1] = -k[ref, 0] / q[ref]
    M[i, ref] = k[ref, 1] / q[ref]
    if i < npla - 2:
      j = i if i < npla + ref - 1 else i + 1
      if q[j] == 0:
        M[npla + i, npla + j] = 1
        M[npla + i, npla + j + 1] = -1
      elif q[j + 1] == 0:
        ci = _calc_ci(k, q, j, degree, npla)
        M[npla + i, npla + j] = k[j, 0] / q[j] / ci
        M[npla + i, npla + j + 1] = -(k[j, 1] / q[j] + k[j + 2, 0] / q[j + 2]) / ci
        M[npla + i, npla + j + 3] = k[j + 2, 1] / q[j + 2] / ci
      else:
        ci = _calc_ci(k, q, j, degree, npla)
        M[npla + i, npla + j] = k[j, 0] / q[j] / ci
        M[npla + i, npla + j + 1] = -(k[j, 1] / q[j] + k[j + 1, 0] / q[j + 1]) / ci
        M[npla + i, npla + j + 2] = k[j + 1, 1] / q[j + 1] / ci
  M[-2, ref - 1] = -k[ref, 0] / q[ref]
  M[-2, ref] = k[ref, 1] / q[ref]
  M[-1, ref - 1] = 1
  M[-1, ref] = -1
  return M


def _calc_lij(k, q, i, j):
  if i < j:
    return 0
  lij = mf.Fraction(q[j], 1)
  for l in range(j, i):
    lij = lij * k[l + 1, 1] / k[l, 0] + q[l + 1]
  return lij / k[i, 0]


def _calc_ci(k, q, i, degree, npla):
  nums = []
  denoms = []
  for p1 in range(i + 1):
    for p2 in range(p1 + 1, npla + 1):
      rP = mf.Fraction(np.prod(k[p1:p2, 1]), np.prod(k[p1:p2, 0]))
      k1 = rP.denominator
      k2 = rP.numerator
      if k2 - k1 <= degree:
        coefi = abs(k2 * _calc_lij(k, q, i, p2) - k1 * _calc_lij(k, q, i, p1))
        nums.append(coefi.numerator)
        denoms.append(coefi.denominator)
  return prime.lcm(denoms) / prime.gcd(nums)


def _merge_points(xs, min_rep, max_dist):
  if xs.shape[0] == 0:
    return xs
  mxs = [xs[0]]
  nxs = [1]
  for x in xs[1:]:
    dists = np.array([np.sqrt(np.mean(np.abs(x - mx) ** 2)) for mx in mxs])
    imin = np.argmin(dists)
    if dists[imin] < max_dist:
      mxs[imin] = mxs[imin] * nxs[imin] + x
      nxs[imin] += 1
      mxs[imin] /= nxs[imin]
    else:
      mxs.append(x)
      nxs.append(1)
  mxs = [mv for mv, nv in zip(mxs, nxs) if nv >= min_rep]
  return np.array(mxs)


def _link_points(xs, refs, refages, max_dist, max_age):
  nref = len(refs)
  nx = len(xs)

  # compute all dists
  dists = []
  krs = []
  kxs = []
  for kr in range(nref):
    if refages[kr] > max_age:
      continue
    r = refs[kr]
    for kx, x in enumerate(xs):
      krs.append(kr)
      kxs.append(kx)
      dists.append(np.sqrt(np.mean(np.abs(r - x) ** 2)))

  # Find best couple iteratively
  newlist = [] if nref == 0 else [np.full(refs[0].shape, np.nan)] * nref
  remaininds = [j for j in range(nx)]
  while len(dists) > 0:
    kmin = np.argmin(dists)
    if dists[kmin] >= max_dist:
      break
    kr = krs[kmin]
    kx = kxs[kmin]
    newlist[kr] = xs[kx]
    refs[kr] = xs[kx]
    refages[kr] = 1
    remaininds.remove(kx)
    while kr in krs:
      krem = krs.index(kr)
      del krs[krem]
      del kxs[krem]
      del dists[krem]
    while kx in kxs:
      krem = kxs.index(kx)
      del krs[krem]
      del kxs[krem]
      del dists[krem]

  # New points
  for j in remaininds:
    newlist.append(xs[j])
    refs.append(xs[j])
    refages.append(1)

  # Dead old points
  for kr in range(nref):
    if np.any(np.isnan(newlist[kr])):
      refages[kr] += 1

  return newlist


def _clean_points(xs, refs, refages, remaining, max_age, min_len):
  nref = len(refs)
  for k in range(nref - 1, -1, -1):
    count = 0
    for x in xs:
      if len(x) > k and np.isfinite(x[k][0]):
        count += 1
        if count >= min_len:
          break
    if (count < min_len and refages[k] > max_age) or count + remaining < min_len:
      refs.pop(k)
      refages.pop(k)
      for x in xs:
        if len(x) > k:
          x.pop(k)


@dataclass
class NewtonResult:
  r"""
  Result of a root-finding using :func:`newton`.

  Attributes
  ----------
  x : (ndim,) ndarray
    Values of the parameters.
  success : bool
    Whether the algorithm converged.
  niter : int
    Number of Newton steps.
  message : str
    Additional information on the convergence.
  """

  x: np.ndarray
  success: bool
  niter: int
  message: str


def newton(
  f, x0, jac, max_iter=100, xtol=1e-15, ftol=1e-15, xscale=1, fscale=1, args=()
):
  r"""
  Root-finding using a simple Newton method.

  Parameters
  ----------
  f : function
    Function for which we search for the roots.
  x0 : (ndim,) ndarray
    Initial guess of the parameters.
  jac : function
    Jacobian matrix :math:`J_{i,j} = \partial f_i / \partial x_j`.
  max_iter : int
    Maximum number of Newton steps.
  xtol : float
    Precision on x to consider x-type convergence.
  ftol : float
    Precision on f to consider f-type convergence.
  xscale : (ndim,) ndarray or float
    Scaling of the parameters (for x-type convergence).
    The criterion is :math:`\forall i\ |\delta x_i * \mathrm{xscale}_i| < \mathrm{xtol}`.
  fscale : (ndim,) ndarray or float
    Scaling of the functions (for f-type convergence).
    The criterion is :math:`\forall i\ |\delta f_i * \mathrm{fscale}_i| < \mathrm{ftol}`.
  args : tuple
    Additional arguments to pass to f and jac (should be the same).

  Returns
  -------
  sol : NewtonResult
    The solution represented as a :class:`NewtonResult` object.
  """

  x = x0.copy()
  success = False
  message = 'Did not converge.'
  for kit in range(max_iter):
    fx = f(x, *args)
    if np.all(np.abs(fx * fscale) < ftol):
      success = True
      message = 'f-type convergence.'
      break

    Jx = jac(x, *args)
    dx = np.linalg.solve(Jx, fx)
    x -= dx
    if np.all(np.abs(dx * xscale) < xtol):
      success = True
      message = 'x-type convergence.'
      break
  return NewtonResult(x=x, success=success, niter=kit, message=message)


def continuous_angle(theta, center=0):
  r"""
  Ensure continuity of a series of values of an angle.

  Parameters
  ----------
  theta : (n,) ndarray
    Angle series (rad).
  center : float
    Value around which to start.
    By default a value of 0 means that the angle will start in the range [-pi, pi].

  Returns
  -------
  ctheta : (n,) ndarray
    Continuous series of the angle.
  """
  n = len(theta)
  ref = 0
  while ref < n and np.isnan(theta[ref]):
    ref += 1
  ctheta = theta.copy()
  if ref == n:
    return ctheta
  ctheta[ref] = (theta[ref] - center + np.pi) % (2 * np.pi) + center - np.pi
  j = ref + 1
  while j < n:
    if not np.isnan(theta[j]):
      ctheta[j] = (theta[j] - ctheta[ref] + np.pi) % (2 * np.pi) + ctheta[ref] - np.pi
      ref = j
    j += 1
  return ctheta
