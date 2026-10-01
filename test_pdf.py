from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", size=10)

html = """
<h1 align="center">Xarajatlar Hisoboti</h1>
<p><b>Jami summa:</b> 1 550 000 so'm</p>
<table border="1" width="100%">
    <thead>
        <tr bgcolor="#d3d3d3">
            <th width="20%">Sana</th>
            <th width="25%">Do'kon</th>
            <th width="40%">Mahsulotlar</th>
            <th width="15%">Summa</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2026-08-24 15:30</td>
            <td>Korzinka</td>
            <td>1. Non<br>2. Choy</td>
            <td>50 000</td>
        </tr>
    </tbody>
</table>
"""
pdf.write_html(html)
pdf.output("test_pdf.pdf")
