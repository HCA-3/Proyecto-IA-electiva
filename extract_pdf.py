import pdfplumber
import sys

def extract_pdf_extra(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n\n"
            return all_text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    path = r"Taller-Practico-Seleccion-de-Flujos-de-Trabajo-de-IA (1).pdf"
    content = extract_pdf_extra(path)
    print(content)
