# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later
from fractions import Fraction as _Fraction

from mpmath import fp, mp, mpc, mpf
from numpy import vectorize as _vect

fp.hypot = lambda x, y: fp.sqrt(x**2 + y**2)
for ctx in [fp, mp]:
  for func in [
    'sqrt',
    'exp',
    'expj',
    'conj',
    're',
    'im',
    'cos',
    'sin',
    'tan',
    'acos',
    'asin',
    'atan',
    'atan2',
  ]:
    ctx.__dict__['v' + func] = _vect(ctx.__getattribute__(func), otypes=[object])


class _State:
  ctx = fp


def setctx(ctx):
  _State.ctx = ctx


def getctx():
  return _State.ctx


def isnumber(x):
  return any(
    [
      isinstance(x, typek)
      for typek in [int, Fraction, float, complex, mpf, mpc, SmartComplex]
    ]
  )


def isfloat(x):
  return any([isinstance(x, typek) for typek in [float, mpf]])


def iscomplex(x):
  return any([isinstance(x, typek) for typek in [complex, mpc, SmartComplex]])


def ismp(x):
  return any([isinstance(x, typek) for typek in [mpf, mpc]])


def _isnotrat(x):
  return any([isinstance(x, typek) for typek in [float, complex, mpf, mpc]])


def smartdiv(a, b):
  """Divide a by b and try to express the result
  as a rational number (Fraction) when possible.
  """
  if isinstance(a, int) and isinstance(b, int):
    return Fraction(a, b)
  else:
    return a / b


def smartpower(a, b):
  """Raise a to power b and try to express the result
  as an integer or a rational number (Fraction) when possible.
  """
  if (not iscomplex(b)) and b < 0:
    return smartpower(smartdiv(1, a), -b)
  if isinstance(b, Fraction):
    b = b.toctx()
    if isinstance(a, int):
      apb = _State.ctx.power(a, b)
      iapb = int(apb)
      if apb == iapb:
        return iapb
      return apb
    elif isinstance(a, Fraction):
      numpb = _State.ctx.power(a.numerator, b)
      if not iscomplex(numpb):
        inumpb = int(numpb)
        if numpb == inumpb:
          denpb = _State.ctx.power(a.denominator, b)
          idenpb = int(denpb)
          if denpb == idenpb:
            return Fraction(inumpb, idenpb)
  if isinstance(b, int) and isinstance(a, (int, Fraction)):
    return a**b
  if isinstance(a, Fraction):
    a = a.toctx()
  if iscomplex(a):
    a = _State.ctx.mpc(a.real, a.imag)
  return _State.ctx.power(a, toctx(b))


def _cleantype(x):
  if type(x) is _Fraction:
    return Fraction(x)
  else:
    return x


class Fraction(_Fraction):
  def toctx(self):
    return _State.ctx.fdiv(int(self.numerator), int(self.denominator))

  def __pos__(self):
    """Compute +self"""
    return _cleantype(super().__pos__())

  def __neg__(self):
    """Compute -self"""
    return _cleantype(super().__neg__())

  def __add__(self, y):
    """Compute self + y."""
    if _isnotrat(y):
      return self.toctx() + y
    elif isnumber(y):
      return _cleantype(super().__add__(y))
    else:
      return NotImplemented

  def __radd__(self, y):
    """Commutativity of addition."""
    return self.__add__(y)

  def __sub__(self, y):
    """Substraction self - y."""
    if _isnotrat(y):
      return self.toctx() - y
    elif isnumber(y):
      return _cleantype(super().__sub__(y))
    else:
      return NotImplemented

  def __rsub__(self, y):
    """Substraction y - self."""
    if _isnotrat(y):
      return y - self.toctx()
    elif isnumber(y):
      return _cleantype(super().__rsub__(y))
    else:
      return NotImplemented

  def __mul__(self, y):
    """Multiplication self * y."""
    if _isnotrat(y):
      return self.toctx() * y
    elif isnumber(y):
      return _cleantype(super().__mul__(y))
    else:
      return NotImplemented

  def __rmul__(self, y):
    """Commutativity of multiplication."""
    return self.__mul__(y)

  def __truediv__(self, y):
    """Division self / y."""
    if _isnotrat(y):
      return self.toctx() / y
    elif isnumber(y):
      return _cleantype(super().__truediv__(y))
    else:
      return NotImplemented

  def __rtruediv__(self, y):
    """Division y / self"""
    if _isnotrat(y):
      return y / self.toctx()
    elif isnumber(y):
      return _cleantype(super().__rtruediv__(y))
    else:
      return NotImplemented

  def __pow__(self, y):
    if _isnotrat(y):
      return self.toctx() ** y
    elif isnumber(y):
      return _cleantype(super().__pow__(y))
    else:
      return NotImplemented

  def __rpow__(self, y):
    if _isnotrat(y):
      return y ** self.toctx()
    elif isnumber(y):
      return _cleantype(super().__rpow__(y))
    else:
      return NotImplemented


class SmartComplex:
  def __init__(self, real, imag):
    self.real = real
    self.imag = imag

  def __str__(self):
    string = ''
    if self == 0:
      return '0'
    if self.real != 0:
      string += str(self.real)
      if self.imag > 0:
        string += '+'
    if self.imag != 0:
      string += str(self.imag) + 'i'
    return string

  def __repr__(self):
    return str(self)

  def toctx(self):
    real = self.real.toctx() if isinstance(self.real, Fraction) else self.real
    imag = self.imag.toctx() if isinstance(self.imag, Fraction) else self.imag
    return _State.ctx.mpc(real, imag)

  def conj(self):
    """Compute conjugate"""
    return SmartComplex(self.real, -self.imag)

  def __abs__(self):
    return smartpower(self.real**2 + self.imag**2, Fraction(1, 2))

  def __eq__(self, y):
    if iscomplex(y):
      return self.real == y.real and self.imag == y.imag
    elif isnumber(y):
      return self.real == y and self.imag == 0
    else:
      return NotImplemented

  def __pos__(self):
    """Compute +self"""
    return SmartComplex(self.real, self.imag)

  def __neg__(self):
    """Compute -self"""
    return SmartComplex(-self.real, -self.imag)

  def __add__(self, y):
    """Compute self + y."""
    if iscomplex(y):
      real = self.real + y.real
      imag = self.imag + y.imag
      if imag == 0:
        return real
      else:
        return SmartComplex(real, imag)
    elif isnumber(y):
      return SmartComplex(self.real + y, self.imag)
    else:
      return NotImplemented

  def __radd__(self, y):
    """Commutativity of addition."""
    return self.__add__(y)

  def __sub__(self, y):
    """Substraction self - y."""
    if iscomplex(y):
      real = self.real - y.real
      imag = self.imag - y.imag
      if imag == 0:
        return real
      else:
        return SmartComplex(real, imag)
    elif isnumber(y):
      return SmartComplex(self.real - y, self.imag)
    else:
      return NotImplemented

  def __rsub__(self, y):
    """Substraction y - self."""
    if iscomplex(y):
      real = y.real - self.imag
      imag = y.imag - self.imag
      if imag == 0:
        return real
      else:
        return SmartComplex(real, imag)
    elif isnumber(y):
      return SmartComplex(y - self.real, -self.imag)
    else:
      return NotImplemented

  def __mul__(self, y):
    """Multiplication self * y."""
    if iscomplex(y):
      real = self.real * y.real - self.imag * y.imag
      imag = self.real * y.imag + self.imag * y.real
      if imag == 0:
        return real
      else:
        return SmartComplex(real, imag)
    elif isnumber(y):
      return SmartComplex(self.real * y, self.imag * y)
    else:
      return NotImplemented

  def __rmul__(self, y):
    """Commutativity of multiplication."""
    return self.__mul__(y)

  def __truediv__(self, y):
    """Division self / y."""
    if iscomplex(y):
      denom = y.real**2 + y.imag**2
      return self * y.conj() / denom
    elif isnumber(y):
      return SmartComplex(smartdiv(self.real, y), smartdiv(self.imag, y))
    else:
      return NotImplemented

  def __rtruediv__(self, y):
    """Division y / self"""
    if isnumber(y):
      denom = self.real**2 + self.imag**2
      return y * self.conj() / denom
    else:
      return NotImplemented

  def __pow__(self, y):
    if isinstance(y, int):
      if y < 0:
        return (1 / self) ** (-y)
      if isinstance(self.real, Fraction):
        a = self.real.numerator
        b = self.real.denominator
      elif isinstance(self.real, int):
        a = self.real
        b = 1
      else:
        return self.toctx() ** y
      if isinstance(self.imag, Fraction):
        c = self.imag.numerator
        d = self.imag.denominator
      elif isinstance(self.imag, int):
        c = self.imag
        d = 1
      else:
        return self.toctx() ** y
      numerator = _State.ctx.mpc(a * d, b * c) ** y
      denominator = (b * d) ** y
      return SmartComplex(
        Fraction(int(numerator.real), denominator),
        Fraction(int(numerator.imag), denominator),
      )
    elif isnumber(y):
      return self.toctx() ** y
    else:
      return NotImplemented

  def __rpow__(self, y):
    if isnumber(y):
      return y ** self.toctx()
    else:
      return NotImplemented


def toctx(x):
  if isinstance(x, (Fraction, SmartComplex)):
    return x.toctx()
  else:
    return x


i = SmartComplex(0, 1)
