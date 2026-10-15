from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from analyze_phase_a import _load, analyze


def fixture(tmp_path, direction=1, days=7, missing=False):
    sites = pd.DataFrame({"pair_id": ["p1", "p1"], "site_id": ["A", "B"],
                          "lst_c": [40, 30], "calibration_offset_c": [0.3, -0.2]})
    rows = []
    for day in range(days):
        for i in range(24):
            stamp = datetime(2026, 10, 1, 12, tzinfo=timezone(timedelta(hours=5, minutes=30))) + timedelta(days=day, minutes=i * 10)
            rows.append(("A", stamp.isoformat(), 31 + direction + 0.3))
            if not missing or i < 10:
                rows.append(("B", stamp.isoformat(), 31 - 0.2))
    observations = pd.DataFrame(rows, columns=["site_id", "timestamp_local", "temp_c"])
    sp, op = tmp_path / "sites.csv", tmp_path / "observations.csv"
    sites.to_csv(sp, index=False)
    observations.to_csv(op, index=False)
    return sp, op



def declared_manifest(sites, observations, *, log_missing=True):
    """Synthetic declaration; never evidence of physical deployment."""
    start = datetime(2026, 10, 1, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    observed = set(zip(observations.site_id.astype(str),
                       pd.to_datetime(observations.timestamp_local, utc=True)
                       .dt.tz_convert("Asia/Kolkata").dt.date))
    log = []
    for site in sites.site_id.astype(str):
        for d in range(7):
            day = (start + timedelta(days=d)).date()
            if log_missing and (site, day) not in observed:
                log.append({"site_id": site, "date": day.isoformat(),
                            "reason": "No samples recovered; cause unknown"})
    return {"deployment_start_local": start.isoformat(),
            "deployment_end_local": (start + timedelta(days=7)).isoformat(),
            "site_ids": sites.site_id.astype(str).tolist(),
            "preselected_pairs": [
                {"pair_id": str(pid), "site_ids": group.site_id.astype(str).tolist()}
                for pid, group in sites.groupby("pair_id")
            ],
            "direction_uncertainty_c": 0.05,
            "direction_uncertainty_basis": "illustrative synthetic test bound only",
            "lst_direction_uncertainty_c": 0.05,
            "lst_direction_uncertainty_basis": "illustrative synthetic test bound only",
            "missingness_log_reviewed": True,
            "missingness_log": log}


def test_matching_and_calibration(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    result = analyze(sites, obs, manifest=declared_manifest(sites, obs))
    assert result["pairs"][0]["valid_days"] == 7
    assert result["pairs"][0]["air_contrast_c"] == pytest.approx(1)
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_incomplete_pilot"


def test_negative_result_is_retained(tmp_path):
    sites, obs = _load(*fixture(tmp_path, direction=-1))
    result = analyze(sites, obs, manifest=declared_manifest(sites, obs))
    assert result["pairs"][0]["agrees_with_LST_direction"] is False
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_incomplete_pilot"


def test_insufficient_matching_not_interpreted(tmp_path):
    sites, obs = _load(*fixture(tmp_path, missing=True))
    result = analyze(sites, obs)
    assert result["pairs"][0]["status"] == "insufficient_valid_days"
    assert result["pair_agreement"] is None


def test_naive_timestamps_rejected(tmp_path):
    sp, op = fixture(tmp_path)
    df = pd.read_csv(op)
    df["timestamp_local"] = df.timestamp_local.str.slice(0, 19)
    df.to_csv(op, index=False)
    with pytest.raises(ValueError, match="UTC offset"):
        _load(sp, op)


def test_duplicate_measurements_fail_closed(tmp_path):
    sp, op = fixture(tmp_path)
    df = pd.read_csv(op)
    pd.concat([df, df.iloc[[0]]]).to_csv(op, index=False)
    with pytest.raises(ValueError, match="duplicate"):
        _load(sp, op)


def test_equal_LST_is_unidentifiable(tmp_path):
    sp, op = fixture(tmp_path)
    df = pd.read_csv(sp)
    df.loc[:, "lst_c"] = 30
    df.to_csv(sp, index=False)
    sites, obs = _load(sp, op)
    result = analyze(sites, obs)
    assert result["pairs"][0]["status"] == "unidentifiable_equal_LST"
    assert result["pair_agreement"] is None


def test_seeded_day_block_interval_reproducible(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    assert analyze(sites, obs, seed=12) == analyze(sites, obs, seed=12)


def test_four_complete_pairs_support_a_falsification_decision(tmp_path):
    sp, op = fixture(tmp_path, direction=-1)
    sites = pd.read_csv(sp)
    obs = pd.read_csv(op)
    sites = pd.concat([sites.assign(pair_id=f"p{i}", site_id=lambda df: df.site_id + str(i)) for i in range(1, 5)], ignore_index=True)
    obs = pd.concat([obs.assign(site_id=lambda df: df.site_id + str(i)) for i in range(1, 5)], ignore_index=True)
    sites.to_csv(sp, index=False)
    obs.to_csv(op, index=False)
    loaded_sites, loaded_obs = _load(sp, op)
    result = analyze(loaded_sites, loaded_obs, manifest=declared_manifest(loaded_sites, loaded_obs))
    assert result["pair_agreement"]["eligible_pairs"] == 4
    assert result["pair_agreement"]["agree"] == 0
    assert result["pair_agreement"]["falsification_gate"] == "fail"


def test_three_eligible_of_four_is_inconclusive(tmp_path):
    sp, op = fixture(tmp_path)
    sites = pd.read_csv(sp)
    obs = pd.read_csv(op)
    sites = pd.concat([sites.assign(pair_id=f"p{i}", site_id=lambda df: df.site_id + str(i)) for i in range(1, 5)], ignore_index=True)
    obs = pd.concat([obs.assign(site_id=lambda df: df.site_id + str(i)) for i in range(1, 5)], ignore_index=True)
    obs = obs.loc[obs.site_id != "B4"]
    sites.to_csv(sp, index=False)
    obs.to_csv(op, index=False)
    loaded_sites, loaded_obs = _load(sp, op)
    result = analyze(loaded_sites, loaded_obs, manifest=declared_manifest(loaded_sites, loaded_obs))
    assert result["pair_agreement"]["eligible_pairs"] == 3
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_incomplete_pilot"


def test_burst_sampling_does_not_fake_daily_coverage(tmp_path):
    sp, op = fixture(tmp_path)
    obs = pd.read_csv(op)
    # 24 matched readings in just 4 minutes, for each of seven days.
    # Raw-count logic would incorrectly treat them as 24 ten-minute intervals.
    obs["timestamp_local"] = obs["timestamp_local"].map(
        lambda s: s[:11] + "12:00:00+05:30"
    )
    for day in range(7):
        mask = obs.timestamp_local.str.startswith(f"2026-10-{day+1:02d}")
        indices = obs.index[mask]
        for j, idx in enumerate(indices):
            minute = (j // 2) // 6
            second = (j // 2) % 6 * 10
            obs.loc[idx, "timestamp_local"] = f"2026-10-{day+1:02d}T12:{minute:02d}:{second:02d}+05:30"
    obs.to_csv(op, index=False)
    sites, readings = _load(sp, op)
    result = analyze(sites, readings)
    assert result["pairs"][0]["status"] == "insufficient_valid_days"
    assert result["pair_agreement"] is None


def test_eight_day_campaign_is_inconclusive(tmp_path):
    sp, op = fixture(tmp_path, days=4)
    sites, obs = pd.read_csv(sp), pd.read_csv(op)
    obs["timestamp_local"] = obs.timestamp_local.map(
        lambda s: (datetime.fromisoformat(s) + timedelta(days=4 if s.startswith("2026-10-04") else 0)).isoformat()
    )
    sites = pd.concat([sites.assign(pair_id=f"p{i}", site_id=lambda df: df.site_id + str(i)) for i in range(4)], ignore_index=True)
    obs = pd.concat([obs.assign(site_id=lambda df: df.site_id + str(i)) for i in range(4)], ignore_index=True)
    sites.to_csv(sp, index=False)
    obs.to_csv(op, index=False)
    result = analyze(*_load(sp, op))
    assert result["pair_agreement"]["eligible_pairs"] == 4
    assert result["campaign_window"]["calendar_days_spanned"] == 8
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_invalid_campaign_window"


def test_four_pairs_without_manifest_are_inconclusive(tmp_path):
    sp, op = fixture(tmp_path)
    sites, obs = pd.read_csv(sp), pd.read_csv(op)
    sites = pd.concat([sites.assign(pair_id=f"p{i}", site_id=lambda d: d.site_id + str(i))
                       for i in range(4)], ignore_index=True)
    obs = pd.concat([obs.assign(site_id=lambda d: d.site_id + str(i))
                     for i in range(4)], ignore_index=True)
    sites.to_csv(sp, index=False)
    obs.to_csv(op, index=False)
    result = analyze(*_load(sp, op))
    assert result["pair_agreement"]["eligible_pairs"] == 4
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_missing_deployment_manifest"


def test_four_observed_days_require_logged_missing_site_days(tmp_path):
    sp, op = fixture(tmp_path, days=4)
    sites, obs = pd.read_csv(sp), pd.read_csv(op)
    sites = pd.concat([sites.assign(pair_id=f"p{i}", site_id=lambda d: d.site_id + str(i))
                       for i in range(4)], ignore_index=True)
    obs = pd.concat([obs.assign(site_id=lambda d: d.site_id + str(i))
                     for i in range(4)], ignore_index=True)
    sites.to_csv(sp, index=False)
    obs.to_csv(op, index=False)
    sites, obs = _load(sp, op)
    declared = declared_manifest(sites, obs)
    result = analyze(sites, obs, manifest=declared)
    assert result["campaign_window"]["deployment_manifest_details"]["missingness_entries"] == 24
    assert result["pair_agreement"]["falsification_gate"] == "not_failed_on_observed_pairs"
    result = analyze(sites, obs, manifest=declared_manifest(sites, obs, log_missing=False))
    assert result["campaign_window"]["deployment_manifest_status"] == "unlogged_missing_site_day"
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_invalid_deployment_manifest"


def test_missingness_reason_must_be_nonempty_string(tmp_path):
    sp, op = fixture(tmp_path, days=4)
    sites, obs = _load(sp, op)
    for bad_reason in (None, float("nan"), 0, {}, "   "):
        manifest = declared_manifest(sites, obs)
        manifest["missingness_log"][0]["reason"] = bad_reason
        result = analyze(sites, obs, manifest=manifest)
        assert result["campaign_window"]["deployment_manifest_status"] == "invalid_missingness_entry"


def test_short_deployment_manifest_rejected(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    manifest = declared_manifest(sites, obs)
    manifest["deployment_end_local"] = "2026-10-05T00:00:00+05:30"
    result = analyze(sites, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "not_seven_full_days"


def test_observations_outside_declared_window_rejected(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    manifest = declared_manifest(sites, obs)
    manifest["deployment_start_local"] = "2026-10-02T00:00:00+05:30"
    manifest["deployment_end_local"] = "2026-10-09T00:00:00+05:30"
    result = analyze(sites, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "observations_outside_deployment"


def test_manifest_site_ids_require_explicit_list(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    manifest = declared_manifest(sites, obs)
    manifest["site_ids"] = "AB"
    result = analyze(sites, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "invalid_format"


def test_missingness_log_rejects_timestamp_instead_of_date(tmp_path):
    sites, obs = _load(*fixture(tmp_path, days=4))
    manifest = declared_manifest(sites, obs)
    manifest["missingness_log"][0]["date"] += "T23:59:00"
    result = analyze(sites, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "invalid_missingness_entry"


def test_missingness_log_rejects_duplicate_site_day(tmp_path):
    sites, obs = _load(*fixture(tmp_path, days=4))
    manifest = declared_manifest(sites, obs)
    manifest["missingness_log"].append(dict(manifest["missingness_log"][0]))
    result = analyze(sites, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "invalid_missingness_entry"


def test_manifest_requires_explicit_preselected_pairs(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    manifest = declared_manifest(sites, obs)
    del manifest["preselected_pairs"]
    result = analyze(sites, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "invalid_preselected_pairs"


def test_manifest_rejects_duplicate_and_malformed_pairs(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    for bad in (
        [{"pair_id": "p1", "site_ids": ["A", "B"]},
         {"pair_id": "p1", "site_ids": ["A", "B"]}],
        [{"pair_id": "p1", "site_ids": ["A", "A"]}],
        [{"pair_id": "p1", "site_ids": "AB"}],
    ):
        manifest = declared_manifest(sites, obs)
        manifest["preselected_pairs"] = bad
        result = analyze(sites, obs, manifest=manifest)
        assert result["campaign_window"]["deployment_manifest_status"] == "invalid_preselected_pairs"


def test_reassigning_same_sites_invalidates_preregistered_pairs(tmp_path):
    sp, op = fixture(tmp_path)
    original_sites, original_obs = pd.read_csv(sp), pd.read_csv(op)
    sites = pd.concat([
        original_sites.assign(pair_id=f"p{i}", site_id=lambda frame: frame.site_id + str(i))
        for i in (1, 2)
    ], ignore_index=True)
    obs = pd.concat([
        original_obs.assign(site_id=lambda frame: frame.site_id + str(i))
        for i in (1, 2)
    ], ignore_index=True)
    sites.to_csv(sp, index=False)
    obs.to_csv(op, index=False)
    sites, obs = _load(sp, op)
    manifest = declared_manifest(sites, obs)
    assert analyze(sites, obs, manifest=manifest)["campaign_window"]["deployment_manifest_status"] == (
        "declared_seven_days_not_independently_verified"
    )
    tampered = sites.copy()
    tampered.loc[tampered.site_id == "B1", "pair_id"] = "p2"
    tampered.loc[tampered.site_id == "B2", "pair_id"] = "p1"
    result = analyze(tampered, obs, manifest=manifest)
    assert result["campaign_window"]["deployment_manifest_status"] == "preselected_pair_set_mismatch"
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_invalid_deployment_manifest"
    assert len(result["pairs"]) == 2  # Retain descriptive contrasts, even for invalid declarations.
