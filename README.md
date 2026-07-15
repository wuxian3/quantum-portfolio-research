# Quantum Portfolio Research

Reproducible research on quantum and hybrid quantum-classical methods for portfolio selection, asset-correlation graphs, and related combinatorial optimization problems.

## Current Study

The first study examines the qReduMIS pipeline reported in [Quantum-Informed Portfolio Selection: An End-to-End Pipeline Validated on Trapped-Ion Hardware with Real Market Data](https://arxiv.org/abs/2607.01037).

It tests whether uniform random frozen-node selection can explain the reported four-market results and compares it with a reduction-aware classical selector.

- [Study report](studies/qredumis-random-ablation/report.md)
- [Python reproduction script](studies/qredumis-random-ablation/qredumis_random_baseline.py)
- [Concise CSV results](studies/qredumis-random-ablation/results.csv)
- [Full JSON evidence](studies/qredumis-random-ablation/evidence.json)

## Main Finding

Uniform random selection does not explain the reported qReduMIS hardware performance on the exact DAX reconstruction. A simple reduction-aware classical selector is also a materially stronger baseline on three of the four reconstructed or proxy instances.

## Setup

```bash
git clone https://github.com/wuxian3/quantum-portfolio-research.git
cd quantum-portfolio-research
python -m venv .venv
python -m pip install -r requirements.txt
python studies/qredumis-random-ablation/qredumis_random_baseline.py --help
```

The full experiment additionally requires the public market-correlation datasets referenced by the paper. The current script records the original external data paths; see the study report for exact-match, near-match, and proxy boundaries. The paper does not publish all graph instances and hardware-level evidence needed for a bit-identical reproduction.

## Research Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
