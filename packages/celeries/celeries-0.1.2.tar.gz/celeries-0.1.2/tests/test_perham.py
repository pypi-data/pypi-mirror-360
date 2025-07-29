import celeries.series as se
from celeries.perham import PerHam


def test_21_d1():
  ph = PerHam(1, 1)

  # Direct part
  h21 = ph.direct([1, -2])
  c1 = 2 * h21.coefext({ph.X[0]: 1})
  c2 = 2 * h21.coefext({ph.X[1]: 1})

  # Indirect part
  hi21 = ph.indirect([1, -2])
  ci1 = 2 * hi21.coefext({ph.X[0]: 1})
  ci2 = 2 * hi21.coefext({ph.X[1]: 1})

  # From Delisle (2017) Appendix B:
  assert c1 == ph.b[(3, 0)] * (-1 - ph.alpha**2 * 5 / 2) + ph.b[(3, 1)] * (
    ph.alpha ** (-1) * 2 / 3 + ph.alpha * 7 / 6 + ph.alpha**3 * 5 / 3
  )
  assert c2 == ph.b[(3, 0)] * ph.alpha * 5 / 2 - ph.b[(3, 1)] * (
    1 + ph.alpha**2 * 3 / 2
  )
  assert ci1 == se.Series()
  assert ci2 == se.Series() + 1


def test_coorb_d2():
  ph = PerHam(2, -1)

  hd = ph.coorbital_direct()
  hi = ph.coorbital_indirect()

  # Planar-circular part
  hd0 = hd.coefext({x: 0 for x in ph.XY})
  hi0 = hi.coefext({x: 0 for x in ph.XY})

  # Robutel & Pousse (2013) Eq. 11
  assert hd0 == 1 / ph.sqA
  assert hi0 == ph.theta.cos()

  # Eccentric part (deg 2)
  # Robutel & Pousse (2013) Eqs. 34, 36
  de1 = hd.coefext({ph.X[0]: 1, ph.Xb[0]: 1})
  ie1 = hi.coefext({ph.X[0]: 1, ph.Xb[0]: 1})
  de1sqA5 = (de1 * ph.sqA**5).subst(
    ph.sqA, 1 + ph.alpha**2 - 2 * ph.alpha * ph.theta.cos(), 2
  )
  assert de1sqA5 == -ph.alpha / 8 * (
    ph.alpha * (5 * (2 * ph.theta).cos() - 13) + 4 * (1 + ph.alpha**2) * ph.theta.cos()
  )
  assert ie1 == -ph.theta.cos() / 2

  de2 = hd.coefext({ph.X[1]: 1, ph.Xb[1]: 1})
  ie2 = hi.coefext({ph.X[1]: 1, ph.Xb[1]: 1})
  assert de2 == de1
  assert ie2 == ie1

  de12 = hd.coefext({ph.X[0]: 1, ph.Xb[1]: 1})
  ie12 = hi.coefext({ph.X[0]: 1, ph.Xb[1]: 1})
  de12sqA5 = (de12 * ph.sqA**5).subst(
    ph.sqA, 1 + ph.alpha**2 - 2 * ph.alpha * ph.theta.cos(), 2
  )
  assert de12sqA5 == ph.alpha / 16 * (
    ph.alpha * ((-3 * ph.theta).expi() + 9 * ph.theta.expi() - 26 / ph.theta.expi())
    + 8 * (1 + ph.alpha**2) / ph.theta.expi() ** 2
  )
  assert ie12 == 1 / (2 * ph.theta.expi() ** 2)

  # Inclination part (deg 2)
  # Robutel & Pousse (2013) Eqs. 35, 36
  # There is a sign error for theta in Bv (Eq. 36) of RP13
  # it should be exp(-i theta) instead of exp(i theta)
  # See Morais (1999) Eq. 18 19 + Morais (2001) Eq. 5
  di1 = hd.coefext({ph.Y[0]: 1, ph.Yb[0]: 1})
  ii1 = hi.coefext({ph.Y[0]: 1, ph.Yb[0]: 1})
  assert di1 == -ph.alpha / ph.sqA**3 * ph.theta.cos()
  assert ii1 == -ph.theta.cos()

  di2 = hd.coefext({ph.Y[1]: 1, ph.Yb[1]: 1})
  ii2 = hi.coefext({ph.Y[1]: 1, ph.Yb[1]: 1})
  assert di2 == di1
  assert ii2 == ii1

  di12 = hd.coefext({ph.Y[0]: 1, ph.Yb[1]: 1})
  ii12 = hi.coefext({ph.Y[0]: 1, ph.Yb[1]: 1})
  assert di12 == ph.alpha / ph.sqA**3 / ph.theta.expi()
  assert ii12 == 1 / ph.theta.expi()
