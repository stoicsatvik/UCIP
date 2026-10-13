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


def test_matching_and_calibration(tmp_path):
    sites, obs = _load(*fixture(tmp_path))
    result = analyze(sites, obs)
    assert result["pairs"][0]["valid_days"] == 7
    assert result["pairs"][0]["air_contrast_c"] == pytest.approx(1)
    assert result["pair_agreement"]["falsification_gate"] == "inconclusive_incomplete_pilot"


def test_negative_result_is_retained(tmp_path):
    sites, obs = _load(*fixture(tmp_path, direction=-1))
    result = analyze(sites, obs)
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
    result = analyze(*_load(sp, op))
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
    result = analyze(*_load(sp, op))
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
