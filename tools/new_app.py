import os
import sys
import re
import json
import argparse
from datetime import date
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_next_id(tracking_file):
    if not os.path.exists(tracking_file):
        return 1
    
    highest_id = 0
    with open(tracking_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^\|\s*(\d{2,})\s*\|', line)
            if match:
                highest_id = max(highest_id, int(match.group(1)))
    return highest_id + 1

def check_onboarding(base_dir):
    metadata_file = os.path.join(base_dir, 'cv', 'database', 'active', 'metadata.tex')
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            if 'Jane Doe' in f.read():
                console.print(Panel.fit(
                    "It looks like you are still using the default 'Jane Doe'\n"
                    "placeholder data. To prevent accidentally generating fake\n"
                    "applications, this script has been halted.\n\n"
                    "[bold yellow]ACTION REQUIRED:[/bold yellow]\n"
                    "Please provide the AI with your old CV and ask it to\n"
                    "run the Onboarding Process (docs/AI_ONBOARDING_PROMPT.md)\n"
                    "before creating a new application.",
                    title="[bold red]🛑 ONBOARDING REQUIRED 🛑[/bold red]",
                    border_style="red"
                ))
                sys.exit(1)

def get_user_name(base_dir):
    metadata_file = os.path.join(base_dir, 'cv', 'database', 'active', 'metadata.tex')
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'\\newcommand{\\cvname}{(.*?)}', content)
            if match:
                raw_name = match.group(1)
                # Remove titles like Dr., Prof. and keep only letters/spaces
                clean_name = re.sub(r'[^a-zA-Z\s]', '', raw_name)
                clean_name = clean_name.replace('Dr', '').replace('Prof', '').strip()
                # Return CamelCase name without spaces
                return "".join(word.capitalize() for word in clean_name.split())
    return "Applicant"

def create_new_app(company, role, dry_run=False):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Hard stop if the user hasn't onboarded yet
    check_onboarding(base_dir)
    
    tracking_file = os.path.join(base_dir, 'application_tracking.md')
    
    next_id = get_next_id(tracking_file)
    id_str = f"{next_id:02d}"
    
    # Sanitize inputs
    company = re.sub(r'[^a-zA-Z0-9]', '', company)
    role = re.sub(r'[^a-zA-Z0-9]', '', role)
    
    user_name = get_user_name(base_dir)
    
    folder_name = f"{id_str}-CV-{user_name}-{company}-{role}" if role else f"{id_str}-CV-{user_name}-{company}"
    folder_path = os.path.join(base_dir, 'application-packages', folder_name)
    
    if os.path.exists(folder_path):
        console.print(f"[bold red]Error: Folder {folder_path} already exists.[/bold red]")
        sys.exit(1)
        
    jd_filename = f"JD_{date.today().strftime('%Y-%m-%d')}.md"
    
    # Dynamically load education IDs from the active database
    edu_ids_str = '[]'
    edu_path = os.path.join(base_dir, 'cv', 'database', 'active', 'education.json')
    if os.path.exists(edu_path):
        try:
            with open(edu_path, 'r', encoding='utf-8') as f:
                edu_ids_str = json.dumps(list(json.load(f).keys()))
        except Exception:
            pass

    config_template = """{
  "job_title": "",
  "keywords": "",
  "geometry_options": "left=0.625in, right=0.625in, top=0.45in, bottom=0.45in",
  "company_accent_color": "",
  "profile": "",
  "skill_categories": [],
  "experience": {},
  "projects": [],
  "education": %s,
  "extracurriculars_title": "",
  "extracurriculars": [],
  "missing_skills": [],
  "cover_letter": {
    "company_name": "%s",
    "recruiting_team": "Hiring Team",
    "location": "Germany (Remote)",
    "subject_role": "Application: ",
    "salutation": "Dear Hiring Team,",
    "intro_paragraph": "",
    "body_paragraphs": [],
    "outro_paragraph": ""
  },
  "probability_matrix": {
    "invitation_probability": "",
    "technical_pass_probability": "",
    "job_offer_probability": "",
    "salary_estimate": "",
    "biggest_vulnerability": ""
  }
}
""" % (edu_ids_str, company)

    if dry_run:
        console.print(Panel.fit(
            f"[bold cyan]Folder to be created:[/bold cyan]\n{folder_path}\n\n"
            f"[bold cyan]Files to be created:[/bold cyan]\n- {jd_filename}\n- build_config.json\n\n"
            f"[bold cyan]build_config.json Content Preview:[/bold cyan]\n{config_template}",
            title="[bold yellow]DRY RUN MODE[/bold yellow]",
            border_style="yellow"
        ))
        return

    os.makedirs(folder_path)
    
    with open(os.path.join(folder_path, jd_filename), 'w', encoding='utf-8') as f:
        f.write("<!-- PASTE JOB DESCRIPTION HERE -->\n")
        
    with open(os.path.join(folder_path, "build_config.json"), 'w', encoding='utf-8') as f:
        f.write(config_template)
        
    console.print(Panel.fit(
        f"[bold green]Created {folder_path}[/bold green]\n\n"
        f"1. Please save the Job Description in {os.path.join(folder_name, jd_filename)}\n"
        f"2. Fill out the generated build_config.json file.",
        title="[bold green]SUCCESS[/bold green]",
        border_style="green"
    ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new EigenCV application package.")
    parser.add_argument("company", help="The name of the target company")
    parser.add_argument("role", help="A short snippet representing the role")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without creating files")
    
    args = parser.parse_args()
    create_new_app(args.company, args.role, args.dry_run)
