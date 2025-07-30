#!/usr/bin/env bash
# refresh_uv_deps.sh – drop version pins and install newest releases with uv
# Compatible with the default macOS Bash 3.2
set -euo pipefail
PYPROJECT=${1:-pyproject.toml}

###############################################################################
# 1. prerequisites
###############################################################################
command -v uv >/dev/null 2>&1 || {
  echo "❌  'uv' not found – install it first: https://docs.astral.sh/uv" >&2; exit 1; }

PYBIN=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && PYBIN=$c && break; done
[[ -z $PYBIN ]] && { echo "❌  Python 3.x not found in \$PATH" >&2; exit 1; }

###############################################################################
# 2. build a TSV:  group<TAB>root<TAB>add_spec
#    - root      → just the bare name (fastapi-users)
#    - add_spec  → name + extras but **no** version / marker (fastapi-users[sqlalchemy])
###############################################################################
tmp=$(mktemp)
"$PYBIN" - "$PYPROJECT" >"$tmp" <<'PY'
import sys, re, importlib, itertools, pathlib, subprocess

def toml():                         # tomllib on 3.11+, tomli otherwise
    try: return importlib.import_module("tomllib")
    except ModuleNotFoundError:
        try: return importlib.import_module("tomli")
        except ModuleNotFoundError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "tomli"])
            return importlib.import_module("tomli")

doc   = toml().loads(pathlib.Path(sys.argv[1]).read_text())
proj  = doc.get("project", {})
core  = proj.get("dependencies", [])
opt   = proj.get("optional-dependencies", {})

def root(spec: str) -> str:             # remove extras + everything after
    return re.split(r'[\[\s<>=!~]', spec, 1)[0]

def add_spec(spec: str) -> str:         # keep extras, drop version / markers
    return re.split(r'\s*[<>=!~]', spec, 1)[0].strip()

# core first
for spec in core:
    print("core", root(spec), add_spec(spec), sep="\t")

# then every optional-dependency group
for extra in sorted(opt):
    for spec in opt[extra]:
        print(extra, root(spec), add_spec(spec), sep="\t")
PY

###############################################################################
# 3. remove everything
###############################################################################
echo "🗑  Removing current packages …"
while IFS=$'\t' read -r grp pkg _; do
  if [[ $grp == core ]]; then
    uv remove "$pkg"        >/dev/null 2>&1 || true
  else
    uv remove "$pkg" --optional "$grp" >/dev/null 2>&1 || true
  fi
done <"$tmp"

###############################################################################
# 4. add back – *latest* version on PyPI, same table as before
###############################################################################
echo "➕  Adding newest available releases …"
while IFS=$'\t' read -r grp _ spec; do
  if [[ $grp == core ]]; then
    uv add "$spec"                               # newest release
  else
    uv add "$spec" --optional "$grp"
  fi
done <"$tmp"

###############################################################################
# 5. rebuild lock-file & sync env
###############################################################################
uv lock --upgrade        # make lock show the just-installed versions  :contentReference[oaicite:0]{index=0}
uv sync                  # install / prune to match the lock          :contentReference[oaicite:1]{index=1}

rm -f "$tmp"
echo "✅  All dependencies upgraded to their latest versions (core + extras)!"