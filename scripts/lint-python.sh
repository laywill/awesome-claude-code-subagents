#!/usr/bin/env bash
#
# Runs every Python check over scripts/ and tests/:
#
#     ./scripts/lint-python.sh
#
# CI runs it from .github/workflows/validate.yml and pre-commit runs it when a
# .py file changes, so both check exactly what a local run checks. Tools come
# from requirements-dev.txt, config from pyproject.toml (.flake8 for flake8).
# MegaLinter's Python linters are disabled so nothing is checked twice.
#
# Reports every failing tool rather than stopping at the first. Exits 0 when
# all pass, 1 otherwise.

set -uo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

paths=(scripts tests)
failed=()

if ! python=$(command -v python3 || command -v python); then
  echo 'FAIL  Python 3 is required' >&2
  exit 1
fi

check() {
  local name=$1
  shift
  printf '\n== %s\n' "$name"
  if "$python" -m "$@"; then
    printf 'ok\n'
  else
    failed+=("$name")
  fi
}

check 'ruff (lint)' ruff check "${paths[@]}"
check 'black (format)' black --check --quiet "${paths[@]}"
check 'isort (imports)' isort --check-only --quiet "${paths[@]}"
check 'flake8 (style)' flake8 "${paths[@]}"
check 'pylint (design and bugs)' pylint --score=n "${paths[@]}"
check 'mypy --strict (types)' mypy "${paths[@]}"
check 'bandit (security)' bandit --quiet -c pyproject.toml -r "${paths[@]}"

# Radon lists what it finds at or below a rank and exits 0 either way, so a
# gate fails on any output. $1 = check name, $2 = what the output lists,
# the rest = the radon command.
radon_gate() {
  local name=$1 what=$2 out
  shift 2
  printf '\n== %s\n' "$name"
  if ! out=$("$python" -m radon "$@" "${paths[@]}"); then
    failed+=("$name")
  elif [ -n "$out" ]; then
    printf '%s:\n%s\n' "$what" "$out"
    failed+=("$name")
  else
    printf 'ok\n'
  fi
}

# No function, method or class worse than cyclomatic complexity B (10).
# That caps every module's average at B too.
radon_gate 'radon cyclomatic complexity' 'Blocks worse than rank B' cc -s -n C

# Every module's maintainability index rated A.
radon_gate 'radon maintainability index' 'Modules below rank A' mi -s -n B

# The code base averaging cyclomatic complexity A (5 or less).
printf '\n== radon average complexity\n'
average=$("$python" -m radon cc --total-average "${paths[@]}" | tail -n 1)
printf '%s\n' "$average"
case "$average" in
  'Average complexity: A '*) ;;
  *) failed+=('radon average complexity') ;;
esac

printf '\n'
if [ "${#failed[@]}" -ne 0 ]; then
  printf 'FAIL  %s\n' "${failed[@]}" >&2
  exit 1
fi
printf 'All Python checks passed.\n'
