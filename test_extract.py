import PyPDF2

pdf_path = r'e:\CivilEng\foundation_engineering\pdfs\اسئلة وزاري محلولة 25-4-2024.pdf'
try:
    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for i in range(min(3, len(reader.pages))):
        text += reader.pages[i].extract_text() + "\n"
        
    print(text[:1000])
except Exception as e:
    print(f"Error: {e}")
