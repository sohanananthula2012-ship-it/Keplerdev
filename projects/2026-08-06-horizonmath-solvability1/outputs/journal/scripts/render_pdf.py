#!/usr/bin/env python3
# render_pdf.py — render report.html to a print-quality PDF via headless Chromium (Playwright).
import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
src="file://"+os.path.join(HERE,"report.html")
out=os.path.join(HERE,"diff_basis_research_journal.pdf")
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page()
    pg.goto(src, wait_until="networkidle", timeout=120000)
    pg.pdf(path=out, format="A4", print_background=True,
           margin={"top":"14mm","bottom":"16mm","left":"14mm","right":"14mm"},
           display_header_footer=False, prefer_css_page_size=True)
    b.close()
sz=os.path.getsize(out)
# count pages via pypdf if available
try:
    from pypdf import PdfReader
    n=len(PdfReader(out).pages); print("PDF pages:",n)
except Exception as e:
    print("pagecount skipped:",e)
print("PDF bytes:",sz,"->",out)
