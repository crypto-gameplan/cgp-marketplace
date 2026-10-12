#!/usr/bin/env python3
"""Check a project's Docker files for the mistakes beginners hit most.

Errors are things that leak secrets, lose data or break builds later:
unpinned base images, a final stage running as root, secrets baked into the
image, a missing .dockerignore entry for .env, a tracked .env file, a
database without a volume, and services reaching each other via localhost.
Warnings are hygiene: install without a lock file, code copied before the
dependency install, database ports open to the network, start order without
a health condition, a missing .env.example.

Uses only the Python standard library and reads compose files line by line,
so it needs no YAML package. Usage:
    python3 check_docker.py [project-dir]
Exit code 1 when there are errors.
"""

import os
import re
import subprocess
import sys

DB_IMAGES = ("postgres", "mysql", "mariadb", "mongo", "redis", "valkey")
DB_PORTS = {"5432", "3306", "27017", "6379"}
SECRET_NAME = re.compile(r"(SECRET|PASSWORD|PASSWD|TOKEN|API_?KEY|PRIVATE_?KEY)", re.I)
INSTALL = re.compile(r"\b(npm (ci|install|i)\b|pnpm install|yarn( install)?\b|bun install|uv sync|pip install|poetry install|bundle install|composer install|go mod download|cargo build)")

errors, warnings = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def logical_lines(text):
    """Dockerfile lines with continuations joined and comments dropped."""
    out, buf = [], ""
    for raw in text.splitlines():
        line = raw.strip()
        if not buf and (not line or line.startswith("#")):
            continue
        if line.endswith("\\"):
            buf += line[:-1] + " "
            continue
        out.append(buf + line)
        buf = ""
    if buf:
        out.append(buf)
    return out


def image_unpinned(ref):
    """True when an image reference has no tag/digest or uses latest."""
    if "@sha256:" in ref:
        return False
    last = ref.rsplit("/", 1)[-1]
    if ":" not in last:
        return True
    return last.split(":", 1)[1] in ("latest", "")


def check_dockerfile(path, rel):
    lines = logical_lines(read(path))
    stages, current = [], None
    for line in lines:
        word, _, rest = line.partition(" ")
        word = word.upper()
        if word == "FROM":
            parts = [p for p in rest.split() if not p.startswith("--")]
            ref = parts[0] if parts else ""
            alias = parts[2].lower() if len(parts) >= 3 and parts[1].lower() == "as" else None
            known = {s["alias"] for s in stages if s["alias"]}
            if ref != "scratch" and ref.lower() not in known and "$" not in ref and image_unpinned(ref):
                err(rel, f"base image '{ref}' is not pinned to a version (use for example node:24-slim, never latest)")
            current = {"alias": alias, "user": None, "copied_all": False, "installed": False}
            stages.append(current)
            continue
        if current is None:
            continue
        if word == "USER":
            current["user"] = rest.strip().split(":")[0]
        elif word in ("COPY", "ADD"):
            srcs = [p for p in rest.split() if not p.startswith("--")][:-1]
            if any(os.path.basename(s) == ".env" or s.endswith("/.env") for s in srcs):
                err(rel, "copies .env into the image; secrets belong in .env at runtime, not in the image")
            if any(s in (".", "./") for s in srcs) and "--from=" not in rest and not current["installed"]:
                current["copied_all"] = True
        elif word == "RUN":
            if INSTALL.search(rest):
                if current["copied_all"] and not current["installed"] and "--mount=type=bind" not in rest:
                    warn(rel, "copies all code before installing dependencies; copy the manifest and lock file first so code changes do not reinstall everything")
                current["installed"] = True
                if re.search(r"\bnpm (install|i)\b", rest) and "npm ci" not in rest:
                    warn(rel, "uses 'npm install'; 'npm ci' installs exactly what package-lock.json says")
                if re.search(r"\bpip install\b", rest) and " -r " not in rest and "--requirement" not in rest and " -e " not in rest and " ." not in rest:
                    warn(rel, "pip install without a requirements file; versions are not pinned")
        elif word in ("ENV", "ARG"):
            for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\"[^\"]*\"|'[^']*'|\S+)", rest):
                name, value = m.group(1), m.group(2).strip("'\"")
                if SECRET_NAME.search(name) and value and not value.startswith("$"):
                    err(rel, f"{word} {name} puts a secret value into the image; pass it at runtime from .env")
    if stages:
        final = stages[-1]
        if final["user"] in (None, "root", "0"):
            err(rel, "the final stage runs as root; add a normal user and USER before CMD")


def check_dockerignore(root):
    path = os.path.join(root, ".dockerignore")
    if not os.path.exists(path):
        err(".dockerignore", "missing; without it .env, .git and node_modules/.venv end up in the image")
        return
    entries = {l.strip().rstrip("/").lstrip("/") for l in read(path).splitlines() if l.strip() and not l.startswith("#")}
    if not ({".env", ".env*", "*.env", "**/.env"} & entries):
        err(".dockerignore", ".env is not excluded; secrets would be copied into the image")
    if ".git" not in entries and "**/.git" not in entries:
        warn(".dockerignore", ".git is not excluded")
    if os.path.exists(os.path.join(root, "package.json")) and not ({"node_modules", "**/node_modules"} & entries):
        warn(".dockerignore", "node_modules is not excluded; the build copies local packages built for your computer")
    if os.path.exists(os.path.join(root, "pyproject.toml")) or os.path.exists(os.path.join(root, "requirements.txt")):
        if not ({".venv", "venv", "**/.venv"} & entries):
            warn(".dockerignore", ".venv is not excluded")


def parse_compose(text):
    """Very small reader: services with their image, volumes, ports, env values, depends_on and healthcheck."""
    services, in_services, cur, section = {}, False, None, None
    svc_indent = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0:
            in_services = line.startswith("services:")
            cur = None
            continue
        if not in_services:
            continue
        if svc_indent is None:
            svc_indent = indent
        if indent == svc_indent and line.endswith(":"):
            cur = line[:-1].strip().strip("'\"")
            services[cur] = {"image": None, "volumes": [], "ports": [], "env": [], "depends": {}, "health": False, "build": False}
            section = None
            continue
        if cur is None:
            continue
        s = services[cur]
        if indent == svc_indent + 2 or (section is None and indent > svc_indent):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            section = key
            if key == "image":
                s["image"] = val.strip("'\"")
            elif key == "healthcheck":
                s["health"] = True
            elif key == "build":
                s["build"] = True
            elif key == "depends_on" and val.startswith("["):
                for d in re.findall(r"[\w-]+", val):
                    s["depends"][d] = None
            continue
        item = line[2:].strip().strip("'\"") if line.startswith("- ") else line
        if section == "volumes":
            s["volumes"].append(item)
        elif section == "ports":
            s["ports"].append(item)
        elif section == "environment":
            s["env"].append(item)
        elif section == "depends_on":
            if line.startswith("- "):
                s["depends"][item] = None
            elif line.endswith(":") and indent == svc_indent + 4:
                s["depends"][line[:-1]] = None
            elif line.startswith("condition:"):
                last = list(s["depends"])[-1] if s["depends"] else None
                if last:
                    s["depends"][last] = line.split(":", 1)[1].strip()
    return services


def check_compose(path, rel, root):
    text = read(path)
    services = parse_compose(text)
    for name, s in services.items():
        img = s["image"] or ""
        base = img.rsplit("/", 1)[-1].split(":")[0]
        if img and "$" not in img and image_unpinned(img):
            err(rel, f"service '{name}' uses image '{img}' without a pinned version")
        is_db = base in DB_IMAGES
        if is_db:
            if not s["volumes"]:
                (warn if base in ("redis", "valkey") else err)(rel, f"service '{name}' has no volume; its data is lost on 'docker compose down'")
            for p in s["ports"]:
                if not p.startswith(("127.0.0.1:", "localhost:", "[::1]:")):
                    warn(rel, f"service '{name}' publishes port '{p}' to the whole network; use '127.0.0.1:{p.split(':')[-1]}:{p.split(':')[-1]}' or no port")
            if base == "postgres":
                m = re.match(r"postgres:(\d+)", img)
                if m and int(m.group(1)) >= 18 and any(v.rstrip("/").endswith("/var/lib/postgresql/data") for v in s["volumes"]):
                    err(rel, f"service '{name}': Postgres 18+ keeps data under /var/lib/postgresql, mount the volume there")
        for e in s["env"]:
            if re.search(r"(localhost|127\.0\.0\.1):(\d+)", e):
                port = re.search(r"(localhost|127\.0\.0\.1):(\d+)", e).group(2)
                if port in DB_PORTS or any(port in p for o in services.values() for p in o["ports"]):
                    err(rel, f"service '{name}' reaches another service via localhost ('{e[:60]}'); inside compose use the service name")
            m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.+)", e)
            if m and SECRET_NAME.search(m.group(1)) and "${" not in m.group(2) and m.group(2).strip("'\" ") not in ("", "null"):
                warn(rel, f"service '{name}' has {m.group(1)} written into compose.yaml; read it from .env with ${{{m.group(1)}}}")
        for dep, cond in s["depends"].items():
            if dep not in services:
                continue
            if services[dep]["health"] and cond != "service_healthy":
                warn(rel, f"service '{name}' starts before '{dep}' is ready; use depends_on with condition: service_healthy")
            dep_base = (services[dep]["image"] or "").rsplit("/", 1)[-1].split(":")[0]
            if dep_base in DB_IMAGES and not services[dep]["health"]:
                warn(rel, f"service '{dep}' has no healthcheck, so '{name}' cannot wait until it accepts connections")
    for m in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*):?-([^}]+)\}", text):
        if SECRET_NAME.search(m.group(1)) and m.group(2).strip():
            err(rel, f"${{{m.group(1)}:-...}} gives a secret a default that works when nobody sets it; use ${{{m.group(1)}:?set {m.group(1)} in .env}}")
    for line in text.splitlines():
        if "pg_isready" in line and not line.lstrip().startswith("#") and not re.search(r"-h\s|--host", line):
            warn(rel, "pg_isready without -h 127.0.0.1 reports ready during Postgres's first-start setup; the app may connect too early")
    uses_env = "${" in text or "env_file" in text
    if uses_env and not os.path.exists(os.path.join(root, ".env.example")):
        warn(".env.example", "missing; the next person cannot see which variables to fill in")


def check_git(root):
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", ".env", "**/.env"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return
    if out.returncode == 0 and out.stdout.strip():
        err(".env", "is tracked by git; remove it from git (git rm --cached .env), add it to .gitignore and rotate the secrets in it")
    if out.returncode == 0 and os.path.exists(os.path.join(root, ".env")):
        ign = subprocess.run(["git", "-C", root, "check-ignore", "-q", ".env"], capture_output=True)
        if ign.returncode == 1:
            warn(".gitignore", ".env is not ignored by git")


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    skip = {"node_modules", ".git", ".venv", "venv", "dist", "build", ".next"}
    dockerfiles, composes = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if f == "Dockerfile" or f.startswith("Dockerfile.") or f.endswith(".Dockerfile"):
                dockerfiles.append(p)
            elif re.fullmatch(r"(docker-)?compose([.\w-]*)?\.ya?ml", f):
                composes.append(p)
    if not dockerfiles and not composes:
        print(f"No Dockerfile or compose file found in {root}")
        return 1
    for p in dockerfiles:
        check_dockerfile(p, os.path.relpath(p, root))
    if dockerfiles:
        check_dockerignore(root)
    for p in composes:
        check_compose(p, os.path.relpath(p, root), root)
    check_git(root)

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
