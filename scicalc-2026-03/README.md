# scicalc — a robust scientific calculator in C++

A single-file, dependency-free scientific calculator built around a proper
tokenizer and recursive-descent parser. It evaluates expressions with correct
operator precedence and associativity, a large function library, user
variables, and careful error handling (every error points at the offending
character).

## Build

```sh
g++ -std=c++17 -O2 -o scicalc calculator.cpp -lm
```

## Run

```sh
./scicalc                     # interactive REPL
./scicalc "2+2" "sin(pi)"     # evaluate each argument
echo "3*4" | ./scicalc        # read from a pipe
```

## Language

| Category      | Supported |
|---------------|-----------|
| Operators     | `+ - * / % ^` (also `**`), unary `-`/`+`, postfix `!` (factorial) |
| Grouping      | `( )` and implicit multiplication: `2pi`, `3(4+1)`, `2sin(x)` |
| Literals      | decimal `3.14`, scientific `1.2e-3`, hex `0xFF`, binary `0b1010` |
| Constants     | `pi tau e phi inf nan`, plus `ans` (last result) |
| Assignment    | `x = 3`, then reuse `x` in later expressions |

Precedence, low → high: `+ -` < `* / % (implicit)` < unary `- +` < `^`
(right-assoc) < postfix `!` < primary. Exponentiation binds tighter than unary
minus, so `-2^2 = -4` and `2^-3 = 0.125`, matching standard convention.

### Functions

- **trig:** `sin cos tan cot sec csc asin acos atan atan2`
- **hyperbolic:** `sinh cosh tanh asinh acosh atanh`
- **exp/log:** `exp exp2 expm1 ln log10 log2 log1p`, `log(x)`, `log(base, x)`
- **powers/roots:** `sqrt cbrt pow(a,b) root(x,n) hypot(a,b)`
- **rounding:** `abs floor ceil round trunc frac sign`
- **angles:** `deg(x) rad(x)`
- **integer:** `mod(a,b) gcd(a,b) lcm(a,b)`
- **combinatorics:** `fact(n)`, `n!`, `gamma lgamma ncr(n,r) npr(n,r)`
- **reducers (variadic):** `min max sum mean median`, `clamp(x,lo,hi)`

### REPL commands

`help` · `deg` / `rad` (angle mode) · `vars` · `clear` · `quit` / `exit`

## Robustness

- Division/modulo by zero, domain errors (`sqrt(-1)`, `ln(0)`, `asin(2)`, …),
  unknown identifiers/functions, arity mismatches, malformed numbers, and
  unbalanced parentheses are all reported with a message and a caret under the
  problem position.
- Trig functions respect the active angle mode (radians by default).
- Factorial and `ncr`/`npr` generalize to non-integers via the Gamma function.

## Tests

```sh
./run_tests.sh    # 59 checks covering arithmetic, functions, and error paths
```
