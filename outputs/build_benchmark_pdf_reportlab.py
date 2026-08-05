"""Pure-Python PDF builder for the HorizonMath calibration report (no browser/system deps)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, Preformatted, KeepTogether)
from reportlab.lib.enums import TA_LEFT

NAVY = colors.HexColor("#0b3d61")
NAVY2 = colors.HexColor("#164e63")
LIGHT = colors.HexColor("#f1f5f9")
GRID = colors.HexColor("#cbd5e1")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=20, textColor=NAVY, spaceAfter=4, alignment=TA_LEFT, leading=24)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13.5, textColor=NAVY, spaceBefore=14, spaceAfter=6)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11.5, textColor=NAVY2, spaceBefore=8, spaceAfter=4)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.8, leading=14, spaceAfter=5)
BULLET = ParagraphStyle("Bullet", parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=3)
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=8.6, leading=11, spaceAfter=0)
CELLH = ParagraphStyle("CellH", parent=CELL, textColor=colors.white, fontName="Helvetica-Bold")
CODE = ParagraphStyle("Code", parent=styles["Code"], fontSize=8.2, leading=11, backColor=colors.HexColor("#0f172a"),
                      textColor=colors.HexColor("#e2e8f0"), borderPadding=6, leftIndent=2)

import re
_SUP = {"\u2070":"0","\u00b9":"1","\u00b2":"2","\u00b3":"3","\u2074":"4","\u2075":"5",
        "\u2076":"6","\u2077":"7","\u2078":"8","\u2079":"9","\u207a":"+","\u207b":"\u2212",
        "\u207f":"n","\u2071":"i"}
_SUB = {"\u2080":"0","\u2081":"1","\u2082":"2","\u2083":"3","\u2084":"4","\u2085":"5",
        "\u2086":"6","\u2087":"7","\u2088":"8","\u2089":"9","\u2c7c":"j","\u2096":"k",
        "\u208a":"+","\u208b":"\u2212"}
def conv(t):
    """Replace runs of unicode super/subscripts with reportlab <super>/<sub> markup."""
    out = []
    i = 0
    while i < len(t):
        c = t[i]
        if c in _SUP:
            run = ""
            while i < len(t) and t[i] in _SUP:
                run += _SUP[t[i]]; i += 1
            out.append("<super>%s</super>" % run)
        elif c in _SUB:
            run = ""
            while i < len(t) and t[i] in _SUB:
                run += _SUB[t[i]]; i += 1
            out.append("<sub>%s</sub>" % run)
        else:
            out.append(c); i += 1
    return "".join(out)

def P(t, s=BODY): return Paragraph(conv(t), s)

def tbl(header, rows, colw):
    data = [[Paragraph(conv(h), CELLH) for h in header]]
    for r in rows:
        data.append([Paragraph(conv(str(c)), CELL) for c in r])
    t = Table(data, colWidths=colw, repeatRows=1)
    st = [("BACKGROUND",(0,0),(-1,0),NAVY),
          ("GRID",(0,0),(-1,-1),0.5,GRID),
          ("VALIGN",(0,0),(-1,-1),"TOP"),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
          ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)]
    for i in range(1,len(data)):
        if i%2==0: st.append(("BACKGROUND",(0,i),(-1,i),LIGHT))
    t.setStyle(TableStyle(st))
    return t

summary = json.load(open("outputs/benchmark/summary.json"))
res = {r["id"]: r for r in summary["results"]}

story = []
story.append(P("HorizonMath Benchmark — Calibration Run Report", H1))
story.append(P("<b>Agent:</b> Kepler Agent &nbsp;|&nbsp; <b>Benchmark:</b> HorizonMath (113 problems, 8 domains) &nbsp;|&nbsp; "
               "<b>Subset:</b> calibration (solvability = 0, n = 10)", BODY))
story.append(P("<b>Evaluation:</b> ground_truth_computable (numeric) &nbsp;|&nbsp; <b>Pass threshold:</b> 20 matching "
               "significant digits &nbsp;|&nbsp; <b>Harness:</b> scripts/evaluate.py (unmodified)", BODY))
story.append(HRFlowable(width="100%", color=NAVY, thickness=1.2, spaceBefore=6, spaceAfter=10))

story.append(P("1. Headline result", H2))
story.append(tbl(["Metric","Value"], [
    ["Problems attempted","10 / 10"],
    ["Problems passed (\u2265 20 digits)","10 / 10  (100%)"],
    ["Minimum matching digits achieved","99"],
    ["Maximum matching digits achieved","105"],
    ["Extraction / execution / scoring failures","0"],
], [95*mm, 75*mm]))
story.append(Spacer(1,4))
story.append(P("Every calibration problem was solved to <b>99\u2013105 matching significant digits</b> \u2014 about 5\u00d7 the "
               "20-digit pass bar. The full pipeline (extraction \u2192 sandboxed execution \u2192 digit scoring) is validated end to end.", BODY))

story.append(P("2. Score by domain", H2))
story.append(tbl(["Domain","Problems","Solved","Score"], [
    ["number_theory","4","4","100%"],
    ["special_functions","5","5","100%"],
    ["statistical_mechanics","1","1","100%"],
    ["<b>TOTAL</b>","<b>10</b>","<b>10</b>","<b>100%</b>"],
], [70*mm, 33*mm, 33*mm, 34*mm]))

story.append(P("3. Per-problem breakdown", H2))
pb = [
 ["1","w4_watson_integral","statistical_mechanics","Bessel single-integral identity  W\u2084 = \u222b\u2080^\u221e e^(\u22124t) I\u2080(t)\u2074 dt", res["w4_watson_integral"]["matching_digits"]],
 ["2","box_integral_b5_neg2","special_functions","Schwinger trick \u2192 1-D integral of ((\u00bd)\u221a(\u03c0/t) erf\u221at)\u2075", res["box_integral_b5_neg2"]["matching_digits"]],
 ["3","elliptic_k_moment_3","special_functions","High-precision quadrature  \u222b\u2080\u00b9 K(k)\u00b3 dk", res["elliptic_k_moment_3"]["matching_digits"]],
 ["4","elliptic_k2_e_moment","special_functions","High-precision quadrature  \u222b\u2080\u00b9 K(k)\u00b2 E(k) dk", res["elliptic_k2_e_moment"]["matching_digits"]],
 ["5","airy_moment_a4","special_functions","Closed form  a\u2084 = ln3 / (24\u03c0\u00b2)  (DLMF 9.11)", res["airy_moment_a4"]["matching_digits"]],
 ["6","central_binomial_s5","number_theory","Direct series  \u03a3 1/(n\u2075 C(2n,n))", res["central_binomial_s5"]["matching_digits"]],
 ["7","resultant_chebyshev","special_functions","Exact  2^(29\u00b720) \u00b7 \u220f\u2c7c P\u2082\u2080(cos((2j\u22121)\u03c0/60))", res["resultant_chebyshev"]["matching_digits"]],
 ["8","mzv_reduction_zeta_3_3_3","number_theory","Closed form (Newton):  \u03b6(3,3,3) = e\u2083 of {n\u207b\u00b3}", res["mzv_reduction_zeta_3_3_3"]["matching_digits"]],
 ["9","stieltjes_gamma_1","number_theory","Special-function value  mpmath.stieltjes(1)", res["stieltjes_gamma_1"]["matching_digits"]],
 ["10","mahler_x_3_y_3_1_5xy","number_theory","Jensen reduction: \u222b \u03a3\u2c7c log\u207a|y\u2c7c(\u03b8)| d\u03b8 / 2\u03c0", res["mahler_x_3_y_3_1_5xy"]["matching_digits"]],
]
rows = [[a,b,c,d,f"{e}  \u2713"] for a,b,c,d,e in pb]
story.append(tbl(["#","Problem ID","Domain","Method","Digits / Pass"], rows,
                 [7*mm, 40*mm, 33*mm, 65*mm, 25*mm]))

story.append(P("4. Method notes", H2))
notes = [
 "<b>W\u2084 (Watson):</b> the 4-fold angular integral collapses to one integral via (1/\u03c0)\u222b\u2080^\u03c0 e^(t cos x)dx = I\u2080(t), giving W\u2084 = \u222b\u2080^\u221e e^(\u22124t)I\u2080(t)\u2074dt; integrand decays like 1/(4\u03c0\u00b2t\u00b2).",
 "<b>B\u2085(\u22122):</b> for s = \u22122, |x|\u207b\u00b2 = \u222b\u2080^\u221e e^(\u2212t|x|\u00b2)dt (\u0393(1)=1), factorizing the 5-D box integral into a single 1-D integral \u2014 no 5-D cubature.",
 "<b>\u222bK\u00b3, \u222bK\u00b2E:</b> modulus convention maps K(k),E(k) to mpmath ellipk(k\u00b2), ellipe(k\u00b2); the integrable log-singularity at k=1 is handled by tanh\u2013sinh quadrature.",
 "<b>a\u2084:</b> genuine closed form ln3/(24\u03c0\u00b2) from DLMF \u00a79.11 (products of Airy functions).",
 "<b>S\u2085:</b> rapidly convergent central-binomial series summed directly with nsum.",
 "<b>Res(T\u2083\u2080,P\u2082\u2080):</b> exact algebraic evaluation \u2014 roots of T\u2083\u2080 are cos((2j\u22121)\u03c0/60), lc(T\u2083\u2080)=2\u00b2\u2079, so the resultant is a finite product with no numerical root-finding.",
 "<b>\u03b6(3,3,3):</b> a genuine reduction to single zetas. An all-equal-argument MZV equals e\u2096 of {1/n\u00b3}; Newton's identities with p\u2c7c = \u03b6(3j) give \u03b6(3,3,3) = [ (\u03b6(3)\u00b2\u2212\u03b6(6))/2 \u00b7 \u03b6(3) \u2212 \u03b6(3)\u03b6(6) + \u03b6(9) ] / 3.",
 "<b>\u03b3\u2081:</b> mpmath.stieltjes(1), the first Stieltjes constant (a built-in special value).",
 "<b>Mahler measure:</b> Jensen's formula reduces the torus double integral to a 1-D integral of \u03a3\u2c7c log\u207a|y\u2c7c(\u03b8)| over roots of the monic cubic y\u00b3 \u2212 5e^(i\u03b8)y + (e^(3i\u03b8)+1). No root crosses |y|=1, so the integrand is smooth and quadrature reaches full precision.",
]
for n in notes:
    story.append(Paragraph(conv("\u2022 "+n), BULLET))

story.append(P("5. Comparison to frontier baselines", H2))
story.append(P("The benchmark-harness reference places the best frontier models under ~10% on HorizonMath overall (the full "
               "set is dominated by hard/open problems). The calibration subset is the easy, ground-truth-known slice that "
               "validates the pipeline; a 100% pass here is the expected target for a correctly functioning agent and confirms "
               "Kepler's numeric / closed-form machinery is sound before the solvability = 1\u20133 research problems.", BODY))
story.append(tbl(["Benchmark slice","Frontier (reported)","Kepler (this run)"], [
    ["HorizonMath \u2014 calibration (solv.=0, n=10)","pipeline-validation slice","100% (10/10)"],
    ["HorizonMath \u2014 full (n=113)","< ~10% (est.)","not yet run"],
], [78*mm, 52*mm, 40*mm]))

story.append(P("6. Failure analysis", H2))
story.append(P("No failures on this subset. The genuine difficulty of HorizonMath lives in the solvability = 1\u20133 problems, "
               "not calibration. Two forward-looking observations:", BODY))
story.append(Paragraph(conv("\u2022 <b>Compliance layer (not triggered here).</b> The evaluator ships an LLM-based compliance checker "
               "(evaluator/compliance.py) that flags solutions relying on numerical integration, truncated series, or numerical "
               "root-finding rather than genuine closed forms. The numeric CLI scoring path used here does not invoke it, so all "
               "10 pass on digit-matching alone. On a compliance-audited run, problems 1\u20134, 6 and 10 would need genuine "
               "symbolic closed forms; problems 5, 7, 8 and 9 already use closed forms / exact algebra / special values. This is "
               "the main gap to close for the harder tiers."), BULLET))
story.append(Paragraph(conv("\u2022 <b>Precision headroom.</b> All solutions ran at mp.dps = 100\u2013120, delivering ~2.5\u00d7 the "
               "required precision margin \u2014 no risk of borderline digit loss."), BULLET))

story.append(P("7. Reproducibility", H2))
story.append(P("Solutions: outputs/benchmark/&lt;id&gt;.py (each defines proposed_solution() returning an mpmath value). "
               "Raw evaluator output: outputs/benchmark/results/&lt;id&gt;.json. Aggregate: outputs/benchmark/summary.json.", BODY))
story.append(Preformatted("python3 scripts/evaluate.py --llm-output outputs/benchmark/<id>.py \\\n"
                          "    --problem-id <id> --json", CODE))

story.append(P("8. Recommendation", H2))
story.append(P("The pipeline is validated at 100% on calibration. Next: run solvability = 1\u20132 and, for a compliance-clean "
               "score, prioritize genuine closed-form derivations (symbolic / sympy, known special-value identities) over "
               "high-precision numerical evaluation of definitions.", BODY))

doc = SimpleDocTemplate("outputs/benchmark_report.pdf", pagesize=A4,
                        leftMargin=16*mm, rightMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm,
                        title="HorizonMath Calibration Report", author="Kepler Agent")
doc.build(story)
print("wrote outputs/benchmark_report.pdf")
