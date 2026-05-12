from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)
for y in range(20, 120, 20):
    pdf.set_xy(10, y)
    pdf.cell(0, 8, f"Prueba en Y={y}", border=1)
print("Coordenadas Y generadas correctamente")
