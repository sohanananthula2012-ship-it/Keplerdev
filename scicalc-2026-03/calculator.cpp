// ============================================================================
//  scicalc — a robust scientific calculator in C++
// ----------------------------------------------------------------------------
//  Features
//    * Full recursive-descent expression parser with correct precedence and
//      associativity, informative error messages with caret position.
//    * Operators:  + - * / % ^  unary +/-  postfix factorial (!)
//                  implicit multiplication (e.g. 2pi, 3(4+1), 2sin(x))
//    * Large function library (trig, hyperbolic + inverses, logs, roots,
//      combinatorics, number theory, statistics-style reducers, ...).
//    * Constants: pi, tau, e, phi, inf, nan.
//    * Variables & assignment:  x = 3,  y = x^2 + 1.  'ans' holds last result.
//    * Angle modes: radians (default) or degrees, affecting trig functions.
//    * REPL with commands, plus one-shot evaluation from argv.
//
//  Build:   g++ -std=c++17 -O2 -o scicalc calculator.cpp -lm
//  Run:     ./scicalc                 (interactive)
//           ./scicalc "2+2" "sin(pi)" (evaluate arguments)
//           echo "3*4" | ./scicalc    (pipe)
// ============================================================================

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#if !defined(_WIN32)
#include <cstdio>
#include <unistd.h>
#endif

// ----------------------------------------------------------------------------
//  Error type carrying a position so we can point at the offending character.
// ----------------------------------------------------------------------------
struct CalcError : std::runtime_error {
    std::size_t pos;
    CalcError(const std::string& msg, std::size_t p = std::string::npos)
        : std::runtime_error(msg), pos(p) {}
};

// ----------------------------------------------------------------------------
//  Tokenizer
// ----------------------------------------------------------------------------
enum class Tok {
    Number, Ident, Plus, Minus, Star, Slash, Percent, Caret,
    LParen, RParen, Comma, Bang, Assign, End
};

struct Token {
    Tok         type;
    double      num = 0.0;   // for Number
    std::string text;        // for Ident
    std::size_t pos = 0;     // start position in the source
};

class Lexer {
public:
    explicit Lexer(const std::string& src) : s_(src) {}

    std::vector<Token> tokenize() {
        std::vector<Token> out;
        while (true) {
            skipSpaces();
            std::size_t start = i_;
            if (i_ >= s_.size()) { out.push_back({Tok::End, 0, "", start}); break; }

            char c = s_[i_];
            if (std::isdigit((unsigned char)c) || c == '.') {
                out.push_back(number(start));
            } else if (std::isalpha((unsigned char)c) || c == '_') {
                out.push_back(ident(start));
            } else {
                out.push_back(symbol(start));
            }
        }
        return out;
    }

private:
    const std::string& s_;
    std::size_t i_ = 0;

    void skipSpaces() {
        while (i_ < s_.size() && std::isspace((unsigned char)s_[i_])) ++i_;
    }

    Token number(std::size_t start) {
        // Accept decimal, scientific notation, and hex/binary integer literals.
        if (s_[i_] == '0' && i_ + 1 < s_.size() &&
            (s_[i_ + 1] == 'x' || s_[i_ + 1] == 'X')) {
            i_ += 2;
            std::size_t b = i_;
            while (i_ < s_.size() && std::isxdigit((unsigned char)s_[i_])) ++i_;
            if (i_ == b) throw CalcError("malformed hex literal", start);
            return {Tok::Number, (double)std::stoll(s_.substr(b, i_ - b), nullptr, 16), "", start};
        }
        if (s_[i_] == '0' && i_ + 1 < s_.size() &&
            (s_[i_ + 1] == 'b' || s_[i_ + 1] == 'B')) {
            i_ += 2;
            std::size_t b = i_;
            while (i_ < s_.size() && (s_[i_] == '0' || s_[i_] == '1')) ++i_;
            if (i_ == b) throw CalcError("malformed binary literal", start);
            return {Tok::Number, (double)std::stoll(s_.substr(b, i_ - b), nullptr, 2), "", start};
        }

        bool seenDot = false, seenExp = false;
        while (i_ < s_.size()) {
            char c = s_[i_];
            if (std::isdigit((unsigned char)c)) { ++i_; }
            else if (c == '.' && !seenDot && !seenExp) { seenDot = true; ++i_; }
            else if ((c == 'e' || c == 'E') && !seenExp) {
                // Only treat as exponent if followed by digits (optionally signed).
                std::size_t j = i_ + 1;
                if (j < s_.size() && (s_[j] == '+' || s_[j] == '-')) ++j;
                if (j < s_.size() && std::isdigit((unsigned char)s_[j])) {
                    seenExp = true;
                    i_ = j;  // consume 'e' and sign
                } else break;
            } else break;
        }
        std::string lit = s_.substr(start, i_ - start);
        try {
            return {Tok::Number, std::stod(lit), "", start};
        } catch (...) {
            throw CalcError("invalid number '" + lit + "'", start);
        }
    }

    Token ident(std::size_t start) {
        while (i_ < s_.size() &&
               (std::isalnum((unsigned char)s_[i_]) || s_[i_] == '_')) ++i_;
        return {Tok::Ident, 0, s_.substr(start, i_ - start), start};
    }

    Token symbol(std::size_t start) {
        char c = s_[i_++];
        switch (c) {
            case '+': return {Tok::Plus,    0, "", start};
            case '-': return {Tok::Minus,   0, "", start};
            case '*': // '**' is an alias for '^'
                if (i_ < s_.size() && s_[i_] == '*') { ++i_; return {Tok::Caret, 0, "", start}; }
                return {Tok::Star, 0, "", start};
            case '/': return {Tok::Slash,   0, "", start};
            case '%': return {Tok::Percent, 0, "", start};
            case '^': return {Tok::Caret,   0, "", start};
            case '(': return {Tok::LParen,  0, "", start};
            case ')': return {Tok::RParen,  0, "", start};
            case ',': return {Tok::Comma,   0, "", start};
            case '!': return {Tok::Bang,    0, "", start};
            case '=': return {Tok::Assign,  0, "", start};
            default:
                throw CalcError(std::string("unexpected character '") + c + "'", start);
        }
    }
};

// ----------------------------------------------------------------------------
//  Evaluation environment: constants, variables, and functions.
// ----------------------------------------------------------------------------
class Environment {
public:
    // Angle handling for trig functions.
    bool degrees = false;

    Environment() {
        vars_["pi"]  = M_PI;
        vars_["tau"] = 2.0 * M_PI;
        vars_["e"]   = M_E;
        vars_["phi"] = (1.0 + std::sqrt(5.0)) / 2.0;
        vars_["inf"] = std::numeric_limits<double>::infinity();
        vars_["nan"] = std::numeric_limits<double>::quiet_NaN();
        vars_["ans"] = 0.0;
        installFunctions();
    }

    bool hasVar(const std::string& n) const { return vars_.count(n) != 0; }
    double getVar(const std::string& n) const { return vars_.at(n); }
    void setVar(const std::string& n, double v) { vars_[n] = v; }

    bool hasFunc(const std::string& n) const { return funcs_.count(n) != 0; }

    double callFunc(const std::string& n, const std::vector<double>& a,
                    std::size_t pos) const {
        const auto& f = funcs_.at(n);
        if (f.arity >= 0 && (int)a.size() != f.arity)
            throw CalcError("function '" + n + "' expects " +
                            std::to_string(f.arity) + " argument(s), got " +
                            std::to_string(a.size()), pos);
        if (f.arity < 0 && a.empty())
            throw CalcError("function '" + n + "' expects at least 1 argument", pos);
        return f.fn(a, *this);
    }

    // Variables map exposed read-only for the 'vars' command.
    const std::unordered_map<std::string, double>& variables() const { return vars_; }

private:
    struct Func {
        int arity;  // -1 == variadic
        std::function<double(const std::vector<double>&, const Environment&)> fn;
    };

    std::unordered_map<std::string, double> vars_;
    std::unordered_map<std::string, Func>   funcs_;

    // Convert an angle to radians on input based on mode.
    double toRad(double x) const { return degrees ? x * M_PI / 180.0 : x; }
    // Convert a radian result to the active unit on output.
    double fromRad(double x) const { return degrees ? x * 180.0 / M_PI : x; }

    void installFunctions() {
        auto U = [](std::function<double(double)> g) {
            return Func{1, [g](const std::vector<double>& a, const Environment&) {
                            return g(a[0]);
                        }};
        };

        // --- Trigonometric (respect angle mode) ---------------------------
        funcs_["sin"]  = {1, [](const std::vector<double>& a, const Environment& e){ return std::sin(e.toRad(a[0])); }};
        funcs_["cos"]  = {1, [](const std::vector<double>& a, const Environment& e){ return std::cos(e.toRad(a[0])); }};
        funcs_["tan"]  = {1, [](const std::vector<double>& a, const Environment& e){ return std::tan(e.toRad(a[0])); }};
        funcs_["cot"]  = {1, [](const std::vector<double>& a, const Environment& e){ return 1.0/std::tan(e.toRad(a[0])); }};
        funcs_["sec"]  = {1, [](const std::vector<double>& a, const Environment& e){ return 1.0/std::cos(e.toRad(a[0])); }};
        funcs_["csc"]  = {1, [](const std::vector<double>& a, const Environment& e){ return 1.0/std::sin(e.toRad(a[0])); }};

        funcs_["asin"] = {1, [](const std::vector<double>& a, const Environment& e){
            if (a[0] < -1 || a[0] > 1) throw CalcError("asin: argument out of domain [-1,1]");
            return e.fromRad(std::asin(a[0])); }};
        funcs_["acos"] = {1, [](const std::vector<double>& a, const Environment& e){
            if (a[0] < -1 || a[0] > 1) throw CalcError("acos: argument out of domain [-1,1]");
            return e.fromRad(std::acos(a[0])); }};
        funcs_["atan"] = {1, [](const std::vector<double>& a, const Environment& e){ return e.fromRad(std::atan(a[0])); }};
        funcs_["atan2"]= {2, [](const std::vector<double>& a, const Environment& e){ return e.fromRad(std::atan2(a[0], a[1])); }};

        // --- Hyperbolic ---------------------------------------------------
        funcs_["sinh"]  = U([](double x){ return std::sinh(x); });
        funcs_["cosh"]  = U([](double x){ return std::cosh(x); });
        funcs_["tanh"]  = U([](double x){ return std::tanh(x); });
        funcs_["asinh"] = U([](double x){ return std::asinh(x); });
        funcs_["acosh"] = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] < 1) throw CalcError("acosh: argument must be >= 1");
            return std::acosh(a[0]); }};
        funcs_["atanh"] = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] <= -1 || a[0] >= 1) throw CalcError("atanh: argument out of domain (-1,1)");
            return std::atanh(a[0]); }};

        // --- Exponential / logarithmic ------------------------------------
        funcs_["exp"]   = U([](double x){ return std::exp(x); });
        funcs_["exp2"]  = U([](double x){ return std::exp2(x); });
        funcs_["expm1"] = U([](double x){ return std::expm1(x); });
        funcs_["ln"]    = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] <= 0) throw CalcError("ln: argument must be > 0");
            return std::log(a[0]); }};
        funcs_["log10"] = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] <= 0) throw CalcError("log10: argument must be > 0");
            return std::log10(a[0]); }};
        funcs_["log2"]  = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] <= 0) throw CalcError("log2: argument must be > 0");
            return std::log2(a[0]); }};
        funcs_["log1p"] = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] <= -1) throw CalcError("log1p: argument must be > -1");
            return std::log1p(a[0]); }};
        // log(x) = natural log;  log(b, x) = log base b of x.
        funcs_["log"]   = {-1, [](const std::vector<double>& a, const Environment&){
            if (a.size() == 1) {
                if (a[0] <= 0) throw CalcError("log: argument must be > 0");
                return std::log(a[0]);
            }
            if (a.size() == 2) {
                if (a[1] <= 0 || a[0] <= 0 || a[0] == 1)
                    throw CalcError("log(base,x): need base>0, base!=1, x>0");
                return std::log(a[1]) / std::log(a[0]);
            }
            throw CalcError("log expects 1 or 2 arguments"); }};

        // --- Powers / roots ----------------------------------------------
        funcs_["sqrt"] = {1, [](const std::vector<double>& a, const Environment&){
            if (a[0] < 0) throw CalcError("sqrt: argument must be >= 0");
            return std::sqrt(a[0]); }};
        funcs_["cbrt"] = U([](double x){ return std::cbrt(x); });
        funcs_["pow"]  = {2, [](const std::vector<double>& a, const Environment&){ return std::pow(a[0], a[1]); }};
        funcs_["root"] = {2, [](const std::vector<double>& a, const Environment&){
            // n-th root of x
            double x = a[0], n = a[1];
            if (n == 0) throw CalcError("root: degree must be non-zero");
            if (x < 0) {
                double ni;
                if (std::modf(n, &ni) == 0.0 && std::fmod(ni, 2.0) != 0.0)
                    return -std::pow(-x, 1.0 / n);      // odd integer root of negative
                throw CalcError("root: negative radicand with non-odd degree");
            }
            return std::pow(x, 1.0 / n); }};
        funcs_["hypot"] = {2, [](const std::vector<double>& a, const Environment&){ return std::hypot(a[0], a[1]); }};

        // --- Rounding / sign ----------------------------------------------
        funcs_["abs"]   = U([](double x){ return std::fabs(x); });
        funcs_["floor"] = U([](double x){ return std::floor(x); });
        funcs_["ceil"]  = U([](double x){ return std::ceil(x); });
        funcs_["round"] = U([](double x){ return std::round(x); });
        funcs_["trunc"] = U([](double x){ return std::trunc(x); });
        funcs_["frac"]  = U([](double x){ double ip; return std::modf(x, &ip); });
        funcs_["sign"]  = U([](double x){ return (double)((x > 0) - (x < 0)); });
        funcs_["deg"]   = U([](double x){ return x * 180.0 / M_PI; });
        funcs_["rad"]   = U([](double x){ return x * M_PI / 180.0; });

        // --- Modular / integer --------------------------------------------
        funcs_["mod"]   = {2, [](const std::vector<double>& a, const Environment&){
            if (a[1] == 0) throw CalcError("mod: division by zero");
            return std::fmod(a[0], a[1]); }};
        funcs_["gcd"]   = {2, [](const std::vector<double>& a, const Environment&){
            long long x = llround(std::fabs(a[0])), y = llround(std::fabs(a[1]));
            while (y) { long long t = x % y; x = y; y = t; }
            return (double)x; }};
        funcs_["lcm"]   = {2, [](const std::vector<double>& a, const Environment&){
            long long x = llround(std::fabs(a[0])), y = llround(std::fabs(a[1]));
            if (x == 0 || y == 0) return 0.0;
            long long g = x, h = y; while (h) { long long t = g % h; g = h; h = t; }
            return (double)(x / g * y); }};

        // --- Combinatorics -------------------------------------------------
        funcs_["fact"] = {1, [](const std::vector<double>& a, const Environment&){
            return Environment::factorial(a[0]); }};
        funcs_["gamma"] = U([](double x){ return std::tgamma(x); });
        funcs_["lgamma"] = U([](double x){ return std::lgamma(x); });
        funcs_["ncr"]  = {2, [](const std::vector<double>& a, const Environment&){
            return Environment::choose(a[0], a[1]); }};
        funcs_["npr"]  = {2, [](const std::vector<double>& a, const Environment&){
            double n = a[0], r = a[1];
            return Environment::factorial(n) / Environment::factorial(n - r); }};

        // --- Variadic reducers --------------------------------------------
        funcs_["min"] = {-1, [](const std::vector<double>& a, const Environment&){
            double m = a[0]; for (double v : a) m = std::min(m, v); return m; }};
        funcs_["max"] = {-1, [](const std::vector<double>& a, const Environment&){
            double m = a[0]; for (double v : a) m = std::max(m, v); return m; }};
        funcs_["sum"] = {-1, [](const std::vector<double>& a, const Environment&){
            double s = 0; for (double v : a) s += v; return s; }};
        funcs_["mean"]= {-1, [](const std::vector<double>& a, const Environment&){
            double s = 0; for (double v : a) s += v; return s / (double)a.size(); }};
        funcs_["median"] = {-1, [](const std::vector<double>& a, const Environment&){
            std::vector<double> v = a; std::sort(v.begin(), v.end());
            std::size_t n = v.size();
            return n % 2 ? v[n/2] : (v[n/2 - 1] + v[n/2]) / 2.0; }};
        funcs_["clamp"] = {3, [](const std::vector<double>& a, const Environment&){
            return std::max(a[1], std::min(a[0], a[2])); }};
    }

public:
    static double factorial(double x) {
        double ip;
        if (std::modf(x, &ip) != 0.0 || x < 0)
            // Generalize to non-integers / negatives via the Gamma function.
            return std::tgamma(x + 1.0);
        if (x > 170) return std::numeric_limits<double>::infinity();
        double r = 1.0;
        for (int k = 2; k <= (int)ip; ++k) r *= k;
        return r;
    }

    static double choose(double n, double r) {
        if (r < 0 || n < 0) throw CalcError("ncr: arguments must be non-negative");
        double ni, ri;
        if (std::modf(n, &ni) == 0.0 && std::modf(r, &ri) == 0.0) {
            if (ri > ni) return 0.0;
            ri = std::min(ri, ni - ri);
            double res = 1.0;
            for (int k = 0; k < (int)ri; ++k)
                res = res * (ni - k) / (k + 1);
            return std::round(res);
        }
        return std::tgamma(n + 1) / (std::tgamma(r + 1) * std::tgamma(n - r + 1));
    }
};

// ----------------------------------------------------------------------------
//  Parser: recursive descent producing a value directly (tree-walking).
//
//  Grammar (lowest to highest precedence):
//    statement   := Ident '=' expression | expression
//    expression  := term (('+' | '-') term)*
//    term        := unary (('*' | '/' | '%' | implicit) unary)*
//    unary       := ('+' | '-') unary | power
//    power       := postfix ('^' unary)?          right-assoc; binds tighter
//                                                 than unary minus (-2^2 = -4)
//    postfix     := primary ('!')*
//    primary     := Number | constant | Ident | func '(' args ')' | '(' expr ')'
// ----------------------------------------------------------------------------
class Parser {
public:
    Parser(std::vector<Token> toks, Environment& env)
        : t_(std::move(toks)), env_(env) {}

    // Returns {value, assignedName or ""}.
    std::pair<double, std::string> parse() {
        std::string assigned;
        double v;

        // Look for   Ident '='  at the very start (assignment statement).
        if (t_[0].type == Tok::Ident && t_.size() > 1 && t_[1].type == Tok::Assign) {
            std::string name = t_[0].text;
            if (isReserved(name))
                throw CalcError("cannot assign to reserved name '" + name + "'", t_[0].pos);
            k_ = 2;  // skip 'name ='
            v = expression();
            expect(Tok::End);
            env_.setVar(name, v);
            assigned = name;
        } else {
            v = expression();
            expect(Tok::End);
        }
        return {v, assigned};
    }

private:
    std::vector<Token> t_;
    Environment&       env_;
    std::size_t        k_ = 0;

    const Token& cur() const { return t_[k_]; }
    const Token& advance() { return t_[k_++]; }
    bool check(Tok tp) const { return cur().type == tp; }
    bool match(Tok tp) { if (check(tp)) { ++k_; return true; } return false; }

    void expect(Tok tp) {
        if (!check(tp))
            throw CalcError("unexpected trailing input", cur().pos);
    }

    static bool isReserved(const std::string& n) {
        static const std::vector<std::string> r = {
            "pi","tau","e","phi","inf","nan"};
        for (auto& s : r) if (s == n) return true;
        return false;
    }

    // Determine whether the current token can begin a primary expression
    // (used to detect implicit multiplication like 2pi or 3(4)).
    bool startsPrimary() const {
        switch (cur().type) {
            case Tok::Number: case Tok::Ident: case Tok::LParen: return true;
            default: return false;
        }
    }

    double expression() {
        double v = term();
        while (true) {
            if (match(Tok::Plus))       v += term();
            else if (match(Tok::Minus)) v -= term();
            else break;
        }
        return v;
    }

    double term() {
        double v = unary();
        while (true) {
            if (match(Tok::Star))         v *= unary();
            else if (match(Tok::Slash)) {
                std::size_t p = t_[k_ - 1].pos;
                double d = unary();
                if (d == 0.0) throw CalcError("division by zero", p);
                v /= d;
            } else if (match(Tok::Percent)) {
                std::size_t p = t_[k_ - 1].pos;
                double d = unary();
                if (d == 0.0) throw CalcError("modulo by zero", p);
                v = std::fmod(v, d);
            } else if (startsPrimary()) {
                // Implicit multiplication: 2pi, 3(4+1), 2sqrt(2), (1+2)(3+4).
                v *= unary();
            } else break;
        }
        return v;
    }

    double unary() {
        if (match(Tok::Plus))  return unary();
        if (match(Tok::Minus)) return -unary();
        return power();
    }

    double power() {
        double base = postfix();
        if (match(Tok::Caret)) {
            double exp = unary();  // right associative; allows 2^-3
            return std::pow(base, exp);
        }
        return base;
    }

    double postfix() {
        double v = primary();
        while (check(Tok::Bang)) {
            std::size_t p = cur().pos;
            advance();
            if (v < 0) throw CalcError("factorial of a negative number", p);
            v = Environment::factorial(v);
        }
        return v;
    }

    double primary() {
        const Token tk = cur();

        if (match(Tok::Number)) return tk.num;

        if (match(Tok::LParen)) {
            double v = expression();
            if (!match(Tok::RParen))
                throw CalcError("missing closing ')'", cur().pos);
            return v;
        }

        if (check(Tok::Ident)) {
            std::string name = tk.text;
            advance();
            // Function call?
            if (check(Tok::LParen)) {
                if (!env_.hasFunc(name))
                    throw CalcError("unknown function '" + name + "'", tk.pos);
                advance();  // consume '('
                std::vector<double> args;
                if (!check(Tok::RParen)) {
                    args.push_back(expression());
                    while (match(Tok::Comma)) args.push_back(expression());
                }
                if (!match(Tok::RParen))
                    throw CalcError("missing closing ')' in call to '" + name + "'", cur().pos);
                return env_.callFunc(name, args, tk.pos);
            }
            // Variable / constant?
            if (env_.hasVar(name)) return env_.getVar(name);
            if (env_.hasFunc(name))
                throw CalcError("function '" + name + "' used without arguments", tk.pos);
            throw CalcError("unknown identifier '" + name + "'", tk.pos);
        }

        throw CalcError("expected a number, identifier, or '('", tk.pos);
    }
};

// ----------------------------------------------------------------------------
//  Output formatting: print integers cleanly, otherwise a trimmed value.
// ----------------------------------------------------------------------------
static std::string formatNumber(double v) {
    if (std::isnan(v)) return "nan";
    if (std::isinf(v)) return v < 0 ? "-inf" : "inf";

    // Integer-valued and within safe range -> print without a decimal point.
    if (std::fabs(v) < 1e15 && v == std::floor(v)) {
        std::ostringstream os;
        os << (long long)v;
        return os.str();
    }
    std::ostringstream os;
    os.precision(15);
    os << v;
    return os.str();
}

// ----------------------------------------------------------------------------
//  Evaluate a single line; updates 'ans'. Throws CalcError on failure.
// ----------------------------------------------------------------------------
static double evalLine(const std::string& line, Environment& env,
                       std::string& assignedName) {
    Lexer lex(line);
    Parser parser(lex.tokenize(), env);
    auto pr = parser.parse();
    assignedName = pr.second;
    env.setVar("ans", pr.first);
    return pr.first;
}

// Render a "^" caret line under the input pointing at an error position.
static std::string caretLine(const std::string& src, std::size_t pos) {
    if (pos == std::string::npos || pos > src.size()) return "";
    std::string s(pos, ' ');
    s += "^";
    return s;
}

// ----------------------------------------------------------------------------
//  Help / command handling for the REPL.
// ----------------------------------------------------------------------------
static void printHelp() {
    std::cout <<
R"(scicalc — scientific calculator
--------------------------------------------------------------------
Operators : +  -  *  /  %  ^ (or **)   unary -   postfix !  (factorial)
Grouping  : ( )        Implicit x : 2pi, 3(4+1), 2sin(x)
Literals  : 3.14, 1.2e-3, 0xFF, 0b1010
Constants : pi tau e phi inf nan   (ans = last result)
Assignment: x = 3     then use x in later expressions

Functions
  trig    : sin cos tan cot sec csc  asin acos atan atan2
  hyperbol: sinh cosh tanh asinh acosh atanh
  exp/log : exp exp2 expm1 ln log10 log2 log1p log(x) log(base,x)
  powers  : sqrt cbrt pow(a,b) root(x,n) hypot(a,b)
  round   : abs floor ceil round trunc frac sign
  angles  : deg(x) rad(x)
  intmath : mod(a,b) gcd(a,b) lcm(a,b)
  combin. : fact(n) n! gamma lgamma ncr(n,r) npr(n,r)
  reducers: min max sum mean median clamp(x,lo,hi)  (variadic)

Commands
  help            show this help
  deg | rad       set angle mode (current shown in prompt)
  vars            list user-defined variables
  clear           delete user variables
  quit | exit     leave
--------------------------------------------------------------------
)";
}

// Returns true if the line was a command and was handled.
static bool handleCommand(const std::string& line, Environment& env, bool& running) {
    std::size_t a = line.find_first_not_of(" \t");
    if (a == std::string::npos) return true;  // blank line: consume silently
    std::size_t b = line.find_last_not_of(" \t");
    std::string cmd = line.substr(a, b - a + 1);

    if (cmd == "quit" || cmd == "exit") { running = false; return true; }
    if (cmd == "help" || cmd == "?")    { printHelp(); return true; }
    if (cmd == "deg") { env.degrees = true;  std::cout << "angle mode: degrees\n"; return true; }
    if (cmd == "rad") { env.degrees = false; std::cout << "angle mode: radians\n"; return true; }
    if (cmd == "vars") {
        static const std::vector<std::string> builtin = {
            "pi","tau","e","phi","inf","nan"};
        for (const auto& kv : env.variables()) {
            bool isBuiltin = false;
            for (auto& s : builtin) if (s == kv.first) isBuiltin = true;
            if (!isBuiltin)
                std::cout << "  " << kv.first << " = " << formatNumber(kv.second) << "\n";
        }
        return true;
    }
    if (cmd == "clear") {
        bool d = env.degrees; env = Environment(); env.degrees = d;
        std::cout << "variables cleared\n";
        return true;
    }
    return false;
}

// ----------------------------------------------------------------------------
//  Modes: one-shot (argv), piped stdin, or interactive REPL.
// ----------------------------------------------------------------------------
static int runOneShot(int argc, char** argv) {
    Environment env;
    int rc = 0;
    for (int i = 1; i < argc; ++i) {
        std::string line = argv[i];
        try {
            std::string name;
            double v = evalLine(line, env, name);
            if (!name.empty()) std::cout << name << " = ";
            std::cout << formatNumber(v) << "\n";
        } catch (const CalcError& e) {
            std::cerr << "error: " << e.what() << "\n";
            std::cerr << "  " << line << "\n";
            std::string c = caretLine(line, e.pos);
            if (!c.empty()) std::cerr << "  " << c << "\n";
            rc = 1;
        }
    }
    return rc;
}

static int runStream(std::istream& in, bool interactive) {
    Environment env;
    bool running = true;
    std::string line;

    if (interactive) {
        std::cout << "scicalc ready. Type 'help' for commands, 'quit' to exit.\n";
    }

    while (running) {
        if (interactive)
            std::cout << (env.degrees ? "deg> " : "rad> ") << std::flush;
        if (!std::getline(in, line)) break;

        if (handleCommand(line, env, running)) continue;

        try {
            std::string name;
            double v = evalLine(line, env, name);
            if (!name.empty()) std::cout << name << " = ";
            std::cout << formatNumber(v) << "\n";
        } catch (const CalcError& e) {
            std::cout << "error: " << e.what() << "\n";
            std::string c = caretLine(line, e.pos);
            if (!c.empty()) std::cout << line << "\n" << c << "\n";
        } catch (const std::exception& e) {
            std::cout << "error: " << e.what() << "\n";
        }
    }
    return 0;
}

int main(int argc, char** argv) {
    std::ios::sync_with_stdio(false);

    if (argc > 1) return runOneShot(argc, argv);

    bool interactive = []() {
#if defined(_WIN32)
        return true;
#else
        return isatty(fileno(stdin)) != 0;
#endif
    }();

    return runStream(std::cin, interactive);
}
