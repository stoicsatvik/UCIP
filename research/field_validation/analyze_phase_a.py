#!/usr/bin/env python3
"""UCIP Phase A matched-site diagnostic. No real field observations included.

Usage: python analyze_phase_a.py sites.csv observations.csv > report.json
Sites: pair_id,site_id,lst_c,calibration_offset_c
Observations: site_id,timestamp_local,temp_c
Timestamps must include UTC offsets; matching requires exact UTC instants.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

IST = "Asia/Kolkata"
MIN_MATCHED_INTERVALS_PER_DAY = 18
MIN_VALID_DAYS = 4
MAX_CAMPAIGN_CALENDAR_DAYS = 7
PREREGISTERED_PAIRS = 4
BOOTSTRAP_SAMPLES = 2000


def _load(sites_path: Path, obs_path: Path):
    sites = pd.read_csv(sites_path)
    obs = pd.read_csv(obs_path)
    if not {"pair_id", "site_id", "lst_c", "calibration_offset_c"} <= set(sites):
        raise ValueError("sites.csv missing required columns")
    if not {"site_id", "timestamp_local", "temp_c"} <= set(obs):
        raise ValueError("observations.csv missing required columns")
    # Missing CSV identifiers can match other missing identifiers in pandas.
    # Fail closed before matching observations to site metadata.
    if (sites.site_id.isna().any()
            or sites.site_id.astype(str).str.strip().eq("").any()
            or sites.pair_id.isna().any()
            or sites.pair_id.astype(str).str.strip().eq("").any()
            or sites.site_id.duplicated().any()):
        raise ValueError("site_id must be unique and nonempty; pair_id must be nonempty")
    if obs.site_id.isna().any() or obs.site_id.astype(str).str.strip().eq("").any():
        raise ValueError("observation site_id must be nonempty")
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



def _check_deployment_manifest(manifest: dict | None, sites: pd.DataFrame, obs: pd.DataFrame):
    """Validate declared deployment provenance, not physical sensor operation."""
    if manifest is None:
        return "missing", None
    if not isinstance(manifest, dict):
        return "invalid_format", None
    try:
        start = pd.Timestamp(manifest["deployment_start_local"])
        end = pd.Timestamp(manifest["deployment_end_local"])
        if start.tzinfo is None or end.tzinfo is None:
            return "invalid_timezone", None
        start, end = start.tz_convert(IST), end.tz_convert(IST)
        if (start.hour, start.minute, start.second, start.microsecond) != (0, 0, 0, 0):
            return "start_not_midnight", None
        if (end.hour, end.minute, end.second, end.microsecond) != (0, 0, 0, 0):
            return "end_not_midnight", None
        if end - start != pd.Timedelta(days=7):
            return "not_seven_full_days", None
        site_ids = manifest["site_ids"]
        if (not isinstance(site_ids, list)
                or not all(isinstance(site, str) and site.strip() for site in site_ids)
                or len(site_ids) != len(set(site_ids))):
            return "invalid_format", None
        if sorted(site_ids) != sorted(map(str, sites.site_id)):
            return "site_set_mismatch", None
        # Site membership alone does not preserve the preregistered matching.
        # This is a structural check, not independent timestamped preregistration.
        declared_pairs = manifest.get("preselected_pairs")
        if not isinstance(declared_pairs, list):
            return "invalid_preselected_pairs", None
        expected_pairs = {str(pid): sorted(group.site_id.astype(str).tolist())
                          for pid, group in sites.groupby("pair_id")}
        observed_pairs = {}
        for pair in declared_pairs:
            if not isinstance(pair, dict):
                return "invalid_preselected_pairs", None
            pid, members = pair.get("pair_id"), pair.get("site_ids")
            if (not isinstance(pid, str) or not pid.strip()
                    or pid in observed_pairs or not isinstance(members, list)
                    or len(members) != 2
                    or not all(isinstance(x, str) and x.strip() for x in members)
                    or len(set(members)) != 2):
                return "invalid_preselected_pairs", None
            observed_pairs[pid] = sorted(members)
        if observed_pairs != expected_pairs:
            return "preselected_pair_set_mismatch", None
        # Uncertainty bounds must be independently justified and frozen before
        # field outcomes are examined. They are not inferred from this dataset.
        air_bound = manifest.get("direction_uncertainty_c")
        air_basis = manifest.get("direction_uncertainty_basis")
        if (isinstance(air_bound, bool) or not isinstance(air_bound, (int, float))
                or not np.isfinite(air_bound) or air_bound <= 0
                or not isinstance(air_basis, str) or not air_basis.strip()):
            return "invalid_direction_uncertainty", None
        lst_bound = manifest.get("lst_direction_uncertainty_c")
        lst_basis = manifest.get("lst_direction_uncertainty_basis")
        if (isinstance(lst_bound, bool) or not isinstance(lst_bound, (int, float))
                or not np.isfinite(lst_bound) or lst_bound <= 0
                or not isinstance(lst_basis, str) or not lst_basis.strip()):
            return "invalid_lst_direction_uncertainty", None
        log = manifest["missingness_log"]
        if not isinstance(log, list) or manifest.get("missingness_log_reviewed") is not True:
            return "missingness_not_reviewed", None
        observed = set(zip(obs.site_id.astype(str), obs.local.dt.date))
        recorded = set()
        for entry in log:
            site = str(entry["site_id"])
            date_value = entry["date"]
            if not isinstance(date_value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value) is None:
                return "invalid_missingness_entry", None
            day = pd.Timestamp(date_value)
            if (site not in set(map(str, sites.site_id))
                    or day.tzinfo is not None
                    or not start.date() <= day.date() < end.date()
                    or not isinstance(entry["reason"], str)
                    or not entry["reason"].strip()
                    or (site, day.date()) in observed
                    or (site, day.date()) in recorded):
                return "invalid_missingness_entry", None
            recorded.add((site, day.date()))
        if not obs.empty and ((obs.local < start) | (obs.local >= end)).any():
            return "observations_outside_deployment", None
        for site in map(str, sites.site_id):
            for day in pd.date_range(start, periods=7, freq="D"):
                if (site, day.date()) not in observed and (site, day.date()) not in recorded:
                    return "unlogged_missing_site_day", None
        return "declared_seven_days_not_independently_verified", {
            "start_local": start.isoformat(),
            "end_local_exclusive": end.isoformat(),
            "missingness_entries": len(log),
            "direction_uncertainty_c": float(air_bound),
            "direction_uncertainty_basis": air_basis,
            "lst_direction_uncertainty_c": float(lst_bound),
            "lst_direction_uncertainty_basis": lst_basis}
    except (KeyError, TypeError, ValueError, OverflowError):
        return "invalid_format", None


def analyze(sites: pd.DataFrame, obs: pd.DataFrame, *, seed: int = 20261013,
            manifest: dict | None = None):
    rng = np.random.default_rng(seed)
    manifest_status, manifest_details = _check_deployment_manifest(manifest, sites, obs)
    air_bound = (manifest_details["direction_uncertainty_c"]
                 if manifest_details is not None else None)
    lst_bound = (manifest_details["lst_direction_uncertainty_c"]
                 if manifest_details is not None else None)
    # Use every observation, including those outside the analysis hours, so
    # extra campaign days cannot disappear when the midday filter is applied.
    campaign_days = ((obs.local.dt.date.max() - obs.local.dt.date.min()).days + 1
                     if not obs.empty else 0)
    campaign_valid = 0 < campaign_days <= MAX_CAMPAIGN_CALENDAR_DAYS
    obs = obs.loc[(obs.local.dt.hour >= 12) & (obs.local.dt.hour < 16)].copy()
    obs = obs.merge(sites[["site_id", "calibration_offset_c"]], on="site_id", validate="many_to_one")
    obs["corrected_c"] = obs.temp_c - obs.calibration_offset_c
    output = {"status": "diagnostic_only_not_HVI_validation", "pairs": [], "pair_agreement": None,
              "campaign_window": {"calendar_days_spanned": int(campaign_days),
                                  "within_preregistered_seven_day_window": bool(campaign_valid),
                                  "deployment_manifest_status": manifest_status,
                                  "deployment_manifest_details": manifest_details}}
    for pair_id, pair_sites in sites.groupby("pair_id", sort=True):
        high, low = pair_sites.sort_values(["lst_c", "site_id"], ascending=[False, True]).iloc[:2].to_dict("records")
        lst_diff = float(high["lst_c"] - low["lst_c"])
        if lst_diff <= 0:
            output["pairs"].append({"pair_id": str(pair_id), "status": "unidentifiable_equal_LST"})
            continue
        if lst_bound is not None and lst_diff <= lst_bound:
            output["pairs"].append({"pair_id": str(pair_id),
                                    "status": "unidentifiable_LST_within_uncertainty",
                                    "lst_contrast_c": lst_diff,
                                    "lst_direction_uncertainty_c": lst_bound})
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
            direction = (None if air_bound is not None and abs(contrast) <= air_bound
                         else True if contrast > 0 else False if contrast < 0 else None)
            item.update(status="descriptive_only", air_contrast_c=round(contrast, 5),
                        air_contrast_unrounded_c=contrast,
                        direction_uncertainty_c=air_bound,
                        agrees_with_LST_direction=direction,
                        day_block_bootstrap_95pct_c=[round(float(lo), 5), round(float(hi), 5)])
        output["pairs"].append(item)
    eligible = [p for p in output["pairs"] if p["status"] == "descriptive_only"]
    if eligible:
        n_agree = sum(p["agrees_with_LST_direction"] is True for p in eligible)
        n_contrary = sum(p["agrees_with_LST_direction"] is False for p in eligible)
        n_neutral = sum(p["agrees_with_LST_direction"] is None for p in eligible)
        complete = (len(output["pairs"]) == PREREGISTERED_PAIRS
                    and len(eligible) == PREREGISTERED_PAIRS)
        gate = ("inconclusive_invalid_campaign_window" if not campaign_valid else
                "inconclusive_missing_deployment_manifest" if manifest_status == "missing" else
                "inconclusive_invalid_deployment_manifest" if manifest_status != "declared_seven_days_not_independently_verified" else
                "inconclusive_incomplete_pilot" if not complete else
                "fail" if n_contrary >= 2 else
                "inconclusive_zero_air_contrast" if n_neutral else
                "not_failed_on_observed_pairs")
        output["pair_agreement"] = {"agree": n_agree, "contrary": n_contrary, "neutral": n_neutral,
                                    "eligible_pairs": len(eligible),
                                    "all_preselected_pairs": len(output["pairs"]),
                                    "falsification_gate": gate,
                                    "warning": "Descriptive feasibility only; small nonrandom site sample."}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sites", type=Path)
    parser.add_argument("observations", type=Path)
    parser.add_argument("--manifest", type=Path, help="JSON declaration of deployment and missingness")
    args = parser.parse_args()
    sites, obs = _load(args.sites, args.observations)
    manifest = json.loads(args.manifest.read_text()) if args.manifest else None
    print(json.dumps(analyze(sites, obs, manifest=manifest), indent=2))


if __name__ == "__main__":
    main()
