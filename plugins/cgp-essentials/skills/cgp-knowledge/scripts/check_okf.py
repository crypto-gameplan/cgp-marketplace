#!/usr/bin/env python3
"""Check a folder against Open Knowledge Format (OKF) v0.2.

Errors are conformance failures (spec section 11): a concept without
parseable frontmatter or without a non-empty `type`, frontmatter in a
non-root index.md, or a malformed log.md date heading. Warnings are
hygiene: missing descriptions, stale or unknown-status concepts, and links
to concepts that do not exist (allowed by the spec, but worth a look).

Uses only the Python standard library. Usage:
    python3 check_okf.py <bundle-dir>
Exit code 1 when there are errors.
"""

import datetime
import os
import re
import sys

RESERVED = {"index.md", "log.md"}
STATUSES = {"draft", "stable", "deprecated"}
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)(?:#[^)]*)?\)")


def frontmatter(text):
    """Returns (frontmatter text, body) or (None, text) when there is none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def top_level(fm, key):
    """Value of a top-level `key:` line (not indented), or None."""
    m = re.search(r"^" + re.escape(key) + r":[ \t]*(.*)$", fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip("\"'")


def parse_time(value):
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__.strip())
        return 2
    root = os.path.abspath(sys.argv[1])
    errors, warnings, concepts = [], [], 0
    now = datetime.datetime.now(datetime.timezone.utc)

    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(folder, name)
            rel = os.path.relpath(path, root)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            fm, body = frontmatter(text)

            if name == "index.md":
                if fm is not None:
                    keys = [k for k in re.findall(r"^([A-Za-z_][\w-]*):", fm, re.MULTILINE)]
                    if folder != root or any(k != "okf_version" for k in keys):
                        errors.append(f"{rel}: index.md may only carry frontmatter at the bundle root, and only okf_version")
                continue
            if name == "log.md":
                for heading in re.findall(r"^## (.+)$", text, re.MULTILINE):
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", heading.strip()):
                        errors.append(f"{rel}: log date heading '{heading.strip()}' is not YYYY-MM-DD")
                continue

            concepts += 1
            if fm is None:
                errors.append(f"{rel}: no YAML frontmatter block (--- at the top and a closing ---)")
                continue
            if not top_level(fm, "type"):
                errors.append(f"{rel}: frontmatter has no non-empty `type`")
            if not top_level(fm, "description"):
                warnings.append(f"{rel}: no `description`; indexes and search have nothing to show")
            status = top_level(fm, "status")
            if status and status not in STATUSES:
                warnings.append(f"{rel}: status '{status}' is not draft, stable or deprecated")
            stale = top_level(fm, "stale_after")
            if stale:
                when = parse_time(stale)
                if when is None or when.tzinfo is None:
                    warnings.append(f"{rel}: stale_after '{stale}' is not an ISO 8601 time with offset")
                elif now >= when:
                    warnings.append(f"{rel}: stale since {stale}; re-verify or deprecate it")

            for target in LINK.findall(body):
                if re.match(r"^[a-z]+://", target):
                    continue
                resolved = os.path.join(root, target.lstrip("/")) if target.startswith("/") \
                    else os.path.join(folder, target)
                if not os.path.exists(os.path.normpath(resolved)):
                    warnings.append(f"{rel}: link to {target} has no concept yet")

    for line in errors:
        print(f"ERROR   {line}")
    for line in warnings:
        print(f"WARNING {line}")
    print(f"\n{concepts} concept(s), {len(errors)} error(s), {len(warnings)} warning(s).")
    if not errors:
        print("Conformant with OKF v0.2.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
