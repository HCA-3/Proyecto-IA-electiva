from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)
text = "Este es un texto largo que debe envolverse automáticamente en la siguiente línea cuando alcanza el ancho de la página."
pdf.multi_cell(0, 8, text, border=1)
print("Wrap de texto probado")
