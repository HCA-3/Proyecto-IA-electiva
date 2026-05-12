from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)
for i in range(10):
    pdf.cell(0, 8, f"Línea de prueba {i+1}", border=1, ln=1)
print("Loop generado correctamente")
