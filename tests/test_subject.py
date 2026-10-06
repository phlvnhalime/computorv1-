#!/usr/bin/env python3
"""Quick checks against the subject PDF examples."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(eq: str, *extra: str) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    out = subprocess.check_output(
        [sys.executable, str(ROOT / "computor"), "--no-color", *extra, eq],
        text=True,
        cwd=ROOT,
        env=env,
        stderr=subprocess.STDOUT,
    )
    return out.strip()


def expect(eq: str, *needles: str, extra: tuple[str, ...] = ()) -> None:
    out = run(eq, *extra)
    for n in needles:
        if n not in out:
            print(f"FAIL: {eq!r}\n  missing {n!r}\n  got:\n{out}")
            sys.exit(1)
    print(f"OK  {eq!r}")


def main() -> None:
    expect(
        "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0",
        "Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0",
        "Polynomial degree: 2",
        "Discriminant is strictly positive",
        "0.905238990791",
        "-0.475131463909",
    )
    expect(
        "5 * X^0 + 4 * X^1 = 4 * X^0",
        "Reduced form: 1 * X^0 + 4 * X^1 = 0",
        "Polynomial degree: 1",
        "The solution is:",
        "-1/4",
    )
    expect(
        "8 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 3 * X^0",
        "Reduced form: 5 * X^0 - 6 * X^1 + 0 * X^2 - 5.6 * X^3 = 0",
        "Polynomial degree: 3",
        "I can't solve.",
    )
    expect(
        "6 * X^0 = 6 * X^0",
        "Reduced form: 0 * X^0 = 0",
        "Any real number is a solution.",
    )
    expect(
        "10 * X^0 = 15 * X^0",
        "Reduced form: -5 * X^0 = 0",
        "No solution.",
    )
    expect(
        "1 * X^0 + 2 * X^1 + 5 * X^2 = 0",
        "Discriminant is strictly negative",
        "-1/5 + 2i/5",
        "-1/5 - 2i/5",
    )
    expect(
        "5 + 4 * X + X^2= X^2",
        "The solution is:",
        "-5/4",
    )
    expect(
        "5 + 4 * X = 0",
        "Reduced form: 5 + 4 * X = 0",
        "-5/4",
        extra=("-n",),
    )
    try:
        run("not an equation")
        print("FAIL: expected parse error")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("OK  syntax error rejected")
    print("All checks passed.")


if __name__ == "__main__":
    main()
