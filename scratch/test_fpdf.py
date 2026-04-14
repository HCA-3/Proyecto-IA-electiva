from fpdf import FPDF
import os

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 10)
print(f"Page width: {pdf.w}")
print(f"Effective page width (epw): {pdf.epw}")
print(f"X before: {pdf.get_x()}")
pdf.cell(60, 8, "Test", border=1)
print(f"X after cell(60): {pdf.get_x()}")
try:
    pdf.multi_cell(0, 8, "This is a test of multi_cell(0) after a cell(60).", border=1)
    print("multi_cell(0) worked")
except Exception as e:
    print(f"multi_cell(0) failed: {e}")
