"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError(f"length mismatch: {len(human)} vs {len(judge)}")
    cm = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for h, j in zip(human, judge):
        if h not in ("PASS", "FAIL") or j not in ("PASS", "FAIL"):
            raise ValueError(f"non-binary label: human={h!r} judge={j!r}")
        if j == POS:                       # judge says FAIL
            cm["tp" if h == POS else "fp"] += 1
        else:                              # judge says PASS
            cm["fn" if h == POS else "tn"] += 1
    return cm


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    cm = confusion(human, judge)
    p = cm["tp"] / (cm["tp"] + cm["fp"]) if cm["tp"] + cm["fp"] else 0.0
    r = cm["tp"] / (cm["tp"] + cm["fn"]) if cm["tp"] + cm["fn"] else 0.0
    return p, r


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    if len(human) != len(judge):
        raise ValueError(f"length mismatch: {len(human)} vs {len(judge)}")
    n = len(human)
    p_o = sum(1 for h, j in zip(human, judge) if h == j) / n
    h_yes = sum(1 for h in human if h == POS) / n
    j_yes = sum(1 for j in judge if j == POS) / n
    p_e = h_yes * j_yes + (1 - h_yes) * (1 - j_yes)        # expected agreement by chance
    if p_e >= 1.0:
        raise ValueError("kappa undefined: expected agreement is 1 (constant judge)")
    return (p_o - p_e) / (1 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    denom = sensitivity + specificity - 1.0
    if denom <= 0.0:
        raise ValueError("Rogan-Gladen undefined: sensitivity + specificity - 1 <= 0")
    p = (observed_rate + specificity - 1.0) / denom
    return min(1.0, max(0.0, p))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    import numpy as np
    from scipy.stats import bootstrap
    diffs = [float(x) - float(y) for x, y in zip(a, b)]
    if all(d == 0.0 for d in diffs):
        return (0.0, 0.0, 0.0)
    data = (np.asarray(diffs, dtype=float),)
    res = bootstrap(data, np.mean, n_resamples=n_resamples, paired=True, method="percentile",
                    confidence_level=confidence, rng=np.random.default_rng(rng))
    lo, hi = res.confidence_interval.low, res.confidence_interval.high
    return (float(np.mean(diffs)), float(lo), float(hi))


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    raise NotImplementedError
