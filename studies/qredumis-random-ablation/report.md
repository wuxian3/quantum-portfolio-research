# Random-selector ablation for arXiv:2607.01037

## Scope and reproducibility boundary

The finance paper does not release the exact four first-kernel graph files, unrounded thresholds, Helios bitstrings, or per-trial frozen-node logs. This report therefore reconstructs the graphs from the public correlation datasets cited by the paper and mirrors the exposed-clique reducer in the public qReduMIS repository.

- DAX is an exact public reconstruction at the level of kernel nodes, edges/density, and circuit edge count.
- S&P and Nikkei are circuit-matched proxies obtained with unrounded thresholds that round to the values printed in the paper.
- FTSE remains one node different: the closest public reconstruction has 46 nodes rather than the reported 45, although its 287 edges reproduce the reported 574 two-qubit gates for p=2 and its density rounds to 0.28.

These distinctions matter: only DAX supports a strict instance-level comparison; the other comparisons are strong reconstructions/proxies, not a claim of bit-identical hardware instances.

## Method

For each first kernel, run 100,000 trials with fixed seed 260701037:

1. choose one current-kernel node uniformly at random and force it into the independent set;
2. delete its closed neighborhood;
3. apply exposed-neighborhood-clique reduction to a fixed point;
4. repeat until the graph is empty.

Exact MIS sizes are obtained with a binary MILP solved by SciPy/HiGHS. Success means the final first-kernel solution size equals the exact kernel MIS size. Approximation ratio is measured on the first kernel, matching the paper comparison—not on the original graph after adding the already-exact initial reductions.

## Main results

| Instance | Reconstruction | Kernel n / edges | Safe nodes in first kernel | Random exact MIS P (95% CI) | Random mean kernel AR | Paper qReduMIS P | Paper qReduMIS AR |
|---|---|---:|---:|---:|---:|---:|---:|
| DAX 100 | exact_match | 49 / 346 | 27/49 (55.1%) | 40.14% [39.84, 40.45] | 0.915 | 95% | 1.00 |
| FTSE 100 | near_match | 46 / 287 | 22/46 (47.8%) | 39.83% [39.53, 40.14] | 0.905 | 70% | 0.98 |
| S&P 100 | circuit_matched_proxy | 68 / 457 | 23/68 (33.8%) | 7.27% [7.11, 7.44] | 0.857 | 40% | 0.96 |
| Nikkei 225 | circuit_matched_proxy | 78 / 508 | 36/78 (46.2%) | 13.16% [12.96, 13.38] | 0.895 | 95% | 0.99 |

The five-call cap is not driving these numbers: the probability of both succeeding and finishing within five random selections is virtually identical to the unrestricted success probability for all four reconstructions.

## Secondary classical heuristic

A non-oracle heuristic was also tested: for every candidate node, simulate `select v -> delete N[v] -> exact reduction`, then choose the node that eliminates the most vertices immediately. This uses only the graph and the same polynomial reduction; it does not query the exact MIS solver.

| Instance | One-step max-reduction-gain result | Kernel AR | Informer selections |
|---|---:|---:|---:|
| DAX 100 exact-match | exact MIS | 1.000 | 1 |
| FTSE 100 closest-match | exact MIS | 1.000 | 1 |
| S&P 100 circuit-matched | exact MIS | 1.000 | 1 |
| Nikkei 225 circuit-matched | suboptimal | 0.893 | 1 |

This heuristic finds the exact reconstructed DAX, FTSE, and S&P solutions after one selected node, but not the Nikkei proxy. It is therefore an important missing ablation: the QAOA selector should be compared not only with uniform random choice, but also with reduction-aware classical selectors.

## Interpretation

- Uniform random selection is not enough to explain the reported qReduMIS hardware results. On the exact DAX reconstruction, random selection succeeds about 40%, versus 19/20 = 95% in the paper.
- The framework itself is nevertheless strong: random selection still produces kernel AR around 0.86–0.91, and only 1.3–2.7 random informer selections on average are needed before reductions finish the graph.
- First-kernel safe-node coverage is 34%–55%, not close to 100%. Thus these instances are not cases where almost every node can be safely guessed.
- A simple reduction-aware classical heuristic is much stronger than uniform random on three reconstructions. The paper’s current comparison does not isolate QAOA against this more relevant baseline.

## Files

- `qredumis_random_baseline.py`: executable reproduction script
- `qredumis_four_market_random_ablation_results.csv`: concise results
- `qredumis_four_market_random_ablation_evidence.json`: full evidence, CIs, trajectories, and deterministic heuristic outputs