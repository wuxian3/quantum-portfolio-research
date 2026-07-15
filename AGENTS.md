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
