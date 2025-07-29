# Copyright 2016-2025 Jean-Baptiste Delisle
# Licensed under the EUPL-1.2 or later
from . import mpfrac as mf


class _State:
  r"""Hidden global parameters of the module."""

  var_list = []  # list of defined variables
  var_index = {}  # dictionary of the form: variable name (str) -> index
  nvars = 0  # number of variables
  trunc_inds = []  # Indices of variables considered for a truncation of series
  trunc_degree = None  # Degree at which the series will be truncated
  saved_truncs = []  # Saved truncations list
  display = 'expi'


def setdisplay(display):
  r"""
  Set the display mode for angle variables.

  Parameters
  ----------
  display : str
    Display mode to be set, among:
      - "trigo": cos(angle), sin(angle),
      - "expi": exp(i angle)).
  """

  if display not in ['expi', 'trigo']:
    raise Exception('setdisplay: display must be expi or trigo')
  _State.display = display


def getdisplay():
  r"""
  Get the display mode for angle variables.

  Returns
  -------
  display : str
    Current display mode, among:
      - "trigo": cos(angle), sin(angle),
      - "expi": exp(i angle)).
  """
  return _State.display


def settrunc(truncvars, degree):
  r"""
  Set the truncation for futur computations.

  Parameters
  ----------
  truncvars : list
    Variables on which to apply the truncation.
  degree : int
    Degree of the truncation.
  """
  _State.trunc_inds = [x.index() for x in truncvars]
  _State.trunc_degree = degree


def unsettrunc():
  r"""Unset the truncation for futur computations."""
  _State.trunc_inds = []
  _State.trunc_degree = None


def gettrunc():
  r"""
  Get the current truncation.

  Returns
  -------
  truncvars : list
    Variables on which to apply the truncation.
  degree : int
    Degree of the truncation.
  """
  if _State.trunc_degree is None:
    return None
  else:
    return ([_State.var_list[k] for k in _State.trunc_inds], _State.trunc_degree)


def savetrunc():
  r"""Append the current truncation to the saved truncation list."""
  _State.saved_truncs.append((_State.trunc_inds, _State.trunc_degree))


def resttrunc():
  r"""Restitute the last saved truncation."""
  if _State.saved_truncs == []:
    unsettrunc()
  else:
    _State.trunc_inds, _State.trunc_degree = _State.saved_truncs.pop()


def listvars():
  r"""List all currently defined variables.

  Returns
  -------
  var_list : list
    All currently defined variables.
  """
  return _State.var_list.copy()


class _Monomial(dict):
  r"""Hidden monomial class.
  A monomial is a product of variables raised to integer powers.
  Ex: x**2 * y**-3 * z.
  It is represented as a dictionary of the form: variable index -> power.
  Ex: {0:2, 1:-3, 2:1}.
  """

  def copy(self):
    mon = _Monomial()
    mon.update(self)
    return mon

  def __mul__(self, mon):
    """Compute the product self*mon."""
    prod = self.copy()  # start from self
    # For each variable in the monomial
    for k, powk in mon.items():
      tmp = prod.get(k, 0) + powk  # compute the power of the k-th variable
      prod[k] = tmp  # put it in prod
      if tmp == 0:
        del prod[k]  # if the power is 0, remove the k-th variable
    return prod

  def degree(self, indlist=None):
    """Compute the degree of the monomial with respect to
    the variables with indices in indlist, if provided,
    and to the trunc vars if indlist is None."""
    if indlist is None:
      indlist = _State.trunc_inds
    return sum(powk for k, powk in self.items() if k in indlist)

  def __hash__(self):
    """Hash function to be able to use a monomial
    as a dictionary key (see the Series class).
    This function could be better optimized...
    A compromise must be found between the ability to distinguish two monomials,
    and the computation time.
    """
    value = 1987
    for k, powk in self.items():
      value = value ^ (powk << k)
    return value

  def __gt__(self, mon):
    """Ordering of monomials (used when printing a series, see the Series class).
    Check if self > mon.
    """
    # For each variable (index)
    for k in range(_State.nvars):
      # compute power of this variable in self and mon
      powk = self.get(k, 0)
      mpowk = mon.get(k, 0)
      if powk != mpowk:
        return powk > mpowk
    return False


_const_mon = _Monomial()  # Constant monomial (= 1)


class Series(dict):
  """Series class.

  A series is a sum of coefficient * monomial.
  It is represented as a dictionary of the form: monomial -> coefficient.
  It is initialized at 0.
  """

  def listvars(self):
    r"""List of variables that appear in the series.

    Returns
    -------
    var_list : list
      All variables that appear in the series.
    """
    var_list = []
    for mon in sorted(self.keys()):
      for k in sorted(mon.keys()):
        if _State.var_list[k] not in var_list:
          var_list.append(_State.var_list[k])
    return var_list

  def _str(self):
    """Create a string representing the series"""
    if not self:
      return '0'
    string = ''
    times = True
    # Sort the monomials
    for mon in sorted(self.keys()):
      coef = self[mon]
      # clean unnecessary imaginary part
      if mf.iscomplex(coef) and coef.imag == 0:
        coef = coef.real
      strcoef = str(coef)
      # Deal with 1, -1, 1i...
      if mon != {}:
        if strcoef == '1':
          strcoef = ''
          times = False
        elif strcoef == '-1':
          strcoef = '-'
          times = False
      if strcoef == '1i':
        strcoef = 'i'
      elif strcoef == '-1i':
        strcoef = '-i'
      if mf.iscomplex(coef) and coef.real != 0 and coef.imag != 0:
        if coef.real < 0 and coef.imag < 0:
          strcoef = f'-({str(-coef)})'
        else:
          strcoef = f'({strcoef})'
      # Deal with +/-
      if string != '':
        if strcoef.startswith('-'):
          string += ' - '
          strcoef = strcoef[1:]
        else:
          string += ' + '
      string += strcoef
      # Deal with variables/exponents
      strexpiangles = ''
      for k, powk in sorted(mon.items()):
        if _State.var_list[k]._expiangle:
          if powk > 0 and strexpiangles:
            strexpiangles += '+'
          if powk == -1:
            strexpiangles += '-'
          elif powk != 1:
            strexpiangles += str(powk) + '*'
          strexpiangles += _State.var_list[k]._name[4:]
        else:
          if times:
            string += '*'
          string += _State.var_list[k]._name
          if powk != 1:
            string += '**' + str(powk)
          times = True
      if strexpiangles:
        if times:
          string += '*'
        string += f'expi({strexpiangles:s})'
    return string

  def _totrigo(self):
    """Convert the series to use cos, sin of angles, instead of expi.
    Used if display = "trigo".
    """
    R = Series()
    for mon in sorted(self.keys()):
      coef = self[mon]
      Rmon = _Monomial()
      # Check if the monomial contains variables of the form expi(angle)
      # If it the case, replace them with cos/isin variables
      sign = 0
      name = ''
      for k, powk in sorted(mon.items()):
        if _State.var_list[k]._expiangle:
          if sign == 0:
            sign = 1 if powk > 0 else -1
            if sign * powk != 1:
              name += str(sign * powk) + '*'
          else:
            if sign * powk == 1:
              name += '+'
            elif sign * powk == -1:
              name += '-'
            else:
              if sign * powk > 0:
                name += '+'
              name += str(sign * powk) + '*'
          name += _State.var_list[k]._name[4:]
        else:
          Rmon[k] = powk
      Rm = Series()
      Rm[Rmon] = coef
      if name:
        # Create temporary variables
        # with the name of the angle
        cosv = Var(f'cos({name:s})')
        sinv = Var(f'sin({name:s})')
        if sign > 0:
          Rm *= cosv + mf.i * sinv
        else:
          Rm *= cosv - mf.i * sinv
      # Add the modified monomial to the new series
      R += Rm
    return R

  def __str__(self):
    """Create a string representing the series.
    Use expi or cos/sin depending on chosen display type.
    """
    # Check if display is trigo
    if _State.display == 'trigo':
      # If trigo, first convert the series to trigonometric form
      # using the _totrigo function,
      # then call _str
      nvars = _State.nvars
      strtrigo = self._totrigo()._str()
      # Delete temporary variables / clean things
      for k in range(nvars, _State.nvars):
        del _State.var_index[_State.var_list[k]._name]
      _State.var_list = _State.var_list[:nvars]
      _State.nvars = nvars
      return strtrigo
    return self._str()

  def __repr__(self):
    """Return a representation (string) of the series."""
    return self.__str__()

  def copy(self):
    r"""
    Copy of the series.

    Returns
    -------
    R : Series
      Copy of the series.
    """
    R = Series()
    R.update(self)
    return R

  def maxpow(self, x):
    r"""
    Find the highest exponent of x in the series.

    Returns
    -------
    mpow : int
      Highest exponent.
    """
    mpow = -mf.getctx().inf
    k = x.index()
    for mon in self:
      mpow = max(mpow, mon.get(k, 0))
    return mpow

  def minpow(self, x):
    r"""
    Find the lowest exponent of x in the series.

    Returns
    -------
    mpow : int
      lowest exponent.
    """
    mpow = mf.getctx().inf
    k = x.index()
    for mon in self:
      mpow = min(mpow, mon.get(k, 0))
    return mpow

  def maxdeg(self, varlist=None):
    r"""
    Find the highest degree in the series with respect to the variables
    in varlist (if provided) or to the truncation variables (if varlist is None).

    Parameters
    ----------
    varlist : iterable or None
      List of variables to consider for the degree of a monomial.

    Returns
    -------
    md : int
      highest degree.
    """
    indlist = None if varlist is None else [x.index() for x in varlist]
    md = -mf.getctx().inf
    for mon in self:
      md = max(md, mon.degree(indlist))
    return md

  def mindeg(self, varlist=None):
    r"""
    Find the lowest degree in the series with respect to the variables
    in varlist (if provided) or to the truncation variables (if varlist is None).

    Parameters
    ----------
    varlist : iterable or None
      List of variables to consider for the degree of a monomial.

    Returns
    -------
    md : int
      lowest degree.
    """
    indlist = None if varlist is None else [x.index() for x in varlist]
    md = mf.getctx().inf
    for mon in self:
      md = min(md, mon.degree(indlist))
    return md

  def sortdegree(self, varlist=None):
    """Sort the terms (monomials) of the series depending on their degree
    with respect to the variables in varlist (if provided)
    or to the truncation variables (if varlist is None).

    Parameters
    ----------
    varlist : iterable or None
      List of variables to consider for the degree of a monomial.

    Returns
    -------
      sortdeg: dict
        Dictionary of the form: degree -> part of the series of that degree.
    """
    indlist = None if varlist is None else [x.index() for x in varlist]
    sortdeg = {}
    # For each monomial in the series
    for mon, coef in self.items():
      # compute the degree
      dmon = mon.degree(indlist)
      # add the monomial in the series of degree dmon
      sortdeg[dmon] = sortdeg.get(dmon, Series())
      sortdeg[dmon][mon] = coef
    return sortdeg

  def __pos__(self):
    """Return a copy of the series."""
    return self.copy()

  def __neg__(self):
    """Negate the series (return -self)."""
    R = Series()
    for mon, coef in self.items():
      R[mon] = -coef  # change the sign of each coefficient of the series.
    return R

  def __add__(self, Q):
    """Computed self + Q.
    Q can be a series (or variable) or a number.
    """
    if isinstance(Q, Series):
      R = self.copy()  # start from self
      for mon, coef in Q.items():
        tmp = R.get(mon, 0) + coef  # compute coefficient of monomial mon.
        R[mon] = tmp  # put it in the dict
        if tmp == 0:
          del R[mon]  # remove the monomial if the coefficient is zero
      return R
    elif mf.isnumber(Q):
      R = self.copy()  # start from self
      tmp = R.get(_const_mon, 0) + Q  # compute coefficient of the constant term
      R[_const_mon] = tmp  # put it in the dict
      if tmp == 0:
        del R[_const_mon]  # remove the constant term if it is zero
      return R
    else:
      return NotImplemented

  def __radd__(self, Q):
    """Commutativity of addition."""
    return self.__add__(Q)

  def __sub__(self, Q):
    """Substraction self - Q.
    Same as __add__ but with - signes.
    """
    if isinstance(Q, Series):
      R = self.copy()
      for mon, coef in Q.items():
        tmp = R.get(mon, 0) - coef
        R[mon] = tmp
        if tmp == 0:
          del R[mon]
      return R
    elif mf.isnumber(Q):
      R = self.copy()
      tmp = R.get(_const_mon, 0) - Q
      R[_const_mon] = tmp
      if tmp == 0:
        del R[_const_mon]
      return R
    else:
      return NotImplemented

  def __rsub__(self, Q):
    """Substraction Q - self.
    This is only called if Q is not a series (or variable).
    """
    if mf.isnumber(Q):
      R = -self + Q  # Use negate and addition functions.
      return R
    else:
      return NotImplemented

  def __mul__(self, Q):
    """Multiplication self * Q.
    Q can be a series (or variable) or a number.
    """
    if isinstance(Q, Series):
      R = Series()
      # For each couple of monomial in self and Q:
      for mon, coef in self.items():
        for Qmon, Qcoef in Q.items():
          Rmon = mon * Qmon  # Compute the product of monomials
          # Check the degree of the new monomial (if the truncation is defined)
          if _State.trunc_degree is None or Rmon.degree() <= _State.trunc_degree:
            # Compute the product of coefficient and add it in the dict
            tmp = R.get(Rmon, 0) + coef * Qcoef
            R[Rmon] = tmp
            if tmp == 0:
              del R[Rmon]  # If the new coefficient is zero remove the monomial
      return R
    elif mf.isnumber(Q):
      R = Series()
      if Q != 0:
        # For each monomial in self
        for mon, coef in self.items():
          # Check the degree of the monomial (if the truncation is defined)
          if _State.trunc_degree is None or mon.degree() <= _State.trunc_degree:
            R[mon] = Q * coef  # Compute the new coefficient
      return R
    else:
      return NotImplemented

  def __rmul__(self, Q):
    """Commutativity of multiplication."""
    return self.__mul__(Q)

  def euclide(self, B, x):
    r"""
    Euclidian division of the series by B according to variable x:
    self = B * Q + R.

    Parameters
    ----------
    B : Series
      Divisor.
    x : Var
      Variable to consider for the Euclidian division.

    Returns
    -------
    Q : Series
      Quotient of the division.
    R : Series
      Rest of the division.
    """
    pB = B.maxpow(x)
    aB = B.coefext({x: pB})
    R = self.copy()
    Q = Series()
    for p in range(self.maxpow(x), pB - 1, -1):
      Qp = (R.coefext({x: p}) * x ** (p - pB)) / aB
      Q += Qp
      R -= Qp * B
    return (Q, R)

  def _leading_Monomial(self):
    """Extract the leading monomial of the series according to the current truncation.
    Raise error when leading monomial is not unique.
    """
    sortdeg = (
      self.sortdegree()
    )  # Sort the series depending on the degree (in the trunc vars)
    listdeg = sorted(sortdeg)  # produce a sorted list of degrees
    P = sortdeg[listdeg[0]]  # get the leading series (P)
    if len(P) > 1:  # Check if it is a single term
      raise Exception('Series._leading_Monomial: leading monomial is not unique.')
    return P

  def _invert(self):
    """Invert a series (return 1/self)."""
    # If self contains a single term.
    if len(self) == 1:
      R = Series()
      mon, coef = next(iter(self.items()))  # Get the monomial and coefficient
      # Invert the monomial
      Rmon = _Monomial()
      for k, powk in mon.items():
        Rmon[k] = -powk
      # Invert the coefficient
      R[Rmon] = mf.smartdiv(1, coef)
      return R
    else:
      # For a more complex series, it must be expanded as a power series of the form:
      # 1/(P+epsilon) = 1/P * 1/(1 + epsilon/P) = 1/P * (1 - epsilon/P + ...)
      # where epsilon << P and P can be inverted (single monomial)
      P = self._leading_Monomial()
      invP = P._invert()  # Invert it
      Q = (self - P) * invP  # Compute Q = epsilon/P
      # Compute the development in powers of Q:
      Qp = Series() + invP
      R = Qp
      for _ in range(1, _State.trunc_degree + 1):
        Qp *= -Q
        R += Qp
      return R

  def __truediv__(self, B):
    """Division self / B.
    B can be a series (or variable) or a number.
    """
    if isinstance(B, Series):
      lv = B.listvars()
      if lv:
        try:
          Q, R = self.euclide(B, lv[0])
          if Series() == R:
            return Q
        except:
          pass
      return self * B._invert()  # return self * (1/B)
    elif mf.isnumber(B):
      R = Series()
      # divide each coefficient in the series by B
      for mon, coef in self.items():
        R[mon] = mf.smartdiv(coef, B)
      return R
    else:
      return NotImplemented

  def __rtruediv__(self, Q):
    """Division Q / self.
    This is only called if Q is not a series (or variable).
    """
    if mf.isnumber(Q):
      return self._invert() * Q  # return (1/self * Q)
    else:
      return NotImplemented

  def __pow__(self, alpha):
    """Raise series to integer power alpha."""
    # convert type of fractions that are integers
    if isinstance(alpha, mf.Fraction) and alpha.denominator == 1:
      alpha = alpha.numerator
    # If integer power, easy.
    if isinstance(alpha, int):
      if alpha == -1:
        return self._invert()
      elif alpha < -1:
        return (self._invert()) ** (-alpha)
      elif alpha == 0:
        return Series() + 1
      elif alpha == 1:
        return self.copy()
      else:
        return self * self ** (alpha - 1)
    # If self contains a single term.
    elif len(self) == 1:
      mon, coef = next(iter(self.items()))  # Get the monomial and coefficient
      R = Series()  # initialize result
      Rmon = _Monomial()  # initialize monomial
      # Rational power
      if isinstance(alpha, mf.Fraction):
        # Raise the monomial to power alpha
        for k, powk in mon.items():
          Rpowk = powk * alpha
          if Rpowk.denominator != 1:
            raise Exception(
              f'Series.__pow__: leading monomial ({str(self):s})'
              f'cannot be raised to power {alpha.numerator:d}/{alpha.denominator:d}'
            )
          Rmon[k] = Rpowk.numerator
      # Non-rational power
      else:
        # Check that the monomial is constant
        if mon != _const_mon:
          raise Exception(
            'Series.__pow__: non-rational power, leading term is not constant.'
          )
      # Raise the coefficient to power alpha
      R[Rmon] = mf.smartpower(coef, alpha)
      return R
    # Non-integer, multiple terms, need truncation
    else:
      # Get leading term (self = P + epsilon = P (1 + Q), Q=epsilon/P)
      P = self._leading_Monomial()
      Pa = P**alpha  # raise it to power alpha
      Q = (self - P) / P  # Compute Q = epsilon/P
      # Compute the series: self**alpha = P**alpha (1 + alpha Q + ...)
      Pp = Pa
      R = Pp
      for p in range(1, _State.trunc_degree + 1):
        Pp *= Q * (alpha + 1 - p) * mf.Fraction(1, p)
        R += Pp
      return R

  def sqrt(self):
    r"""
    Square root of the series.

    Returns
    -------
    R : Series
      Series expansion (with respect to truncation variables) of the square root.
    """
    return self.__pow__(mf.Fraction(1, 2))

  def exp(self):
    r"""
    Exponential of the series.

    Returns
    -------
    R : Series
      Series expansion (with respect to truncation variables) of the exponential.
    """

    if _State.trunc_degree is None:
      raise Exception('Series.exp: No truncation is set.')
    if self.mindeg() < 0:
      raise Exception('Series.exp: minimum degree is negative.')
    const = self.get(_const_mon, 0)
    vari = self - const
    Pp = Series() + 1
    R = Pp
    for p in range(1, _State.trunc_degree + 1):
      Pp *= vari * mf.Fraction(1, p)
      R += Pp
    if const != 0:
      R *= mf.getctx().exp(mf.toctx(const))
    return R

  def log(self):
    r"""
    Logarithm of the series.

    Returns
    -------
    R : Series
      Series expansion (with respect to truncation variables) of the log.
    """
    if _State.trunc_degree is None:
      raise Exception('Series.log: No truncation is set.')
    const = self.get(_const_mon, 0)
    if const == 0:
      return NotImplemented
    vari = self * mf.smartdiv(1, const) - 1
    Pp = Series() - 1
    R = Series()
    if const != 1:
      R += mf.getctx().log(mf.toctx(const))
    for p in range(1, _State.trunc_degree + 1):
      Pp *= -vari
      R += Pp * mf.Fraction(1, p)
    return R

  def expi(self):
    r"""
    Imaginary exponential of the series.
    This only work for integer linear combination of angles.

    Returns
    -------
    R : Series
      Imaginary exponential.
    """
    R = Series() + 1
    for key, coef in self.items():
      if not isinstance(coef, int):
        raise Exception('expi: coef is not integer.')
      if len(key) != 1:
        raise Exception('expi: monomial with several variables.')
      kv, p = list(key.items())[0]
      if p != 1:
        raise Exception('expi: monomial with power != 1')
      v = _State.var_list[kv]
      if not isinstance(v, Angle):
        raise Exception('expi: variable is not an angle')
      R *= v._expi**coef
    return R

  def cos(self):
    r"""
    Cosine of the series.
    This only work for integer linear combination of angles.

    Returns
    -------
    R : Series
      Series expansion (with respect to truncation variables) of the cosine.
    """
    try:
      expis = self.expi()
      return (expis + 1 / expis) / 2
    except:
      pass
    if _State.trunc_degree is None:
      raise Exception('Series.cos: No truncation is set.')
    if self.mindeg() < 0:
      raise Exception('Series.cos: minimum degree is negative.')
    const = self.get(_const_mon, 0)
    vari = self - const
    Pp = Series() + 1
    if const == 0:
      coefs = [1, 0, -1, 0]
    else:
      ctx = mf.getctx()
      cconst = mf.toctx(const)
      cc = ctx.cos(cconst)
      sc = ctx.sin(cconst)
      coefs = [cc, -sc, -cc, sc]
    R = coefs[0] * Pp
    for p in range(1, _State.trunc_degree + 1):
      Pp *= vari * mf.Fraction(1, p)
      R += coefs[p % 4] * Pp
    return R

  def sin(self):
    r"""
    Sine of the series.
    This only work for integer linear combination of angles.

    Returns
    -------
    R : Series
      Series expansion (with respect to truncation variables) of the sine.
    """
    try:
      expis = self.expi()
      return (expis - 1 / expis) / (2 * mf.i)
    except:
      pass
    if _State.trunc_degree is None:
      raise Exception('Series.sin: No truncation is set.')
    if self.mindeg() < 0:
      raise Exception('Series.sin: minimum degree is negative.')
    const = self.get(_const_mon, 0)
    vari = self - const
    Pp = Series() + 1
    if const == 0:
      coefs = [0, 1, 0, -1]
    else:
      ctx = mf.getctx()
      cconst = mf.toctx(const)
      cc = ctx.cos(cconst)
      sc = ctx.sin(cconst)
      coefs = [sc, cc, -sc, -cc]
    R = coefs[0] * Pp
    for p in range(1, _State.trunc_degree + 1):
      Pp *= vari * mf.Fraction(1, p)
      R += coefs[p % 4] * Pp
    return R

  def deriv(self, x):
    r"""
    Derivative of the series with respect to the variable x.

    Parameters
    ----------
    x : Var
      Variable for which to compute the derivative.

    Returns
    -------
    R : Series
      Derivative.
    """
    R = Series()
    k = x.index()
    # For each monomial
    for mon, coef in self.items():
      Rmon = mon.copy()
      powx = Rmon.get(k, 0)  # Get power of x in the monomial
      if powx != 0:
        if powx == 1:
          del Rmon[k]  # Remove x from the monomial if it was raised to power 1
        else:
          Rmon[k] = powx - 1  # Reduce by 1 the power otherwise
        R[Rmon] = powx * coef  # Multiply the coefficient by powx
    # check if x is an angle and add derivative of x.expi()
    if isinstance(x, Angle):
      R += mf.i * x._expi * self.deriv(x._expi)
    return R

  def integ(self, x):
    r"""
    Integrate the series with respect to the variable x.

    Parameters
    ----------
    x : Var
      Variable for which to compute the integral.

    Returns
    -------
    R : Series
      Integral.
    """
    R = Series()
    k = x.index()
    if isinstance(x, Angle):
      # x is an angle, need to take into account both x and exp(ix)
      keix = x._expi.index()
      # For each monomial
      for mon, coef in self.items():
        powx = mon.get(k, 0)  # Get power of x in the monomial
        if powx == -1:  # Cannot integrate 1/x as a series...
          raise Exception('Series.integ: exponent -1 found. Result is not a series')
        poweix = mon.get(keix, 0)  # Get power of expix in the monomial
        if poweix == 0:
          Rmon = mon.copy()
          powx += 1  # Raise power by 1
          Rmon[k] = powx
          R[Rmon] = R.get(Rmon, 0) + mf.smartdiv(
            coef, powx
          )  # Divide coefficient by powx
          if R[Rmon] == 0:
            del R[Rmon]
        elif powx >= 0:
          Rmon = mon.copy()
          Rcoef = mf.smartdiv(-mf.i * coef, poweix)
          R[Rmon] = R.get(Rmon, 0) + Rcoef
          if R[Rmon] == 0:
            del R[Rmon]
          for p in range(powx):
            Rmon = mon.copy()
            Rcoef = mf.smartdiv(mf.i * Rcoef * (powx - p), poweix)
            if p + 1 == powx:
              del Rmon[k]
            else:
              Rmon[k] = powx - p - 1
            R[Rmon] = R.get(Rmon, 0) + Rcoef
            if R[Rmon] == 0:
              del R[Rmon]
        else:
          raise Exception(
            'Series.integ: negative exponent for an angle. Result is not a series'
          )
    else:
      # Not an angle
      # For each monomial
      for mon, coef in self.items():
        Rmon = mon.copy()
        powx = Rmon.get(k, 0)  # Get power of x in the monomial
        if powx == -1:  # Cannot integrate 1/x as a series...
          raise Exception('Series.integ: exponent -1 found. Result is not a series')
        powx += 1  # Raise power by 1
        Rmon[k] = powx
        R[Rmon] = mf.smartdiv(coef, powx)  # Divide coefficient by powx
    return R

  def toConst(self):
    r"""
    Convert a constant series to a constant value.
    The series must not contain any variable part.

    Returns
    -------
    value : int, Fraction, float...
      Constant value.
    """
    nmons = len(self)
    if nmons == 0:
      return 0
    elif nmons == 1 and _const_mon in self:
      return self[_const_mon]
    for mon in self:
      for k in mon:
        print(_State.var_list[k])
    raise Exception('Series.toConst: series is not constant.')

  def coefext(self, monomial):
    r"""
    Extract the coefficient in front of a monomial.

    Parameters
    ----------
    monomial : dict
      Monomial provided as a dictionary of the form: variable -> power.

    Returns
    -------
    R : Series
      Coefficient in front of the monomial, given as a series
      depending on all remaining variables.
    """
    R = Series()
    # Build the list of (variable index, power) in the monomial
    powinds = [(x.index(), monomial[x]) for x in monomial]
    # For each monomial (mon) in the series
    for mon, coef in self.items():
      # Check if it should be extracted
      Rmon = mon.copy()
      valid = True
      # For each variable in monomial
      for k, powk in powinds:
        # Chech if mon contains this variable raised to the correct power
        if powk != Rmon.get(k, 0):
          # if not the monomial mon should not be extracted
          valid = False
          break
        if powk != 0:
          del Rmon[k]  # Remove the variable from mon in the result
      if valid:
        R[Rmon] = coef  # Add the monomial mon to the series
    return R

  def evalnum(self, varvalues):
    r"""
    Replace some variables by numerical values.

    Parameters
    ----------
    varvalues : dict
      Dictionary of the form: variable -> value.

    Returns
    -------
    R : Series
      Series where the provided variables have been replaced by their values.
    """
    R = Series()
    # list of index,values (check for angles to also add the expi value)
    indsvalues = [(x.index(), val) for x, val in varvalues.items()] + [
      (x._expi.index(), mf.getctx().exp((mf.i * val).toctx()))
      for x, val in varvalues.items()
      if isinstance(x, Angle)
    ]
    # For each monomial in self
    for mon, coef in self.items():
      Rmon = mon.copy()
      # For each variable to be replaced:
      for k, valk in indsvalues:
        # Check if the variable is present in the monomial
        if k in mon:
          coef *= mf.smartpower(valk, mon[k])  # multiply the coef by valk**powk
          del Rmon[k]  # remove the variable from the monomial
      tmp = R.get(Rmon, 0) + coef  # Compute the new coef of monomial Rmon
      R[Rmon] = tmp  # put it in the series
      if tmp == 0:
        del R[Rmon]  # remove it if it is zero
    return R

  def substvars(self, newvars):
    r"""
    Replace some variables by other variables.

    Parameters
    ----------
    newvars : dict
      Dictionary of the form: variable -> variable.

    Returns
    -------
    R : Series
      Series where the provided variables have been replaced.
    """
    R = Series()
    # Build the list of variable index replacement
    newinds = [k for k in range(_State.nvars)]
    for x in newvars:
      newinds[x.index()] = newvars[x].index()
      # check if x and newvars[x] are angles (to add the expi(x) variable)
      if isinstance(x, Angle) and isinstance(newvars[x], Angle):
        newinds[x._expi.index()] = newvars[x]._expi.index()
    # For each monomial in the series
    for mon, coef in self.items():
      Rmon = _Monomial()
      # For each variable in the monomial
      for k, powk in mon.items():
        # Replace the variable by according to the newinds list
        tmp = Rmon.get(newinds[k], 0) + powk
        Rmon[newinds[k]] = tmp
        if tmp == 0:
          del Rmon[newinds[k]]  # Remove the variable if the power is 0
      R[Rmon] = coef
    return R

  def subst(self, x, Q, power=None, negative=False):
    r"""
    Replace a variable by a series.

    Parameters
    ----------
    x : Var
      Variable to be replaced.
    Q : Series
      Series to be substituted to x.
    power : int or None
      If a power is specified, x**(k*power+r) is replaced by Q**k * x**r,
      where k is an integer (which can be negative if negative is True),
      and r is an integer of the same sign as power and smaller in absolute value.
    negative : bool
      Whether to allow negative multiple of power.

    Returns
    -------
    R : Series
      Series where x has been replaced by Q.
    """
    # Find the min/max power of x in the series.
    pmin = self.minpow(x)
    pmax = self.maxpow(x)
    if pmax < pmin:
      return self.copy()
    R = Series()
    # Decide in which order to explore the powers of x
    # Such as powers of Q are increasing
    if power:
      if power > 0:
        rangep = range(pmin, pmax + 1)  # increasing order
        Qpowmin = pmin // power  # corresponding initial power of Q
      else:
        rangep = range(pmax, pmin - 1, -1)  # decreasing order
        Qpowmin = pmax // power  # corresponding initial power of Q
      if not negative:
        Qpowmin = max(0, Qpowmin)  # start from 0 if negative is False and Qpowmin < 0
    else:
      rangep = range(pmin, pmax + 1)  # increasing order
      Qpowmin = pmin  # corresponding initial power of Q

    # Compute the first needed power of Q
    Qp = Q**Qpowmin
    first = True
    # For each possible power of x
    for powk in rangep:
      # extract the corresponding series
      coefp = self.coefext({x: powk})
      # Check if this power of x should be replaced
      if (not power) or negative or power * powk > 0:
        # Compute the remaining power of x (integer r)
        r = 0 if not power else powk % power
        # Check if Qp should be raised to the next power of Q
        if r == 0 and not first:
          Qp *= Q
        # Add the new series to the result
        R += coefp * Qp * x**r
      else:
        R += coefp * x**powk  # copy the series as it was in self
      first = False
    return R

  def reverse(self, x):
    r"""
    Solve y = self(x) to express x as a series on y.

    Parameters
    ----------
    x : Var
      Variable to be reversed.

    Returns
    -------
    R : Series
      Reversed series where x now plays the role of y.
    """
    if x.index() not in _State.trunc_inds:
      raise Exception('reverse: no truncation set for ' + str(x))
    if self.minpow(x) != 1:
      raise Exception('reverse: minpow is not 1')
    R = Series()
    nvars = _State.nvars
    # Create temporary variables for the coefficients of the result.
    coefs = [
      Var(f'@@@coef_reverse_{d + nvars:d}@@@') for d in range(_State.trunc_degree)
    ]
    try:
      R = sum(coefs[d] * x ** (d + 1) for d in range(_State.trunc_degree))
      # Equation to be solved
      zero = self.subst(x, R) - x
      for d in range(_State.trunc_degree):
        # identify terms of degree d to solve for the corresponding coefficient
        eqd = zero.coefext({x: d + 1})
        coefd = -eqd.coefext({coefs[d]: 0}) / eqd.coefext({coefs[d]: 1})
        # Replace the coef by its value
        R = R.subst(coefs[d], coefd)
        zero = zero.subst(coefs[d], coefd)
    finally:
      # Delete temporary variables
      for coef in coefs:
        del _State.var_index[coef.name()]
      _State.var_list = _State.var_list[:nvars]
      _State.nvars = nvars
    return R

  def clean(self, epsilon=1e-16):
    r"""
    Clean the series from small coefficients.

    Parameters
    ----------
    epsilon : float
      Threshold to delete coefficients.

    Returns
    -------
    R : Series
      Cleaned series.
    """
    R = Series()
    for mon, coef in self.items():
      if mf.iscomplex(coef):
        intcr = int(coef.real)
        intci = int(coef.imag)
        # Check if real part is close to integer
        if abs(coef.real - intcr) < epsilon:
          coef = intcr + mf.i * coef.imag
        # Check if imaginary part is close to integer
        if abs(coef.imag - intci) < epsilon:
          coef = coef.real + mf.i * intci
        # Check if imaginary part is 0
        if coef.imag == 0:
          coef = coef.real
      elif mf.isfloat(coef):
        # Check if float is close to integer
        intc = int(coef)
        if abs(coef - intc) < epsilon:
          coef = intc
      # Check if coef is 0
      if coef != 0:
        R[mon] = coef
    return R

  def _format_coef(self, coef):
    """Format a coefficient to write it in a .pys file."""
    if mf.iscomplex(coef):
      return 'complex' + self._format_coef(coef.real) + self._format_coef(coef.imag)
    elif isinstance(coef, int):
      return f'int\t{coef:d}'
    elif isinstance(coef, mf.Fraction):
      return f'Fraction\t{coef.numerator:d}\t{coef.denominator:d}'
    elif mf.isfloat(coef):
      return f'float\t%.{mf.getctx().dps + 2:d}e' % coef
    else:
      raise Exception('Series._format_coef: Unknown coefficient type.')

  def save(self, filename):
    r"""
    Save the series to a file.

    Parameters
    ----------
    filename : str
      Filename.
    """

    # Find which variables are used in the series
    series_indices = []
    series_nvars = 0
    for mon in self:
      for index in mon:
        if index not in series_indices:
          series_indices.append(index)
          series_nvars += 1
    series_indices = sorted(series_indices)
    # Write file
    with open(filename, 'w') as sfile:
      # write number of variables used in series
      sfile.write(str(series_nvars) + '\n')
      # write variables names
      for index in series_indices:
        sfile.write(_State.var_list[index].name() + '\n')
      # write coefs and exponents
      for mon in sorted(self.keys()):
        coef = self[mon]
        line = '\t'.join([str(mon.get(index, 0)) for index in series_indices])
        line += '\t' + self._format_coef(coef)
        sfile.write(line + '\n')

  def _read_coef(self, elems):
    """Read a coefficient from a .pys file."""
    if elems[0] == 'complex':
      re, relems = self._read_coef(elems[1:])
      im, relems = self._read_coef(relems)
      return (mf.SmartComplex(re, im), relems)
    elif elems[0] == 'int':
      return (int(elems[1]), elems[2:])
    elif elems[0] == 'Fraction':
      return (mf.Fraction(elems[1] + '/' + elems[2]), elems[3:])
    elif elems[0] == 'float':
      return (mf.getctx().mpf(elems[1]), elems[2:])
    else:
      raise Exception('Series._read_coef: Unknown coefficient type.')

  @classmethod
  def load(cls, filename):
    r"""
    Load a series from a file.

    Parameters
    ----------
    filename : str
      Filename.
    """
    P = cls()
    with open(filename) as sfile:
      lines = sfile.read().splitlines()
    # read number of variables
    series_nvars = int(lines[0])
    # Get variables names and indices
    series_indices = [
      Angle(name[4:])._expi.index() if name.startswith('_ei_') else Var(name).index()
      for name in lines[1 : 1 + series_nvars]
    ]
    # read coefs and exponents
    for line in lines[1 + series_nvars :]:
      mon = _Monomial()
      elems = line.strip().split('\t')
      for k in range(series_nvars):
        powk = int(elems[k])
        if powk != 0:
          mon[series_indices[k]] = powk
      P[mon], _ = P._read_coef(elems[series_nvars:])
    return P


class Var(Series):
  r"""Variable (Var) class.

  Parameters
  ----------
  name : str
    Name of the variable.
  """

  def __init__(self, name):
    # Create a variable called name.
    # If a variable with the same name as already been defined,
    # the variable is not recreated.
    super().__init__()
    self._name = name
    self._expiangle = False
    if name not in _State.var_index:
      # Create the variable
      _State.var_list.append(self)
      _State.var_index[name] = _State.nvars
      _State.nvars += 1
    # Get its index
    self._index = _State.var_index[name]
    # Create the corresponding series.
    mon = _Monomial()
    mon[self._index] = 1
    self[mon] = 1

  def name(self):
    r"""
    Name of the variable.

    Returns
    -------
    name : str
      Name.
    """
    return self._name

  def rename(self, name):
    r"""
    Change the name of the variable.

    Parameters
    ----------
    name : str
      New name.
    """
    del _State.var_index[self._name]
    _State.var_index[name] = self._index
    self._name = name

  def index(self):
    r"""
    Index of the variable.

    Returns
    -------
    index : int
      Index.
    """
    return self._index

  def __hash__(self):
    """Hash function."""
    return self._name.__hash__()

  def __pow__(self, k):
    """Raise the variable to power k. Override the series method."""
    if isinstance(k, int):
      if k == 0:
        return Series() + 1
      else:
        R = Series()
        mon = _Monomial()
        mon[self._index] = k
        R[mon] = 1
        return R
    else:
      raise Exception('Var.__pow__: Cannot raise a variable to a non-integer power.')


class Angle(Var):
  r"""
  Angular variable class.

  An angle is a variable for which the cos, sin and expi function are defined.
  The expi is actually itself defined as a variable.

  Parameters
  ----------
  name : str
    Name of the angle.
  """

  def __init__(self, name):
    super().__init__(name)
    self._expi = Var('_ei_' + name)
    self._expi._expiangle = True

  def expi(self):
    r"""
    Imaginary exponential of the angle.

    Returns
    -------
    expi : Series
      Imaginary exponential.
    """
    return self._expi

  def cos(self):
    r"""
    Cosine of the angle.

    Returns
    -------
    cos : Series
      Cosine.
    """
    return (self._expi + 1 / self._expi) / 2

  def sin(self):
    r"""
    Sine of the angle.

    Returns
    -------
    sin : Series
      Sine.
    """
    return (self._expi - 1 / self._expi) / (2 * mf.i)

  def isin(self):
    r"""
    Imaginary sine of the angle.

    Returns
    -------
    isin : Series
      Imaginary sine.
    """
    return (self._expi - 1 / self._expi) / 2
