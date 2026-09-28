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

# Radon, through xenon's thresholds: no function or method worse than
# cyclomatic complexity B (10), no module averaging worse than B, and the
# code base averaging A (5).
check 'radon cyclomatic complexity (xenon)' \
  xenon --max-absolute B --max-modules B --max-average A "${paths[@]}"

# Radon's maintainability index: every module rated A. radon mi -n B lists
# the modules rated B or worse and exits 0 either way, so any output fails.
printf '\n== radon maintainability index\n'
if ! mi=$("$python" -m radon mi -n B "${paths[@]}"); then
  failed+=('radon maintainability index')
elif [ -n "$mi" ]; then
  printf 'Modules below maintainability rank A:\n%s\n' "$mi"
  failed+=('radon maintainability index')
else
  printf 'ok\n'
fi

printf '\n'
if [ "${#failed[@]}" -ne 0 ]; then
  printf 'FAIL  %s\n' "${failed[@]}" >&2
  exit 1
fi
printf 'All Python checks passed.\n'
