"""Labelled synthetic training data for the mule-risk classifier.

There is no real labelled mule dataset in this repository (and there should not be
— all data here is synthetic by design). So instead of faking a dataset, we
generate one from explicit, documented *behavioural archetypes*. Each archetype is
a probability distribution over the feature space that encodes one real typology
described in the mule-network literature.

The important design choice is the **hard negatives**. A naive generator makes
legitimate accounts look uniformly boring, which trains a model that simply flags
"high volume" and produces a wall of false positives on merchants. So three of the
archetypes here are legitimate accounts that superficially resemble mules — a
merchant with heavy fan-in, a payroll account with heavy fan-out, and a genuine
high-value one-off transfer. The model is forced to learn that what separates a
mule is *pass-through velocity combined with behavioural deviation and unstable
counterparties*, not volume alone.

A small amount of label noise is injected on purpose. A model that scores a
perfect 1.00 PR-AUC is not impressive, it is a sign of leakage — and any reviewer
who knows ML will read it that way.
"""
from __future__ import annotations

from typing import Any

from app.ml.feature_spec import FEATURE_NAMES, to_named_vector

# Share of the dataset that is mule-positive.
POSITIVE_RATE = 0.34
# Fraction of labels deliberately flipped to model imperfect ground truth.
LABEL_NOISE = 0.03


def _clip(value: float, low: float, high: float) -> float:
    return float(min(high, max(low, value)))


def _split_fan(rng: Any, fan_in_mean: float, spread: float) -> tuple[float, float]:
    """Generate a fan-in / fan-out pair that sums to ~1, mirroring the live engine.

    ``StatisticalFeatureEngine`` derives these as ``in_degree / total_degree`` and
    ``out_degree / total_degree``, so they are complementary by construction. The
    generator must respect that or the model learns an impossible region.
    """
    fan_in = _clip(rng.normal(fan_in_mean, spread), 0.02, 0.98)
    return round(fan_in, 2), round(1.0 - fan_in, 2)


# --------------------------------------------------------------------------- #
# Legitimate archetypes (label 0)
# --------------------------------------------------------------------------- #

def _retail_salaried(rng: Any) -> dict[str, float]:
    """Ordinary personal account: modest amounts, stable habits, retains balance."""
    fan_in, fan_out = _split_fan(rng, 0.45, 0.12)
    return {
        "transaction_amount": _clip(rng.lognormal(8.6, 0.7), 300, 180_000),
        "transaction_velocity": _clip(rng.normal(9, 4), 1, 30),
        "pass_through_ratio": _clip(rng.beta(2.0, 4.5), 0.02, 0.80),
        "behaviour_deviation": _clip(rng.lognormal(0.05, 0.35), 0.2, 3.2),
        "new_counterparty_ratio": _clip(rng.beta(2.0, 5.0), 0.02, 0.75),
        "network_degree": _clip(rng.normal(5, 2.5), 1, 16),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(0.0, 0.6), 0.15, 5.0),
        "in_cycle": 0.0,
    }


def _merchant_collector(rng: Any) -> dict[str, float]:
    """HARD NEGATIVE. Legitimate merchant: huge fan-in and velocity, but retains funds.

    Distinguishing signal vs a fan-in mule: low pass-through, low deviation, and a
    stable repeat-customer base (low new-counterparty dispersion).
    """
    fan_in, fan_out = _split_fan(rng, 0.86, 0.07)
    return {
        "transaction_amount": _clip(rng.lognormal(9.4, 0.8), 500, 500_000),
        "transaction_velocity": _clip(rng.normal(58, 22), 15, 140),
        "pass_through_ratio": _clip(rng.beta(2.2, 4.0), 0.05, 0.78),
        "behaviour_deviation": _clip(rng.lognormal(0.1, 0.4), 0.2, 3.6),
        "new_counterparty_ratio": _clip(rng.beta(1.8, 5.5), 0.02, 0.62),
        "network_degree": _clip(rng.normal(34, 12), 8, 90),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(1.2, 0.7), 0.4, 14.0),
        "in_cycle": 0.0,
    }


def _payroll_distributor(rng: Any) -> dict[str, float]:
    """HARD NEGATIVE. Legitimate payroll/vendor account: heavy fan-out and high pass-through.

    Looks like a smurfing distributor on volume alone. Separating signal: the
    beneficiary set is stable month to month (very low new-counterparty ratio) and
    amounts track a predictable baseline (low deviation).
    """
    fan_in, fan_out = _split_fan(rng, 0.14, 0.07)
    return {
        "transaction_amount": _clip(rng.lognormal(9.9, 0.7), 2_000, 900_000),
        "transaction_velocity": _clip(rng.normal(46, 18), 10, 130),
        "pass_through_ratio": _clip(rng.beta(6.0, 2.2), 0.35, 0.99),
        "behaviour_deviation": _clip(rng.lognormal(0.0, 0.3), 0.3, 2.4),
        "new_counterparty_ratio": _clip(rng.beta(1.4, 8.0), 0.01, 0.40),
        "network_degree": _clip(rng.normal(30, 11), 8, 85),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(0.7, 0.7), 0.3, 10.0),
        "in_cycle": 0.0,
    }


def _high_value_one_off(rng: Any) -> dict[str, float]:
    """HARD NEGATIVE. Genuine large transfer (property, vehicle, tuition).

    Extreme behaviour deviation and near-total pass-through — the two loudest mule
    signals — but almost no network footprint and a single counterparty.
    """
    fan_in, fan_out = _split_fan(rng, 0.50, 0.18)
    return {
        "transaction_amount": _clip(rng.lognormal(13.2, 0.6), 200_000, 6_000_000),
        "transaction_velocity": _clip(rng.normal(4, 2), 1, 10),
        "pass_through_ratio": _clip(rng.beta(5.0, 2.0), 0.30, 0.99),
        "behaviour_deviation": _clip(rng.lognormal(2.2, 0.6), 3.0, 45.0),
        "new_counterparty_ratio": _clip(rng.beta(3.0, 2.5), 0.10, 1.0),
        "network_degree": _clip(rng.normal(3, 1.6), 1, 8),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(-0.5, 0.5), 0.10, 2.5),
        "in_cycle": 0.0,
    }


# --------------------------------------------------------------------------- #
# Mule archetypes (label 1)
# --------------------------------------------------------------------------- #

def _rapid_relay(rng: Any) -> dict[str, float]:
    """Classic pass-through mule: funds in and straight back out within minutes."""
    fan_in, fan_out = _split_fan(rng, 0.45, 0.14)
    return {
        "transaction_amount": _clip(rng.lognormal(10.9, 0.9), 5_000, 1_200_000),
        "transaction_velocity": _clip(rng.normal(15, 8), 2, 60),
        "pass_through_ratio": _clip(rng.beta(14.0, 1.5), 0.72, 1.0),
        "behaviour_deviation": _clip(rng.lognormal(1.7, 0.7), 1.8, 60.0),
        "new_counterparty_ratio": _clip(rng.beta(7.0, 1.8), 0.45, 1.0),
        "network_degree": _clip(rng.normal(9, 4), 2, 30),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(0.6, 0.7), 0.2, 12.0),
        "in_cycle": float(rng.random() < 0.18),
    }


def _fanout_smurf(rng: Any) -> dict[str, float]:
    """Distribution mule: fragments one inbound sum across many fresh beneficiaries."""
    fan_in, fan_out = _split_fan(rng, 0.13, 0.08)
    return {
        "transaction_amount": _clip(rng.lognormal(10.2, 0.8), 3_000, 700_000),
        "transaction_velocity": _clip(rng.normal(30, 14), 6, 100),
        "pass_through_ratio": _clip(rng.beta(11.0, 1.6), 0.66, 1.0),
        "behaviour_deviation": _clip(rng.lognormal(1.5, 0.7), 1.5, 50.0),
        "new_counterparty_ratio": _clip(rng.beta(9.0, 1.3), 0.60, 1.0),
        "network_degree": _clip(rng.normal(24, 10), 6, 80),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(0.9, 0.7), 0.3, 13.0),
        "in_cycle": float(rng.random() < 0.22),
    }


def _fanin_aggregator(rng: Any) -> dict[str, float]:
    """Collection mule: many victim/mule accounts funnel into one cash-out point."""
    fan_in, fan_out = _split_fan(rng, 0.87, 0.07)
    return {
        "transaction_amount": _clip(rng.lognormal(10.6, 0.9), 4_000, 1_500_000),
        "transaction_velocity": _clip(rng.normal(33, 15), 6, 110),
        "pass_through_ratio": _clip(rng.beta(9.0, 1.8), 0.58, 1.0),
        "behaviour_deviation": _clip(rng.lognormal(1.6, 0.75), 1.5, 55.0),
        "new_counterparty_ratio": _clip(rng.beta(8.0, 1.5), 0.52, 1.0),
        "network_degree": _clip(rng.normal(27, 11), 6, 85),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(1.3, 0.8), 0.4, 16.0),
        "in_cycle": float(rng.random() < 0.25),
    }


def _circular_layering(rng: Any) -> dict[str, float]:
    """Layering mule: funds cycle through a closed loop to obscure origin."""
    fan_in, fan_out = _split_fan(rng, 0.50, 0.10)
    return {
        "transaction_amount": _clip(rng.lognormal(10.5, 0.9), 4_000, 1_000_000),
        "transaction_velocity": _clip(rng.normal(22, 10), 4, 80),
        "pass_through_ratio": _clip(rng.beta(10.0, 2.0), 0.55, 1.0),
        "behaviour_deviation": _clip(rng.lognormal(1.3, 0.7), 1.2, 40.0),
        "new_counterparty_ratio": _clip(rng.beta(4.0, 3.0), 0.20, 1.0),
        "network_degree": _clip(rng.normal(13, 6), 3, 45),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(1.0, 0.8), 0.3, 15.0),
        "in_cycle": 1.0,
    }


def _dormant_reactivated(rng: Any) -> dict[str, float]:
    """Rented/dormant account suddenly reactivated for a single large hop."""
    fan_in, fan_out = _split_fan(rng, 0.48, 0.16)
    return {
        "transaction_amount": _clip(rng.lognormal(11.4, 0.9), 8_000, 2_000_000),
        "transaction_velocity": _clip(rng.normal(4, 2), 1, 12),
        "pass_through_ratio": _clip(rng.beta(16.0, 1.4), 0.78, 1.0),
        "behaviour_deviation": _clip(rng.lognormal(3.0, 0.7), 8.0, 120.0),
        "new_counterparty_ratio": _clip(rng.beta(10.0, 1.2), 0.65, 1.0),
        "network_degree": _clip(rng.normal(4, 2), 1, 12),
        "fan_in_score": fan_in,
        "fan_out_score": fan_out,
        "pagerank_score": _clip(rng.lognormal(-0.3, 0.6), 0.1, 4.0),
        "in_cycle": 0.0,
    }


# archetype -> (generator, relative weight within its class)
LEGIT_ARCHETYPES: list[tuple[str, Any, float]] = [
    ("retail_salaried", _retail_salaried, 0.44),
    ("merchant_collector", _merchant_collector, 0.22),
    ("payroll_distributor", _payroll_distributor, 0.20),
    ("high_value_one_off", _high_value_one_off, 0.14),
]

MULE_ARCHETYPES: list[tuple[str, Any, float]] = [
    ("rapid_relay", _rapid_relay, 0.30),
    ("fanout_smurf", _fanout_smurf, 0.22),
    ("fanin_aggregator", _fanin_aggregator, 0.20),
    ("circular_layering", _circular_layering, 0.16),
    ("dormant_reactivated", _dormant_reactivated, 0.12),
]


def _pick(rng: Any, archetypes: list[tuple[str, Any, float]]):
    weights = [w for _, _, w in archetypes]
    total = sum(weights)
    idx = int(rng.choice(len(archetypes), p=[w / total for w in weights]))
    name, fn, _ = archetypes[idx]
    return name, fn


def generate_dataset(n_samples: int = 12_000, seed: int = 42):
    """Generate a labelled feature matrix.

    Returns ``(X, y, archetypes)`` where ``X`` is an ``(n_samples, n_features)``
    float array ordered by :data:`app.ml.feature_spec.FEATURE_NAMES`, ``y`` is the
    binary label array, and ``archetypes`` names the generator behind each row
    (useful for per-typology recall reporting).
    """
    import numpy as np

    rng = np.random.default_rng(seed)

    rows: list[list[float]] = []
    labels: list[int] = []
    archetypes: list[str] = []

    for _ in range(n_samples):
        is_mule = rng.random() < POSITIVE_RATE
        pool = MULE_ARCHETYPES if is_mule else LEGIT_ARCHETYPES
        name, fn = _pick(rng, pool)
        named = to_named_vector(fn(rng))

        label = 1 if is_mule else 0
        # Imperfect ground truth: some mules are never reported, some legitimate
        # accounts are wrongly flagged by human reviewers.
        if rng.random() < LABEL_NOISE:
            label = 1 - label

        rows.append([named[f] for f in FEATURE_NAMES])
        labels.append(label)
        archetypes.append(name)

    return (
        np.asarray(rows, dtype="float32"),
        np.asarray(labels, dtype="int32"),
        np.asarray(archetypes),
    )
