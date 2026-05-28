import docx
import json

doc_path = r'e:\CivilEng\foundation_engineering\pdfs\exam_questions_answered_may2024-05-12.docx'
doc = docx.Document(doc_path)
text = []
for p in doc.paragraphs:
    if p.text.strip():
        text.append(p.text.strip())

with open(r'e:\CivilEng\foundation_engineering\sample.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(text))
