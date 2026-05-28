import os
import glob
import re
import json
import docx
from docx.enum.text import WD_COLOR_INDEX

def parse_docx(file_path):
    doc = docx.Document(file_path)
    questions = []
    current_q = None
    
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
            
        # Match question start e.g. "1- The end bearing..."
        m_q = re.match(r'^(\d+)[-\.]\s*(.*)', text)
        m_opt = re.match(r'^([a-eA-E])[-\)]\s*(.*)', text)
        
        if m_q:
            if current_q and current_q['opts']:
                questions.append(current_q)
            current_q = {
                'q': m_q.group(2).strip(),
                'opts': [],
                'ans': 0
            }
        elif m_opt and current_q:
            opt_text = m_opt.group(2).strip()
            # Check if this option is highlighted green
            is_correct = False
            for run in p.runs:
                # Check highlight
                if run.font.highlight_color in [WD_COLOR_INDEX.GREEN, WD_COLOR_INDEX.BRIGHT_GREEN]:
                    is_correct = True
                # Check font color
                if run.font.color and run.font.color.rgb:
                    rgb = str(run.font.color.rgb)
                    # Simple check for greenish colors e.g. 00FF00
                    if rgb.startswith('00') and not rgb.endswith('000000'):
                        is_correct = True
                        
            current_q['opts'].append(opt_text)
            if is_correct:
                current_q['ans'] = len(current_q['opts']) - 1
                
    if current_q and current_q['opts']:
        questions.append(current_q)
        
    return questions

def main():
    pdf_dir = r'e:\CivilEng\foundation_engineering\pdfs'
    docx_files = glob.glob(os.path.join(pdf_dir, '*.docx'))
    
    all_exams = {}
    exam_names = ['exam1', 'exam2', 'exam3', 'exam4', 'exam5']
    
    for i, file_path in enumerate(docx_files):
        filename = os.path.basename(file_path)
        # Extract date from filename if possible
        date_match = re.search(r'(\d{1,4}[-\.]\d{1,2}[-\.]\d{1,4})', filename)
        src = date_match.group(1) if date_match else filename
        
        q_list = parse_docx(file_path)
        
        # Add src to all questions
        for q in q_list:
            q['src'] = src
            
        exam_key = exam_names[i] if i < len(exam_names) else f'exam{i+1}'
        all_exams[exam_key] = q_list
        print(f"Parsed {len(q_list)} questions from {filename}")
        
    # Output to a JS file snippet
    js_content = "const QUESTIONS = " + json.dumps(all_exams, ensure_ascii=False, indent=2) + ";"
    with open(r'e:\CivilEng\foundation_engineering\questions_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("Successfully generated questions_data.js")

if __name__ == '__main__':
    main()
