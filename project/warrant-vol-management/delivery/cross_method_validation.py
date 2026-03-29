#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""
Cross-method validation for spread unwinding using lattice, PDE, and LSM.

Unwind payoff definition used throughout:
long leg uses implied vol sigma_fair(S) + sigma_offset,
short leg uses fair vol sigma_fair(S),
exercise value = BS(long leg) - BS(short leg).
"""

import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import lattice
import monte_carlo
import pde


def _estimate_zero_crossing(spots: np.ndarray, premium: np.ndarray, side: str, K: float) -> float:
    """Estimate zero crossing on a given side of strike using linear interpolation."""
    if side not in ("left", "right"):
        raise ValueError("side must be 'left' or 'right'")

    candidates = []
    for i in range(len(spots) - 1):
        s1, s2 = float(spots[i]), float(spots[i + 1])
        p1, p2 = float(premium[i]), float(premium[i + 1])

        if side == "left" and not (s1 <= K and s2 <= K):
            continue
        if side == "right" and not (s1 >= K and s2 >= K):
            continue

        if np.isnan(p1) or np.isnan(p2):
            continue

        if p1 == 0.0:
            zero_spot = s1
        elif p2 == 0.0:
            zero_spot = s2
        elif p1 * p2 < 0.0:
            # Linear interpolation: p(s) = p1 + (p2 - p1) * (s - s1)/(s2 - s1)
            zero_spot = s1 - p1 * (s2 - s1) / (p2 - p1)
        else:
            continue
        candidates.append(zero_spot)

    if not candidates:
        return np.nan

    if side == "left":
        return float(max(candidates))
    return float(min(candidates))


def _build_scenario_summary(df: pd.DataFrame, K: float) -> pd.DataFrame:
    """Create scenario-level metrics across methods for each (sigma_spot, sigma_offset, option_type)."""
    scenario_keys = ["sigma_spot", "sigma_offset", "option_type"]
    rows = []

    for key, g in df.groupby(scenario_keys):
        g = g.sort_values("S0")
        row = {
            "sigma_spot": key[0],
            "sigma_offset": key[1],
            "option_type": key[2],
        }

        # 1) Pairwise average absolute errors across S0 grid (3 measures x 3 method pairs)
        row["avg_abs_err_option_lattice_pde"] = (g["lattice_option_value"] - g["pde_option_value"]).abs().mean()
        row["avg_abs_err_option_lattice_lsm"] = (g["lattice_option_value"] - g["lsm_option_value"]).abs().mean()
        row["avg_abs_err_option_pde_lsm"] = (g["pde_option_value"] - g["lsm_option_value"]).abs().mean()

        row["avg_abs_err_cont_lattice_pde"] = (g["lattice_continuation_value"] - g["pde_continuation_value"]).abs().mean()
        row["avg_abs_err_cont_lattice_lsm"] = (g["lattice_continuation_value"] - g["lsm_continuation_value"]).abs().mean()
        row["avg_abs_err_cont_pde_lsm"] = (g["pde_continuation_value"] - g["lsm_continuation_value"]).abs().mean()

        row["avg_abs_err_premium_lattice_pde"] = (g["lattice_exercise_premium"] - g["pde_exercise_premium"]).abs().mean()
        row["avg_abs_err_premium_lattice_lsm"] = (g["lattice_exercise_premium"] - g["lsm_exercise_premium"]).abs().mean()
        row["avg_abs_err_premium_pde_lsm"] = (g["pde_exercise_premium"] - g["lsm_exercise_premium"]).abs().mean()

        # 2) Average runtime per method
        row["avg_time_lattice_sec"] = g["lattice_time_sec"].mean()
        row["avg_time_pde_sec"] = g["pde_time_sec"].mean()
        row["avg_time_lsm_sec"] = g["lsm_time_sec"].mean()

        # 3) Zero points left/right of strike from premium curves
        spots = g["S0"].to_numpy(dtype=float)
        row["lattice_zero_left"] = _estimate_zero_crossing(spots, g["lattice_exercise_premium"].to_numpy(dtype=float), "left", K)
        row["lattice_zero_right"] = _estimate_zero_crossing(spots, g["lattice_exercise_premium"].to_numpy(dtype=float), "right", K)
        row["pde_zero_left"] = _estimate_zero_crossing(spots, g["pde_exercise_premium"].to_numpy(dtype=float), "left", K)
        row["pde_zero_right"] = _estimate_zero_crossing(spots, g["pde_exercise_premium"].to_numpy(dtype=float), "right", K)
        row["lsm_zero_left"] = _estimate_zero_crossing(spots, g["lsm_exercise_premium"].to_numpy(dtype=float), "left", K)
        row["lsm_zero_right"] = _estimate_zero_crossing(spots, g["lsm_exercise_premium"].to_numpy(dtype=float), "right", K)

        rows.append(row)

    return pd.DataFrame(rows).sort_values(scenario_keys).reset_index(drop=True)


def main() -> pd.DataFrame:
    sigma_fair = 0.20
    K = 100.0
    T = 1.0
    r = 0.05

    sigma_offset_list = [0.00, 0.1, 0.2]
    sigma_spot_list = [0.20, 0.25, 0.30, 0.35, 0.4, 0.45]
    option_types = ["call", "put"]
    s0_grid = np.linspace(50.0, 150.0, 11)

    n_t = 40
    mc_n_paths = 8000
    pde_S_min = 1.0
    pde_S_max = 300.0
    pde_n_S = 40

    print(
        f"Unified temporal grid: n_t={n_t} intervals for lattice/PDE/LSM "
        f"(all use dt=T/n_t)"
    )

    sigma_fair_func = lambda _s: sigma_fair
    rows = []

    total = len(sigma_spot_list) * len(sigma_offset_list) * len(option_types)
    done = 0

    for sigma_spot in sigma_spot_list:
        for sigma_offset in sigma_offset_list:
            for option_type in option_types:
                done += 1
                print(
                    f"[{done}/{total}] sigma_spot={sigma_spot:.2f}, "
                    f"sigma_offset={sigma_offset:.2f}, option={option_type}"
                )

                for s0 in s0_grid:
                    t0 = time.perf_counter()
                    lat_v, lat_ex, lat_cont = lattice.binomial_tree_value(
                        n_t, s0, K, T, r, sigma_spot, sigma_fair_func,
                        sigma_offset, option_type=option_type,
                    )
                    lat_time = time.perf_counter() - t0

                    t0 = time.perf_counter()
                    pde_v, pde_ex, pde_cont = pde.pde_value(
                        pde_S_min, pde_S_max, pde_n_S, n_t, s0, K, T, r,
                        sigma_spot, sigma_fair_func, sigma_offset,
                        option_type=option_type,
                    )
                    pde_time = time.perf_counter() - t0

                    t0 = time.perf_counter()
                    mc_v, mc_ex, mc_cont = monte_carlo.lsm_value(
                        mc_n_paths, n_t, s0, K, T, r, sigma_spot,
                        sigma_fair_func, sigma_offset,
                        option_type=option_type,
                    )
                    mc_time = time.perf_counter() - t0

                    rows.append(
                        {
                            "sigma_spot": sigma_spot,
                            "sigma_offset": sigma_offset,
                            "option_type": option_type,
                            "S0": float(s0),
                            "n_t": n_t,
                            "lattice_option_value": lat_v,
                            "pde_option_value": pde_v,
                            "lsm_option_value": mc_v,
                            "lattice_exercise_value": lat_ex,
                            "pde_exercise_value": pde_ex,
                            "lsm_exercise_value": mc_ex,
                            "lattice_continuation_value": lat_cont,
                            "pde_continuation_value": pde_cont,
                            "lsm_continuation_value": mc_cont,
                            "lattice_exercise_premium": lat_ex - lat_cont,
                            "pde_exercise_premium": pde_ex - pde_cont,
                            "lsm_exercise_premium": mc_ex - mc_cont,
                            "lattice_time_sec": lat_time,
                            "pde_time_sec": pde_time,
                            "lsm_time_sec": mc_time,
                        }
                    )

    df = pd.DataFrame(rows)
    os.makedirs("output", exist_ok=True)

    csv_path = "output/cross_method_validation.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")

    summary_df = _build_scenario_summary(df, K)
    summary_csv_path = "output/cross_method_validation_summary.csv"
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"Saved CSV: {summary_csv_path}")

    # Runtime comparison summary
    runtime_cols = ["lattice_time_sec", "pde_time_sec", "lsm_time_sec"]
    runtime_summary = df[runtime_cols].agg(["mean", "median", "min", "max"])
    print("\nRuntime summary (seconds per valuation):")
    print(runtime_summary.to_string(float_format=lambda x: f"{x:.6f}"))

    total_runtime = df[runtime_cols].sum()
    print("\nTotal runtime by method (seconds):")
    print(total_runtime.to_string(float_format=lambda x: f"{x:.3f}"))

    fig, axes = plt.subplots(len(sigma_spot_list), 2, figsize=(13, 4 * len(sigma_spot_list)), sharex=True)
    if len(sigma_spot_list) == 1:
        axes = np.array([axes])

    color_map = plt.get_cmap("tab10")

    for row, sigma_spot in enumerate(sigma_spot_list):
        for col, option_type in enumerate(option_types):
            ax = axes[row, col]
            for i, sigma_offset in enumerate(sigma_offset_list):
                subset = df[
                    (df["sigma_spot"] == sigma_spot)
                    & (df["sigma_offset"] == sigma_offset)
                    & (df["option_type"] == option_type)
                ].sort_values("S0")

                color = color_map(i)
                lbl = f"offset={sigma_offset:.2f}"
                ax.plot(
                    subset["S0"],
                    subset["lattice_exercise_premium"],
                    color=color,
                    linewidth=2,
                    label=f"{lbl} lattice",
                )
                ax.scatter(
                    subset["S0"],
                    subset["pde_exercise_premium"],
                    marker="x",
                    s=35,
                    color=color,
                    alpha=0.85,
                    label=f"{lbl} pde",
                )
                ax.scatter(
                    subset["S0"],
                    subset["lsm_exercise_premium"],
                    marker="+",
                    s=75,
                    linewidths=1.8,
                    color=color,
                    alpha=0.9,
                    label=f"{lbl} lsm",
                )

            ax.axhline(0.0, color="black", linestyle="--", linewidth=0.8)
            ax.axvline(K, color="gray", linestyle=":", linewidth=1.0)
            ax.set_title(f"{option_type} spread, sigma_spot={sigma_spot:.2f}")
            ax.set_xlabel("S0")
            ax.set_ylabel("exercise premium")
            ax.grid(alpha=0.3)

            if row == 0 and col == 0:
                ax.legend(loc="best", fontsize="small", ncol=2)

    fig.suptitle("Exercise premium comparison across methods", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    plot_path = "output/cross_method_premium_comparison.png"
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    print(f"Saved plot: {plot_path}")

    # Exercise (unwind) value comparison
    fig, axes = plt.subplots(len(sigma_spot_list), 2, figsize=(13, 4 * len(sigma_spot_list)), sharex=True)
    if len(sigma_spot_list) == 1:
        axes = np.array([axes])

    for row, sigma_spot in enumerate(sigma_spot_list):
        for col, option_type in enumerate(option_types):
            ax = axes[row, col]
            for i, sigma_offset in enumerate(sigma_offset_list):
                subset = df[
                    (df["sigma_spot"] == sigma_spot)
                    & (df["sigma_offset"] == sigma_offset)
                    & (df["option_type"] == option_type)
                ].sort_values("S0")

                color = color_map(i)
                lbl = f"offset={sigma_offset:.2f}"
                ax.plot(
                    subset["S0"],
                    subset["lattice_exercise_value"],
                    color=color,
                    linewidth=2,
                    label=f"{lbl} lattice",
                )
                ax.scatter(
                    subset["S0"],
                    subset["pde_exercise_value"],
                    marker="x",
                    s=35,
                    color=color,
                    alpha=0.85,
                    label=f"{lbl} pde",
                )
                ax.scatter(
                    subset["S0"],
                    subset["lsm_exercise_value"],
                    marker="+",
                    s=75,
                    linewidths=1.8,
                    color=color,
                    alpha=0.9,
                    label=f"{lbl} lsm",
                )

            ax.axvline(K, color="gray", linestyle=":", linewidth=1.0)
            ax.set_title(f"{option_type} spread, sigma_spot={sigma_spot:.2f}")
            ax.set_xlabel("S0")
            ax.set_ylabel("exercise value (unwind)")
            ax.grid(alpha=0.3)

            if row == 0 and col == 0:
                ax.legend(loc="best", fontsize="small", ncol=2)

    fig.suptitle("Exercise (unwind) value comparison across methods", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    plot_path = "output/cross_method_exercise_value_comparison.png"
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    print(f"Saved plot: {plot_path}")

    # Continuation value comparison
    fig, axes = plt.subplots(len(sigma_spot_list), 2, figsize=(13, 4 * len(sigma_spot_list)), sharex=True)
    if len(sigma_spot_list) == 1:
        axes = np.array([axes])

    for row, sigma_spot in enumerate(sigma_spot_list):
        for col, option_type in enumerate(option_types):
            ax = axes[row, col]
            for i, sigma_offset in enumerate(sigma_offset_list):
                subset = df[
                    (df["sigma_spot"] == sigma_spot)
                    & (df["sigma_offset"] == sigma_offset)
                    & (df["option_type"] == option_type)
                ].sort_values("S0")

                color = color_map(i)
                lbl = f"offset={sigma_offset:.2f}"
                ax.plot(
                    subset["S0"],
                    subset["lattice_continuation_value"],
                    color=color,
                    linewidth=2,
                    label=f"{lbl} lattice",
                )
                ax.scatter(
                    subset["S0"],
                    subset["pde_continuation_value"],
                    marker="x",
                    s=35,
                    color=color,
                    alpha=0.85,
                    label=f"{lbl} pde",
                )
                ax.scatter(
                    subset["S0"],
                    subset["lsm_continuation_value"],
                    marker="+",
                    s=75,
                    linewidths=1.8,
                    color=color,
                    alpha=0.9,
                    label=f"{lbl} lsm",
                )

            ax.axvline(K, color="gray", linestyle=":", linewidth=1.0)
            ax.set_title(f"{option_type} spread, sigma_spot={sigma_spot:.2f}")
            ax.set_xlabel("S0")
            ax.set_ylabel("continuation value")
            ax.grid(alpha=0.3)

            if row == 0 and col == 0:
                ax.legend(loc="best", fontsize="small", ncol=2)

    fig.suptitle("Continuation value comparison across methods", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    plot_path = "output/cross_method_continuation_value_comparison.png"
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    print(f"Saved plot: {plot_path}")

    return df


if __name__ == "__main__":
    main()