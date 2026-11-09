"""
Module 4 — Synthetic Warehouse Congestion Data Generator

Generates realistic time-dependent warehouse traffic data with:
- Order-volume patterns
- Dock utilization
- Staff shifts
- Truck-arrival bursts
- Shift changes
- Congestion buildup and recovery
- Temporal persistence
- Random operational disturbances

Output:
    data/synthetic_warehouse_congestion.csv

Run:
    python generate_synthetic_data.py
"""

import os
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "synthetic_warehouse_congestion.csv"
)


def generate(n_rows=25000, seed=42):

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # TIME
    # ---------------------------------------------------------

    timestamps = pd.date_range(
        start="2025-01-01 00:00:00",
        periods=n_rows,
        freq="30min"
    )

    hour = timestamps.hour
    day_of_week = timestamps.dayofweek

    # Weekend indicator
    is_weekend = (day_of_week >= 5).astype(int)

    # ---------------------------------------------------------
    # CYCLIC TIME FEATURES
    # ---------------------------------------------------------

    hour_angle = 2 * np.pi * hour / 24

    daily_pattern = (
        0.5
        + 0.5 * np.sin(hour_angle - np.pi / 2)
    )

    # ---------------------------------------------------------
    # SHIFT
    # ---------------------------------------------------------

    # 3 warehouse shifts
    shift = np.select(
        [
            hour < 8,
            (hour >= 8) & (hour < 16),
            hour >= 16
        ],
        [
            0,
            1,
            2
        ]
    )

    # Staff availability by shift
    base_staff = np.select(
        [
            shift == 0,
            shift == 1,
            shift == 2
        ],
        [
            16,
            30,
            24
        ]
    ).astype(float)

    # Reduced weekend staffing
    base_staff -= is_weekend * 6

    # Shift-change periods temporarily reduce effective staff
    shift_change = (
        ((hour == 7) | (hour == 15) | (hour == 23))
        .astype(int)
    )

    base_staff -= shift_change * 4

    staff_count = (
        base_staff
        + rng.normal(0, 2.5, n_rows)
    )

    staff_count = np.clip(
        np.round(staff_count),
        4,
        40
    ).astype(int)

    # ---------------------------------------------------------
    # ORDER VOLUME
    # ---------------------------------------------------------

    # Base warehouse order activity
    order_base = (
        75
        + 35 * daily_pattern
    )

    # Business-hour increase
    business_hours = (
        ((hour >= 7) & (hour <= 19))
        .astype(float)
    )

    order_base += 30 * business_hours

    # Weekend reduction
    order_base -= 20 * is_weekend

    # Random variation
    order_volume = rng.poisson(
        np.clip(order_base, 5, None)
    )

    # ---------------------------------------------------------
    # TRUCK ARRIVALS
    # ---------------------------------------------------------

    truck_rate = (
        4
        + 6 * business_hours
        + 4 * (order_volume / max(order_volume.mean(), 1))
    )

    truck_arrivals = rng.poisson(
        np.clip(truck_rate, 1, None)
    )

    # ---------------------------------------------------------
    # BURST EVENTS
    # ---------------------------------------------------------

    # Some time periods experience sudden truck/order bursts.
    burst_probability = 0.035

    burst_event = (
        rng.random(n_rows) < burst_probability
    ).astype(int)

    burst_strength = np.where(
        burst_event == 1,
        rng.uniform(1.5, 2.5, n_rows),
        1.0
    )

    order_volume = np.round(
        order_volume * burst_strength
    ).astype(int)

    truck_arrivals = np.round(
        truck_arrivals * burst_strength
    ).astype(int)

    # ---------------------------------------------------------
    # DOCK UTILIZATION
    # ---------------------------------------------------------

    # Dock utilization depends on:
    # - orders
    # - truck arrivals
    # - time of day
    # - previous congestion
    # - random noise

    utilization_base = (
        0.20
        + 0.0035 * order_volume
        + 0.025 * truck_arrivals
        + 0.15 * business_hours
    )

    dock_utilization = (
        utilization_base
        + rng.normal(0, 0.06, n_rows)
    )

    # ---------------------------------------------------------
    # TEMPORAL CONGESTION PRESSURE
    # ---------------------------------------------------------

    pressure = np.zeros(n_rows)

    for i in range(n_rows):

        current_pressure = (
            0.004 * order_volume[i]
            + 0.20 * dock_utilization[i]
            + 0.035 * truck_arrivals[i]
            - 0.035 * staff_count[i]
        )

        # Congestion persists from previous period
        if i > 0:
            current_pressure += 0.35 * pressure[i - 1]

        # Burst events create additional pressure
        if burst_event[i]:
            current_pressure += 0.6

        pressure[i] = current_pressure

    # ---------------------------------------------------------
    # NORMALIZE DOCK UTILIZATION
    # ---------------------------------------------------------

    dock_utilization = np.clip(
        dock_utilization
        + 0.08 * np.tanh(pressure - 0.5),
        0.05,
        1.0
    )

    # ---------------------------------------------------------
    # CONGESTION PROBABILITY
    # ---------------------------------------------------------

    # Logistic congestion model used ONLY to generate
    # realistic synthetic labels.

    raw_risk = (
        -5.0
        + 4.8 * dock_utilization
        + 0.018 * order_volume
        + 0.075 * truck_arrivals
        - 0.09 * staff_count
        + 0.65 * burst_event
        + 0.35 * shift_change
    )

    # Temporal persistence
    temporal_component = np.zeros(n_rows)

    for i in range(1, n_rows):
        temporal_component[i] = (
            0.25 * temporal_component[i - 1]
        )

    raw_risk += temporal_component

    congestion_probability = (
        1 / (1 + np.exp(-raw_risk))
    )

    # Add a small amount of uncertainty so the target
    # isn't perfectly deterministic.
    congestion_probability = np.clip(
        congestion_probability
        + rng.normal(0, 0.04, n_rows),
        0.001,
        0.999
    )

    # ---------------------------------------------------------
    # SAMPLE CONGESTION LABEL
    # ---------------------------------------------------------

    congestion = (
        rng.random(n_rows)
        < congestion_probability
    ).astype(int)

    # ---------------------------------------------------------
    # FINAL DATAFRAME
    # ---------------------------------------------------------

    df = pd.DataFrame({
        "timestamp": timestamps,
        "hour": hour,
        "day_of_week": day_of_week,
        "shift": shift,
        "shift_change": shift_change,
        "order_volume": order_volume,
        "truck_arrivals": truck_arrivals,
        "dock_utilization": dock_utilization,
        "staff_count": staff_count,
        "burst_event": burst_event,
        "congestion": congestion
    })

    return df


if __name__ == "__main__":

    print("Generating synthetic warehouse congestion data...")

    df = generate()

    os.makedirs(
        os.path.dirname(OUT_PATH),
        exist_ok=True
    )

    df.to_csv(
        OUT_PATH,
        index=False
    )

    print()
    print("=" * 60)
    print("Synthetic warehouse dataset created")
    print("=" * 60)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Congestion rate: {df['congestion'].mean():.2%}")
    print(f"Output: {OUT_PATH}")
    print("=" * 60)

    print("\nClass distribution:")
    print(
        df["congestion"]
        .value_counts(normalize=True)
        .sort_index()
    )

    print("\nFirst five rows:")
    print(df.head())