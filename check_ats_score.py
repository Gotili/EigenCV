import sys
import os
import re
import glob
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

try:
    import fitz  # PyMuPDF
except ImportError:
    console.print("[bold red]PyMuPDF is required to read PDFs. Please run: pip install pymupdf[/bold red]")
    sys.exit(1)

try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    from rapidfuzz import fuzz
except ImportError:
    console.print("[bold red]NLTK and RapidFuzz are required for advanced ATS matching. Please run: pip install nltk rapidfuzz[/bold red]")
    sys.exit(1)

# Ensure NLTK resources are available silently
import warnings
warnings.filterwarnings("ignore")
try:
    nltk.data.find('corpora/wordnet.zip')
    nltk.data.find('tokenizers/punkt.zip')
except LookupError:
    with console.status("[bold yellow]Downloading NLTK resources for ATS lemmatization (first run only)...[/bold yellow]"):
        nltk.download('wordnet', quiet=True)
        nltk.download('punkt', quiet=True)

lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    tokens = word_tokenize(text)
    return " ".join([lemmatizer.lemmatize(t.lower()) for t in tokens])

def load_master_skills(base_dir):
    skills_file = os.path.join(base_dir, "cv", "database", "active", "master_skills.md")
    skills = set()
    if not os.path.exists(skills_file):
        return skills
        
    with open(skills_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    for line in lines:
        if "Self-Assessed Skill Ratings" in line:
            break
        if line.startswith('##') or line.startswith('**') or not line.strip():
            continue
        # Split by comma first
        parts = line.split(',')
        for p in parts:
            # Remove brackets and asterisks
            p = re.sub(r'[\[\]\*]', '', p)
            
            # Split by pipe | or slash / or ampersand & to get aliases
            aliases = re.split(r'[\|/&]', p)
            for s in aliases:
                # Remove parentheses and trim
                s = re.sub(r'[\(\)]', '', s).strip()
                if len(s) >= 1:
                    skills.add(s.lower())
    return skills

def extract_text_from_pdf(filepath):
    text = ""
    try:
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        
        # Also extract PDF metadata (invisible keywords)
        metadata = doc.metadata
        if metadata and 'keywords' in metadata and metadata['keywords']:
            text += " " + metadata['keywords']
            
    except Exception as e:
        console.print(f"[bold red]Error reading PDF {filepath}: {e}[/bold red]")
    return text.lower()

def extract_text_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().lower()

def is_skill_in_text(skill, text, lemmatized_text):
    skill_lower = skill.lower()
    
    # 1. Exact Substring/Regex Match
    if skill_lower.isalnum():
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text):
            return True
    else:
        if skill_lower in text:
            return True
            
    # 2. Lemmatized Match (e.g. "optimization" -> "optimization", "optimizing" -> "optimize")
    lemmatized_skill = lemmatize_text(skill_lower)
    if lemmatized_skill and lemmatized_skill in lemmatized_text:
        return True
        
    # 3. Fuzzy Match (Partial Ratio) to catch minor typos or pluralization differences
    # Only apply fuzzy match for skills longer than 3 chars to prevent false positives on 'C' or 'R'
    if len(skill_lower) > 3:
        words = text.split()
        for word in words:
            if fuzz.ratio(skill_lower, word) > 88: # 88 is a good threshold for minor typos
                return True
                
    return False

def check_ats(package_folder):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(package_folder):
        console.print(f"[bold red]Error: Folder {package_folder} does not exist.[/bold red]")
        sys.exit(1)
        
    jd_files = glob.glob(os.path.join(package_folder, "JD_*.md"))
    if not jd_files:
        console.print(f"[bold yellow]Warning: No Job Description (JD_*.md) found in {package_folder}.[/bold yellow]")
        console.print("Skipping ATS Check.")
        return
        
    jd_files.sort(key=os.path.getmtime, reverse=True)
    jd_file = jd_files[0]
    jd_text = extract_text_from_file(jd_file)
    jd_text_lemmatized = lemmatize_text(jd_text)
    
    master_skills = load_master_skills(base_dir)
    
    requested_skills = set()
    for skill in master_skills:
        if is_skill_in_text(skill, jd_text, jd_text_lemmatized):
            requested_skills.add(skill)
            
    if not requested_skills:
        console.print("[dim]No master skills detected in the Job Description.[/dim]")
        
    # Check for missing skills in build_config.json
    config_path = os.path.join(package_folder, "build_config.json")
    llm_missing_skills = []
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'missing_skills' in config and config['missing_skills']:
                    llm_missing_skills = config['missing_skills']
        except Exception as e:
            console.print(f"[bold yellow]Warning: Could not read build_config.json: {e}[/bold yellow]")

    for ms in llm_missing_skills:
        requested_skills.add(ms)
        
    if not requested_skills:
        console.print("No skills to check against. ATS score not applicable.")
        return
        
    pdf_files = glob.glob(os.path.join(package_folder, "CV*.pdf"))
    if not pdf_files:
        console.print("[bold yellow]No compiled CV PDF found. Please run 'make' or 'pdflatex' first.[/bold yellow]")
        return
        
    pdf_files.sort(key=os.path.getmtime, reverse=True)
    cv_pdf_path = pdf_files[0]
    cv_text = extract_text_from_pdf(cv_pdf_path)
    cv_text_lemmatized = lemmatize_text(cv_text)
    
    found_skills = set()
    missing_skills = set()
    
    for skill in requested_skills:
        if is_skill_in_text(skill, cv_text, cv_text_lemmatized):
            found_skills.add(skill)
        else:
            missing_skills.add(skill)
            
    score = (len(found_skills) / len(requested_skills)) * 100
    
    # Rich Terminal Output
    console.print()
    table = Table(title=f"ATS Match Score: {score:.1f}%", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Skills", style="white")
    
    table.add_row("Target File", os.path.basename(cv_pdf_path))
    table.add_row("Total Evaluated", str(len(requested_skills)))
    table.add_row(f"Found ({len(found_skills)})", "[green]" + ", ".join(sorted(found_skills)) + "[/green]")
    if missing_skills:
        table.add_row(f"Missing ({len(missing_skills)})", "[red]" + ", ".join(sorted(missing_skills)) + "[/red]")
        
    console.print(table)
    
    actual_missing_llm_skills = [ms for ms in llm_missing_skills if ms in missing_skills]
    if actual_missing_llm_skills:
        console.print(f"\n[bold red][!] ATS Penalty Applied:[/bold red] {len(actual_missing_llm_skills)} critical gaps identified in build_config.json were added to the denominator.\n")
        
    if not missing_skills:
        console.print("[bold green]All requested skills are present in the PDF![/bold green]\n")
        
    # Markdown Report for README
    report = f"\n\n==========================================\n"
    report += f"ATS OPTIMIZATION REPORT (SOTA NLP PARSER)\n"
    report += f"==========================================\n"
    report += f"Target File: {os.path.basename(cv_pdf_path)}\n"
    report += f"ATS Keyword Match Score: {score:.1f}%\n"
    report += f"Total Skills Evaluated: {len(requested_skills)}\n"
    report += f"Requested Skills Found ({len(found_skills)}): {', '.join(sorted(found_skills))}\n"
    if missing_skills:
        report += f"Requested Skills Missing ({len(missing_skills)}): {', '.join(sorted(missing_skills))}\n"
    if actual_missing_llm_skills:
        report += f"\n[!] ATS Penalty Applied: {len(actual_missing_llm_skills)} critical gaps identified in build_config.json were added to the denominator.\n"
    if not missing_skills:
        report += f"All requested skills are present in the PDF!\n"
    report += f"==========================================\n"
    
    readme_path = os.path.join(package_folder, "README.md")
    if os.path.exists(readme_path) or os.path.exists(os.path.join(package_folder, "README.txt")):
        if not os.path.exists(readme_path): 
             readme_path = os.path.join(package_folder, "README.txt")
        with open(readme_path, 'a', encoding='utf-8') as f:
            f.write(report)
        console.print(f"[dim]ATS Report appended to {readme_path}[/dim]")

    # Auto-update tracking
    tracking_path = os.path.join(base_dir, "application_tracking.md")
    if os.path.exists(tracking_path):
        app_id = os.path.basename(os.path.normpath(package_folder))[:2]
        if app_id.isdigit():
            try:
                with open(tracking_path, 'r', encoding='utf-8') as f:
                    tracking_lines = f.readlines()
                
                with open(tracking_path, 'w', encoding='utf-8') as f:
                    for line in tracking_lines:
                        if line.startswith(f"| {app_id} |"):
                            line = line.replace("| ATS |", f"| {score:.1f}% |")
                        f.write(line)
                console.print(f"[dim]Updated application_tracking.md with ATS Score: {score:.1f}%[/dim]")
            except Exception as e:
                console.print(f"[bold red]Warning: Could not update application_tracking.md: {e}[/bold red]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("Usage: python check_ats_score.py <package_folder_path>")
        sys.exit(1)
        
    check_ats(sys.argv[1])
