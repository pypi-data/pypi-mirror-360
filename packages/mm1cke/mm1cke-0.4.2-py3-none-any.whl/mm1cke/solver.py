import logging

import numpy as np
import polars as pl
from scipy.integrate import solve_ivp

from .case import Epoch, TimeDependentCase

log = logging.getLogger(__name__)


def rhs_transient(t, p, lamT, muT, ls_max):
    """
    RHS of the CKEs
    rhs_transient(t,p,coef) implements the right hand sides of the CKE at time t and state vector p[]
    """
    i = 0
    pdot = np.zeros(ls_max + 1)

    cT = 1

    pdot[0] = muT * p[1] - lamT * p[0]
    for i in range(1, cT):
        pdot[i] = (
            (i + 1) * muT * p[i + 1]
            + lamT * p[i - 1]
            - (i * muT + lamT) * p[i]
        )
    for i in range(cT, ls_max):
        pdot[i] = (
            cT * muT * p[i + 1] + lamT * p[i - 1] - (cT * muT + lamT) * p[i]
        )
    pdot[ls_max] = lamT * p[ls_max - 1] - cT * muT * p[ls_max]

    return pdot


def solve_transient(
    case_config: Epoch, return_df=True, convergence_atol=1e-8
) -> pl.DataFrame:
    log.debug(f"Solve transient. Case: {case_config}")
    ls_max = case_config.ls_max
    time_step = case_config.time_step

    rows = []

    pT = np.zeros(ls_max + 1)

    if case_config.L_0 is not None:
        try:
            pT[case_config.L_0] = 1
        except Exception as e:
            log.error(f"Could not set p to 1: {case_config.L_0=}")
            log.exception(e)
            raise e
    elif case_config.p0 is not None:
        pT = case_config.p0

    if case_config.off_set == 0:
        rows = [
            dict(t=case_config.off_set, l_s=l_s, p=p)
            for l_s, p in zip(np.arange(0, ls_max + 1), pT)
        ]

    t = 0.0
    while True:
        log.debug(f"Entering main transient loop. {t=}")
        last_pT = pT.copy()
        time_step = (
            time_step
            if case_config.duration is None
            else min(case_config.duration - t, time_step)
        )
        solver = solve_ivp(
            fun=rhs_transient,
            args=(
                case_config.arrival_rate,
                case_config.service_rate,
                ls_max,
            ),
            method="RK45",
            y0=pT,
            t_span=[t, t + time_step],
            rtol=1e-8,
        )

        pT = solver.y[:, -1]
        if np.sum(pT) != 1:
            pT = pT / np.sum(pT)

        new_rows = [
            dict(t=t + case_config.off_set + time_step, l_s=l_s, p=p)
            for l_s, p in zip(np.arange(0, ls_max + 1), pT)
        ]
        rows.extend(new_rows)

        if (
            t > 0
            and case_config.duration is None
            and np.allclose(last_pT, pT, atol=convergence_atol)
        ):
            log.debug(f"Converged {t=}. Terminating main loop.")
            break
        if (
            case_config.duration is not None
            and t + time_step >= case_config.duration
        ):
            log.debug(
                f"Reached T={case_config.duration} Terminating main loop."
            )
            break
        t += time_step

    if return_df:
        return pl.DataFrame(rows)
    else:
        return rows, pT


def solve_time_dependent(td_case: TimeDependentCase):
    rows = []
    pT = None
    for e, epoch in enumerate(td_case.iter_epochs()):
        if e > 0:
            epoch.p0 = pT
        log.info(f"Current epoch: {epoch}")

        epoch_row, pT = solve_transient(epoch, return_df=False)
        rows.extend(epoch_row)
    return pl.DataFrame(rows)
