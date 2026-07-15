#!/usr/bin/env python3
"""Reproducible random-selector ablation for arXiv:2607.01037 public market data.

Uses the public Chang/Knazakis pairwise-correlation datasets, the thresholds printed
in the finance paper, and an implementation of the exposed-clique reduction rule
used in the public qReduMIS repository.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence, Set, Tuple

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

Adj = Dict[int, Set[int]]


@dataclass(frozen=True)
class InstanceSpec:
    name: str
    path: str
    threshold: float
    paper_original_n: int
    paper_kernel_n: int
    paper_density: float
    paper_pmis: float
    paper_ar: float


SPECS = [
    InstanceSpec("DAX 100", "/mnt/data/assets2.txt", 0.24, 85, 49, 0.29, 0.95, 1.00),
    InstanceSpec("FTSE 100", "/mnt/data/assets3.txt", 0.32, 89, 45, 0.28, 0.70, 0.98),
    InstanceSpec("S&P 100", "/mnt/data/assets4.txt", 0.24, 98, 68, 0.20, 0.40, 0.96),
    InstanceSpec("Nikkei 225", "/mnt/data/assets5.txt", 0.62, 225, 78, 0.17, 0.95, 0.99),
]


def parse_correlation_graph(path: str, threshold: float) -> Adj:
    lines = Path(path).read_text(encoding="utf-8").strip().splitlines()
    n = int(lines[0].strip())
    # Next n rows contain return and standard deviation; remaining rows contain i,j,corr.
    adj: Adj = {i: set() for i in range(n)}
    for line in lines[1 + n :]:
        parts = line.split()
        if len(parts) != 3:
            continue
        i, j = int(parts[0]) - 1, int(parts[1]) - 1
        corr = float(parts[2])
        if i != j and abs(corr) > threshold:
            adj[i].add(j)
            adj[j].add(i)
    return adj


def copy_adj(adj: Mapping[int, Set[int]]) -> Adj:
    return {v: set(nbrs) for v, nbrs in adj.items()}


def remove_vertices(adj: MutableMapping[int, Set[int]], vertices: Iterable[int]) -> None:
    doomed = set(vertices)
    for v in doomed:
        for u in list(adj.get(v, ())):
            if u not in doomed and u in adj:
                adj[u].discard(v)
    for v in doomed:
        adj.pop(v, None)


def is_exposed_clique(adj: Mapping[int, Set[int]], v: int) -> bool:
    nbrs = adj[v]
    # Empty / singleton neighborhoods are cliques.
    if len(nbrs) <= 1:
        return True
    nbr_list = list(nbrs)
    for idx, u in enumerate(nbr_list):
        au = adj[u]
        for w in nbr_list[idx + 1 :]:
            if w not in au:
                return False
    return True


def exact_reduce(adj: Mapping[int, Set[int]]) -> Tuple[Adj, List[int]]:
    """Apply exposed-neighborhood-clique reductions to a fixed point.

    Candidate order mirrors the public reducer's degree-then-node ordering.
    The selected nodes are provably extendable to an MIS under this reduction.
    """
    g = copy_adj(adj)
    selected: List[int] = []
    while True:
        chosen = None
        for v in sorted(g, key=lambda x: (len(g[x]), x)):
            if is_exposed_clique(g, v):
                chosen = v
                break
        if chosen is None:
            break
        selected.append(chosen)
        remove_vertices(g, set(g[chosen]) | {chosen})
    return g, selected


def graph_edges(adj: Mapping[int, Set[int]]) -> List[Tuple[int, int]]:
    return [(u, v) for u, nbrs in adj.items() for v in nbrs if u < v]


def density(adj: Mapping[int, Set[int]]) -> float:
    n = len(adj)
    if n < 2:
        return 0.0
    return 2.0 * len(graph_edges(adj)) / (n * (n - 1))


def exact_mis_size(adj: Mapping[int, Set[int]], time_limit: float = 120.0) -> int:
    """Solve unweighted MIS exactly using SciPy/HiGHS MILP."""
    nodes = sorted(adj)
    n = len(nodes)
    if n == 0:
        return 0
    index = {v: i for i, v in enumerate(nodes)}
    edges = graph_edges(adj)
    if not edges:
        return n
    rows: List[int] = []
    cols: List[int] = []
    vals: List[float] = []
    for r, (u, v) in enumerate(edges):
        rows.extend((r, r))
        cols.extend((index[u], index[v]))
        vals.extend((1.0, 1.0))
    A = coo_matrix((vals, (rows, cols)), shape=(len(edges), n)).tocsr()
    constraints = LinearConstraint(A, lb=np.full(len(edges), -np.inf), ub=np.ones(len(edges)))
    res = milp(
        c=-np.ones(n),
        integrality=np.ones(n, dtype=int),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=constraints,
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )
    if not res.success or res.fun is None:
        raise RuntimeError(f"MILP failed: status={res.status}, message={res.message}")
    return int(round(-float(res.fun)))


def first_kernel_safe_fraction(kernel: Mapping[int, Set[int]], alpha_kernel: int) -> Tuple[int, int, float]:
    safe = 0
    for v in sorted(kernel):
        reduced = copy_adj(kernel)
        remove_vertices(reduced, set(reduced[v]) | {v})
        # Reduction does not alter optimum except by number selected; using it speeds the MILP.
        k2, sel2 = exact_reduce(reduced)
        a2 = len(sel2) + exact_mis_size(k2)
        if 1 + a2 == alpha_kernel:
            safe += 1
    total = len(kernel)
    return safe, total, safe / total if total else 1.0


def choose_random(g: Mapping[int, Set[int]], rng: np.random.Generator) -> int:
    nodes = np.fromiter(g.keys(), dtype=np.int64)
    return int(nodes[rng.integers(0, len(nodes))])


def choose_max_degree(g: Mapping[int, Set[int]]) -> int:
    return min(g, key=lambda v: (-len(g[v]), v))


def choose_max_reduction_gain(g: Mapping[int, Set[int]]) -> int:
    """Choose v maximizing immediate vertices eliminated after delete N[v] + exact reduction."""
    n0 = len(g)
    best_v = None
    best_key = None
    for v in sorted(g):
        h = copy_adj(g)
        remove_vertices(h, set(h[v]) | {v})
        h2, sel2 = exact_reduce(h)
        eliminated = n0 - len(h2)
        # Prefer more eliminated, then more selected by exact reduction, then higher degree.
        key = (eliminated, len(sel2), len(g[v]), -v)
        if best_key is None or key > best_key:
            best_key = key
            best_v = v
    assert best_v is not None
    return best_v


def run_policy(
    first_kernel: Mapping[int, Set[int]],
    initial_selected: int,
    policy: str,
    rng: np.random.Generator | None = None,
) -> Tuple[int, int, List[int]]:
    g = copy_adj(first_kernel)
    selected_count = initial_selected
    informer_calls = 0
    trajectory = [len(g)]
    while g:
        # Kernel should already be reduced at the top of each iteration.
        if policy == "random":
            assert rng is not None
            v = choose_random(g, rng)
        elif policy == "max_degree":
            v = choose_max_degree(g)
        elif policy == "max_reduction_gain":
            v = choose_max_reduction_gain(g)
        else:
            raise ValueError(policy)
        informer_calls += 1
        selected_count += 1
        remove_vertices(g, set(g[v]) | {v})
        g, sel = exact_reduce(g)
        selected_count += len(sel)
        trajectory.append(len(g))
    return selected_count, informer_calls, trajectory


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - half, center + half


def mean_ci(values: Sequence[float], z: float = 1.959963984540054) -> Tuple[float, float]:
    n = len(values)
    if n < 2:
        return (values[0], values[0]) if n else (math.nan, math.nan)
    m = statistics.fmean(values)
    s = statistics.stdev(values)
    half = z * s / math.sqrt(n)
    return m - half, m + half


def benchmark_instance(spec: InstanceSpec, trials: int, seed: int) -> dict:
    t0 = time.time()
    original = parse_correlation_graph(spec.path, spec.threshold)
    first_kernel, init_sel_nodes = exact_reduce(original)
    initial_selected = len(init_sel_nodes)

    alpha_original = exact_mis_size(original)
    alpha_kernel = exact_mis_size(first_kernel)
    reduction_identity_ok = alpha_original == initial_selected + alpha_kernel
    if not reduction_identity_ok:
        raise AssertionError(
            f"Reduction identity failed for {spec.name}: {alpha_original} != {initial_selected}+{alpha_kernel}"
        )

    safe, total, safe_frac = first_kernel_safe_fraction(first_kernel, alpha_kernel)

    rng = np.random.default_rng(seed)
    successes = 0
    ars: List[float] = []
    kernel_ars: List[float] = []
    calls: List[int] = []
    success_within5 = 0
    trajectories_sample: List[List[int]] = []
    for i in range(trials):
        size, n_calls, traj = run_policy(first_kernel, initial_selected, "random", rng)
        success = size == alpha_original
        successes += int(success)
        ar = size / alpha_original
        kernel_ar = (size - initial_selected) / alpha_kernel
        ars.append(ar)
        kernel_ars.append(kernel_ar)
        calls.append(n_calls)
        if success and n_calls <= 5:
            success_within5 += 1
        if i < 25:
            trajectories_sample.append(traj)

    p = successes / trials
    p_lo, p_hi = wilson_interval(successes, trials)
    mean_ar = statistics.fmean(ars)
    ar_lo, ar_hi = mean_ci(ars)
    mean_kernel_ar = statistics.fmean(kernel_ars)
    kernel_ar_lo, kernel_ar_hi = mean_ci(kernel_ars)

    deterministic = {}
    for policy in ("max_degree", "max_reduction_gain"):
        size, n_calls, traj = run_policy(first_kernel, initial_selected, policy)
        deterministic[policy] = {
            "solution_size": size,
            "success": size == alpha_original,
            "approximation_ratio": size / alpha_original,
            "kernel_approximation_ratio": (size - initial_selected) / alpha_kernel,
            "informer_calls": n_calls,
            "trajectory": traj,
        }

    return {
        "instance": spec.name,
        "threshold_printed": spec.threshold,
        "public_data_original_n": len(original),
        "paper_original_n": spec.paper_original_n,
        "public_reconstruction_kernel_n": len(first_kernel),
        "public_reconstruction_kernel_edges": len(graph_edges(first_kernel)),
        "public_reconstruction_density": density(first_kernel),
        "paper_kernel_n": spec.paper_kernel_n,
        "paper_density": spec.paper_density,
        "kernel_matches_paper_n": len(first_kernel) == spec.paper_kernel_n,
        "initial_exact_reduction_selected": initial_selected,
        "alpha_original": alpha_original,
        "alpha_first_kernel": alpha_kernel,
        "reduction_identity_ok": reduction_identity_ok,
        "first_kernel_safe_nodes": safe,
        "first_kernel_total_nodes": total,
        "first_kernel_safe_fraction": safe_frac,
        "random_trials": trials,
        "random_seed": seed,
        "random_successes": successes,
        "random_success_probability": p,
        "random_success_ci95": [p_lo, p_hi],
        "random_mean_ar": mean_ar,
        "random_mean_ar_ci95": [ar_lo, ar_hi],
        "random_mean_kernel_ar": mean_kernel_ar,
        "random_mean_kernel_ar_ci95": [kernel_ar_lo, kernel_ar_hi],
        "random_mean_informer_calls": statistics.fmean(calls),
        "random_median_informer_calls": statistics.median(calls),
        "random_p95_informer_calls": float(np.quantile(calls, 0.95)),
        "random_probability_success_within_5_calls": success_within5 / trials,
        "random_trajectory_samples": trajectories_sample,
        "max_degree": deterministic["max_degree"],
        "max_reduction_gain": deterministic["max_reduction_gain"],
        "paper_qredumis_pmis": spec.paper_pmis,
        "paper_qredumis_mean_ar": spec.paper_ar,
        "elapsed_seconds": time.time() - t0,
    }


def write_outputs(results: List[dict], out_json: str, out_csv: str) -> None:
    Path(out_json).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = [
        "instance",
        "threshold_printed",
        "public_data_original_n",
        "public_reconstruction_kernel_n",
        "public_reconstruction_density",
        "paper_kernel_n",
        "paper_density",
        "kernel_matches_paper_n",
        "alpha_original",
        "alpha_first_kernel",
        "initial_exact_reduction_selected",
        "first_kernel_safe_nodes",
        "first_kernel_total_nodes",
        "first_kernel_safe_fraction",
        "random_trials",
        "random_success_probability",
        "random_success_ci95_low",
        "random_success_ci95_high",
        "random_mean_ar",
        "random_mean_ar_ci95_low",
        "random_mean_ar_ci95_high",
        "random_mean_kernel_ar",
        "random_mean_kernel_ar_ci95_low",
        "random_mean_kernel_ar_ci95_high",
        "random_mean_informer_calls",
        "random_p95_informer_calls",
        "random_probability_success_within_5_calls",
        "max_degree_success",
        "max_degree_ar",
        "max_degree_kernel_ar",
        "max_degree_calls",
        "max_reduction_gain_success",
        "max_reduction_gain_ar",
        "max_reduction_gain_kernel_ar",
        "max_reduction_gain_calls",
        "paper_qredumis_pmis",
        "paper_qredumis_mean_ar",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            row = {
                "instance": r["instance"],
                "threshold_printed": r["threshold_printed"],
                "public_data_original_n": r["public_data_original_n"],
                "public_reconstruction_kernel_n": r["public_reconstruction_kernel_n"],
                "public_reconstruction_density": r["public_reconstruction_density"],
                "paper_kernel_n": r["paper_kernel_n"],
                "paper_density": r["paper_density"],
                "kernel_matches_paper_n": r["kernel_matches_paper_n"],
                "alpha_original": r["alpha_original"],
                "alpha_first_kernel": r["alpha_first_kernel"],
                "initial_exact_reduction_selected": r["initial_exact_reduction_selected"],
                "first_kernel_safe_nodes": r["first_kernel_safe_nodes"],
                "first_kernel_total_nodes": r["first_kernel_total_nodes"],
                "first_kernel_safe_fraction": r["first_kernel_safe_fraction"],
                "random_trials": r["random_trials"],
                "random_success_probability": r["random_success_probability"],
                "random_success_ci95_low": r["random_success_ci95"][0],
                "random_success_ci95_high": r["random_success_ci95"][1],
                "random_mean_ar": r["random_mean_ar"],
                "random_mean_ar_ci95_low": r["random_mean_ar_ci95"][0],
                "random_mean_ar_ci95_high": r["random_mean_ar_ci95"][1],
                "random_mean_kernel_ar": r["random_mean_kernel_ar"],
                "random_mean_kernel_ar_ci95_low": r["random_mean_kernel_ar_ci95"][0],
                "random_mean_kernel_ar_ci95_high": r["random_mean_kernel_ar_ci95"][1],
                "random_mean_informer_calls": r["random_mean_informer_calls"],
                "random_p95_informer_calls": r["random_p95_informer_calls"],
                "random_probability_success_within_5_calls": r["random_probability_success_within_5_calls"],
                "max_degree_success": r["max_degree"]["success"],
                "max_degree_ar": r["max_degree"]["approximation_ratio"],
                "max_degree_kernel_ar": r["max_degree"]["kernel_approximation_ratio"],
                "max_degree_calls": r["max_degree"]["informer_calls"],
                "max_reduction_gain_success": r["max_reduction_gain"]["success"],
                "max_reduction_gain_ar": r["max_reduction_gain"]["approximation_ratio"],
                "max_reduction_gain_kernel_ar": r["max_reduction_gain"]["kernel_approximation_ratio"],
                "max_reduction_gain_calls": r["max_reduction_gain"]["informer_calls"],
                "paper_qredumis_pmis": r["paper_qredumis_pmis"],
                "paper_qredumis_mean_ar": r["paper_qredumis_mean_ar"],
            }
            w.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=260701037)
    parser.add_argument("--out-json", default="/mnt/data/qredumis_random_baseline_evidence.json")
    parser.add_argument("--out-csv", default="/mnt/data/qredumis_random_baseline_results.csv")
    parser.add_argument("--instances", nargs="*", default=[])
    args = parser.parse_args()

    specs = SPECS
    if args.instances:
        wanted = {x.lower() for x in args.instances}
        specs = [s for s in specs if any(w in s.name.lower() for w in wanted)]
    results = []
    for idx, spec in enumerate(specs):
        print(f"Benchmarking {spec.name}...", flush=True)
        result = benchmark_instance(spec, args.trials, args.seed + idx)
        results.append(result)
        print(
            f"  kernel={result['public_reconstruction_kernel_n']} "
            f"alpha={result['alpha_original']} random P={result['random_success_probability']:.4f} "
            f"AR={result['random_mean_ar']:.4f} elapsed={result['elapsed_seconds']:.1f}s",
            flush=True,
        )
    write_outputs(results, args.out_json, args.out_csv)
    print(f"Wrote {args.out_json} and {args.out_csv}")


if __name__ == "__main__":
    main()
