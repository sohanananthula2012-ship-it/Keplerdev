#!/usr/bin/env bash
# Test harness: feed expressions to scicalc one-shot mode and compare output.
set -u
BIN=./scicalc
pass=0; fail=0

# check "<expr>" "<expected stdout>"
check() {
  local expr="$1" want="$2"
  local got
  got="$($BIN "$expr" 2>/dev/null)"
  if [[ "$got" == "$want" ]]; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
    printf 'FAIL: %-28s got [%s]  want [%s]\n' "$expr" "$got" "$want"
  fi
}

# check_err "<expr>" "<substring expected on stderr>"
check_err() {
  local expr="$1" sub="$2"
  local got
  got="$($BIN "$expr" 2>&1 >/dev/null)"
  if [[ "$got" == *"$sub"* ]]; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
    printf 'FAIL(err): %-24s got [%s]  want substr [%s]\n' "$expr" "$got" "$sub"
  fi
}

# --- Arithmetic & precedence ---
check "2+2" "4"
check "2+3*4" "14"
check "(2+3)*4" "20"
check "2-3-4" "-5"                 # left assoc
check "100/4/5" "5"                # left assoc
check "2^3^2" "512"                # right assoc: 2^(3^2)
check "-2^2" "-4"                  # unary binds looser than ^
check "2^-3" "0.125"               # negative exponent
check "-3^2+1" "-8"                # -(3^2)+1
check "(-2)^2" "4"
check "10%3" "1"
check "7 % 4 + 1" "4"
check "2 ** 10" "1024"             # ** alias

# --- Unary / signs ---
check "-5" "-5"
check "--5" "5"
check "-+-3" "3"
check "3*-2" "-6"

# --- Implicit multiplication ---
check "2(3)" "6"
check "(1+2)(3+4)" "21"
check "2pi" "6.28318530717959"

# --- Factorial / postfix ---
check "5!" "120"
check "0!" "1"
check "3!+1" "7"
check "(2+1)!" "6"

# --- Functions ---
check "sqrt(16)" "4"
check "cbrt(27)" "3"
check "pow(2,10)" "1024"
check "root(27,3)" "3"
check "abs(-7)" "7"
check "floor(3.7)" "3"
check "ceil(3.2)" "4"
check "round(2.5)" "3"
check "gcd(48,36)" "12"
check "lcm(4,6)" "12"
check "ncr(5,2)" "10"
check "npr(5,2)" "20"
check "max(3,9,2,7)" "9"
check "min(3,9,2,7)" "2"
check "sum(1,2,3,4)" "10"
check "mean(2,4,6)" "4"
check "hypot(3,4)" "5"
check "log(2,8)" "3"
check "log2(1024)" "10"
check "log10(1000)" "3"
check "clamp(15,0,10)" "10"
check "sign(-42)" "-1"
check "mod(10,3)" "1"

# --- Constants / nesting ---
check "gcd(ncr(6,3),20)" "20"      # 20 gcd 20
check "sqrt(2)^2" "2"

# --- Variables / assignment ---
check "x = 5" "x = 5"

# --- Error handling ---
check_err "1/0"        "division by zero"
check_err "sqrt(-4)"   ">= 0"
check_err "ln(0)"      "must be > 0"
check_err "2+"         "expected a number"
check_err "(1+2"       "missing closing"
check_err "foo(3)"     "unknown function"
check_err "asin(2)"    "out of domain"
check_err "3 4 +"      "expected a number"
check_err "@"          "unexpected character"

echo "---------------------------------------------"
echo "PASS: $pass   FAIL: $fail"
[[ $fail -eq 0 ]]
