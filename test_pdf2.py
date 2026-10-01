from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", size=10)

pdf.set_font("helvetica", "B", 16)
pdf.cell(0, 10, "Xarajatlar Hisoboti", align="C")
pdf.ln(10)

pdf.set_font("helvetica", size=12)
pdf.cell(0, 10, "Jami summa: 1 550 000 so'm", align="L")
pdf.ln(10)

from fpdf.fonts import FontFace
import fpdf

pdf.set_font("helvetica", size=10)
with pdf.table(col_widths=(30, 40, 90, 30)) as table:
    # Header
    row = table.row()
    for header in ["Sana", "Do'kon", "Mahsulotlar", "Summa"]:
        row.cell(header)
    
    # Data
    row = table.row()
    row.cell("2026-08-24 15:30")
    row.cell("Korzinka")
    row.cell("1. Non\n2. Choy")
    row.cell("50 000")

pdf.output("test_pdf2.pdf")
