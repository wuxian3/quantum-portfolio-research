# Quantum Portfolio Research Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the existing qReduMIS ablation as the first study in a clean, extensible public quantum portfolio research repository.

**Architecture:** Keep the repository research-first: root documentation defines the wider program, while each experiment lives under `studies/` with its own code, results, and reproducibility notes. Preserve all existing artifact contents and add only lightweight dependency and CI surfaces needed to validate that the current script remains loadable.

**Tech Stack:** Python 3.11, NumPy, SciPy/HiGHS MILP, Markdown, GitHub Actions, GitHub CLI.

---

### Task 1: Preserve and organize the initial study

**Files:**
- Move: `qredumis_random_baseline.py` to `studies/qredumis-random-ablation/qredumis_random_baseline.py`
- Move: `qredumis_four_market_random_ablation_report.md` to `studies/qredumis-random-ablation/report.md`
- Move: `qredumis_four_market_random_ablation_results.csv` to `studies/qredumis-random-ablation/results.csv`
- Move: `qredumis_four_market_random_ablation_evidence.json` to `studies/qredumis-random-ablation/evidence.json`

- [ ] **Step 1: Record source artifact hashes**

Run:

```powershell
Get-FileHash qredumis_random_baseline.py,qredumis_four_market_random_ablation_report.md,qredumis_four_market_random_ablation_results.csv,qredumis_four_market_random_ablation_evidence.json -Algorithm SHA256
```

Expected: four SHA-256 hashes are printed.

- [ ] **Step 2: Create the study directory and move artifacts with Git-aware moves**

Run:

```powershell
New-Item -ItemType Directory -Force studies/qredumis-random-ablation
git add qredumis_random_baseline.py qredumis_four_market_random_ablation_report.md qredumis_four_market_random_ablation_results.csv qredumis_four_market_random_ablation_evidence.json
git mv qredumis_random_baseline.py studies/qredumis-random-ablation/qredumis_random_baseline.py
git mv qredumis_four_market_random_ablation_report.md studies/qredumis-random-ablation/report.md
git mv qredumis_four_market_random_ablation_results.csv studies/qredumis-random-ablation/results.csv
git mv qredumis_four_market_random_ablation_evidence.json studies/qredumis-random-ablation/evidence.json
```

Expected: the four artifacts appear under `studies/qredumis-random-ablation/`.

- [ ] **Step 3: Verify content preservation**

Run:

```powershell
Get-FileHash studies/qredumis-random-ablation/qredumis_random_baseline.py,studies/qredumis-random-ablation/report.md,studies/qredumis-random-ablation/results.csv,studies/qredumis-random-ablation/evidence.json -Algorithm SHA256
```

Expected: the hashes match Step 1 in the same artifact order.

- [ ] **Step 4: Commit the study organization**

```powershell
git commit -m "chore: organize initial qredumis study"
```

Expected: one commit containing only the four study artifacts.

### Task 2: Add the public research documentation surface

**Files:**
- Create: `README.md`
- Create: `docs/roadmap.md`
- Create: `AGENTS.md`
- Create: `CLAUDE.md`

- [ ] **Step 1: Write the root README**

Create `README.md` with:

```markdown
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
```

- [ ] **Step 2: Write the roadmap**

Create `docs/roadmap.md` with:

```markdown
# Research Roadmap

## Near-term priorities

1. Strengthen the provenance and acquisition instructions for the public market-correlation datasets used in the qReduMIS study.
2. Compare quantum-informed node selection with uniform random, degree-based, and reduction-aware classical selectors under matched evaluation budgets.
3. Test robustness across correlation thresholds, market time windows, graph construction choices, and random seeds.
4. Add further quantum and hybrid portfolio-selection studies as peer directories under `studies/`.

## Evidence standard

Each study must document its source data, deterministic seeds, executable commands, dependencies, and machine-readable evidence. Exact reconstructions, near matches, proxies, emulator runs, and hardware runs must be labeled separately. Missing inputs or unpublished evidence must be stated explicitly.
```

- [ ] **Step 3: Write contributor instructions**

Create `AGENTS.md` with:

````markdown
# Repository Instructions

## Purpose

This repository contains reproducible research on quantum and hybrid quantum-classical methods for portfolio selection. Keep claims proportional to the available data and evidence.

## Structure

- Put each research artifact under `studies/<study-name>/`.
- Keep code, a human-readable report, concise results, and machine-readable evidence together.
- Extract shared packages only after at least two studies need the same implementation.

## Validation

Run before committing:

```bash
python -m compileall studies
python studies/qredumis-random-ablation/qredumis_random_baseline.py --help
```

Full numerical experiments require the external datasets documented by each study and should not be run implicitly.

## Evidence rules

- Preserve committed result artifacts unless an experiment is deliberately rerun.
- Record seeds, dependencies, commands, and data provenance for new results.
- Distinguish exact reproductions, near matches, proxies, emulator results, and hardware results.
- Never claim exact reproduction when required source inputs or hardware evidence are unavailable.

## Repo-local skills

There are currently no repo-local skills to install. If `skills/*/SKILL.md` files are added later, Codex-compatible installation uses:

```bash
mkdir -p ~/.agents/skills
for skill_dir in "$PWD"/skills/*; do
  [ -d "$skill_dir" ] || continue
  ln -sfn "$skill_dir" ~/.agents/skills/"$(basename "$skill_dir")"
done
```

For Claude compatibility:

```bash
mkdir -p ~/.claude
if [ ! -e ~/.claude/skills ]; then
  ln -s ~/.agents/skills ~/.claude/skills
else
  echo "Do not overwrite ~/.claude/skills; symlink individual repo skills instead."
fi
```

Do not overwrite an existing non-symlink `~/.claude/skills` directory without explicit approval.
````

- [ ] **Step 4: Add Claude compatibility pointer**

Create `CLAUDE.md` with:

```markdown
# Claude Instructions

Read and follow [AGENTS.md](AGENTS.md) as the canonical repository instructions.
```

- [ ] **Step 5: Check documentation links and placeholders**

Run:

```powershell
rg -n "T[B]D|T[O]DO|PLACEHOLD[E]R|2607\.05501" README.md AGENTS.md CLAUDE.md docs studies/qredumis-random-ablation/report.md
```

Expected: no output.

- [ ] **Step 6: Commit documentation**

```powershell
git add README.md docs/roadmap.md AGENTS.md CLAUDE.md
git commit -m "docs: introduce quantum portfolio research program"
```

Expected: the repository purpose and first study are discoverable from `README.md`.

### Task 3: Add licensing, dependencies, ignore rules, and CI

**Files:**
- Create: `LICENSE`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Add Apache-2.0 license**

Copy the canonical license text from `C:/Users/67518/.codex/skills/github-new-repo/assets/LICENSE-APACHE-2.0` to `LICENSE` without editing its terms.

- [ ] **Step 2: Declare runtime dependencies**

Create `requirements.txt` with:

```text
numpy>=1.26,<3
scipy>=1.11,<2
```

- [ ] **Step 3: Add Python and secret ignore rules**

Create `.gitignore` with:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
coverage.xml
htmlcov/
.env
.env.*
!.env.example
.DS_Store
Thumbs.db
.idea/
.vscode/
```

- [ ] **Step 4: Add lightweight CI**

Create `.github/workflows/ci.yml` with:

```yaml
name: CI

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  integrity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: python -m pip install -r requirements.txt
      - run: python -m compileall studies
      - run: python studies/qredumis-random-ablation/qredumis_random_baseline.py --help
```

- [ ] **Step 5: Run local integrity checks**

Run:

```powershell
python -m pip install -r requirements.txt
python -m compileall studies
python studies/qredumis-random-ablation/qredumis_random_baseline.py --help
```

Expected: dependency installation succeeds, compileall reports the study directory without syntax errors, and the CLI prints options including `--trials`, `--seed`, `--out-json`, `--out-csv`, and `--instances`.

- [ ] **Step 6: Commit repository infrastructure**

```powershell
git add LICENSE requirements.txt .gitignore .github/workflows/ci.yml
git commit -m "ci: add research repository integrity checks"
```

Expected: one commit with licensing and validation infrastructure.

### Task 4: Audit and publish the repository

**Files:**
- Verify: entire repository

- [ ] **Step 1: Verify tracked and untracked state**

Run:

```powershell
git status --short --branch
git ls-files
git log --oneline --decorate -5
```

Expected: branch is `main`, the intended files are tracked, and the worktree is clean.

- [ ] **Step 2: Verify no public repository already exists**

Run:

```powershell
gh repo view wuxian3/quantum-portfolio-research
```

Expected: GitHub reports that the repository is not found. If it exists, stop and inspect it rather than overwriting or force-pushing.

- [ ] **Step 3: Create the public GitHub repository and push**

Run:

```powershell
gh repo create wuxian3/quantum-portfolio-research --public --description "Reproducible research on quantum and hybrid methods for portfolio selection" --source . --remote origin --push
```

Expected: GitHub creates `https://github.com/wuxian3/quantum-portfolio-research`, adds `origin`, and pushes `main`.

- [ ] **Step 4: Verify remote visibility and CI**

Run:

```powershell
gh repo view wuxian3/quantum-portfolio-research --json nameWithOwner,url,visibility,defaultBranchRef
gh run list --repo wuxian3/quantum-portfolio-research --limit 1
```

Expected: visibility is `PUBLIC`, default branch is `main`, and a CI workflow run is queued, in progress, or completed.

- [ ] **Step 5: Wait for CI conclusion**

Run:

```powershell
gh run watch --repo wuxian3/quantum-portfolio-research --exit-status
```

Expected: the workflow exits successfully. If it fails, inspect the logs, fix only the scoped failure, re-run local verification, commit, and push.
