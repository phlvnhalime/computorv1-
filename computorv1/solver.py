"""Solve reduced polynomial equations of degree ≤ 2."""

from __future__ import annotations

from dataclasses import dataclass, field

from .math_utils import format_complex, format_number, is_close, sqrt
from .parser import Equation, format_reduced


@dataclass
class SolveResult:
    reduced: str
    degree: int | None
    message_lines: list[str]
    steps: list[str] = field(default_factory=list)


def solve(eq: Equation, *, natural: bool = False, fractions: bool = True) -> SolveResult:
    reduced = format_reduced(eq, natural=natural)
    steps: list[str] = [
        "Move all terms to the left-hand side so the equation becomes P(X) = 0.",
        f"Reduced form: {reduced}",
    ]

    a = eq.coeff(2)
    b = eq.coeff(1)
    c = eq.coeff(0)
    # Higher degrees
    higher = [exp for exp, coef in eq.coefficients.items() if exp > 2 and not is_close(coef)]

    # All coefficients ~ 0  →  0 = 0
    if all(is_close(coef) for coef in eq.coefficients.values()) or not eq.coefficients:
        steps.append("Every coefficient is zero: the identity 0 = 0 holds for all X.")
        return SolveResult(
            reduced=reduced,
            degree=None,
            message_lines=["Any real number is a solution."],
            steps=steps,
        )

    degree = eq.degree()
    steps.append(f"Polynomial degree: {degree}")

    if higher or degree > 2:
        return SolveResult(
            reduced=reduced,
            degree=degree,
            message_lines=[
                f"Polynomial degree: {degree}",
                "The polynomial degree is strictly greater than 2, I can't solve.",
            ],
            steps=steps,
        )

    if degree == 0:
        # Non-zero constant = 0 → no solution (subject omits the degree line)
        steps.append(f"Constant equation: {format_number(c, fractions)} = 0 (impossible)")
        return SolveResult(
            reduced=reduced,
            degree=0,
            message_lines=["No solution."],
            steps=steps,
        )

    if degree == 1:
        # b X + c = 0  →  X = -c / b
        steps.append(f"Linear equation: {format_number(b, fractions)} * X + {format_number(c, fractions)} = 0")
        steps.append(f"X = -({format_number(c, fractions)}) / ({format_number(b, fractions)})")
        solution = -c / b
        steps.append(f"X = {format_number(solution, fractions)}")
        return SolveResult(
            reduced=reduced,
            degree=1,
            message_lines=[
                "Polynomial degree: 1",
                "The solution is:",
                format_number(solution, fractions),
            ],
            steps=steps,
        )

    # degree == 2: a X^2 + b X + c = 0
    steps.append(
        f"Quadratic: a = {format_number(a, fractions)}, "
        f"b = {format_number(b, fractions)}, c = {format_number(c, fractions)}"
    )
    disc = b * b - 4 * a * c
    steps.append(f"Discriminant Δ = b² - 4ac = {format_number(disc, fractions)}")

    if is_close(disc):
        steps.append("Δ = 0 → one real double root: X = -b / (2a)")
        sol = -b / (2 * a)
        return SolveResult(
            reduced=reduced,
            degree=2,
            message_lines=[
                "Polynomial degree: 2",
                "Discriminant is zero, the solution is:",
                format_number(sol, fractions),
            ],
            steps=steps,
        )

    if disc > 0:
        steps.append("Δ > 0 → two distinct real roots")
        root = sqrt(disc)
        steps.append(f"√Δ = {format_number(root, fractions)}")
        # Subject order: (-b - √Δ) / 2a then (-b + √Δ) / 2a
        s1 = (-b - root) / (2 * a)
        s2 = (-b + root) / (2 * a)
        return SolveResult(
            reduced=reduced,
            degree=2,
            message_lines=[
                "Polynomial degree: 2",
                "Discriminant is strictly positive, the two solutions are:",
                format_number(s1, as_fraction=False),
                format_number(s2, as_fraction=False),
            ],
            steps=steps
            + [
                f"X₁ = (-b - √Δ) / (2a) = {format_number(s1, False)}",
                f"X₂ = (-b + √Δ) / (2a) = {format_number(s2, False)}",
            ],
        )

    # disc < 0 → complex
    steps.append("Δ < 0 → two complex conjugate roots")
    root = sqrt(-disc)
    real = -b / (2 * a)
    imag = root / (2 * a)
    c1 = format_complex(real, imag, fractions)
    c2 = format_complex(real, -imag, fractions)
    steps.append(f"X = -b/(2a) ± i√|Δ|/(2a)")
    return SolveResult(
        reduced=reduced,
        degree=2,
        message_lines=[
            "Polynomial degree: 2",
            "Discriminant is strictly negative, the two complex solutions are:",
            c1,
            c2,
        ],
        steps=steps + [f"X₁ = {c1}", f"X₂ = {c2}"],
    )
