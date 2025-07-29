# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later

import numpy as np


def primefac(n):
  r"""
  Prime factors decomposition.

  Parameters
  ----------
  n : int
    Integer to be decomposed.

  Returns
  -------
  dic : dict
    Dictionary of the form prime factor -> power.
  """
  dic = {}
  k = 2
  r = n
  sqn = np.sqrt(n)
  while r > sqn and k <= sqn:
    while r % k == 0:
      r //= k
      dic[k] = dic.get(k, 0) + 1
    k += 1
  if r != 1:
    dic[r] = 1
  return dic


def pf2int(pf):
  r"""
  Compute an integer from its prime factors decomposition.


  Parameters
  ----------
  dic : dict
    Dictionary of prime factor -> power.

  Returns
  -------
  n : int
    Integer corresponding to the decomposition.
  """
  n = 1
  for k, p in pf.items():
    n *= k**p
  return n


def lcm(l):
  r"""
  Least common multiple.

  Parameters
  ----------
  l : list
    Integers for which to compute the lcm.

  Returns
  -------
  lcm : int
    Least common multiple.
  """
  pflcm = primefac(l[0])
  for el in l[1:]:
    pfel = primefac(el)
    for k, p in pfel.items():
      pflcm[k] = max(pflcm.get(k, 0), p)
  return pf2int(pflcm)


def gcd(l):
  r"""
  Greatest common divisor.

  Parameters
  ----------
  l : list
    Integers for which to compute the gcd.

  Returns
  -------
  gcd : int
    Greatest common divisor.
  """
  pfgcd = primefac(l[0])
  for el in l[1:]:
    pfel = primefac(el)
    for k, p in pfgcd.items():
      pfgcd[k] = min(pfel.get(k, 0), p)
  return pf2int(pfgcd)
