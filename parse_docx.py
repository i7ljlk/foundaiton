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
            
        # Match question start e.g. "1- The end bearing..." or "1. Which class..."
        m_q = re.match(r'^(\d+)[\.-]\s*(.*)', text)
        # Match option start e.g. "a) ...", "a- ...", "1) ...", "(a) ..."
        m_opt = re.match(r'^([a-eA-E1-5])[\.\-\)]\s*(.*)', text) or re.match(r'^\(([a-eA-E1-5])\)\s*(.*)', text)
        
        if m_q:
            if current_q and current_q['opts']:
                questions.append(current_q)
            current_q = {
                'q': m_q.group(2).strip(),
                'opts': [],
                'ans': None
            }
        elif m_opt and current_q:
            opt_text = m_opt.group(2).strip()
            is_correct = False
            
            # 1. Check run highlights and font colors
            for run in p.runs:
                if run.font.highlight_color in [
                    WD_COLOR_INDEX.GREEN, 
                    WD_COLOR_INDEX.BRIGHT_GREEN, 
                    WD_COLOR_INDEX.YELLOW,
                    WD_COLOR_INDEX.TURQUOISE
                ]:
                    is_correct = True
                if run.font.color and run.font.color.rgb:
                    rgb = str(run.font.color.rgb).upper()
                    if rgb in ['2E7D32', '00FF00', '92D050', '375623', '00B050', '008000', '70AD47']:
                        is_correct = True
                
                # Check run shading
                rPr = run._element.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
                if rPr is not None:
                    shd = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                    if shd is not None:
                        fill = str(shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill', '')).upper()
                        if fill in ['92D050', '00FF00', 'C6EFCE', 'A9D08E', 'E2EFDA', '548235', '70AD47']:
                            is_correct = True
                            
            # 2. Check paragraph shading (used in exam 27-5-2024)
            pPr = p._element.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
            if pPr is not None:
                shd = pPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                if shd is not None:
                    fill = str(shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill', '')).upper()
                    if fill in ['92D050', '00FF00', 'C6EFCE', 'A9D08E', 'E2EFDA', '548235', '70AD47']:
                        is_correct = True
                        
            current_q['opts'].append(opt_text)
            if is_correct:
                current_q['ans'] = len(current_q['opts']) - 1
                
    if current_q and current_q['opts']:
        questions.append(current_q)
        
    # Fallback / sanity check for missing answer detection
    for q in questions:
        if q['ans'] is None:
            print(f"Warning: No answer detected for question: {q['q'][:50]}... Defaulting to 0")
            q['ans'] = 0
            
    return questions

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dir = os.path.join(base_dir, 'pdfs')
    
    exam_configs = [
        ('exam1', '*2024-04-25*.docx', 'أسئلة دور أول 2024 (25-4)'),
        ('exam2', '*may2024-05-12*.docx', 'أسئلة دور أول 2024 (12-5)'),
        ('exam3', '*27-5-2024*.docx', 'أسئلة دور أول 2024 (27-5)'),
        ('exam4', '*2024-06-30*.docx', 'أسئلة دور ثاني 2024 (30-6)'),
        ('exam5', '*2025-09-10*.docx', 'أسئلة دور ثاني 2025 (10-9)'),
        ('exam6', '*2026*.docx', 'أسئلة دور أول 2026 (2-6)')
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
            ans_dist = {}
            for q in q_list:
                ans_dist[q['ans']] = ans_dist.get(q['ans'], 0) + 1
            print(f"Parsed {len(q_list)} questions for {key} from {os.path.basename(file_path)} | Answers: {ans_dist}")
        else:
            print(f"Warning: pattern {pattern} not found!")
            
    js_content = "const QUESTIONS = " + json.dumps(all_exams, ensure_ascii=False, indent=2) + ";\n"
    output_path = os.path.join(base_dir, 'questions_data.js')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("Successfully generated questions_data.js")

if __name__ == '__main__':
    main()

