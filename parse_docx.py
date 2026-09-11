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
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_dir = os.path.join(base_dir, 'pdfs')
    
    exam_configs = [
        ('exam1', '*2024-04-25*.docx', '2024-04-25'),
        ('exam2', '*may2024-05-12*.docx', '2024-05-12'),
        ('exam3', '*27-5-2024*.docx', '27-5-2024'),
        ('exam4', '*2024-06-30*.docx', '2024-06-30'),
        ('exam5', '*2025-09-10*.docx', '2025-09-10'),
        ('exam6', '*2026*.docx', 'دور اول 2026')
    ]
    
    all_exams = {}
    for key, pattern, src in exam_configs:
        matches = glob.glob(os.path.join(pdf_dir, pattern))
        if not matches:
            matches = glob.glob(os.path.join(base_dir, pattern))
        if matches:
            file_path = matches[0]
            q_list = parse_docx(file_path)
            for q in q_list:
                q['src'] = src
            all_exams[key] = q_list
            print(f"Parsed {len(q_list)} questions for {key} from {os.path.basename(file_path)}")
        else:
            print(f"Warning: pattern {pattern} not found!")
            
    js_content = "const QUESTIONS = " + json.dumps(all_exams, ensure_ascii=False, indent=2) + ";\n"
    output_path = os.path.join(base_dir, 'questions_data.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("Successfully generated questions_data.js")

if __name__ == '__main__':
    main()
