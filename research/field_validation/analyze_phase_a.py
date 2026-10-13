#!/usr/bin/env python3
"""UCIP Phase A matched-site diagnostic. No real field observations included.

Usage: python analyze_phase_a.py sites.csv observations.csv > report.json
Sites: pair_id,site_id,lst_c,calibration_offset_c
Observations: site_id,timestamp_local,temp_c
Timestamps must include UTC offsets; matching requires exact UTC instants.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

IST = "Asia/Kolkata"
MIN_MATCHED_INTERVALS_PER_DAY = 18
MIN_VALID_DAYS = 4
PREREGISTERED_PAIRS = 4
BOOTSTRAP_SAMPLES = 2000


def _load(sites_path: Path, obs_path: Path):
    sites = pd.read_csv(sites_path)
    obs = pd.read_csv(obs_path)
    if not {"pair_id", "site_id", "lst_c", "calibration_offset_c"} <= set(sites):
        raise ValueError("sites.csv missing required columns")
    if not {"site_id", "timestamp_local", "temp_c"} <= set(obs):
        raise ValueError("observations.csv missing required columns")
    if sites.site_id.duplicated().any() or sites.pair_id.isna().any():
        raise ValueError("site_id must be unique and pair_id nonempty")
    if not sites.groupby("pair_id").size().eq(2).all():
        raise ValueError("each pair must contain exactly two sites")
    for col in ("lst_c", "calibration_offset_c"):
        sites[col] = pd.to_numeric(sites[col], errors="raise")
    obs["temp_c"] = pd.to_numeric(obs.temp_c, errors="raise")
    if not np.isfinite(sites[["lst_c", "calibration_offset_c"]].to_numpy()).all():
        raise ValueError("site values must be finite")
    if not np.isfinite(obs.temp_c.to_numpy()).all():
        raise ValueError("temperature values must be finite")
    if not obs.site_id.isin(sites.site_id).all():
        raise ValueError("unknown site_id in observations")
    if not obs.timestamp_local.astype(str).str.contains(r"(?:Z|[+-]\d\d:\d\d)$").all():
        raise ValueError("all timestamps must include UTC offset or Z")
    obs["utc"] = pd.to_datetime(obs.timestamp_local, utc=True, errors="raise")
    obs["local"] = obs.utc.dt.tz_convert(IST)
    if obs.duplicated(["site_id", "utc"]).any():
        raise ValueError("duplicate site/timestamp measurement")
    return sites, obs


def analyze(sites: pd.DataFrame, obs: pd.DataFrame, *, seed: int = 20261013):
    rng = np.random.default_rng(seed)
    obs = obs.loc[(obs.local.dt.hour >= 12) & (obs.local.dt.hour < 16)].copy()
    obs = obs.merge(sites[["site_id", "calibration_offset_c"]], on="site_id", validate="many_to_one")
    obs["corrected_c"] = obs.temp_c - obs.calibration_offset_c
    output = {"status": "diagnostic_only_not_HVI_validation", "pairs": [], "pair_agreement": None}
    for pair_id, pair_sites in sites.groupby("pair_id", sort=True):
        high, low = pair_sites.sort_values(["lst_c", "site_id"], ascending=[False, True]).iloc[:2].to_dict("records")
        lst_diff = float(high["lst_c"] - low["lst_c"])
        if lst_diff <= 0:
            output["pairs"].append({"pair_id": str(pair_id), "status": "unidentifiable_equal_LST"})
            continue
        pair_obs = obs[obs.site_id.isin([high["site_id"], low["site_id"]])]
        wide = pair_obs.pivot(index="utc", columns="site_id", values="corrected_c")
        if high["site_id"] not in wide or low["site_id"] not in wide:
            matched = pd.Series(dtype=float)
        else:
            matched = (wide[high["site_id"]] - wide[low["site_id"]]).dropna()
        if matched.empty:
            output["pairs"].append({"pair_id": str(pair_id), "status": "no_matched_observations"})
            continue
        # Count unique 10-minute bins, not raw samples: burst logging must not
        # masquerade as 75% coverage of the four-hour daily measurement window.
        local_times = matched.index.tz_convert(IST)
        day_data = pd.DataFrame({"difference_c": matched.to_numpy(),
                                 "day": local_times.date,
                                 "bin": local_times.floor("10min")})
        bin_means = day_data.groupby(["day", "bin"], sort=True)["difference_c"].mean()
        day_stats = bin_means.groupby(level="day").agg(n="size", mean="mean")
        valid = day_stats.loc[day_stats.n >= MIN_MATCHED_INTERVALS_PER_DAY, "mean"].to_numpy()
        item = {"pair_id": str(pair_id), "higher_LST_site": str(high["site_id"]),
                "lower_LST_site": str(low["site_id"]), "lst_contrast_c": lst_diff,
                "days_seen": int(len(day_stats)), "valid_days": int(len(valid)),
                "daily_differences_c": [round(float(v), 5) for v in valid]}
        if len(valid) < MIN_VALID_DAYS:
            item["status"] = "insufficient_valid_days"
        else:
            contrast = float(np.mean(valid))
            draws = np.mean(rng.choice(valid, size=(BOOTSTRAP_SAMPLES, len(valid)), replace=True), axis=1)
            lo, hi = np.quantile(draws, [0.025, 0.975])
            item.update(status="descriptive_only", air_contrast_c=round(contrast, 5),
                        agrees_with_LST_direction=bool(contrast > 0),
                        day_block_bootstrap_95pct_c=[round(float(lo), 5), round(float(hi), 5)])
        output["pairs"].append(item)
    eligible = [p for p in output["pairs"] if p["status"] == "descriptive_only"]
    if eligible:
        n_agree = sum(p["agrees_with_LST_direction"] for p in eligible)
        complete = len(output["pairs"]) == PREREGISTERED_PAIRS and len(eligible) == PREREGISTERED_PAIRS
        gate = ("inconclusive_incomplete_pilot" if not complete else
                "fail" if n_agree <= PREREGISTERED_PAIRS / 2 else "not_failed_on_observed_pairs")
        output["pair_agreement"] = {"agree": n_agree, "eligible_pairs": len(eligible),
                                    "all_preselected_pairs": len(output["pairs"]),
                                    "falsification_gate": gate,
                                    "warning": "Descriptive feasibility only; small nonrandom site sample."}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sites", type=Path)
    parser.add_argument("observations", type=Path)
    args = parser.parse_args()
    sites, obs = _load(args.sites, args.observations)
    print(json.dumps(analyze(sites, obs), indent=2))


if __name__ == "__main__":
    main()
