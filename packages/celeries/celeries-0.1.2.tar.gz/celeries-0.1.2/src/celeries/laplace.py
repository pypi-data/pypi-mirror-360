# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later
from .mpfrac import getctx


def b(s, k, alpha):
  r"""
  Laplace coefficient b_s^(k) (alpha).

  Parameters
  ----------
  s : float
  k : int
  alpha : float

  Returns
  -------
  b : float
    Laplace coefficient.
  """
  if k < 0:
    return b(s, -k, alpha)
  ctx = getctx()
  skkfac = ctx.fprod([ctx.fdiv(s + j, 1 + j) for j in range(k)])
  bska = 2 * skkfac * alpha**k * ctx.hyp2f1(s, s + k, k + 1, alpha**2)
  return bska


def deriv_b(s, k, alpha):
  r"""
  Derivative of the Laplace coefficient b_s^(k) (alpha) with respect to alpha.

  Parameters
  ----------
  s : float
  k : int
  alpha : float

  Returns
  -------
  db : float
    Derivative Laplace coefficient.
  """
  return s * (
    b(s + 1, k - 1, alpha) + b(s + 1, k + 1, alpha) - 2 * alpha * b(s + 1, k, alpha)
  )
