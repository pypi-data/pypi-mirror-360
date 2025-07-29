import numpy as np

from . import series as se


class NormalForm:
  r"""
  Birkhoff normal form of an Hamiltonian.

  The Hamiltonian H should already be centered around an elliptical fixed point,
  and its quadratic part diagonalized:
  :math:`H = constant + i \sum_k \nu_k x_k \tilde{x}_k +  O(x^3)`.

  The change of variables is expressed as the flow at time 1
  of an auxiliary Hamiltonian W:
  :math:`\bar{H} = \exp(L_W) H`,
  where :math:`L_W = \{W, f\}` is the Lie derivative.

  Parameters
  ----------
  H : Series
    Hamiltonian as of function of x.
  x : (2*ndof,) ndarray
    Set of canonically conjugated variables with all math:`x` first,
    and all :math:`\tilde{x}` after.
  order : int
    Order of the expansion of the normal form.
    Order 2 correspond to keeping only the quadratic part of H.
  resonances : (nr, ndof) ndarray or None
    Resonances to keep in the normal form (as well as any combination).

  Attributes
  ----------
  Hb : Series
    Normal form of the Hamiltonian :math:`\bar{H}`.
  phi : (2*ndof,) ndarray
    Expression (as Series) of the new coordinates from the original ones.
  inv_phi : (2*ndof,) ndarray
    Expression (as Series) of the original coordinates from the new ones.
  W : (order - 1,) ndarray
    Expansion of the auxiliary Hamiltonian for the change of variables.
  """

  def __init__(self, H, x, order, resonances=None):
    self.H = H
    self.x = x
    self.ndof = len(self.x) // 2
    self.order = order
    self._indvar = [xk.index() for xk in self.x]

    self._factorial = np.empty(self.order - 1, dtype=int)
    self._factorial[0] = 1
    for k in range(1, self.order - 1):
      self._factorial[k] = k * self._factorial[k - 1]

    self._proj = np.identity(self.ndof)
    if resonances is not None:
      res = np.array(resonances).reshape((-1, self.ndof))
      self._proj -= res.T @ np.linalg.inv(res @ res.T) @ res

    se.savetrunc()
    se.settrunc(self.x, self.order )
    self._Hsort = H.sortdegree()

    self._nu0 = np.array(
      [
        self._Hsort[2].coefext({self.x[k]: 1, self.x[self.ndof + k]: 1}).toConst()
        for k in range(self.ndof)
      ]
    )

    self.W = np.array([se.Series() for _ in range(self.order - 1)])
    self._WH = {}
    self._Wx = {}
    self.Hb = self._Hsort.get(0, se.Series()) + self._Hsort[2].copy()
    self.phi = self.x.copy()
    self.phi_inv = self.x.copy()
    for o in range(1, self.order - 1):
      Ro = sum(
        [self._get_WH(o, p) / self._factorial[p] for p in range(o + 1)],
        start=se.Series(),
      )
      for mon, coef in Ro.items():
        ks = np.array([mon.get(indvk, 0) for indvk in self._indvar], dtype=int)
        phase = ks[: self.ndof] - ks[self.ndof :]
        if np.all(np.abs(self._proj @ phase) < 1e-12):
          self.Hb[mon] = coef
        else:
          self.W[o][mon] = -coef / (phase @ self._nu0)
      self._WH[o, 1] += self.poisson(self.W[o], self._Hsort[2])
      for k in range(2 * self.ndof):
        self.phi[k] += sum(
          [self._get_Wx(o, p, k) / self._factorial[p] for p in range(1, o + 1)],
          start=se.Series(),
        )
        self.phi_inv[k] += sum(
          [
            self._get_Wx(o, p, k) * (-1) ** p / self._factorial[p]
            for p in range(1, o + 1)
          ],
          start=se.Series(),
        )
    se.resttrunc()

  def eval_phi(self, x):
    r"""
    Evaluate the new coordinates as a function of the original ones.

    Parameters
    ----------
    x : (2*ndof,) ndarray
      Values of the original coordinates.

    Returns
    -------
    xb : (2*ndof,) ndarray
      Values of the new coordinates.
    """
    values = {vark: valk for vark, valk in zip(self.x, x)}
    return np.array([phik.evalnum(values).toConst() for phik in self.phi])

  def eval_phi_inv(self, x):
    r"""
    Evaluate the original coordinates as a function of the new ones.

    Parameters
    ----------
    x : (2*ndof,) ndarray
      Values of the new coordinates.

    Returns
    -------
    xb : (2*ndof,) ndarray
      Values of the original coordinates.
    """
    values = {vark: valk for vark, valk in zip(self.x, x)}
    return np.array([iphik.evalnum(values).toConst() for iphik in self.phi_inv])

  def poisson(self, f, g):
    r"""
    Poisson bracket :math:`\{f, g\}`.

    Parameters
    ----------
    f, g : Series
      Series for which to compute the Poisson bracket.

    Returns
    -------
    h : Series
      Poisson bracket.
    """
    return sum(
      [
        f.deriv(self.x[k]) * g.deriv(self.x[self.ndof + k])
        - f.deriv(self.x[self.ndof + k]) * g.deriv(self.x[k])
        for k in range(self.ndof)
      ],
      start=se.Series(),
    )

  def _get_WH(self, o, p):
    if p == 0:
      return self._Hsort.get(o + 2, se.Series())
    if (o, p) not in self._WH:
      self._WH[o, p] = sum(
        [self.poisson(self.W[o - j], self._get_WH(j, p - 1)) for j in range(p - 1, o)],
        start=se.Series(),
      )
    return self._WH[o, p]

  def _get_Wx(self, o, p, k):
    if p == 0:
      if o == 0:
        return self.x[k]
      else:
        return se.Series()
    if (o, p, k) not in self._Wx:
      self._Wx[o, p, k] = sum(
        [
          self.poisson(self.W[o - j], self._get_Wx(j, p - 1, k))
          for j in range(p - 1, o)
        ],
        start=se.Series(),
      )
    return self._Wx[o, p, k]
