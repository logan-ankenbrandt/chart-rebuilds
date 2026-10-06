"""Check every published text file against the writing rules.

Scans the files git tracks or would track (not ignored) for dash characters, banned words and banned
phrases (src/writing_rules.py), and Markdown files for semicolons in prose outside code blocks.

Usage: python3 src/check_writing.py   (exits non-zero on any finding)
"""

import subprocess
import sys
from pathlib import Path

from writing_rules import violations

ROOT = Path(__file__).resolve().parent.parent
TEXT = {".md", ".csv", ".json", ".txt", ".py", ".js", ".mjs", ".sh", ".html", ""}


def published_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.splitlines() if (ROOT / p).is_file()]


def main() -> int:
    findings = []
    scanned = 0
    for path in published_files():
        if path.suffix.lower() not in TEXT:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        rel = path.relative_to(ROOT)
        in_code = False
        for n, line in enumerate(text.splitlines(), start=1):
            for v in violations(line):
                findings.append(f"{rel}:{n}: {v!r}")
            if path.suffix == ".md":
                if line.lstrip().startswith("```"):
                    in_code = not in_code
                elif not in_code and ";" in line:
                    findings.append(f"{rel}:{n}: semicolon in Markdown prose")
    for f in findings:
        print(f)
    print(f"writing rules: {scanned} text files scanned, {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
