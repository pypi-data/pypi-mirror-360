import os
from pathlib import Path
import shutil
import csv
from physethta.utils import sortable_name
import subprocess
import glob

def generate_summary(pis, courses, config, lang, emails, out_dir: str = 'output', draft : bool = False):
    """ 
    Paramters
    =========
    pis : dict
    courses : dict
    out_dir : str
    semester : str
        e.g. HS25
    draft : bool
    """



    meta=config.get('meta',{})
    os.makedirs(out_dir, exist_ok=True)

    src_logo = Path(__file__).parent / "assets" / "Logo.pdf"
    dst_logo = Path(out_dir) / "Logo.pdf"
    if src_logo.exists():
        shutil.copy(src_logo, dst_logo)
    else:
        print(f"Warning: Logo file not found at {src_logo}")


    fnamepV = os.path.join(out_dir, f"Ass{meta['semester']}_perGroup.tex")

    header=r'''
    \documentclass[9pt,a4paper]{article}
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{longtable}
    \usepackage{graphicx}
    \usepackage[table]{xcolor} 
    \usepackage{sectsty}
    \sectionfont{\fontsize{12}{15}\selectfont}
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{helvet}
    \renewcommand{\familydefault}{\sfdefault}
    \usepackage{geometry}
    \geometry{a4paper,top=2cm,bottom=2cm,left=2cm,right=2cm,headsep=4.325mm}
    \usepackage{fancyhdr}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyfoot[C]{\thepage}
    \fancyfoot[L]{\includegraphics[height=9pt]{Logo}}
    \fancyfoot[R]{'''+meta['author']+r''', \today}
    \renewcommand{\headrulewidth}{0pt}
    ''' 
    if draft:
        header+=r'''
        \usepackage{draftwatermark}
        \SetWatermarkText{Draft}
        \SetWatermarkScale{2}
        '''
    header+=r'''
    \begin{document}
    \noindent
    {\LARGE \bf Zuteilung Assistierende '''+meta['semester']+r''' nach Gruppe geordnet}\bigskip
    '''
    with open(fnamepV, 'w', encoding='utf-8') as file:
        file.write(header)

    string=""
    for pi in sorted(pis.keys(), key=sortable_name):
        string+=r"""
        \section*{%s}
        \noindent
        \rowcolors{2}{gray!25}{white}
        \begin{longtable}{p{0.5cm}p{4cm}p{3.5cm}p{2.5cm}p{3cm}}
        \rowcolor{gray!50}
        & {\bf First name} & {\bf Last name}& {\bf Assigned to}& {\bf Reason}\\
        """%(pi)
        front = ""
        back = ""
        sorted_data = sorted(pis[pi], key=lambda x: x[1])
        for i in range(len(sorted_data)):
            pp=sorted_data[i]
            if pp[2] == "":
                back += f" & {pp[0]} & {pp[1]} & {pp[2]} & {pp[3]} \\\\ \n"
            else:
                front += f" & {pp[0]} & {pp[1]} & {pp[2]} & {pp[3]} \\\\ \n"
        string += front
        string += back
        string += r"\end{longtable}"
    
    string += r"\end{document}"
    with open(fnamepV, 'a', encoding='utf-8') as file:
        file.write(string)


    fnamepC = os.path.join(out_dir, f"Ass{meta['semester']}_perCourse.tex")

    
    header=r'''\documentclass[9pt,a4paper]{article}
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    %\usepackage[spanish]{babel}
    \usepackage{longtable}
    \usepackage{graphicx}
    \usepackage[table]{xcolor} 
    \usepackage{sectsty}
    \sectionfont{\fontsize{12}{15}\selectfont}
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{helvet}
    \renewcommand{\familydefault}{\sfdefault}
    \usepackage{geometry}
    \geometry{a4paper,top=2cm,bottom=2cm,left=2cm,right=2cm,headsep=4.325mm}
    \usepackage{fancyhdr}
    \pagestyle{fancy}
    \fancyhf{}
    \fancyfoot[C]{\thepage}
    \fancyfoot[L]{\includegraphics[height=9pt]{Logo}}
    \fancyfoot[R]{'''+meta['author']+r''', \today}
    \renewcommand{\headrulewidth}{0pt}
    ''' 
    if draft:
        header+=r'''
        \usepackage{draftwatermark}
        \SetWatermarkText{Draft}
        \SetWatermarkScale{2}
        '''
    header+=r'''
    \begin{document}
    \noindent
    {\LARGE \bf Zuteilung Assistierende '''+meta['semester']+r''' nach Vorlesung geordnet}\bigskip
    '''
    with open(fnamepC, 'w', encoding='utf-8') as file:
        file.write(header)
    
    string=""
    for s in sorted(courses):     
        ppl=courses[s]
        if len(ppl)>0:
            
            string+=r"""
            \section*{%s}
            \noindent
            \rowcolors{2}{gray!25}{white}
            \begin{longtable}{p{0.35cm}p{5cm}p{4cm}p{2.5cm}p{2.5cm}}
            \rowcolor{gray!50}
            & {\bf First name} & {\bf Last name}& {\bf Group} & \\
            """%(s)
            for j,pp in enumerate(ppl):
                string+="%s. & %s & %s &%s&\\\\ \n"%(j+1,pp[0],pp[1],pp[2])
            string+="\end{longtable}\n"
        
    string+=r"\end{document}"
    with open(fnamepC, 'a') as file:
        file.write(string)

    os.makedirs(os.path.join(out_dir, 'tables'), exist_ok=True)
    draftable=[]
    for s in sorted(lang):
        st=s.split(" ")
        if st[-1] in config.get("courses_for_correction",[]):
            ppl=lang[s]
            for person in ppl:
                draftable.append(person+[st[-1]])
    draftable = sorted(draftable, key=lambda x: x[1])
    fname = os.path.join(out_dir, 'tables' ,'draftable.csv' )
    with open(fname, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Vorname","Name","Email","Deutsch","PI","Vorlesung"])
        for person in draftable:
            writer.writerow(person)


    for s in sorted(emails):
        st=s.split(" ")
        fname = os.path.join(out_dir, 'tables' , f"{st[-1]}.csv")
        ppl=emails[s]
        
        if len(ppl)>0:

            with open(fname, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["Vorname","Name","Email"])
                for person in ppl:
                    writer.writerow(person)

    fname = os.path.join(out_dir, 'tables' , "VMP.csv")
    with open(fname, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Vorname","Name","Email","Vorlesung"])
        for s in sorted(emails):
            lecture=s.split(" ")[-1]
            ppl=emails[s]
            for p in ppl:
                writer.writerow(p+[lecture])


    if shutil.which("pdflatex") is None:
        print("Warning: pdflatex not found. Skipping PDF compilation.")
        return
    try:
        print 
        subprocess.run(["pdflatex", "-interaction=nonstopmode", os.path.basename(fnamepC)], cwd=out_dir, check=True)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", os.path.basename(fnamepV)], cwd=out_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"LaTeX compilation failed: {e}")

    for pattern in ["*.aux", "*.log"]:
        for f in glob.glob(os.path.join(out_dir, pattern)):
            os.remove(f)




    