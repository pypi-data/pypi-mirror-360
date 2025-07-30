# pythonrc.py
import os
import sys
import glob
import json
import traceback

# ─────────────────────────────────────────────────────────────────────────
# 1) Compute BASE, JSON_DIR, and LOG_DIR robustly
# ─────────────────────────────────────────────────────────────────────────
try:
    BASE = os.path.realpath(os.path.dirname(__file__))
except NameError:
    import inspect
    BASE = os.path.realpath(os.path.dirname(inspect.getfile(inspect.currentframe())))

JSON_DIR = os.path.join(BASE, "..", "json")
LOG_DIR  = os.path.join(BASE, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
ERROR_LOG = os.path.join(LOG_DIR, "pythonrc_error.log")

def logmsg(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")

# ─────────────────────────────────────────────────────────────────────────
# 2) Core functions
# ─────────────────────────────────────────────────────────────────────────
def add_poetry_site_packages(project_env="houdinilab"):
    """
    Locate the Poetry virtualenv for `project_env`, find its
    site-packages directory, and insert it at the front of sys.path.
    """
    home = os.path.expanduser("~")
    venvs_dir = os.path.join(home, "Library", "Caches", "pypoetry", "virtualenvs")
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    pattern = os.path.join(venvs_dir, f"{project_env}-*-py{pyver}")
    matches = glob.glob(pattern)
    if not matches:
        logmsg(f"[pythonrc] no Poetry venv matching {pattern!r}")
        return

    venv_path = sorted(matches, key=os.path.getmtime, reverse=True)[0]
    site_pkgs = os.path.join(venv_path, "lib", f"python{pyver}", "site-packages")

    if os.path.isdir(site_pkgs) and site_pkgs not in sys.path:
        sys.path.insert(0, site_pkgs)
        logmsg(f"[pythonrc] added site-packages: {site_pkgs}")
    else:
        logmsg(f"[pythonrc] site-packages not found or already in path: {site_pkgs!r}")


def load_config(fname):
    """
    Load and parse a JSON file if it exists, otherwise return empty dict.
    """
    path = os.path.join(JSON_DIR, fname)
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logmsg(f"[pythonrc] config not found: {fname}")
    except json.JSONDecodeError as e:
        logmsg(f"[pythonrc] error parsing {fname}: {e}")
    return {}


def apply_dynamic_entry(entry, kind):
    """
    Given one entry (from 'projects' or 'courses'):
      - set each var in 'vars' to its path
      - insert each 'sys_path' into sys.path
      - prepend each 'hda' into HOUDINI_OTLSCAN_PATH
    """
    for var_map in entry.get("vars", []):
        var = var_map.get("name")
        val = var_map.get("value")
        vkind = var_map.get("kind", "value")
        if not var or val is None:
            continue
        if vkind == "path":
            if os.path.isdir(val):
                os.environ[var] = val
                logmsg(f"[pythonrc] set env {var}={val}")
            else:
                logmsg(f"[pythonrc] path not found for {var}: {val}")
        else:
            os.environ[var] = str(val)
            logmsg(f"[pythonrc] set env {var}={val} (kind={vkind})")

    # 2) python imports
    for sp in entry.get("sys_path", []):
        if sp and os.path.isdir(sp) and sp not in sys.path:
            sys.path.insert(0, sp)
            logmsg(f"[pythonrc] added sys.path for {kind}: {sp}")

    # 3) hda scan paths
    scan = os.environ.get("HOUDINI_OTLSCAN_PATH", "")
    for hp in entry.get("hda", []):
        if hp and os.path.isdir(hp):
            parts = scan.split(":") if scan else []
            if hp not in parts:
                scan = hp + (":" + scan if scan else "")
                logmsg(f"[pythonrc] prepended HDA path for {kind}: {hp}")
    os.environ["HOUDINI_OTLSCAN_PATH"] = scan

# ─────────────────────────────────────────────────────────────────────────
# 3) Bootstrap & error handling
# ─────────────────────────────────────────────────────────────────────────
def _bootstrap():
    # 3.1 Poetry packages
    add_poetry_site_packages("houdinilab")

    # 3.2 Projects (vars, python paths, HDAs)
    projects_cfg = load_config("projects.json")
    for entry in projects_cfg.get("projects", []):
        if not entry.get("enable", True):
            logmsg(f"[pythonrc] skipping disabled project: {entry.get('name','<unnamed>')}")
            continue
        apply_dynamic_entry(entry, kind="project")

    # 3.3 Courses (vars, python paths, HDAs)
    courses_cfg = load_config("courses.json")
    for entry in courses_cfg.get("courses", []):
        if not entry.get("enable", True):
            logmsg(f"[pythonrc] skipping disabled course: {entry.get('name','<unnamed>')}")
            continue
        apply_dynamic_entry(entry, kind="course")

try:
    _bootstrap()
except Exception:
    with open(ERROR_LOG, "w") as f:
        traceback.print_exc(file=f)
    # Uncomment to propagate error into Houdini console:
    # raise
