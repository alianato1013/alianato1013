#!/usr/bin/env python3
"""Build the In Order Co. fillable PDFs (US Letter and A4) from contenido.py.

  python3 build_binder.py            -> salida/*.pdf (core binder, kit, digital legacy) x Letter/A4
"""
import os
import sys

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import contenido as C  # noqa: E402

NAVY, CREAM, CORAL = HexColor("#14213D"), HexColor("#FAF6EF"), HexColor("#E4572E")
INK, GRAY, LINE = HexColor("#1E2533"), HexColor("#5B6170"), HexColor("#C9C2B4")
PALE_NAVY, PALE_CORAL = HexColor("#E6E9F0"), HexColor("#FBE7E0")
F = os.path.join(HERE, "fonts")
pdfmetrics.registerFont(TTFont("Serif", os.path.join(F, "Fraunces-Regular.ttf")))
pdfmetrics.registerFont(TTFont("SerifB", os.path.join(F, "Fraunces-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("Sans", os.path.join(F, "PublicSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("SansB", os.path.join(F, "PublicSans-SemiBold.ttf")))

BRAND = "In Order Co."


class Doc:
    def __init__(self, path, size, product_name):
        self.c = canvas.Canvas(path, pagesize=size)
        self.c.setTitle(f"{BRAND} — {product_name}")
        self.c.setAuthor(BRAND)
        self.W, self.H = size
        self.m = 50
        self.product = product_name
        self.page = 0
        self.n = 0
        self.section = ("", "")
        self.y = None

    # ---------------------------------------------------------------- page frame
    def new_page(self, cont=True):
        if self.page:
            self.c.showPage()
        self.page += 1
        c = self.c
        c.setFillColor(CREAM)
        c.rect(0, 0, self.W, self.H, stroke=0, fill=1)
        c.setFont("Sans", 7.5)
        c.setFillColor(GRAY)
        c.drawString(self.m, 28, f"{BRAND}  ·  {self.product}")
        c.drawRightString(self.W - self.m, 28, str(self.page))
        self.y = self.H - self.m
        if cont and self.section[1]:
            c.setFont("SansB", 8)
            c.setFillColor(CORAL)
            num = f"SECTION {self.section[0]}  ·  " if self.section[0] else ""
            c.drawString(self.m, self.y, f"{num}{self.section[1].upper()} (continued)")
            self.y -= 22

    def need(self, h):
        if self.y - h < 50:
            self.new_page()

    def name(self, prefix):
        self.n += 1
        return f"{prefix}_{self.n}"

    # ---------------------------------------------------------------- blocks
    def tab_icon(self, x, y, s, color=NAVY, check=CORAL):
        c = self.c
        c.setFillColor(color)
        p = c.beginPath()
        p.moveTo(x, y); p.lineTo(x, y + s * 0.62); p.lineTo(x + s * 0.38, y + s * 0.62)
        p.lineTo(x + s * 0.46, y + s * 0.75); p.lineTo(x + s, y + s * 0.75); p.lineTo(x + s, y); p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.setStrokeColor(check)
        c.setLineWidth(max(1.2, s * 0.08))
        c.setLineCap(1)
        c.line(x + s * 0.28, y + s * 0.33, x + s * 0.45, y + s * 0.18)
        c.line(x + s * 0.45, y + s * 0.18, x + s * 0.74, y + s * 0.5)

    def cover(self, l1, l2, tagline):
        self.new_page(cont=False)
        c = self.c
        c.setFillColor(NAVY)
        c.rect(0, self.H * 0.38, self.W, self.H * 0.62, stroke=0, fill=1)
        self.tab_icon(self.m, self.H - self.m - 60, 60, color=CREAM)
        c.setFillColor(CREAM)
        c.setFont("SansB", 11)
        c.drawString(self.m + 74, self.H - self.m - 30, BRAND.upper())
        c.setFont("Serif", 30)
        c.drawString(self.m, self.H * 0.62, l1)
        c.setFont("SerifB", 40)
        for i, line in enumerate(simpleSplit(l2, "SerifB", 40, self.W - 2 * self.m)):
            c.drawString(self.m, self.H * 0.62 - 50 - i * 46, line)
        c.setFillColor(CORAL)
        c.rect(self.m, self.H * 0.38 + 40, 80, 4, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Serif", 16)
        for i, line in enumerate(simpleSplit(tagline, "Serif", 16, self.W - 2 * self.m)):
            c.drawString(self.m, self.H * 0.38 - 40 - i * 22, line)
        c.setFont("Sans", 9)
        c.setFillColor(GRAY)
        for i, line in enumerate(simpleSplit(C.DISCLAIMER, "Sans", 8, self.W - 2 * self.m)):
            c.setFont("Sans", 8)
            c.drawString(self.m, 90 - i * 11, line)

    def section_header(self, num, title, subtitle):
        self.section = (num, title)
        self.new_page(cont=False)
        c = self.c
        self.tab_icon(self.m, self.y - 34, 34)
        c.setFillColor(CORAL)
        c.setFont("SansB", 9)
        c.drawString(self.m + 46, self.y - 10, f"SECTION {num}" if num else BRAND.upper())
        c.setFillColor(NAVY)
        c.setFont("SerifB", 24)
        c.drawString(self.m + 46, self.y - 34, title)
        self.y -= 52
        c.setFillColor(GRAY)
        c.setFont("Serif", 12)
        for line in simpleSplit(subtitle, "Serif", 12, self.W - 2 * self.m):
            c.drawString(self.m, self.y, line)
            self.y -= 16
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(self.m, self.y, self.W - self.m, self.y)
        self.y -= 18

    def para(self, text, font="Sans", size=10, color=INK, lead=14):
        lines = simpleSplit(text, font, size, self.W - 2 * self.m)
        self.need(len(lines) * lead + 6)
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        for line in lines:
            self.c.drawString(self.m, self.y, line)
            self.y -= lead
        self.y -= 6

    def heading(self, text):
        self.need(30)
        self.c.setFont("SerifB", 13)
        self.c.setFillColor(NAVY)
        self.c.drawString(self.m, self.y, text)
        self.y -= 18

    def textfield(self, x, y, w, h, multiline=False, tip=""):
        self.c.acroForm.textfield(
            name=self.name("f"), tooltip=tip[:80], x=x, y=y, width=w, height=h,
            borderWidth=0.6, borderColor=LINE, fillColor=white, textColor=INK,
            fontName="Helvetica", fontSize=9 if not multiline else 9,
            fieldFlags="multiline" if multiline else "", forceBorder=True)

    def fields(self, labels):
        for lab in labels:
            self.need(36)
            self.c.setFont("Sans", 8.5)
            self.c.setFillColor(GRAY)
            self.c.drawString(self.m, self.y, lab)
            self.textfield(self.m, self.y - 21, self.W - 2 * self.m, 17, tip=lab)
            self.y -= 32
        self.y -= 4

    def box(self, label, lines):
        h = lines * 15
        self.need(h + 26)
        self.c.setFont("SansB", 9)
        self.c.setFillColor(NAVY)
        self.c.drawString(self.m, self.y, label)
        self.textfield(self.m, self.y - 6 - h, self.W - 2 * self.m, h, multiline=True, tip=label)
        self.y -= h + 22

    def checks(self, labels):
        for lab in labels:
            lines = simpleSplit(lab, "Sans", 9.5, self.W - 2 * self.m - 22)
            self.need(len(lines) * 13 + 8)
            self.c.acroForm.checkbox(name=self.name("c"), tooltip=lab[:80], x=self.m, y=self.y - 3,
                                     size=11, buttonStyle="check", borderColor=NAVY,
                                     fillColor=white, textColor=CORAL, borderWidth=0.8, forceBorder=True)
            self.c.setFont("Sans", 9.5)
            self.c.setFillColor(INK)
            for i, line in enumerate(lines):
                self.c.drawString(self.m + 20, self.y - i * 13, line)
            self.y -= len(lines) * 13 + 6
        self.y -= 4

    def ten(self, tasks):
        h = 30 + len(tasks) * 17
        self.need(h + 10)
        c = self.c
        c.setFillColor(PALE_CORAL)
        c.roundRect(self.m, self.y - h, self.W - 2 * self.m, h, 8, stroke=0, fill=1)
        c.setFillColor(CORAL)
        c.rect(self.m, self.y - h, 4, h, stroke=0, fill=1)
        c.setFont("SansB", 9.5)
        c.drawString(self.m + 16, self.y - 18, "IF YOU ONLY HAVE 10 MINUTES")
        yy = self.y - 38
        for t in tasks:
            c.acroForm.checkbox(name=self.name("c"), tooltip=t[:80], x=self.m + 16, y=yy - 3, size=10,
                                buttonStyle="check", borderColor=CORAL, fillColor=white,
                                textColor=CORAL, borderWidth=0.8, forceBorder=True)
            c.setFont("Sans", 9.5)
            c.setFillColor(INK)
            c.drawString(self.m + 34, yy, t)
            yy -= 17
        self.y -= h + 16

    def note(self, text):
        lines = simpleSplit(text, "Sans", 9, self.W - 2 * self.m - 28)
        h = len(lines) * 12.5 + 16
        self.need(h + 8)
        c = self.c
        c.setFillColor(PALE_NAVY)
        c.roundRect(self.m, self.y - h, self.W - 2 * self.m, h, 6, stroke=0, fill=1)
        c.setFont("Sans", 9)
        c.setFillColor(NAVY)
        for i, line in enumerate(lines):
            c.drawString(self.m + 14, self.y - 16 - i * 12.5, line)
        self.y -= h + 12

    def table(self, title, cols, rows, widths):
        total = sum(widths)
        avail = self.W - 2 * self.m
        ws = [avail * w / total for w in widths]
        row_h = 18
        self.need(48 + row_h * 2)
        self.heading(title)
        c = self.c

        def header():
            c.setFillColor(PALE_NAVY)
            c.rect(self.m, self.y - 16, avail, 18, stroke=0, fill=1)
            c.setFont("SansB", 8)
            c.setFillColor(NAVY)
            x = self.m
            for col, w in zip(cols, ws):
                c.drawString(x + 4, self.y - 10, col[:int(w / 4.6)])
                x += w
            self.y -= 18

        header()
        for _ in range(rows):
            if self.y - row_h < 50:
                self.new_page()
                header()
            x = self.m
            for col, w in zip(cols, ws):
                self.textfield(x, self.y - row_h, w, row_h, tip=f"{title}: {col}")
                x += w
            self.y -= row_h
        self.y -= 14

    def render(self, blocks):
        for b in blocks:
            kind = b[0]
            if kind == "cover":
                self.cover(*b[1:])
            elif kind == "section":
                self.section_header(*b[1:])
            elif kind == "ten":
                self.ten(b[1])
            elif kind == "p":
                self.para(b[1])
            elif kind == "h":
                self.heading(b[1])
            elif kind == "fields":
                self.fields(b[1])
            elif kind == "box":
                self.box(b[1], b[2])
            elif kind == "table":
                self.table(*b[1:])
            elif kind == "checks":
                self.checks(b[1])
            elif kind == "note":
                self.note(b[1])
            elif kind == "pagebreak":
                self.new_page()
        self.c.save()
        return self.page


def main():
    out = os.path.join(HERE, "salida")
    os.makedirs(out, exist_ok=True)
    products = [
        ("The Solo Adult's Just-In-Case Binder", "in-order-co-solo-binder", C.CORE),
        ("Emergency Cards & Quick Sheets", "in-order-co-emergency-kit", C.KIT),
        ("Digital Legacy Deep-Dive", "in-order-co-digital-legacy", C.DIGITAL),
    ]
    for title, slug, blocks in products:
        for label, size in (("US-Letter", LETTER), ("A4", A4)):
            path = os.path.join(out, f"{slug}-{label}.pdf")
            pages = Doc(path, size, title).render(blocks)
            print(f"{path}: {pages} pages")


if __name__ == "__main__":
    main()
