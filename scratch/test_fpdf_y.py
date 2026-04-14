from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)

print(f"Initial Y: {pdf.get_y()}")
pdf.cell(60, 8, "Col1", border=1)
print(f"Y after cell: {pdf.get_y()}")
pdf.multi_cell(0, 8, "Col2 text", border=1)
print(f"Y after multi_cell: {pdf.get_y()}")
print(f"X after multi_cell: {pdf.get_x()}")
