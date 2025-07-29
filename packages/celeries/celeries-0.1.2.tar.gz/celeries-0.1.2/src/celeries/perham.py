# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later
import os
from time import sleep

from . import ellipseries as ell
from . import mpfrac as mf
from . import series as se


class _PerHam:
  def __init__(self, degree, km_max, spatial=True):
    self.degree = degree
    self.km_max = km_max
    self.spatial = spatial

    self.alpha = se.Var('alpha')
    self.b = {}  # dict of Laplace coefficients
    self.X = [se.Var(f'X{j + 1:d}') for j in range(2)]
    self.Xb = [se.Var(f'Xb{j + 1:d}') for j in range(2)]
    self.XXb = self.X + self.Xb
    self.Y = [se.Var(f'Y{j + 1:d}') for j in range(2)]
    self.Yb = [se.Var(f'Yb{j + 1:d}') for j in range(2)]
    self.YYb = self.Y + self.Yb
    self.XY = self.X + self.Y + self.Xb + self.Yb
    self.conj_XY = {self.XY[j]: self.XY[j - 4] for j in range(8)}
    self.theta = se.Angle('theta')
    self.sqA = se.Var('sqrt(A)')


class LazyPerHam(_PerHam):
  r"""
  Lazy version (stores the results for re-use) of :class:`PerHam`.

  Parameters
  ----------
  degree : int
    Degree of the development.
  km_max : int
    Maximum value of k2-k1 that will be required
    (for Laplace coefficients recurrence relations).
    Set km_max=-1 to avoid using recurrence relations.
  spatial : bool
    Whether to consider the 3D or the co-planar only case.
  """

  def __init__(self, degree, km_max, spatial=True):
    super().__init__(degree, km_max, spatial)

    self.folder = os.path.expanduser('~/.celeries/perham')
    os.makedirs(self.folder, exist_ok=True)
    self._perham = None

  def _lazy(self, filename, method, *args):
    if os.path.isfile(filename):
      return se.Series.load(filename)
    else:
      lockfile = filename + '.lock'
      try:
        open(lockfile, 'x').close()
        if self._perham is None:
          self._perham = PerHam(self.degree, self.km_max, self.spatial)
        R = getattr(self._perham, method)(*args)
        R.save(filename)
        os.remove(lockfile)
        return R
      except FileExistsError:
        while os.path.isfile(lockfile):
          sleep(1)
        return se.Series.load(filename)

  def direct(self, k):
    r"""
    Direct part of the Hamiltonian with coefficients k for the mean longitudes.

    Parameters
    ----------
    k : list
      Coefficents k1, k2 of the mean longitudes.

    Returns
    -------
    R : Series
      Direct part of the Hamiltonian with coefficients k,
      up to the current degree of development in eccentricity.
    """
    if self.km_max < 0:
      filename = (
        f'{self.folder}/dir_{k[0]:d}:{k[1]:d}_deg{self.degree:d}'
        f'_{3 if self.spatial else 2:d}d_norec.pys'
      )
    else:
      if abs(k[1] - k[0]) > self.km_max:
        raise Exception(
          f'k ({k}) is incompatible with km_max ({self.km_max}).\n'
          f'Please increase km_max to at least {abs(k[1] - k[0])}.'
        )
      filename = (
        self.folder
        + f'/dir_{k[0]:d}:{k[1]:d}_deg{self.degree:d}_{3 if self.spatial else 2:d}d.pys'
      )
    return self._lazy(filename, 'direct', k)

  def indirect(self, k):
    r"""
    Indirect part of the Hamiltonian with coefficients k for the mean longitudes.

    Parameters
    ----------
    k : list
      Coefficents k1, k2 of the mean longitudes.

    Returns
    -------
    R : Series
      Indirect part of the Hamiltonian with coefficients k,
      up to the current degree of development in eccentricity.
    """
    filename = (
      self.folder
      + f'/ind_{k[0]:d}:{k[1]:d}_deg{self.degree:d}_{3 if self.spatial else 2:d}d.pys'
    )
    return self._lazy(filename, 'indirect', k)

  def coorbital_direct(self):
    r"""
    Direct part of the coorbital Hamiltonian
    using the method of Robutel & Pousse (2013).

    Returns
    -------
    R : Series
      Direct part of the coorbital Hamiltonian,
      up to the current degree of development in eccentricity.
    """
    filename = (
      f'{self.folder}/dir_coorb_deg{self.degree:d}_{3 if self.spatial else 2:d}d.pys'
    )
    return self._lazy(filename, 'coorbital_direct')

  def coorbital_indirect(self):
    r"""
    Indirect part of the coorbital Hamiltonian
    using the method of Robutel & Pousse (2013).

    Returns
    -------
    R : Series
      Indirect part of the coorbital Hamiltonian,
      up to the current degree of development in eccentricity.
    """
    filename = (
      f'{self.folder}/ind_coorb_deg{self.degree:d}_{3 if self.spatial else 2:d}d.pys'
    )
    return self._lazy(filename, 'coorbital_indirect')


class PerHam(_PerHam):
  r"""
  Perturbative part of the 3 body Hamiltonian
  using the general method described in Laskar & Robutel (1995)
  and the Robutel & Pousse (2013) method for the coorbital case.

  This implementation was inspired by
  the TRIP macros fperpla.t (J. Laskar) - 15/03/2011.

  Parameters
  ----------
  degree : int
    Degree of the development.
  km_max : int
    Maximum value of k2-k1 that will be required
    (for Laplace coefficients recurrence relations).
    Set km_max=-1 to avoid using recurrence relations.
  spatial : bool
    Whether to consider the 3D or the co-planar only case.
  """

  def __init__(self, degree, km_max, spatial=True):
    super().__init__(degree, km_max, spatial)
    self._init_vars()
    if km_max >= 0:
      self._init_coefLap()
    self._init_cosS()
    self._init_U()
    self._indpart()

  def direct(self, k):
    r"""
    Direct part of the Hamiltonian with coefficients k for the mean longitudes,
    using the method of Laskar & Robutel (1995).

    Parameters
    ----------
    k : list
      Coefficents k1, k2 of the mean longitudes.

    Returns
    -------
    R : Series
      Direct part of the Hamiltonian with coefficients k,
      up to the current degree of development in eccentricity.
    """
    use_laplace_rec = self.km_max >= 0
    charact = k[0] + k[1]
    R = se.Series()
    for j, Uj in enumerate(self._U):
      for key in Uj:
        if key[0] + key[1] == charact:
          klap = abs(k[0] - key[0])
          for deg in Uj[key]:
            if use_laplace_rec:
              R += self._brec[(2 * j + 1, klap)][deg] * Uj[key][deg]
            else:
              R += se.Var(f'b_{2 * j + 1:d}_{klap:d}') * Uj[key][deg]
    if use_laplace_rec:
      return self._simplifyA2(R)
    else:
      return R

  def indirect(self, k):
    r"""
    Indirect part of the Hamiltonian with coefficients k for the mean longitudes,
    using the method of Laskar & Robutel (1995).

    Parameters
    ----------
    k : list
      Coefficents k1, k2 of the mean longitudes.

    Returns
    -------
    R : Series
      Indirect part of the Hamiltonian with coefficients k,
      up to the current degree of development in eccentricity.
    """
    return self._indirect.coefext({self._eil[0]: k[0], self._eil[1]: k[1]})

  def coorbital_direct(self):
    r"""
    Direct part of the coorbital Hamiltonian
    using the method of Robutel & Pousse (2013).

    Returns
    -------
    R : Series
      Direct part of the coorbital Hamiltonian,
      up to the current degree of development in eccentricity.
    """
    se.savetrunc()
    se.settrunc(self.XY, self.degree)
    invA = self.sqA ** (-2)
    R = se.Series()
    tmp = self._aor2 / self.sqA
    for j in range(self.degree + 1):
      if j > 0:
        tmp *= -self._V * invA * (2 * j - 1) / (2 * j)
      for k in range(-self.degree - j, self.degree + j + 1):
        R += tmp.coefext({self._eil[0]: k, self._eil[1]: -k}) * self.theta.expi() ** k
    se.resttrunc()
    return R

  def coorbital_indirect(self):
    r"""
    Indirect part of the coorbital Hamiltonian
    using the method of Robutel & Pousse (2013).

    Returns
    -------
    R : Series
      Indirect part of the coorbital Hamiltonian,
      up to the current degree of development in eccentricity.
    """
    R = se.Series()
    for k in range(-self.degree - 1, self.degree + 2):
      R += (
        self._indirect.coefext({self._eil[0]: k, self._eil[1]: -k})
        * self.theta.expi() ** k
      )
    return R

  # Hidden methods
  def _init_vars(self):
    """Initialisation of intermediate variables and truncation at given degree."""
    self._eil = [se.Var(f'eil{j + 1:d}') for j in range(2)]
    self._eiphi = self._eil[0] / self._eil[1]
    self._eipi = [se.Var(f'eipi{j + 1:d}') for j in range(2)]
    self._eiM = [self._eil[j] / self._eipi[j] for j in range(2)]
    self._eiOm = [se.Var(f'eiOm{j + 1:d}') for j in range(2)]
    self._e = [se.Var(f'e{j + 1:d}') for j in range(2)]
    self._si = [se.Var(f'si{j + 1:d}') for j in range(2)]

    self._chg12_XYl = {}
    self._chg12_XYl[self.X[0]] = self.X[1]
    self._chg12_XYl[self.Xb[0]] = self.Xb[1]
    self._chg12_XYl[self.Y[0]] = self.Y[1]
    self._chg12_XYl[self.Yb[0]] = self.Yb[1]
    self._chg12_XYl[self._eil[0]] = self._eil[1]

    se.savetrunc()
    se.settrunc(self.XY, self.degree)
    self._z = [self.X[j] * (1 - self.X[j] * self.Xb[j] / 4).sqrt() for j in range(2)]
    self._zb = [zj.substvars(self.conj_XY) for zj in self._z]
    self._dze = [
      self.Y[j] * (1 - self.X[j] * self.Xb[j] / 2) ** (mf.Fraction(-1, 2))
      for j in range(2)
    ]
    self._dzeb = [dzej.substvars(self.conj_XY) for dzej in self._dze]
    se.resttrunc()

  def _init_coefLap(self):
    """Compute recurrence relations between Laplace coefficients"""
    kbmax = 1 + int((self.km_max + 3 * self.degree) / 2)
    self._A2 = se.Var('A2')  # 1/(1-alpha**2)
    self._brec = {}
    for s in range(self.degree + 1):
      for kb in range(kbmax + 1):
        self.b[(2 * s + 1, kb)] = se.Var(f'b_{2 * s + 1:d}_{kb:d}')
        self._brec[(2 * s + 1, kb)] = []
    for d in range(self.degree + 1):
      s0 = int((d + 1) / 2)
      self._brec[(2 * s0 + 1, 0)].append(self.b[(2 * s0 + 1, 0)])
      self._brec[(2 * s0 + 1, 1)].append(self.b[(2 * s0 + 1, 1)])
      for s in range(s0, self.degree):
        self._brec[(2 * s + 3, 0)].append(
          self._A2**2 * (1 + self.alpha**2) * self._brec[(2 * s + 1, 0)][d]
          + 2
          * self._A2**2
          * mf.Fraction(2 * s - 1, 2 * s + 1)
          * self.alpha
          * self._brec[(2 * s + 1, 1)][d]
        )
        self._brec[(2 * s + 3, 1)].append(
          self._A2**2
          * mf.Fraction(2 * s - 1, 2 * s + 1)
          * (1 + self.alpha**2)
          * self._brec[(2 * s + 1, 1)][d]
          + 2 * self._A2**2 * self.alpha * self._brec[(2 * s + 1, 0)][d]
        )
      for s in range(s0, 0, -1):
        self._brec[(2 * s - 1, 0)].append(
          (1 + self.alpha**2) * self._brec[(2 * s + 1, 0)][d]
          - 2 * self.alpha * self._brec[(2 * s + 1, 1)][d]
        )
        self._brec[(2 * s - 1, 1)].append(
          mf.Fraction(2 * s - 1, 2 * s - 3)
          * (
            (1 + self.alpha**2) * self._brec[(2 * s + 1, 1)][d]
            - 2 * self.alpha * self._brec[(2 * s + 1, 0)][d]
          )
        )
    for d in range(self.degree + 1):
      for s in range(self.degree + 1):
        for kb in range(kbmax - 1):
          self._brec[(2 * s + 1, kb + 2)].append(
            mf.Fraction(1, 2 * kb + 3 - 2 * s)
            * (
              (2 * kb + 2)
              * (self.alpha + self.alpha**-1)
              * self._brec[(2 * s + 1, kb + 1)][d]
              - (2 * kb + 2 * s + 1) * self._brec[(2 * s + 1, kb)][d]
            )
          )

  def _chgell(self, expr, j=0):
    """Change of coordinates in expr
    from e, si, eipi, eiOm
    to X, Y for planet j.
    """
    aux1 = expr.subst(self._eipi[j], self._z[j] / self._e[j], power=1)
    aux1 = aux1.subst(self._eipi[j], self._zb[j] / self._e[j], power=-1)
    e2 = self._z[j] * self._zb[j]
    aux1 = aux1.subst(self._e[j], e2, power=2, negative=True)
    aux1 = aux1.subst(self._eiOm[j], self._dze[j] / self._si[j], power=1)
    aux1 = aux1.subst(self._eiOm[j], self._dzeb[j] / self._si[j], power=-1)
    si2 = self._dze[j] * self._dzeb[j]
    aux1 = aux1.subst(self._si[j], si2, power=2, negative=True)
    return aux1

  def _simplifyA2(self, expr):
    """Simplify expr to remove any occurrence of A2 = 1/(1-alpha**2)"""
    pmin = min(expr.minpow(self.alpha), 0)
    simp = expr * self.alpha ** (-pmin)
    simp = simp.subst(self.alpha, 1 - 1 / self._A2, 2)
    simp = simp.subst(self._A2, 1 - self.alpha**2, -1)
    simp = simp * self.alpha**pmin
    simp2 = simp.coefext({self._A2: 0})
    if simp2 != simp:
      raise Exception('Error: could not simplify A2 = 1/(1-alpha**2)')
    return simp

  def _init_cosS(self):
    """Development of cos(S) as a power series in X, Y,...
    in the 2d or 3d case depending on spatial.
    Also return the AA and BB series which are useful for the indirect part.
    """
    se.savetrunc()
    se.settrunc(self.XY, self.degree)
    TE1 = ell.eiv(self._e[0], self._eiM[0], self.degree) / self._eiM[0]
    TE1 = self._chgell(TE1)
    TE2 = TE1.substvars(self._chg12_XYl)
    TEb2 = TE2.substvars(self.conj_XY).subst(self._eil[1], 1 / self._eil[1])

    if self.spatial:
      se.savetrunc()
      se.settrunc(self._si, self.degree)
      ci = [(1 - self._si[j] ** 2).sqrt() for j in range(2)]
      self._AA = (
        ci[0] * ci[1] + self._si[0] * self._si[1] * self._eiOm[1] / self._eiOm[0]
      ) ** 2 / 2
      self._BB = (
        ci[1] * self._si[0] / self._eiOm[0] - ci[0] * self._si[1] / self._eiOm[1]
      ) ** 2 / 2
      se.resttrunc()
      self._AA = self._chgell(self._AA)
      self._AA = self._chgell(self._AA, 1)
      self._BB = self._chgell(self._BB)
      self._BB = self._chgell(self._BB, 1)
    else:
      self._AA = mf.Fraction(1, 2)
      self._BB = 0

    a_U = (
      TE1 * TE2 * self._BB * self._eil[0] * self._eil[1]
      + TE1 * TEb2 * self._AA * self._eil[0] / self._eil[1]
    )
    self._cS = a_U + a_U.substvars(self.conj_XY).subst(
      self._eil[0], 1 / self._eil[0]
    ).subst(self._eil[1], 1 / self._eil[1])
    se.resttrunc()

  def _init_U(self):
    """Initialisation of the U_i list sorted by degree in X, Y."""
    se.savetrunc()
    se.settrunc(self.XY, self.degree)
    roa1 = ell.rOa(self._e[0], self._eiM[0], degree=self.degree + 1)
    roa1 = self._chgell(roa1)
    self._aor2 = ell.aOr(self._e[1], self._eiM[1], degree=self.degree + 1)
    self._aor2 = self._chgell(self._aor2, 1)
    rhoOalpha = roa1 * self._aor2
    cphi = (self._eiphi + 1 / self._eiphi) / 2
    self._V = 2 * self.alpha * (cphi - rhoOalpha * self._cS) + self.alpha**2 * (
      rhoOalpha**2 - 1
    )
    U_unsorted = self._aor2 * mf.Fraction(1, 2)
    zero = se.Series()
    self._U = [{}]
    for k2 in range(-self.degree, self.degree + 1):
      tmp = U_unsorted.coefext({self._eil[1]: k2})
      if tmp != zero:
        self._U[0][(0, k2)] = tmp.sortdegree()
    for j in range(1, self.degree + 1):
      U_unsorted = -mf.Fraction(2 * j - 1, 2 * j) * self._V * U_unsorted
      self._U.append({})
      for k1 in range(-self.degree - j, self.degree + j + 1):
        for k2 in range(-self.degree - j, self.degree + j + 1):
          tmp = U_unsorted.coefext({self._eil[0]: k1, self._eil[1]: k2})
          if tmp != zero:
            self._U[-1][(k1, k2)] = tmp.sortdegree()
    se.resttrunc()

  def _indpart(self):
    """Indirect part of the Hamiltonian (using AA, BB from the cosS function).
    Warning: the result should be multiplied by beta*beta'/m0 * n*a*n'*a'
    """
    Z1 = ell.eiv(self._e[0], self._eiM[0], self.degree)
    se.savetrunc()
    se.settrunc(self._e, self.degree)
    Z1 = (Z1 + self._e[0]) * self._eipi[0] / (1 - self._e[0] ** 2).sqrt()
    se.settrunc(self.XY, self.degree)
    Z1 = self._chgell(Z1)
    Z2 = Z1.substvars(self._chg12_XYl)
    Zb2 = Z2.substvars(self.conj_XY).subst(self._eil[1], 1 / self._eil[1])
    V1 = Z1 * Zb2 * self._AA - Z1 * Z2 * self._BB
    self._indirect = V1 + (
      V1.substvars(self.conj_XY)
      .subst(self._eil[0], 1 / self._eil[0])
      .subst(self._eil[1], 1 / self._eil[1])
    )
    se.resttrunc()
