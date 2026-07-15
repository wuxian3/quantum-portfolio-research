# Quantum Portfolio Research Repository Design

## Purpose

Create a public research repository named `wuxian3/quantum-portfolio-research` for reproducible investigations of quantum and hybrid quantum-classical methods for portfolio selection. The repository is broader than a single paper, while remaining focused on portfolio construction, asset-correlation graphs, and related combinatorial optimization problems.

The initial published study is the existing qReduMIS four-market random-selector ablation for arXiv:2607.01037, *Quantum-Informed Portfolio Selection: An End-to-End Pipeline Validated on Trapped-Ion Hardware with Real Market Data*.

## Repository Structure

The root presents the research program rather than one experiment. It contains:

- `README.md` for the project purpose, current studies, setup, reproducibility boundaries, and citation links.
- `LICENSE` under Apache-2.0.
- `.gitignore` for Python caches, local environments, generated coverage, and secrets.
- `AGENTS.md` as the canonical contributor and coding-agent guide.
- `CLAUDE.md` as a short compatibility pointer to `AGENTS.md`.
- `docs/roadmap.md` for focused future research directions.
- `studies/qredumis-random-ablation/` for the current script, report, CSV summary, and JSON evidence.

The first study remains a standalone research artifact. It will not be prematurely converted into an installable library. Future studies can be added as peer directories under `studies/` and shared code can be extracted only when repeated use justifies it.

## Reproducibility and Data Boundary

The existing numerical results are preserved without recalculation or alteration. Documentation will distinguish exact reconstruction, near-match reconstruction, and circuit-matched proxies exactly as the current report does.

The public correlation datasets required by the script are not present in the current folder, and the script currently references external data paths. The repository will state this limitation explicitly and document the required Python dependencies. It will not claim a turnkey, bit-identical reproduction of unpublished graphs, unrounded thresholds, hardware bitstrings, or frozen-node logs.

## Validation and Automation

A lightweight GitHub Actions workflow will install the declared Python dependencies, compile the study script, and verify that its command-line help loads. This provides a real, visible integrity check without claiming that the full 100,000-trial experiment runs in CI.

The initial repository will not add package publishing, release automation, issue templates, project boards, branch protection, or fabricated coverage badges. Tests and coverage can be introduced when reusable code is extracted or additional studies create a stable shared API.

## Documentation and Research Roadmap

The root README will frame qReduMIS as the first case study and link directly to its detailed report and evidence files. The roadmap will prioritize:

1. Strengthening qReduMIS reproduction and data provenance.
2. Comparing quantum-informed selectors with meaningful classical reduction-aware baselines.
3. Evaluating robustness across thresholds, market windows, and graph construction methods.
4. Adding further quantum portfolio-selection studies under the same reproducibility standard.

## Publication

The local directory will be initialized on branch `main`. After the repository structure and checks are complete, the work will be committed, a public GitHub repository named `quantum-portfolio-research` will be created under the authenticated `wuxian3` account, `origin` will be set to that repository, and `main` will be pushed.

## Success Criteria

- The public repository exists at `https://github.com/wuxian3/quantum-portfolio-research`.
- A new reader can understand the broader research goal and locate the qReduMIS results from the root README.
- Existing result artifacts remain unchanged in content.
- Reproducibility limitations and external data requirements are explicit.
- The documented lightweight validation commands pass locally and in GitHub Actions.
