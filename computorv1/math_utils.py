"""Elementary math helpers without using the math library.

Only +, -, *, / on reals are allowed by the subject; square root and GCD
are implemented from scratch.
"""

from __future__ import annotations


def abs_val(x: float) -> float:
    return x if x >= 0 else -x


def is_close(a: float, b: float = 0.0, eps: float = 1e-12) -> bool:
    return abs_val(a - b) < eps


def sqrt(n: float, precision: float = 1e-14) -> float:
    """Newton–Raphson square root. Raises ValueError for negative input."""
    if n < 0:
        raise ValueError("Cannot compute square root of a negative number")
    if is_close(n, 0.0):
        return 0.0
    x = n if n >= 1.0 else 1.0
    while True:
        nxt = 0.5 * (x + n / x)
        if abs_val(nxt - x) < precision:
            return nxt
        x = nxt


def gcd(a: int, b: int) -> int:
    """Euclidean algorithm on non-negative integers."""
    a = abs_val(a)
    b = abs_val(b)
    while b:
        a, b = b, a % b
    return a


def float_to_fraction(value: float, max_den: int = 1_000_000) -> tuple[int, int] | None:
    """Best rational approximation of *value* with denominator ≤ max_den.

    Returns (numerator, denominator) in lowest terms, or None if the value
    is not close enough to a simple fraction.
    """
    if is_close(value):
        return 0, 1

    sign = 1
    if value < 0:
        sign = -1
        value = -value

    # Continued-fraction / Farey approximation
    a = int(value)
    if is_close(value, a):
        return sign * a, 1

    lower_n, lower_d = int(value), 1
    upper_n, upper_d = int(value) + 1, 1

    while True:
        med_n = lower_n + upper_n
        med_d = lower_d + upper_d
        if med_d > max_den:
            break
        med = med_n / med_d
        if is_close(med, value, 1e-10):
            g = gcd(med_n, med_d)
            return sign * (med_n // g), med_d // g
        if med < value:
            lower_n, lower_d = med_n, med_d
        else:
            upper_n, upper_d = med_n, med_d

    # Pick the closer bound
    candidates = [(lower_n, lower_d), (upper_n, upper_d)]
    best = min(candidates, key=lambda nd: abs_val(nd[0] / nd[1] - value))
    if abs_val(best[0] / best[1] - value) < 1e-9:
        g = gcd(best[0], best[1])
        return sign * (best[0] // g), best[1] // g
    return None


def format_number(value: float, as_fraction: bool = True) -> str:
    """Format a float, preferring an irreducible fraction when relevant."""
    if is_close(value):
        return "0"
    if as_fraction:
        frac = float_to_fraction(value)
        if frac is not None:
            num, den = frac
            if den == 1:
                return str(num)
            return f"{num}/{den}"
    # Compact float formatting (strip trailing zeros)
    text = f"{value:.12g}"
    return text


def format_complex(real: float, imag: float, as_fraction: bool = True) -> str:
    """Format a + bi with optional irreducible fractions."""
    r = format_number(real, as_fraction)
    i_abs = format_number(abs_val(imag), as_fraction)
    sign = "+" if imag >= 0 else "-"

    if is_close(imag):
        return r
    if is_close(real):
        if is_close(abs_val(imag), 1.0):
            return "i" if imag > 0 else "-i"
        return f"{format_number(imag, as_fraction)}i"

    # Prefer forms like "2i/5" when imag is a fraction num/den
    if as_fraction:
        frac = float_to_fraction(abs_val(imag))
        if frac is not None and frac[1] != 1:
            num, den = frac
            imag_part = f"{num}i/{den}"
        elif frac is not None and frac[0] == 1:
            imag_part = "i"
        else:
            imag_part = f"{i_abs}i"
    else:
        imag_part = f"{i_abs}i"

    return f"{r} {sign} {imag_part}"
