# AI GENERATION PROMPT: Onboarding a New User

> [!CAUTION]
> **READ THIS ENTIRE FILE BEFORE STARTING.** Do not skim. Do not create an "Implementation Plan." You must execute the onboarding directly. Pay STRICT attention to the "CRITICAL EXCEPTION" rules below (especially regarding mutually exclusive variants and forbidden files). Failure to do so will break the user's database.
You are an AI assistant tasked with onboarding a NEW USER into the EigenCV framework. 
The user will provide you with their existing raw CV data (e.g., a text dump of their old CV, a LinkedIn export, or a list of achievements). 

Your objective is to extract their data and translate it into the strictly defined JSON/Markdown architecture of this repository.

### 🔄 DUAL-MODE ONBOARDING
Before you write any files, you MUST check the existing `cv/database/active/metadata.tex`.
- **Mode 1 (Bootstrap):** If the database contains the "Jane Doe" placeholder, you will OVERWRITE the entire database with the new user's data.
- **Mode 2 (Incremental Merge):** If the database already belongs to the user, you must append and merge the new data. 
- **Semantic Deduplication Rule:** When merging new experience bullets into `experience.json`, you MUST compare them against existing bullets. If a new bullet describes the exact same task/project as an existing bullet, do NOT create a redundant ID. Instead, compare their strength. Keep the formulation with the strongest quantifiable metrics and action verbs, and discard the weaker one.
- **CRITICAL EXCEPTION (Mutually Exclusive Variants):** Do NOT deduplicate bullets that cover distinct technical domains or contain unique, specialized keywords (e.g., "EUV physics" vs "ETL pipelines"), even if they occurred in the same role. They must be saved as separate bullet IDs so the pipeline can tailor CVs to highly specific niches. 
- **Naming Rule:** If two bullets describe the same underlying project/task but with different technical focuses, you MUST name their IDs to reflect this relationship (e.g., `tech_corp_etl_base` and `tech_corp_etl_cloud`). This signals to the generation phase that they are mutually exclusive variants.

### 🛑 CRITICAL SAFETY DIRECTIVE: DO NOT BREAK THE ENGINE
You are updating the **Content Database**, NOT the engine. 
You are strictly FORBIDDEN from editing or overwriting any of the following files:
- `cv/template/eigencv_resume.tex.j2`
- `cv/template/eigencv_cover_letter.tex.j2`
- `cv/template/header.tex`
- `cv/template/preamble.tex`
- `cv/scripts/cv_compiler.py`
- `cv/scripts/cv_schema.py`
- `check_ats_score.py`
- `tools/new_app.py`

## Phase 1: Update Personal Metadata
Edit `cv/database/active/metadata.tex`.
Extract the user's name, current position/title, email, phone number, LinkedIn URL, GitHub URL, and website. Overwrite the existing LaTeX macros in this file. Do NOT change the macro names (e.g., keep `\newcommand{\cvname}{...}`, `\newcommand{\cvposition}{...}`).
**CRITICAL:** You MUST preserve the `\cvtemplate`, `\cvcolor`, and `\cvorder` macros exactly as you found them, so the user's preferred template layout, colors, and section sorting are not destroyed during onboarding.

## Phase 2: Build the Experience Database
Edit `cv/database/active/experience.json`.
1. Break down the user's work history into distinct companies/roles.
2. For each company, create a top-level key (e.g., `"google"`, `"bmw"`).
3. Populate `"company"`, `"location"`, and `"dates"`.
4. **The Bullet System (Crucial):** Do NOT write a single block of text for the experience. You must split their achievements into granular, highly modular bullet points. 
5. Assign a unique, descriptive ID to each bullet point (e.g., `"cloud_migration"`, `"team_leadership"`, `"api_development"`).
6. Ensure all text inside the bullets is formatted for LaTeX (e.g., escape `%` as `\%` and use `\textbf{}` for emphasis on key metrics/tools).

*Example Structure:*
```json
{
  "company_id": {
    "company": "Company Name",
    "location": "City, Country",
    "dates": "Month Year -- Month Year",
    "bullets": {
      "bullet_id_1": "Developed \\textbf{scalable APIs} using Python, increasing throughput by 20\\%.",
      "bullet_id_2": "Led a team of 5 engineers..."
    }
  }
}
```

## Phase 3: Build the Projects, Education, and Extracurriculars Databases
Edit the following files, replacing the existing content with the new user's data while maintaining the exact JSON schema:
**CRITICAL:** These files are FLAT dictionaries mapping an ID directly to a SINGLE string containing LaTeX-formatted text. Do NOT use nested objects.
1. **`cv/database/active/projects.json`**: Extract major projects. Assign a unique ID and write a single bullet string (e.g., `"proj_1": "\\textbf{Project Name:} Built X using Y."`).
   - **Preserve Hyperlinks:** If the source document contains URLs (e.g., GitHub, live apps), you MUST preserve them using the LaTeX macro `\href{URL}{Link Text}` (e.g., `... \href{https://github.com/user/repo}{[GitHub]}`).
2. **`cv/database/active/education.json`**: Extract degrees. Assign IDs like `"msc"`. Write a single string (e.g., `"msc": "\\textbf{MSc in X}, University \\hfill \\textit{2020 - 2022}"`).
3. **`cv/database/active/languages.json`**: Extract languages and proficiencies. Assign IDs like `"english"` and write a single string (e.g., `"english": "English (Fluent)"`).
4. **`cv/database/active/extracurriculars.json`**: Extract volunteering, hobbies, speaking engagements, publications, or awards. Assign IDs and format as a single string similarly to projects. 
   - **Publication Formatting Rule:** If extracting a publication, DO NOT use job-title prefixes like `\textbf{Published Author:}` or `\textbf{Writer:}`. Format it as a clean academic citation (e.g., `\textbf{Springer Publication:} Co-authored \textit{"Paper Title"} in Conference/Journal (Year).`).
   - **Preserve Hyperlinks:** Use `\href{URL}{Link Text}` for DOI links or publication URLs.

## Phase 4: Construct the Master Skills Pool
Edit `cv/database/active/master_skills.md`.
Extract every single tool, language, methodology, and framework the user knows.
You MUST format this file with TWO distinct sections so both the ATS parser and the AI generator can read it:

1. **Comma-Separated Categories (Top):** Create headers like `## Programming` or `## Machine Learning` and list the relevant skills as simple comma-separated strings below them. This section is required for the ATS parsing script.
2. **Self-Assessed Skill Ratings Table (Bottom):** Create a section named EXACTLY `## Self-Assessed Skill Ratings` followed by a Markdown table with the following columns:
   (a). **Skill Name:** The exact ATS-friendly name.
   (b). **Category:** E.g., Programming, Cloud, Machine Learning.
   (c). **Rating:** The user's self-assessed proficiency (0 % - 100 %).
   (d). **Synonyms/Variants:** Note any alternative names or groupings. 
      - Use `(A | B)` for exact synonyms where the AI must pick ONE (e.g., `(React | React.js)`).
      - Use `[A, B]` for clusters where the AI can pick multiple (e.g., `[AWS, Azure]`).

## Phase 5: Initialize the Personal Dossier
**CRITICAL RULE:** You are strictly FORBIDDEN from editing or overwriting `cv/database/active/personal_dossier.md` during the automated onboarding. 
The user manually maintains their soft skills, work philosophy, and hobbies in this file. A standard CV is too dry to capture genuine culture, and attempting to auto-generate this results in sterile, hallucinated corporate speak. Do not touch this file!

## Phase 6: Verification & Handoff
1. **Coverage Audit (CRITICAL):** Before finalizing, perform a reverse-lookup. Read the source CVs/data again and systematically verify that *every single bullet point, project, and extracurricular activity* can be mapped to an ID in your JSON database. If you missed specialized variants, go back and add them!
2. Ensure all JSON files contain valid JSON (no trailing commas).
3. Ensure all LaTeX special characters (`&`, `%`, `$`, `#`, `_`) inside the JSON string values are properly escaped (e.g., `\&`, `\%`).
3. Confirm with the user that the Onboarding is complete. 
4. **CRITICAL:** Do NOT tell the user to run terminal commands (like `python tools/new_app.py`). This is an Agentic workflow! Tell the user: "Onboarding is complete. You can now simply paste a Job Description into this chat, and I will automatically initialize the workspace, generate the tailored CV, and compile the PDF for you."
