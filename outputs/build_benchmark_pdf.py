import markdown, pathlib

md_text = pathlib.Path("outputs/benchmark_report.md").read_text()
body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "toc"])

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HorizonMath Calibration Report</title>
<script>
window.MathJax = {
  tex: {inlineMath: [['$','$'],['\\(','\\)']], displayMath: [['$$','$$'],['\\[','\\]']]},
  svg: {fontCache: 'global'}
};
</script>
<script id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
  @page { size: A4; margin: 18mm 16mm; }
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a1a1a;
         font-size: 10.5pt; line-height: 1.5; max-width: 100%; }
  h1 { font-size: 21pt; color: #0b3d61; border-bottom: 3px solid #0b3d61;
       padding-bottom: 6px; margin-bottom: 4px; }
  h2 { font-size: 14pt; color: #0b3d61; margin-top: 22px;
       border-bottom: 1px solid #cbd5e1; padding-bottom: 3px; }
  h3 { font-size: 12pt; color: #164e63; }
  table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; }
  th, td { border: 1px solid #cbd5e1; padding: 5px 8px; text-align: left; vertical-align: top; }
  th { background: #0b3d61; color: #fff; font-weight: 600; }
  tr:nth-child(even) td { background: #f1f5f9; }
  code { background: #eef2f7; padding: 1px 4px; border-radius: 3px;
         font-family: 'SFMono-Regular', Consolas, monospace; font-size: 9pt; }
  pre { background: #0f172a; color: #e2e8f0; padding: 10px 12px; border-radius: 6px;
        overflow-x: auto; font-size: 8.8pt; }
  pre code { background: transparent; color: inherit; padding: 0; }
  strong { color: #0b3d61; }
  hr { border: none; border-top: 1px solid #cbd5e1; margin: 18px 0; }
  ul, ol { margin: 6px 0 6px 18px; }
  li { margin: 3px 0; }
</style>
</head>
<body>
""" + body + "\n</body>\n</html>\n"

pathlib.Path("outputs/benchmark_report.html").write_text(html)
print("wrote outputs/benchmark_report.html", len(html), "bytes")
