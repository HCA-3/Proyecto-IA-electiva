from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)

data = [
    ["Col1", "Col2 is very long. Col2 is very long. Col2 is very long. Col2 is very long."],
    ["ColA", "ColB is also long. ColB is also long. ColB is also long. ColB is also long."]
]

for row in data:
    print(f"Start of loop X: {pdf.get_x()}")
    pdf.cell(60, 8, row[0], border=1)
    print(f"X after cell: {pdf.get_x()}")
    pdf.multi_cell(0, 8, row[1], border=1)
    print(f"X after multi_cell: {pdf.get_x()}")
