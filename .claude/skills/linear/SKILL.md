---
name: linear
description: Work with Linear issues via the linearis CLI. Use when user mentions issue IDs (DEV-123), wants to create issues, start working on a ticket, create branches or worktrees from issues, or asks about sprints/cycles.
allowed-tools: Bash(linearis:*), Bash(git:*), Bash(which linearis)
---

# Linear

Use the `linearis` CLI for all Linear operations. It outputs JSON and supports both UUIDs and issue identifiers (e.g., `DEV-123`).

## Prerequisites

Before using linearis commands, check if it's installed:

```bash
which linearis
```

If not installed, tell the user:

> linearis CLI is not installed. Install it with:
> ```bash
> npm install -g linearis
> ```
> Then set up authentication:
> ```bash
> echo "YOUR_LINEAR_API_TOKEN" > ~/.linear_api_token
> ```
> Get your API token from Linear: Settings → Security & Access → Personal API keys

## Quick Reference

```bash
linearis usage                    # Full command reference
linearis issues read DEV-123    # Get issue details
linearis issues search "query"   # Search issues
linearis issues create "Title" --team DEV -d "Description"
linearis issues update DEV-123 --status "In Progress"
```

## Common Workflows

### 1. Create an Issue

```bash
linearis issues create "Issue title" \
  --team DEV \
  -d "Description here" \
  -p 2 \                          # Priority 1-4 (1=urgent)
  --labels "bug,frontend" \
  --project "Project Name"
```

### 2. Activate an Issue (Start Working)

When user wants to start working on an issue, follow this workflow:

1. **Fetch the issue** to get details:
   ```bash
   linearis issues read DEV-123
   ```

2. **Update status** to "In Progress":
   ```bash
   linearis issues update DEV-123 --status "In Progress"
   ```

3. **Create a git branch** using the naming convention `<username>/<team-key>-<number>-<slug>`:
   ```bash
   # Extract from issue: identifier (DEV-123) and title
   # Create branch like: sameer/demo-123-fix-login-bug
   git checkout -b "sameer/demo-123-slug-from-title"
   ```

### 3. Activate with Git Worktree (Full Setup)

For parallel work, create a worktree instead of switching branches. This is the recommended workflow for working on multiple issues simultaneously.

**Step 1: Get the branch name from the issue**

```bash
linearis issues read DEV-123
# Look for "branchName" in the JSON output
```

**Step 2: Create the worktree**

From the main repo (e.g., `inventory-demo`), create worktree in a parallel directory. Use the branch name from the Linear issue (found in the JSON response as `branchName`).

**Folder naming convention:** `inventory-demo-<descriptive-slug>` based on the ticket title, NOT just the issue key.

Examples:
- DEV-1 "Add search endpoint for inventory" → `inventory-demo-search-endpoint`
- DEV-2 "Fix stock validation bug" → `inventory-demo-stock-validation`
- DEV-3 "Add CSV export feature" → `inventory-demo-csv-export`

```bash
# For a new branch (branch doesn't exist yet)
git worktree add ../inventory-demo-search-endpoint -b "sameer/demo-1-add-search-endpoint"

# For an existing branch (branch already exists in Linear or was pushed)
git worktree add ../inventory-demo-stock-validation sameer/demo-2-fix-stock-validation
```

**Step 3: Set up the worktree environment**

After creating the worktree, run these commands to fully set it up:

```bash
cd ../inventory-demo-search-endpoint

# Push branch to remote and set upstream tracking
git push -u origin HEAD
```

### 4. Search and Filter Issues

```bash
# Search by text
linearis issues search "authentication bug" --team DEV

# Filter by status
linearis issues search "" --status "In Progress,Todo"

# Filter by assignee
linearis issues search "" --assignee USER_ID

# Filter by project
linearis issues search "" --project "Project Name"
```

### 5. Update Issues

```bash
# Change status
linearis issues update DEV-123 --status "Done"

# Add labels
linearis issues update DEV-123 --labels "reviewed"

# Set milestone
linearis issues update DEV-123 --project-milestone "v1.0"

# Add to cycle/sprint
linearis issues update DEV-123 --cycle "Sprint 5"
```

### 6. Add Comments

```bash
linearis comments create DEV-123 --body "Comment text here"
```

## Branch Naming Convention

Format: `<username>/<team-key-lowercase>-<issue-number>-<slugified-title>`

Examples:
- `sameer/demo-1-add-search-endpoint`
- `sameer/demo-2-fix-stock-validation`
- `sameer/demo-3-csv-export`

To slugify a title: lowercase, replace spaces with hyphens, remove special chars, truncate if needed.

## Issue Statuses

Common statuses (may vary by team):
- Backlog
- Todo
- In Progress
- In Review
- Done
- Canceled

## Priorities

- **1** - Urgent
- **2** - High
- **3** - Medium (default)
- **4** - Low

## Markdown Formatting for Descriptions

Linear renders markdown but shell escaping can corrupt it. Follow these rules when passing descriptions via `-d`:

### Write descriptions to a temp file, then pass via `cat`

**Always do this for multi-line descriptions with code blocks, mermaid diagrams, or backticks.** Shell escaping will mangle backticks and special characters when passed inline.

```bash
# 1. Write description to a temp file using the Write tool (NOT echo/cat heredoc)
# 2. Pass it to linearis:
linearis issues create "Title" --team DEV -d "$(cat /tmp/description.md)"
linearis issues update DEV-123 -d "$(cat /tmp/description.md)"
```

**Never** escape backticks as `\`` in descriptions — Linear will store them literally and code blocks / mermaid diagrams won't render.
