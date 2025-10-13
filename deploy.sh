#!/usr/bin/env bash
# Simple deploy script for WEGC static site
# Usage:
#   ./deploy.sh                # normal run
#   DOMAIN=wegc.fund ./deploy.sh   # also ensure CNAME contains domain
#   DRY=1 ./deploy.sh          # show commands only, do not run

set -euo pipefail

run() {
  if [[ "${DRY:-0}" == "1" ]]; then
    printf 'DRY> %s\n' "$*"
  else
    eval "$@"
  fi
}

if [[ ! -d .git ]]; then
  echo "Error: this is not a git repository (.git not found)"
  exit 1
fi

# Show current branch
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "main" ]]; then
  echo "Note: current branch is '$BRANCH' (not 'main'). Deploy will push this branch."
fi

# Optional: ensure CNAME for custom domain
if [[ -n "${DOMAIN:-}" ]]; then
  if [[ ! -f CNAME ]] || ! grep -qx "${DOMAIN}" CNAME ; then
    echo "Ensuring CNAME=${DOMAIN}"
    run "printf '%s\n' '${DOMAIN}' > CNAME"
    run "git add CNAME"
  fi
fi

# Pull latest and rebase
echo "Fetching and rebasing from origin/${BRANCH}..."
run "git fetch origin"
run "git pull --rebase origin ${BRANCH}"

# Stage changes
echo "Staging changes..."
run "git add -A"

# Commit if there is anything to commit
if ! git diff --cached --quiet; then
  TS="$(date -u +'%Y-%m-%d %H:%M:%S UTC')"
  MSG="${MSG:-Site update: ${TS}}"
  echo "Committing: ${MSG}"
  run "git commit -m \"${MSG}\""
else
  echo "Nothing to commit."
fi

# Push
echo "Pushing to origin/${BRANCH}..."
run "git push origin ${BRANCH}"

echo
echo "✅ Push complete."
echo "If GitHub Pages is configured via Actions, a deploy run should start automatically."
echo "Open the Actions tab to watch the workflow:"
REPO_URL="$(git remote get-url origin | sed 's/.git$//')"
echo "  ${REPO_URL}/actions"
echo
echo "Tip: You can run with DRY=1 to preview commands, or set DOMAIN=wegc.fund to enforce CNAME."
