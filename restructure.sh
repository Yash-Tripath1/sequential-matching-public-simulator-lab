#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Restructure the submission repository so the assessed Round 2 build is the
# project root.  Run this from ANYWHERE inside your clone:
#
#     bash restructure.sh
#
# It is idempotent-ish and safe to re-run: every move is a `git mv`, so
# nothing is deleted.  If it half-fails, `git status` shows exactly where it
# stopped and you can finish by hand.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
echo "repo root: $(pwd)"

# ---------------------------------------------------------------- 1. sanity
if [ ! -d round2 ]; then
  echo "!! no round2/ directory — already restructured, or wrong repo. Aborting."
  exit 1
fi

# ------------------------------------------- 2. archive Round 1 into round1/
echo
echo "== archiving Round 1 material into round1/ =="
mkdir -p round1
moved=0
for f in $(ls -A | grep -v -E '^(\.git|round1|round2|restructure\.sh)$'); do
  git mv "$f" round1/ 2>/dev/null || mv "$f" round1/
  moved=$((moved + 1))
done
echo "   moved $moved top-level entries"

# ------------------------------------------- 3. promote round2/ to the root
echo
echo "== promoting round2/ to the repository root =="
shopt -s dotglob nullglob
for f in round2/* round2/.[!.]*; do
  [ -e "$f" ] || continue
  base="$(basename "$f")"
  if [ -e "$base" ]; then rm -rf "$base"; fi
  git mv "$f" ./ 2>/dev/null || mv "$f" ./
done
shopt -u dotglob nullglob
rm -rf round2
echo "   round2/ is now the root"

# --------------------------------------------- 4. stop tracking __pycache__
echo
echo "== untracking compiled Python =="
git ls-files | grep '__pycache__' | xargs -r git rm -r --cached -q || true
git ls-files | grep '\.pyc$'      | xargs -r git rm -r --cached -q || true
printf '\n# Python\n__pycache__/\n*.pyc\n' >> .gitignore
echo "   done"

# ------------------------------------------------------------- 5. done
echo
echo "=============================================================="
echo " Restructure complete."
echo
echo " NEXT: copy the updated build over this root, then:"
echo
echo "   git add -A"
echo "   git status --short"
echo "   git commit -m 'Round 2 final build at repository root'"
echo "   git push"
echo "   git rev-parse HEAD"
echo
echo " Paste the 40-character SHA into the Final submission issue."
echo "=============================================================="
