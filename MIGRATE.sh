#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Update the PUBLIC submission repo with the Round 2 build.
#
# What it does:
#   1. clones the public repo into ~/lab-update
#   2. removes the committed __pycache__/ (it should never have been tracked)
#   3. copies the Round 2 build in as round2/
#   4. replaces the root README with one that points at round2/
#   5. updates .gitignore
#   6. commits  --  but does NOT push. Review first, then push yourself.
#
# Round 1 files are left exactly where they are. Nothing is deleted.
# Usage:  bash MIGRATE.sh
# ---------------------------------------------------------------------------
set -euo pipefail

REPO="https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab.git"
DEST="$HOME/lab-update"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> cloning (or reusing) $DEST"
if [ -d "$DEST/.git" ]; then
  cd "$DEST" && git checkout main -q && git pull -q
else
  git clone -q "$REPO" "$DEST" && cd "$DEST"
fi

echo "==> removing tracked __pycache__"
git rm -r -q --cached __pycache__ 2>/dev/null || true
rm -rf __pycache__
find . -name "__pycache__" -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true

echo "==> installing the Round 2 build as round2/"
rm -rf round2
cp -r "$SRC/round2" round2
rm -rf round2/__pycache__ round2/code/__pycache__

echo "==> updating root README and .gitignore"
cp "$SRC/README.md" README.md
cp "$SRC/.gitignore" .gitignore

echo "==> refreshing checksums"
cd round2 && find . -type f -not -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && cd ..

echo "==> staging"
git add -A
git status --short | head -60
echo

if git diff --cached --quiet; then
  echo "  nothing staged - repo already up to date."
else
  git commit -q -m "Round 2 final build: ship greedy baseline with 2,880-episode evaluation on 120 seeds

- Policy, Dockerfile (zero third-party dependencies), harness and analysis
- 2,880 episodes across four policies, paired on identical worlds
- All three supplied baselines compared; three ablations
- Validated 9/9 against the organiser's own evaluator
- Technical report, reproduction manifest, machine-readable results
- Round 1 lab preserved untouched at the repository root
- Removed the accidentally committed __pycache__/"
  echo
  echo "==> committed. HEAD is now:"
  git log -1 --format="  %H%n  %s"
fi

echo
echo "=========================================================="
echo " NOT PUSHED. Review with:  cd $DEST && git show --stat"
echo "=========================================================="
cat <<TXT

When you are happy with it:

    cd $DEST && git push origin main

Then record the 40-character SHA for your submission form:

    cd $DEST && git rev-parse HEAD

Build and test the image from the round2/ directory:

    cd $DEST/round2 && docker build -t bipartite-bard:round2 .
    echo '{"phase":"ask","state":{"day":0,"members":[],"introductions":[],"ask_budget_remaining":12},"memory":{}}' | docker run --rm -i bipartite-bard:round2
TXT
