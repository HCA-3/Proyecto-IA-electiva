from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)
pdf.cell(60, 8, "Criterio", border=1)
long_text = "This is a very long text that will definitely wrap to the next line. It is intended to test if multi_cell(0) fails when it has to wrap while starting at a non-zero X position."
try:
    pdf.multi_cell(0, 8, long_text, border=1)
    print("multi_cell(0) with wrapping worked")
except Exception as e:
    print(f"multi_cell(0) with wrapping failed: {e}")
    import traceback
    traceback.print_exc()

pdf.ln(10)
pdf.cell(60, 8, "Criterio 2", border=1)
try:
    pdf.multi_cell(pdf.epw - 60, 8, long_text, border=1)
    print("multi_cell(epw-60) with wrapping worked")
except Exception as e:
    print(f"multi_cell(epw-60) with wrapping failed: {e}")
