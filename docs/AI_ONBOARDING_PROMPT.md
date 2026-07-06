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

### 🚫 ZERO-TRUST & ZERO-HALLUCINATION POLICY (STRICT)
1. **NO ON-THE-FLY TRANSLATION:** You are strictly forbidden from automatically translating content to fill gaps. If a bullet or project only exists in English in the source PDFs, it must ONLY exist in English in the database. 
2. **NATIVE MIGRATION ONLY:** You may only extract and migrate authentic, native strings from the provided text. Never hallucinate data.

### 🛡️ VARIANT PRESERVATION RULE (NO DEDUPLICATION)
When merging new experience bullets into `experience.json`, you MUST NOT aggressively deduplicate stylistic or target-audience specific variations of the same task. 
- If the user provides multiple variations of a bullet (e.g., a Management-focused version and a Deep-Tech-focused version of the same project), you must SAVE ALL VARIANTS as distinct, related IDs. This gives the CV Compiler maximum flexibility.
- **Naming Rule:** You MUST name their IDs to reflect this relationship (e.g., `tech_corp_etl_base` and `tech_corp_etl_cloud`). This signals to the generation phase that they are mutually exclusive variants.

### 🌐 SYMMETRIC LOCALE i18n (DATABASE MAPPING)
If data is provided from CVs in different languages (e.g. a German and an English CV):
- The database JSON files (`experience.json`, `projects.json`, `education.json`, etc.) MUST remain **FLAT dictionaries** mapping an ID directly to a single string containing LaTeX-formatted text. Do NOT use nested objects like `{"en-US": "..."}` as they will break the Jinja compiler.
- Instead, for authentic native translations (e.g., you extracted both an English and a German version of a task from the PDFs), save the English string under the base ID (e.g., `bullet_id`), and save the exact native German string under the same ID with a `_de` suffix (e.g., `bullet_id_de`).
- **Remember:** Do NOT generate `_de` IDs if the German text does not natively exist in the source material!

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
Extract the user's name, current position/title, email, phone number, LinkedIn URL, GitHub URL, and website. Overwrite the existing LaTeX macros in this file.
**CRITICAL:** You MUST preserve the `\cvtemplate`, `\cvcolor`, and `\cvorder` macros exactly as you found them.

## Phase 2: Build the Experience Database
Edit `cv/database/active/experience.json`.
1. Break down the user's work history into distinct companies/roles.
2. For each company, create a top-level key (e.g., `"google"`, `"bmw"`).
3. Populate `"company"`, `"location"`, and `"dates"`. (Use `_de` keys if German equivalents exist).
4. **The Bullet System (Crucial):** Do NOT write a single block of text for the experience. You must split their achievements into granular, highly modular bullet points. 
5. Assign a unique, descriptive ID to each bullet point. Add `_de` IDs only for authentic German translations found in the source.
6. Ensure all text inside the bullets is formatted for LaTeX (escape `%` as `\%`). Use `\textbf{}` for emphasis.

## Phase 3: Build the Projects, Education, and Extracurriculars Databases
Edit `projects.json`, `education.json`, `languages.json`, `extracurriculars.json`.
1. **CRITICAL GLOBAL URL INJECTION & CHECK:** Wrap URLs dynamically using LaTeX: `\href{<URL>}{<Visible Text>}`.
2. **Proactive Fallback:** If the user mentions projects, theses, or publications but provides no URLs, you MUST proactively ask the user before finishing: *"Do you have any GitHub, portfolio, or publication URLs for these entries? Standard PDF extraction often loses them..."*
3. **Publication Formatting Rule:** DO NOT use job-title prefixes like `\textbf{Published Author:}`. Format it as a clean academic citation.

## Phase 4: Construct the Master Skills Pool
Edit `cv/database/active/master_skills.md`.
Extract every single tool, language, methodology, and framework the user knows.
1. **Comma-Separated Categories (Top):** Create headers like `## Programming` and list the relevant skills as simple comma-separated strings below them.
2. **Self-Assessed Skill Ratings Table (Bottom):** Create a section named EXACTLY `## Self-Assessed Skill Ratings` followed by a Markdown table.
   - Use `(A | B)` for exact synonyms where the AI must pick ONE.
   - Use `[A, B]` for clusters where the AI can pick multiple.

## Phase 5: Initialize the Personal Dossier
**CRITICAL RULE:** You are strictly FORBIDDEN from editing or overwriting `cv/database/active/personal_dossier.md` during automated onboarding. Do not touch this file!

## Phase 6: Verification & Handoff
1. **Coverage Audit (CRITICAL):** Verify that *every single bullet point, project, and extracurricular activity* can be mapped to an ID in your JSON database. Did you miss specialized variants? Add them! Did you invent translations? Remove them!
2. Ensure all JSON files contain valid JSON (no trailing commas).
3. Confirm with the user that the Onboarding is complete. 
4. **CRITICAL:** Tell the user: "Onboarding is complete. You can now simply paste a Job Description into this chat..."
