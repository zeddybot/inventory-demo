#!/usr/bin/env bash
set -euo pipefail

# ── Project-specific constants ───────────────────────────────────────
SOURCE_REPO="$HOME/Documents/projects/fractal-demo/inventory-demo"
WORKTREE_PARENT="$HOME/Documents/projects/fractal-demo"
DEFAULT_SESSION="fractal"
LINEARIS="$HOME/.local/bin/linearis"

# ── Dependency check ─────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
    echo "ERROR: jq is required but not installed. Install with: sudo apt install jq" >&2
    exit 1
fi

# ── Argument parsing ─────────────────────────────────────────────────
TICKET=""
SLUG=""
BRANCH=""
BASE=""
TMUX_NAME=""
PROMPT=""
SESSION=""
CLAUDE_NAME=""

usage() {
    cat <<'EOF'
Usage: setup-worktree.sh [OPTIONS]

Options:
  --ticket <ID>        Linear ticket ID (e.g. DEMO-123)
  --slug <name>        Worktree folder suffix → inventory-demo-{slug}
  --branch <name>      Git branch name to create/checkout
  --base <branch>      Base branch to fork from (default: current branch)
  --tmux-name <name>   Tmux window name (default: slug)
  --prompt <text>      Initial Claude prompt
  --session <name>     Tmux session name (default: fractal)
  --claude-name <name> Name for Claude /rename (default: tmux-name)
  -h, --help           Show this help
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ticket)     TICKET="$2"; shift 2 ;;
        --slug)       SLUG="$2"; shift 2 ;;
        --branch)     BRANCH="$2"; shift 2 ;;
        --base)       BASE="$2"; shift 2 ;;
        --tmux-name)  TMUX_NAME="$2"; shift 2 ;;
        --prompt)     PROMPT="$2"; shift 2 ;;
        --session)    SESSION="$2"; shift 2 ;;
        --claude-name) CLAUDE_NAME="$2"; shift 2 ;;
        -h|--help)    usage ;;
        *)            echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ── Fetch ticket info ────────────────────────────────────────────────
TICKET_BRANCH=""
TICKET_TITLE=""
TICKET_ID=""

if [[ -n "$TICKET" ]]; then
    echo "==> Fetching ticket $TICKET from Linear..."
    TICKET_JSON=$("$LINEARIS" issues read "$TICKET" 2>/dev/null) || {
        echo "ERROR: Failed to fetch ticket $TICKET from Linear" >&2
        exit 1
    }

    TICKET_BRANCH=$(echo "$TICKET_JSON" | jq -r '.branchName // empty')
    TICKET_TITLE=$(echo "$TICKET_JSON" | jq -r '.title // empty')
    TICKET_ID=$(echo "$TICKET_JSON" | jq -r '.identifier // empty')

    if [[ -z "$TICKET_BRANCH" ]]; then
        echo "ERROR: No branchName found in ticket $TICKET" >&2
        exit 1
    fi

    echo "    Title: $TICKET_TITLE"
    echo "    Branch: $TICKET_BRANCH"
fi

# ── Derive defaults ──────────────────────────────────────────────────
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//' | cut -c1-30 | sed 's/-$//'
}

BRANCH="${BRANCH:-$TICKET_BRANCH}"
if [[ -z "$BRANCH" ]]; then
    echo "ERROR: No branch specified. Provide --branch or --ticket" >&2
    exit 1
fi

if [[ -z "$SLUG" ]]; then
    if [[ -n "$TICKET_TITLE" ]]; then
        SLUG=$(slugify "$TICKET_TITLE")
    else
        echo "ERROR: No slug specified. Provide --slug or --ticket" >&2
        exit 1
    fi
fi

# Default base to current branch in source repo
if [[ -z "$BASE" ]]; then
    BASE=$(git -C "$SOURCE_REPO" rev-parse --abbrev-ref HEAD)
fi

SESSION="${SESSION:-$DEFAULT_SESSION}"
TMUX_NAME="${TMUX_NAME:-$SLUG}"
CLAUDE_NAME="${CLAUDE_NAME:-$TMUX_NAME}"

if [[ -n "$TICKET_ID" ]]; then
    PROMPT="${PROMPT:-hi claude, can you help me make a plan for $TICKET_ID}"
else
    PROMPT="${PROMPT:-hi claude}"
fi

WORKTREE_DIR="$WORKTREE_PARENT/inventory-demo-$SLUG"

echo ""
echo "==> Configuration:"
echo "    Worktree: $WORKTREE_DIR"
echo "    Branch:   $BRANCH"
echo "    Base:     origin/$BASE"
echo "    Tmux:     $SESSION:$TMUX_NAME"
echo "    Claude:   $CLAUDE_NAME"
echo ""

# ── Validation ───────────────────────────────────────────────────────
if [[ -d "$WORKTREE_DIR" ]]; then
    echo "ERROR: Worktree directory already exists: $WORKTREE_DIR" >&2
    echo "Remove it first: git -C $SOURCE_REPO worktree remove inventory-demo-$SLUG" >&2
    exit 1
fi

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "ERROR: tmux session '$SESSION' does not exist" >&2
    exit 1
fi

if tmux list-windows -t "$SESSION" -F '#{window_name}' | grep -qx "$TMUX_NAME"; then
    echo "ERROR: tmux window '$TMUX_NAME' already exists in session '$SESSION'" >&2
    exit 1
fi

# ── Git fetch + worktree creation ────────────────────────────────────
echo "==> Fetching origin..."
git -C "$SOURCE_REPO" fetch origin

REMOTE_BRANCH_EXISTS=false
if git -C "$SOURCE_REPO" rev-parse --verify "origin/$BRANCH" &>/dev/null; then
    REMOTE_BRANCH_EXISTS=true
fi

LOCAL_BRANCH_EXISTS=false
if git -C "$SOURCE_REPO" rev-parse --verify "$BRANCH" &>/dev/null; then
    LOCAL_BRANCH_EXISTS=true
fi

echo "==> Creating worktree at $WORKTREE_DIR..."
if [[ "$REMOTE_BRANCH_EXISTS" == "true" ]]; then
    echo "    Branch '$BRANCH' exists on remote, checking out..."
    git -C "$SOURCE_REPO" worktree add "$WORKTREE_DIR" "$BRANCH"
elif [[ "$LOCAL_BRANCH_EXISTS" == "true" ]]; then
    echo "    Branch '$BRANCH' exists locally, checking out..."
    git -C "$SOURCE_REPO" worktree add "$WORKTREE_DIR" "$BRANCH"
else
    echo "    Creating new branch '$BRANCH' from origin/$BASE..."
    git -C "$SOURCE_REPO" worktree add -b "$BRANCH" "$WORKTREE_DIR" "origin/$BASE"
fi

# ── Push branch ──────────────────────────────────────────────────────
echo "==> Pushing branch to origin..."
git -C "$WORKTREE_DIR" push -u origin HEAD 2>/dev/null || {
    echo "    (Branch may already be tracked on remote, continuing...)"
}

# ── Python venv setup ────────────────────────────────────────────────
echo "==> Setting up Python venv..."
python3 -m venv "$WORKTREE_DIR/.venv"
source "$WORKTREE_DIR/.venv/bin/activate"
pip install -q -r "$WORKTREE_DIR/requirements.txt"

# ── Tmux + Claude ────────────────────────────────────────────────────
echo "==> Creating tmux window '$TMUX_NAME'..."
tmux new-window -t "$SESSION" -n "$TMUX_NAME" -c "$WORKTREE_DIR"

sleep 1

tmux send-keys -t "$SESSION:$TMUX_NAME" -l "source .venv/bin/activate"
tmux send-keys -t "$SESSION:$TMUX_NAME" Enter
sleep 1

tmux send-keys -t "$SESSION:$TMUX_NAME" -l "claude --allow-dangerously-skip-permissions --permission-mode plan"
tmux send-keys -t "$SESSION:$TMUX_NAME" Enter

echo "==> Waiting for Claude to start up..."
sleep 10

tmux send-keys -t "$SESSION:$TMUX_NAME" Enter
sleep 2

tmux send-keys -t "$SESSION:$TMUX_NAME" -l "/rename $CLAUDE_NAME"
tmux send-keys -t "$SESSION:$TMUX_NAME" Enter
sleep 2

tmux send-keys -t "$SESSION:$TMUX_NAME" -l "$PROMPT"
tmux send-keys -t "$SESSION:$TMUX_NAME" Enter

echo ""
echo "==> Done!"
echo "    Worktree: $WORKTREE_DIR"
echo "    Tmux:     $SESSION:$TMUX_NAME"
echo "    Branch:   $BRANCH"
echo "    Claude:   $CLAUDE_NAME"
