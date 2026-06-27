"""
EigenCV Compiler Core.

This script parses the Pydantic-validated JSON data and orchestrates the 
generation of LaTeX documents via Jinja2 templating. It includes the EigenTruth 
Engine to detect LLM hallucinations and langdetect to prevent language mismatches.
"""
import os
import sys
import json
try:
    import jinja2
    from pydantic import ValidationError
except ImportError:
    print("Missing required dependencies. Please run: pip install -r requirements.txt")
    print("Or manually: pip install jinja2 pydantic")
    sys.exit(1)

from datetime import date
from cv_schema import BuildConfig

class EigenTruthViolationError(Exception):
    pass

import re
import uuid
from rich.console import Console
from rich.panel import Panel

# Add tools directory to path and import linter
tools_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tools')
sys.path.append(tools_dir)
try:
    from lint_database import lint_database
except ImportError:
    lint_database = None

console = Console()

# Run Linter before anything else
if lint_database:
    lint_database()

def hex_to_rgb(hex_str: str) -> tuple:
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    return '%02X%02X%02X' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_luminance(rgb: tuple) -> float:
    # W3C Relative Luminance
    a = [c / 255.0 for c in rgb]
    for i in range(3):
        if a[i] <= 0.03928:
            a[i] = a[i] / 12.92
        else:
            a[i] = ((a[i] + 0.055) / 1.055) ** 2.4
    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722

def adjust_color_for_contrast(hex_str: str) -> str:
    """Darkens a color until its luminance is suitable for a white background."""
    if not hex_str or len(hex_str.lstrip('#')) != 6:
        return hex_str
        
    rgb = list(hex_to_rgb(hex_str))
    
    # White background luminance is 1.0. 
    # For a contrast ratio of ~3.0 to 4.5 against white, target max luminance ~0.35.
    while get_luminance(tuple(rgb)) > 0.35:
        rgb[0] = max(0, int(rgb[0] * 0.9))
        rgb[1] = max(0, int(rgb[1] * 0.9))
        rgb[2] = max(0, int(rgb[2] * 0.9))
        
    return rgb_to_hex(tuple(rgb))

def sanitize_latex_text(s):
    """
    Safely escapes dangerous LaTeX characters (&, %, $, #, _, {, }, \) 
    and translates basic Markdown (**bold**, *italic*, [link](url)) to LaTeX.
    """
    if not isinstance(s, str):
        return s
        
    def escape_dangerous_chars(text):
        # Hide backslashes first so we don't double escape
        text = text.replace('\\', '\x00BACKSLASH\x00')
        # Escape dangerous LaTeX grouping braces
        text = text.replace('{', r'\{').replace('}', r'\}')
        # Restore backslashes
        text = text.replace('\x00BACKSLASH\x00', r'\textbackslash{}')
        # Escape standard reserved characters
        text = re.sub(r'(?<!\\)&', r'\\&', text)
        text = re.sub(r'(?<!\\)%', r'\\%', text)
        text = re.sub(r'(?<!\\)\$', r'\\$', text)
        text = re.sub(r'(?<!\\)#', r'\\#', text)
        text = re.sub(r'(?<!\\)_', r'\\_', text)
        text = text.replace('~', r'\textasciitilde{}')
        text = text.replace('^', r'\textasciicircum{}')
        # Typography fixes
        text = text.replace('—', ' - ').replace('–', ' - ')
        return text

    # Extract markdown tags and replace with UUIDs
    bold_pattern = r'\*\*(.*?)\*\*'
    italic_pattern = r'\*(.*?)\*'
    link_pattern = r'\[(.*?)\]\((.*?)\)'
    
    replacements = {}
    
    def bold_repl(m):
        uid = f"UUID{uuid.uuid4().hex}"
        replacements[uid] = rf"\textbf{{{escape_dangerous_chars(m.group(1))}}}"
        return uid
        
    def italic_repl(m):
        uid = f"UUID{uuid.uuid4().hex}"
        replacements[uid] = rf"\textit{{{escape_dangerous_chars(m.group(1))}}}"
        return uid
        
    def link_repl(m):
        uid = f"UUID{uuid.uuid4().hex}"
        # Do not escape the URL completely, but escape the display text
        replacements[uid] = rf"\href{{{m.group(2)}}}{{{escape_dangerous_chars(m.group(1))}}}"
        return uid
        
    s = re.sub(bold_pattern, bold_repl, s)
    s = re.sub(r'(?<!\w)\*(.*?)\*(?!\w)', italic_repl, s)
    s = re.sub(link_pattern, link_repl, s)
    
    # Escape the rest of the string
    s = escape_dangerous_chars(s)
    
    # Re-inject the UUIDs as actual LaTeX commands
    for uid, val in replacements.items():
        s = s.replace(uid, val)
        
    return s
        
    return s

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Could not find configuration file at {filepath}")
        print("Tip: Ensure you have saved the LLM output as 'build_config.json' in this folder.")
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {filepath}.")
        print(f"Details: {e}")
        print("Tip: Check for trailing commas or unescaped quotes (common LLM generation errors).")
        sys.exit(1)

def compile_cv(config_path):
    console.print(Panel(f"Compiling CV from {config_path}...", title="EigenCV Compiler", style="bold blue"))
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'database', 'active')
    template_dir = os.path.join(base_dir, 'template')
    metadata_path = os.path.join(data_dir, 'metadata.tex')
    
    # Pre-flight Check: Ensure metadata exists
    if not os.path.exists(metadata_path):
        console.print("\n[bold red][FATAL ERROR] Missing required file:[/bold red]", metadata_path)
        console.print("Your personal metadata.tex file is missing. The LaTeX compilation will fail without it.")
        console.print("Please ask the AI to run the Onboarding process (docs/AI_ONBOARDING_PROMPT.md) to reconstruct your database.\n")
        sys.exit(1)
    
    raw_config = load_json(config_path)
    
    try:
        config = BuildConfig.model_validate(raw_config)
    except Exception as e:
        console.print(Panel(str(e), title="[bold red]Pydantic Validation Error in build_config.json[/bold red]"))
        print("\n[!!! AI RECOVERY INSTRUCTION !!!]")
        print("The build_config.json contains one or more IDs that do not exist in the database.")
        print("ACTION: Re-read the relevant database JSON file (e.g. cv/database/active/experience.json)")
        print("        and replace all invalid IDs with real IDs from that file.")
        print("        Then overwrite build_config.json with the corrected version and run chatgpt_run.py again.")
        sys.exit(1)
    
    # Dynamically find the requested template and name from metadata.tex
    metadata_path = os.path.join(data_dir, 'metadata.tex')
    template_name = 'eigencv_resume.tex.j2' # default
    cvcolor = 'awesome-emerald'
    section_order = ['Profile', 'Skills', 'Experience', 'Projects', 'Education', 'Languages', 'Extracurriculars']
    user_first_name = "Applicant"
    user_last_name = ""
    parsed_metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_content = f.read()
            match_template = re.search(r'(?m)^[^%]*\\newcommand\{\\cvtemplate\}\{(.*?)\}', metadata_content)
            if match_template:
                template_name = match_template.group(1).strip()
                
            for line in metadata_content.splitlines():
                line = line.strip()
                if line.startswith('%'):
                    continue
                if line.startswith(r'\newcommand{\cvtemplate}'):
                    template_name = re.search(r'\}\{([^}]+)\}', line).group(1).strip()
                elif line.startswith(r'\newcommand{\cvcolor}'):
                    cvcolor = re.search(r'\}\{([^}]+)\}', line).group(1).strip()
                elif line.startswith(r'\newcommand{\cvcoloroverride}'):
                    parsed_metadata['cvcoloroverride'] = re.search(r'\}\{([^}]+)\}', line).group(1).strip().lower() == 'true'
                elif line.startswith(r'\newcommand{\cvorder}'):
                    raw_order = re.search(r'\}\{([^}]+)\}', line).group(1).strip()
                    section_order = [s.strip() for s in raw_order.split(',')]
                elif line.startswith(r'\newcommand{\cvlocale}'):
                    parsed_metadata['cvlocale'] = re.search(r'\}\{([^}]+)\}', line).group(1).strip()
                elif line.startswith(r'\newcommand{\cvname}'):
                    full_name = re.search(r'\}\{([^}]+)\}', line).group(1).strip()
                    parts = full_name.split(' ', 1)
                    user_first_name = parts[0]
                    if len(parts) > 1:
                        user_last_name = parts[1]
                        
    # Cloud-Safe Override (For ChatGPT / OpenAI Sandbox)
    if os.environ.get("EIGENCV_FORCE_CLOUD_SAFE") == "1":
        template_name = 'eigencv_cloud_safe.tex.j2'
        console.print("[bold yellow]CLOUD OVERRIDE ACTIVE: Enforcing eigencv_cloud_safe.tex.j2 to prevent font crashes in sandbox.[/bold yellow]")
                
    # Load and process i18n
    i18n_path = os.path.join(data_dir, 'i18n.json')
    locale = parsed_metadata.get('cvlocale', 'en')
    i18n_all = {}
    if os.path.exists(i18n_path):
        i18n_all = load_json(i18n_path)
        
    # Process dynamic i18n updates from AI
    if getattr(config, 'i18n_updates', None):
        dyn_locale = config.i18n_updates.locale_code
        if dyn_locale not in i18n_all:
            i18n_all[dyn_locale] = {}
        i18n_all[dyn_locale].update(config.i18n_updates.translations)
        try:
            with open(i18n_path, 'w', encoding='utf-8') as f:
                json.dump(i18n_all, f, indent=2, ensure_ascii=False)
            console.print(f"[bold yellow]Dynamically learned new language translations for '{dyn_locale}' and saved to i18n.json[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Warning: Could not save new translations: {e}[/bold red]")
            
        locale = dyn_locale
        
    i18n_dict = i18n_all.get(locale, i18n_all.get('en', {}))
                
    console.print(f"Using layout template: [bold green]{template_name}[/bold green], Locale: [bold green]{locale}[/bold green]")

    # Load Master Databases with Locale Fallback
    def load_locale_db(base_name):
        if locale != 'en':
            loc_path = os.path.join(data_dir, f"{base_name}_{locale}.json")
            if os.path.exists(loc_path):
                console.print(f"[bold green]Loaded locale-specific database: {base_name}_{locale}.json[/bold green]")
                return load_json(loc_path)
        return load_json(os.path.join(data_dir, f"{base_name}.json"))
        
    db_experience = load_locale_db('experience')
    projects_db = load_locale_db('projects')
    education_db = load_locale_db('education')
    extracurriculars_db = load_locale_db('extracurriculars')
    languages_db = load_locale_db('languages')
    
    # Process Experience
    experience_data = []
    for job_id, job_config in config.experience.items():
        master_job = db_experience[job_id]
        bullets = [master_job['bullets'][b_id] for b_id in job_config.bullets]
        experience_data.append({
            'company': master_job['company'],
            'location': master_job['location'],
            'dates': master_job['dates'],
            'title': job_config.title,
            'bullets': bullets
        })
        
    # Process Projects
    projects_data = [projects_db[proj_id] for proj_id in config.projects]
        
    # Process Education
    education_data = [education_db[edu_id] for edu_id in config.education]

    # Process Extracurriculars
    extracurriculars_data = [extracurriculars_db[extra_id] for extra_id in config.extracurriculars]
        
    # Process Languages
    languages_data = []
    if hasattr(config, 'languages') and config.languages:
        languages_data = [languages_db[lang_id] for lang_id in config.languages]

    # Setup Jinja Environment
    # We change Jinja delimiters to avoid clashing with LaTeX
    latex_jinja_env = jinja2.Environment(
        block_start_string='{%',
        block_end_string='%}',
        variable_start_string='{{',
        variable_end_string='}}',
        comment_start_string='{#',
        comment_end_string='#}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(template_dir)
    )
    
    latex_jinja_env.filters['sanitize_latex_text'] = sanitize_latex_text
    
    
    # Language Safety Check: Zero-Trust for Master Databases
    if experience_data:
        try:
            from langdetect import detect
            
            # Extract plain text from bullets to test language
            sample_text = " ".join([b for job in experience_data for b in job['bullets']])
            # Remove LaTeX commands for cleaner detection
            sample_text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', sample_text)
            
            if sample_text.strip():
                detected_lang = detect(sample_text)
                # Map some common langdetect outputs
                lang_map = {'en': 'en', 'de': 'de', 'es': 'es', 'fr': 'fr', 'it': 'it'}
                detected_mapped = lang_map.get(detected_lang, detected_lang)
                
                if locale != 'en' and detected_mapped != locale:
                    console.print(Panel(
                        f"Requested Locale: '{locale}'\\n"
                        f"Detected Database Locale: '{detected_mapped}'\\n\\n"
                        "Zero-Trust Policy Warning: Your master databases (experience, etc.) are NOT translated automatically! "
                        "You must provide database items in the requested locale, otherwise your CV will be bilingual.",
                        title="Language Mismatch Warning", border_style="yellow"
                    ))
                    # Removed raise ValueError to allow bilingual compilation without crashing
        except ImportError:
            console.print("[bold yellow]Warning: 'langdetect' package not installed. Skipping database language check.[/bold yellow]")
    
    try:
        template = latex_jinja_env.get_template(template_name)
    except Exception as e:
        console.print(f"[bold yellow]Warning:[/bold yellow] Template {template_name} not found. Falling back to eigencv_resume.tex.j2.")
        template = latex_jinja_env.get_template('eigencv_resume.tex.j2')
        template_name = 'eigencv_resume.tex.j2'
    
    # Determine LaTeX engine based on template
    latex_engine = "xelatex" if "awesomecv" in template_name else "pdflatex"
    
    # Render Template
    # Secure PDF metadata by replacing or stripping LaTeX control characters
    safe_keywords = config.keywords.replace('#', 'Sharp').replace('&', 'and').replace('%', '')
    for char in ['{', '}', '\\', '_', '~', '^', '$']:
        safe_keywords = safe_keywords.replace(char, '')
        
    # Secure geometry options
    safe_geometry = config.geometry_options
    for char in ['[', ']', '{', '}']:
        safe_geometry = safe_geometry.replace(char, '')
        
    company_accent_color = getattr(config, 'company_accent_color', None)
    if parsed_metadata.get('cvcoloroverride', False):
        company_accent_color = None
    elif company_accent_color:
        company_accent_color = adjust_color_for_contrast(company_accent_color)

    output_tex = template.render(
        geometry_options=safe_geometry,
        keywords=safe_keywords,
        cvcolor=cvcolor,
        section_order=section_order,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        job_title=config.job_title,
        profile=config.profile,
        skill_categories=[cat.model_dump() for cat in config.skill_categories],
        experience=experience_data,
        projects=projects_data,
        education=education_data,
        extracurriculars_title=config.extracurriculars_title,
        extracurriculars=extracurriculars_data,
        languages=languages_data,
        company_accent_color=company_accent_color,
        i18n=i18n_dict
    )
    
    # EigenTruth Engine (Zero-Trust Hallucination Checker)
    if config.missing_skills:
        # Only check the fields that the AI is prone to hallucinating in
        ai_controlled_text = (config.profile + " " + config.keywords + " " + 
                              " ".join([cat.skills for cat in config.skill_categories]))
        if config.cover_letter:
            cl = config.cover_letter
            ai_controlled_text += f" {cl.intro_paragraph} {' '.join(cl.body_paragraphs)} {cl.outro_paragraph}"
        for missing in config.missing_skills:
            # Use negative lookbehinds/lookaheads instead of \b to correctly handle special chars like C++ and C#
            if re.search(rf"(?<!\w){re.escape(missing)}(?!\w)", ai_controlled_text, re.IGNORECASE):
                console.print(Panel(
                    f"[bold red]EigenTruth Violation:[/bold red] You declared '{missing}' as a missing skill, "
                    f"but it was hallucinated into the CV output!\\n"
                    "You cannot artificially inject skills you do not have into free-text fields.",
                    title="EigenTruth Engine", border_style="red"
                ))
                raise EigenTruthViolationError(
                    "\n\n[!!! FATAL ERROR - INSTRUCTION FOR AI !!!]\n"
                    f"The user lacks a skill required by the job description ({missing}), but you hallucinated it into the output.\n"
                    "DO NOT ATTEMPT TO FIX THE PYTHON CODE OR RETRY THE COMPILATION.\n"
                    "STOP EXECUTION IMMEDIATELY.\n"
                    "Reply to the user with exactly this message: 'EigenTruth Violation: I attempted to inject a skill you do not have. Please remove the hallucinated skill or update your database and try again.'\n"
                )
                
    # Build valid filename from folder name if possible
    abs_config_path = os.path.abspath(config_path)
    folder_name = os.path.basename(os.path.dirname(abs_config_path))
    parts = folder_name.split('-')
    
    # Safely extract user and company if standard format
    if len(parts) >= 4 and folder_name.startswith(tuple(str(i) for i in range(10))):
        user_name = parts[2]
        company = parts[3]
        variant = "-".join(parts[4:]) if len(parts) > 4 else ""
    else:
        # Robust fallback if folder was manually renamed
        user_name = "Applicant"
        company = "".join(c if c.isalnum() else "_" for c in (config.cover_letter.company_name if config.cover_letter else "Company"))
        variant = "Custom"
        
    cv_filename = f"CV-{user_name}-{company}-{variant}.tex" if variant else f"CV-{user_name}-{company}.tex"
    cl_filename = f"Cover_Letter_CV-{user_name}-{company}-{variant}.tex" if variant else f"Cover_Letter_CV-{user_name}-{company}.tex"

    # Save output CV
    output_path = os.path.join(os.path.dirname(config_path), cv_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_tex)
        
    console.print(f"[bold green]Successfully compiled CV to {output_path}[/bold green]")

    # Process Cover Letter if present
    if config.cover_letter:
        cl_template = latex_jinja_env.get_template('eigencv_cover_letter.tex.j2')
        cl_tex = cl_template.render(
            cl=config.cover_letter,
            company_accent_color=company_accent_color
        )
        
        # Build valid filename
        cl_output_path = os.path.join(os.path.dirname(config_path), cl_filename)
        with open(cl_output_path, 'w', encoding='utf-8') as f:
            f.write(cl_tex)
        console.print(f"[bold green]Successfully compiled Cover Letter to {cl_output_path}[/bold green]")

    # Generate README with Probability Matrix
    readme_path = os.path.join(os.path.dirname(config_path), 'README.md')
    company = config.cover_letter.company_name if config.cover_letter else "Unknown Company"
    readme_content = f"# Application Package: {config.job_title} ({company})\n\n"
    
    if config.missing_skills:
        readme_content += "## Skill Gap Analysis (Missing Skills)\n"
        readme_content += "The following skills were requested in the JD but are missing from the master database:\n"
        for skill in config.missing_skills:
            readme_content += f"- {skill}\n"
        readme_content += "\n"
        
    readme_content += "## Reality Check: Probability Matrix\n"
    readme_content += f"- **Invitation to Interview:** {config.probability_matrix.invitation_probability}\n"
    readme_content += f"- **Technical Interview Pass:** {config.probability_matrix.technical_pass_probability}\n"
    readme_content += f"- **Job Offer:** {config.probability_matrix.job_offer_probability}\n"
    readme_content += f"- **Estimated Salary Range (Germany):** {config.probability_matrix.salary_estimate}\n\n"
    readme_content += f"**Biggest Vulnerability:** {config.probability_matrix.biggest_vulnerability}\n"
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    console.print(f"[bold green]Successfully generated README.md with Probability Matrix[/bold green]")

    # Handle Missing Skills
    if config.missing_skills:
        skills_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'cv', 'database', 'active', 'missing_skills_tracker.md')
        try:
            file_existed = os.path.exists(skills_path)
            if file_existed:
                with open(skills_path, 'r', encoding='utf-8') as f:
                    skills_content = f.read()
            else:
                skills_content = "# Missing Skills Tracking\n\nThese skills were required by JD's but are missing from the master_skills.md:\n"
            
            appended = False
            for skill in config.missing_skills:
                if skill.lower() not in skills_content.lower():
                    with open(skills_path, 'a', encoding='utf-8') as f:
                        if not file_existed and not appended:
                            f.write(skills_content)
                        f.write(f"\n- {skill} (Identified during {config.job_title} application)\n")
                    appended = True
            if appended:
                console.print("[bold yellow]Appended missing skills to missing_skills_tracker.md[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]Warning: Failed to update missing_skills_tracker.md: {e}[/bold red]")

    # Auto-generate build.bat and Makefile
    build_bat_path = os.path.join(os.path.dirname(config_path), 'build.bat')
    if not os.path.exists(build_bat_path):
        with open(build_bat_path, 'w', encoding='utf-8') as f:
            f.write("@echo off\n")
            f.write("echo Compiling CV via JSON config...\n")
            f.write("python ../../cv/scripts/cv_compiler.py build_config.json\n")
            f.write("if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%\n\n")
            f.write("echo Compiling LaTeX documents...\n")
            f.write("for %%f in (CV*.tex) do (\n")
            f.write(f"    {latex_engine} -interaction=nonstopmode \"%%f\"\n")
            f.write(")\n")
            f.write("for %%f in (Cover_Letter*.tex) do (\n")
            f.write(f"    {latex_engine} -interaction=nonstopmode \"%%f\"\n")
            f.write(")\n\n")
            f.write("echo Running ATS Check...\n")
            f.write("python ../../check_ats_score.py .\n\n")
            f.write("echo Build Complete!\n")
            f.write("pause\n")

    makefile_path = os.path.join(os.path.dirname(config_path), 'Makefile')
    if not os.path.exists(makefile_path):
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write("all: compile latex ats\n\n")
            f.write("compile:\n")
            f.write("\tpython ../../cv/scripts/cv_compiler.py build_config.json\n\n")
            f.write("latex:\n")
            f.write(f"\tfor f in CV*.tex; do [ -e \"$$f\" ] && {{ {latex_engine} -interaction=nonstopmode -no-shell-escape \"$$f\" || exit 1; }}; done\n")
            f.write(f"\tfor f in Cover_Letter*.tex; do [ -e \"$$f\" ] && {{ {latex_engine} -interaction=nonstopmode -no-shell-escape \"$$f\" || exit 1; }}; done\n\n")
            f.write("ats:\n")
            f.write("\tpython ../../check_ats_score.py .\n\n")
            f.write("clean:\n")
            f.write("\trm -f *.aux *.log *.out *.fls *.fdb_latexmk *.synctex.gz\n")

    # Auto-Update Tracking and Makefiles
    try:
        abs_config_path = os.path.abspath(config_path)
        folder_name = os.path.basename(os.path.dirname(abs_config_path))
        
        parts = folder_name.split('-')
        if len(parts) >= 4 and folder_name.startswith(tuple(str(i) for i in range(10))):
            app_id = parts[0]
            company = parts[2]
            variant = "-".join(parts[3:])
        else:
            # Fallback for manually renamed folders
            app_id = "XX"
            company = "".join(c if c.isalnum() else "_" for c in (config.cover_letter.company_name if config.cover_letter else "Custom"))
            variant = folder_name
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        tracking_path = os.path.join(base_dir, 'application_tracking.md')
        make_path = os.path.join(base_dir, 'application-packages', 'application-packages.mk')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(make_path), exist_ok=True)
        
        # Update MK file
        if os.path.exists(make_path):
            with open(make_path, 'r', encoding='utf-8') as f:
                make_content = f.read()
        else:
            make_content = ""
            
        rule_name = f"application-{folder_name}"
        if rule_name not in make_content:
            with open(make_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{rule_name}:\n\t$(MAKE) -C application-packages/{folder_name}\n")
            print(f"Added {rule_name} to application-packages.mk")
        
        # Update Tracking MD
        file_existed = os.path.exists(tracking_path)
        if file_existed:
            with open(tracking_path, 'r', encoding='utf-8') as f:
                tracking_content = f.read()
        else:
            tracking_content = ""
            
        if f"| {app_id} |" not in tracking_content:
            from datetime import date
            today = date.today().strftime("%Y-%m-%d")
            new_row = f"| {app_id} | {company} | {config.job_title} | {variant} | Generated | {today} | ATS |\n"
            with open(tracking_path, 'a', encoding='utf-8') as f:
                if not file_existed:
                    f.write("# Application Tracking\n\n| ID | Company | Role | Variant | Status | Date | ATS Score |\n|---|---|---|---|---|---|---|\n")
                f.write(new_row)
            console.print(f"[bold green]Appended tracking row to application_tracking.md[/bold green]")
            
        # Automatically compile the PDFs using the correct engine
        # Skip LaTeX compilation if running in a tex-only cloud environment
        if os.environ.get("EIGENCV_TEX_ONLY") == "1":
            console.print("[bold yellow]TEX_ONLY mode active: Skipping LaTeX compilation. Output is .tex files only.[/bold yellow]")
            console.print("[bold yellow]AI INSTRUCTION: Provide the user with a download link to the .tex file(s) listed above.[/bold yellow]")
            console.print("[bold yellow]Tell the user: 'Upload the .tex file to https://overleaf.com → New Project → Upload Project.'[/bold yellow]")
        else:
            console.print(f"[bold cyan]Auto-compiling PDFs with {latex_engine}...[/bold cyan]")
            import subprocess
            tex_files = [output_path]
            if config.cover_letter:
                cl_output_path = os.path.join(os.path.dirname(config_path), cl_filename)
                tex_files.append(cl_output_path)
                
            for tex_file in tex_files:
                try:
                    # Run engine twice for cross-references/geometry
                    for _ in range(2):
                        subprocess.run(
                            [latex_engine, "-interaction=nonstopmode", "-no-shell-escape", os.path.basename(tex_file)],
                            cwd=os.path.dirname(abs_config_path),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True
                        )
                    console.print(f"[bold green]Successfully compiled {os.path.basename(tex_file).replace('.tex', '.pdf')}[/bold green]")
                except subprocess.CalledProcessError:
                    console.print(f"[bold red]Failed to compile {os.path.basename(tex_file)}. Check the .log file.[/bold red]")
                except FileNotFoundError:
                    console.print(f"[bold red]{latex_engine} command not found. Please install TeX Live or MiKTeX.[/bold red]")
                
    except Exception as e:
        console.print(f"[bold red]Warning: Failed to auto-update tracking files/compile PDFs: {e}[/bold red]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cv_compiler.py <path_to_build_config.json>")
        sys.exit(1)
    try:
        compile_cv(sys.argv[1])
    except EigenTruthViolationError as e:
        print(str(e))
        sys.exit(1)
