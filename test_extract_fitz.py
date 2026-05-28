import fitz

pdf_path = r'e:\CivilEng\foundation_engineering\pdfs\اسئلة وزاري محلولة 25-4-2024.pdf'
try:
    doc = fitz.open(pdf_path)
    text = ""
    for i in range(min(3, len(doc))):
        page = doc[i]
        text += page.get_text() + "\n"
        
    print("EXTRACTED TEXT:")
    print(text[:1000])
except Exception as e:
    print(f"Error: {e}")
