# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later
from . import series as se


def rOa(e, eiM, degree=10):
  r"""
  Expansion of r/a in power series of the eccentricity.

  Parameters
  ----------
  e : Var
    Eccentricity.
  eiM : Var, Series, or constant.
    Imaginary exponential of the mean anomaly.
  degree : int
    Degree of the expansion in eccentricity.

  Returns
  -------
  R : Series
    Series expansion of r/a.
  """
  se.savetrunc()
  se.settrunc([e], degree)
  eiE = se.Var('eiE')
  cE = (eiE + 1 / eiE) / 2
  isE = (eiE - 1 / eiE) / 2
  f_eiM = eiE * (-e * isE).exp()
  roaeikMdM = (1 - e * cE) ** 2
  R = roaeikMdM.coefext({eiE: 0})
  for k in range(1, degree + 1):
    roaeikMdM *= f_eiM
    R += roaeikMdM.coefext({eiE: 0}) * (eiM**k + eiM ** (-k))
  se.resttrunc()
  return R


def aOr(e, eiM, degree=10):
  r"""
  Expansion of a/r in power series of the eccentricity.

  Parameters
  ----------
  e : Var
    Eccentricity.
  eiM : Var, Series, or constant.
    Imaginary exponential of the mean anomaly.
  degree : int
    Degree of the expansion in eccentricity.

  Returns
  -------
  R : Series
    Series expansion of a/r.
  """
  se.savetrunc()
  se.settrunc([e], degree)
  eiE = se.Var('eiE')
  isE = (eiE - 1 / eiE) / 2
  f_eiM = eiE * (-e * isE).exp()
  aoreikMdM = 1
  R = se.Series() + 1
  for k in range(1, degree + 1):
    aoreikMdM *= f_eiM
    R += aoreikMdM.coefext({eiE: 0}) * (eiM**k + eiM ** (-k))
  se.resttrunc()
  return R


def eiv(e, eiM, degree=10):
  r"""
  Expansion of exp(i v) in power series of the eccentricity,
  where v is the true anomaly.

  Parameters
  ----------
  e : Var
    Eccentricity.
  eiM : Var, Series, or constant.
    Imaginary exponential of the mean anomaly.
  degree : int
    Degree of the expansion in eccentricity.

  Returns
  -------
  R : Series
    Series expansion of exp(i v).
  """
  se.savetrunc()
  se.settrunc([e], degree)
  eiE = se.Var('eiE')
  cE = (eiE + 1 / eiE) / 2
  isE = (eiE - 1 / eiE) / 2
  f_eiM = eiE * (-e * isE).exp()
  f_emiM = 1 / eiE * (e * isE).exp()
  eiveikMdM = cE - e + (1 - e**2).sqrt() * isE
  eivemikMdM = eiveikMdM
  R = eiveikMdM.coefext({eiE: 0})
  eikM = 1
  emikM = 1
  for _ in range(1, degree + 2):
    eiveikMdM *= f_eiM
    eivemikMdM *= f_emiM
    eikM *= eiM
    emikM /= eiM
    R += eiveikMdM.coefext({eiE: 0}) * emikM + eivemikMdM.coefext({eiE: 0}) * eikM
  se.resttrunc()
  return R
