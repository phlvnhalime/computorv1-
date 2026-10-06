"""Equation parser — strict subject format and free-form bonus."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


class ParseError(Exception):
    """Raised when the equation vocabulary or syntax is invalid."""


@dataclass
class Term:
    coefficient: float
    exponent: int

    def __str__(self) -> str:
        return f"{self.coefficient} * X^{self.exponent}"


@dataclass
class Equation:
    """Coefficients indexed by exponent after reducing to left-hand side = 0."""

    coefficients: dict[int, float] = field(default_factory=dict)
    # Exponents that appeared in the input (kept even when coeff becomes 0)
    seen_exponents: set[int] = field(default_factory=set)

    def degree(self) -> int:
        deg = 0
        for exp, coef in self.coefficients.items():
            if abs(coef) > 1e-12 and exp > deg:
                deg = exp
        return deg

    def coeff(self, exp: int) -> float:
        return self.coefficients.get(exp, 0.0)


# Strict term: a * X^p  (optional spaces)
_STRICT_TERM = re.compile(
    r"""
    (?P<sign>[+-]?)
    \s*
    (?P<coef>\d+(?:\.\d+)?)
    \s*\*\s*
    [Xx]
    \s*\^\s*
    (?P<exp>\d+)
    """,
    re.VERBOSE,
)

# Free-form pieces (bonus)
_FREE_NUMBER = re.compile(r"(?P<sign>[+-]?)\s*(?P<coef>\d+(?:\.\d+)?)")
_FREE_TERM = re.compile(
    r"""
    (?P<sign>[+-]?)
    \s*
    (?:
        (?P<coef>\d+(?:\.\d+)?)\s*\*\s*[Xx](?:\s*\^\s*(?P<exp1>\d+))?
      | (?P<coef2>\d+(?:\.\d+)?)\s*[Xx](?:\s*\^\s*(?P<exp2>\d+))?
      | [Xx](?:\s*\^\s*(?P<exp3>\d+))?
      | (?P<const>\d+(?:\.\d+)?)
    )
    """,
    re.VERBOSE,
)


def _add_coeff(bucket: dict[int, float], exp: int, coef: float) -> None:
    bucket[exp] = bucket.get(exp, 0.0) + coef


def _parse_side_strict(side: str) -> dict[int, float]:
    side = side.strip()
    if not side:
        raise ParseError("Empty side of the equation")

    # Normalize leading sign for the first term
    work = side if side[0] in "+-" else "+" + side
    coeffs: dict[int, float] = {}
    pos = 0
    while pos < len(work):
        m = _STRICT_TERM.match(work, pos)
        if not m:
            snippet = work[pos : pos + 20]
            raise ParseError(
                f"Invalid term near '{snippet.strip()}'. "
                "Expected form: a * X^p"
            )
        sign = -1.0 if m.group("sign") == "-" else 1.0
        coef = sign * float(m.group("coef"))
        exp = int(m.group("exp"))
        _add_coeff(coeffs, exp, coef)
        pos = m.end()
        # Allow only whitespace between terms; next char must be +/– or end
        rest = work[pos:]
        if rest and not rest[0].isspace() and rest[0] not in "+-":
            raise ParseError(f"Unexpected character after term: '{rest[0]}'")
        # skip spaces; sign belongs to next term match
        while pos < len(work) and work[pos].isspace():
            pos += 1

    if pos != len(work):
        raise ParseError("Trailing garbage on equation side")
    return coeffs


def _parse_side_free(side: str) -> dict[int, float]:
    side = side.strip()
    if not side:
        raise ParseError("Empty side of the equation")

    work = side if side[0] in "+-" else "+" + side
    coeffs: dict[int, float] = {}
    pos = 0
    while pos < len(work):
        m = _FREE_TERM.match(work, pos)
        if not m:
            snippet = work[pos : pos + 20]
            raise ParseError(f"Invalid free-form term near '{snippet.strip()}'")

        sign = -1.0 if m.group("sign") == "-" else 1.0

        if m.group("const") is not None and m.group("coef") is None and m.group("coef2") is None:
            # Plain constant — but only if the match didn't also eat an X via other groups.
            # The const alternative is last; check we didn't match X-only via exp3 without coef.
            pass

        if m.group("coef") is not None:
            coef = sign * float(m.group("coef"))
            exp = int(m.group("exp1")) if m.group("exp1") is not None else 1
        elif m.group("coef2") is not None:
            coef = sign * float(m.group("coef2"))
            exp = int(m.group("exp2")) if m.group("exp2") is not None else 1
        elif m.group("const") is not None:
            coef = sign * float(m.group("const"))
            exp = 0
        else:
            # Bare X or X^n
            coef = sign * 1.0
            exp = int(m.group("exp3")) if m.group("exp3") is not None else 1

        _add_coeff(coeffs, exp, coef)
        pos = m.end()
        while pos < len(work) and work[pos].isspace():
            pos += 1
        if pos < len(work) and work[pos] not in "+-":
            raise ParseError(f"Unexpected character: '{work[pos]}'")

    return coeffs


def parse_equation(raw: str, free_form: bool = True) -> Equation:
    """Parse an equation string into a reduced left-hand-side Equation."""
    if raw is None or not str(raw).strip():
        raise ParseError("Empty equation")

    text = str(raw).strip()
    # Disallow common junk early
    if text.count("=") != 1:
        raise ParseError("Equation must contain exactly one '=' sign")

    left_s, right_s = text.split("=", 1)
    parser = _parse_side_free if free_form else _parse_side_strict

    left = parser(left_s)
    right = parser(right_s)

    coeffs: dict[int, float] = {}
    seen: set[int] = set()
    for exp, coef in left.items():
        _add_coeff(coeffs, exp, coef)
        seen.add(exp)
    for exp, coef in right.items():
        _add_coeff(coeffs, exp, -coef)
        seen.add(exp)

    return Equation(coefficients=coeffs, seen_exponents=seen)


def format_reduced(eq: Equation, natural: bool = False) -> str:
    """Render reduced form `... = 0`."""
    display = dict(eq.coefficients)
    for exp in eq.seen_exponents:
        display.setdefault(exp, 0.0)

    # All-zero / empty → subject style
    if not display or all(abs(c) < 1e-12 for c in display.values()):
        return "0 = 0" if natural else "0 * X^0 = 0"

    # Drop pure zeros that were never in the input
    exponents = sorted(
        e for e, c in display.items()
        if abs(c) > 1e-12 or e in eq.seen_exponents
    )
    parts: list[str] = []

    for i, exp in enumerate(exponents):
        coef = display[exp]
        abs_coef = abs(coef)
        if abs(abs_coef - round(abs_coef)) < 1e-12:
            coef_txt = str(int(round(abs_coef)))
        else:
            coef_txt = f"{abs_coef:.12g}"

        if natural:
            if abs(coef) < 1e-12:
                continue
            if exp == 0:
                term = coef_txt
            elif exp == 1:
                term = "X" if abs(abs_coef - 1.0) < 1e-12 else f"{coef_txt} * X"
            else:
                if abs(abs_coef - 1.0) < 1e-12:
                    term = f"X^{exp}"
                else:
                    term = f"{coef_txt} * X^{exp}"
        else:
            term = f"{coef_txt} * X^{exp}"

        if not parts:
            parts.append(f"-{term}" if coef < 0 else term)
        else:
            parts.append(f"- {term}" if coef < 0 else f"+ {term}")

    if not parts:
        return "0 = 0" if natural else "0 * X^0 = 0"
    return " ".join(parts) + " = 0"
