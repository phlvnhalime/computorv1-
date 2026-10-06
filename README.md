# Computor v1

Polynomial equation solver (degree ≤ 2) for the 42 *Computor v1* subject, written in Python. Includes the mandatory part and bonuses.

## Requirements

- Python 3.10+
- **No math library** for solving — square root and GCD are implemented from scratch (`+`, `-`, `*`, `/` only).

## Usage

```bash
# From the repo root
./computor "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"

# Or as a module
PYTHONPATH=. python3 -m computorv1 "5 * X^0 + 4 * X^1 = 4 * X^0"

# No argument → read equation from STDIN
./computor
```

### Options

| Flag | Description |
|------|-------------|
| `-v` / `--verbose` | Intermediate calculation steps (bonus) |
| `-n` / `--natural` | Natural reduced form, e.g. `5 + 4 * X = 0` (bonus) |
| `--strict` | Only accept subject form `a * X^p` |
| `--no-fractions` | Prefer decimal output over irreducible fractions |
| `--no-color` | Disable coloured output |

## Mandatory behaviour

For every equation the program prints at least:

1. **Reduced form** (`… = 0`)
2. **Polynomial degree** (when relevant)
3. **Solution(s)** and discriminant polarity for degree 2

Special cases:

- `0 = 0` → any real number is a solution
- Non-zero constant = 0 → no solution
- Degree > 2 → refuses to solve
- Discriminant &lt; 0 → complex solutions

## Bonuses implemented

1. **Free-form entry** — `5 + 4 * X + X^2 = X^2`, bare `X`, constants without `* X^0`, etc.
2. **Syntax / vocabulary errors** — clear `Error: …` messages (exit code 1)
3. **Irreducible fractions** — e.g. `-1/4`, `-1/5 + 2i/5`
4. **Intermediate steps** — `-v`
5. **Coloured output** (TTY)
6. **Natural reduced form** — `-n`

## Subject examples

```text
$ ./computor "5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0"
Reduced form: 4 * X^0 + 4 * X^1 - 9.3 * X^2 = 0
Polynomial degree: 2
Discriminant is strictly positive, the two solutions are:
0.905238990791
-0.475131463909

$ ./computor "5 * X^0 + 4 * X^1 = 4 * X^0"
Reduced form: 1 * X^0 + 4 * X^1 = 0
Polynomial degree: 1
The solution is:
-1/4

$ ./computor "1 * X^0 + 2 * X^1 + 5 * X^2 = 0"
Reduced form: 1 * X^0 + 2 * X^1 + 5 * X^2 = 0
Polynomial degree: 2
Discriminant is strictly negative, the two complex solutions are:
-1/5 + 2i/5
-1/5 - 2i/5

$ ./computor "5 + 4 * X + X^2 = X^2"
Reduced form: 5 * X^0 + 4 * X^1 + 0 * X^2 = 0
Polynomial degree: 1
The solution is:
-5/4
```

## Project layout

```text
computor                 # executable entry point
computorv1/
  __main__.py            # CLI
  parser.py              # strict + free-form parsing
  solver.py              # degree 0 / 1 / 2 solving
  math_utils.py          # sqrt, gcd, fractions
  colors.py              # ANSI colours
```
