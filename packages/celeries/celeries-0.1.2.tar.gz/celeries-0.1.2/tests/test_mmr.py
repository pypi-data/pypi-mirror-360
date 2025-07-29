import numpy as np
from celeries import mmr


def test_32_d1_ell():
  Hmmr = mmr.MMR(1, np.array([1e-5, 1e-5]), np.array([2, 3]), 1)

  ell0 = np.array([[1.0, 0.05, 0, 0], [1.51 ** (2 / 3), 0.05, 0, np.pi]])
  v0, delta, Gamma = Hmmr.ell2v(ell0)
  sol_fp = Hmmr.solve_fp(v0, delta)

  # Check convergence
  assert sol_fp.success

  v_fp = sol_fp.x

  # Check fp is in the x plane (y = 0), i,e., sig_i = 0, pi
  assert np.all(np.abs(v_fp[:2]) < 1e-8 * np.abs(v_fp[2:]))

  eig_val, Q = Hmmr.fp_modes(v_fp, delta)
  iQ = np.linalg.inv(Q)

  # Check fp is elliptical
  assert np.all(np.abs(eig_val.real) / (1e-40 + np.abs(eig_val.imag)) < 1e-8)

  # Check modes are eigenmodes:
  Jac = Hmmr.eval_grad_dv(v_fp, delta)
  assert np.all(
    np.abs(iQ @ Jac @ Q - np.diag(eig_val)) < 1e-8 * np.max(np.abs(eig_val))
  )

  # Check modes are symplectic:
  symp = Q.T @ Hmmr.J @ Q
  assert np.all(np.abs(symp - Hmmr.J) < 1e-8)

  # Check modes are u, -i conj(u)
  assert np.all(np.abs(iQ[Hmmr.ndof :] + 1j * np.conj(iQ[: Hmmr.ndof])) < 1e-8)


def test_32_d1_hyp():
  Hmmr = mmr.MMR(1, np.array([1e-5, 1e-5]), np.array([2, 3]), 1)

  ell0 = np.array([[1.0, 0.05, 0, np.pi], [1.499 ** (2 / 3), 0.05, 0, 0]])
  v0, delta, Gamma = Hmmr.ell2v(ell0)
  sol_fp = Hmmr.solve_fp(v0, delta)

  # Check convergence
  assert sol_fp.success

  v_fp = sol_fp.x

  # Check fp is in the x plane (y = 0), i,e., sig_i = 0, pi
  assert np.all(np.abs(v_fp[:2]) < 1e-8 * np.abs(v_fp[2:]))

  eig_val, Q = Hmmr.fp_modes(v_fp, delta)
  iQ = np.linalg.inv(Q)

  # Check fp is hyperbolic
  assert np.any(np.abs(eig_val.imag) / (1e-40 + np.abs(eig_val.real)) < 1e-8)

  # Check modes are eigenmodes:
  Jac = Hmmr.eval_grad_dv(v_fp, delta)
  print(iQ @ Jac @ Q)
  print(np.diag(iQ @ Jac @ Q))
  print(eig_val)
  assert np.all(
    np.abs(iQ @ Jac @ Q - np.diag(eig_val)) < 1e-8 * np.max(np.abs(eig_val))
  )

  # Check modes are symplectic:
  symp = Q.T @ Hmmr.J @ Q
  assert np.all(np.abs(symp - Hmmr.J) < 1e-8)
