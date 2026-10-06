#!/usr/bin/env python3
"""Computor v1 — solve polynomial equations of degree ≤ 2."""

from __future__ import annotations

import argparse
import sys

from computorv1.colors import Colors
from computorv1.parser import ParseError, parse_equation
from computorv1.solver import solve


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="computor",
        description="Solve polynomial equations of degree 0, 1 or 2.",
        epilog=(
            "Bonuses: free-form input, syntax errors, irreducible fractions, "
            "intermediate steps (-v), colours, natural reduced form (-n)."
        ),
    )
    p.add_argument(
        "equation",
        nargs="?",
        help="Equation to solve. If omitted, read from STDIN.",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show intermediate calculation steps (bonus).",
    )
    p.add_argument(
        "-n",
        "--natural",
        action="store_true",
        help="Print reduced form in natural notation (bonus).",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable coloured output.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Accept only the subject form a * X^p (disable free form).",
    )
    p.add_argument(
        "--no-fractions",
        action="store_true",
        help="Never display solutions as fractions.",
    )
    return p


def read_equation(arg: str | None) -> str:
    if arg is not None:
        return arg
    if sys.stdin.isatty():
        print("Enter an equation:", flush=True)
    line = sys.stdin.readline()
    if not line:
        raise SystemExit("No equation provided.")
    return line.rstrip("\n")


def print_result(result, *, verbose: bool, colors: Colors) -> None:
    if verbose and result.steps:
        print(colors.magenta("── Intermediate steps ──"))
        for step in result.steps:
            print(colors.yellow("•"), step)
        print(colors.magenta("── Result ──"))

    print(f"{colors.bold('Reduced form:')} {colors.cyan(result.reduced)}")

    # Message lines already include degree / solutions / errors in subject wording
    for i, line in enumerate(result.message_lines):
        if line.startswith("Polynomial degree:"):
            print(f"{colors.bold('Polynomial degree:')} {line.split(':', 1)[1].strip()}")
        elif line.startswith("Discriminant"):
            print(colors.green(line) if "positive" in line or "solution is" in line.lower() else colors.yellow(line) if "negative" in line else line)
        elif line in ("No solution.", "Any real number is a solution."):
            print(colors.red(line) if line.startswith("No") else colors.green(line))
        elif line.startswith("The polynomial degree is strictly"):
            print(colors.red(line))
        elif line in ("The solution is:",) or line.endswith("solutions are:"):
            print(line)
        else:
            # solution values
            print(colors.cyan(line) if i > 0 else line)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    colors = Colors(enabled=False if args.no_color else None)

    try:
        raw = read_equation(args.equation)
        equation = parse_equation(raw, free_form=not args.strict)
        result = solve(
            equation,
            natural=args.natural,
            fractions=not args.no_fractions,
        )
        print_result(result, verbose=args.verbose, colors=colors)
        return 0
    except ParseError as exc:
        print(colors.red(f"Error: {exc}"), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
