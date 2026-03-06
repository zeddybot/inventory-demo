---
name: orchestrator
description: Spin up and tear down git worktrees with tmux and Claude session. Trigger on "spin DEV-123", "create worktree", "clean up worktrees", etc.
allowed-tools: Bash(~/.claude/skills/orchestrator/*), Bash(linearis *), Bash(git *), Bash(tmux *), Bash(gh *), Read, Glob, Grep
---

# Orchestrator

Automates creating inventory-demo worktrees with tmux window and Claude Code session.

## Creation Workflow

When the user says "spin DEV-123", "worktree for DEV-456", or similar:

### Step 1: Fetch ticket context

```bash
linearis issues read DEV-123
```

Extract from the JSON response:
- `branchName` — the git branch (e.g. `sameer/demo-123-fix-auth-bug`)
- `title` — ticket title for deriving the slug
- `identifier` — ticket ID (e.g. `DEV-123`)

### Step 2: Derive parameters

- **slug**: Short 2-3 word description from the ticket title. Examples:
  - "Add search endpoint for inventory" → `search-endpoint`
  - "Fix stock validation bug" → `stock-validation`
  - "Add CSV export feature" → `csv-export`
- **tmux-name**: Same as slug
- **claude-name**: Same as tmux-name
- **base**: Current branch in source repo (usually `main`)

Present the derived config to the user briefly, then run the script.

### Step 3: Run setup script

```bash
~/.claude/skills/orchestrator/setup-worktree.sh \
  --ticket DEV-123 \
  --slug search-endpoint \
  --branch "sameer/demo-123-add-search-endpoint" \
  --base main \
  --tmux-name search-endpoint \
  --session fractal \
  --claude-name search-endpoint
```

The script handles everything: git fetch, worktree creation, git push, tmux window creation, and launching Claude in plan mode with the initial prompt.

### Step 4: Report result

Tell the user the worktree path, tmux window name, and branch.

## Script Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--ticket <ID>` | (none) | Linear ticket ID (e.g. DEV-123) |
| `--slug <name>` | from ticket title | Worktree folder suffix → `inventory-demo-{slug}` |
| `--branch <name>` | from Linear branchName | Git branch to create/checkout |
| `--base <branch>` | current branch | Base branch (uses `origin/{base}`) |
| `--tmux-name <name>` | slug | Tmux window name |
| `--prompt <text>` | "hi claude, can you help me make a plan for DEV-XXX" | Initial Claude prompt |
| `--session <name>` | fractal | Tmux session name |
| `--claude-name <name>` | tmux-name | Name for Claude `/rename` |

## Ad-hoc Worktrees (no ticket)

For worktrees without a Linear ticket, provide `--slug` and `--branch` directly:

```bash
~/.claude/skills/orchestrator/setup-worktree.sh \
  --slug experiment \
  --branch "sameer/experiment-branch" \
  --base main
```

## Cleanup Workflow

When the user says "clean up worktrees", "prune worktrees", or similar, follow these steps. Do NOT use a script — run each step directly and report what you find.

### Step 1: List worktrees

```bash
git -C ~/Documents/projects/fractal-demo/inventory-demo worktree list
```

Skip the main `inventory-demo` worktree itself. Collect the remaining worktrees — each has a path and branch.

### Step 2: Check each worktree's status

For each worktree, determine whether it's safe to remove.

**2a. Check if the worktree is in detached HEAD state** (branch was deleted):

```bash
git -C <worktree-path> symbolic-ref HEAD 2>/dev/null
# Exit code 1 = detached HEAD → branch was deleted → safe to remove
```

**2b. For worktrees still on a branch, check PR status:**

```bash
gh pr list --repo zeddybot/inventory-demo --head <branch-name> --state all --json number,state,title
```

**2c. Also check for uncommitted changes:**

```bash
git -C <worktree-path> status --porcelain
```

### Step 3: Categorize

- **Safe to remove**: Detached HEAD (branch deleted), OR all PRs merged/closed, AND no uncommitted changes
- **Needs attention**: Some PRs merged but others still open
- **Keep**: Has open PRs or uncommitted work

### Step 4: Present findings and confirm

Show the user a summary table before removing anything:

```
Worktrees to REMOVE (all PRs merged, no uncommitted work):
  inventory-demo-search-endpoint  →  detached HEAD (branch deleted)
  inventory-demo-old-feature      →  PR #2 merged

Worktrees needing ATTENTION:
  inventory-demo-csv-export       →  PR #3 still open

Worktrees to KEEP:
  inventory-demo-stock-validation →  PR #5 OPEN, has uncommitted changes
```

Wait for user confirmation before proceeding.

### Step 5: Remove confirmed worktrees

For each worktree the user confirms for removal:

```bash
git -C ~/Documents/projects/fractal-demo/inventory-demo worktree remove <worktree-path>
```

If a worktree has uncommitted changes, `git worktree remove` will refuse. Use `--force` only if the user explicitly approves.

After removing worktrees, clean up any remaining local branches:

```bash
git -C ~/Documents/projects/fractal-demo/inventory-demo branch -D <branch-name>
```

### Step 6: Clean up tmux windows

List all tmux windows in the session:

```bash
tmux list-windows -t fractal -F '#{window_index} #{window_name}'
```

For each removed worktree, check if any tmux window name matches its slug. If so, kill that window:

```bash
tmux kill-window -t fractal:<window-name>
```

Not every worktree has a tmux window (it may have been closed manually), and that's fine — just skip if no match.

### Step 7: Report results

Summarize what was removed (worktrees, branches, tmux windows) and what was kept.
