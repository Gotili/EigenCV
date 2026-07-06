# AI GENERATION PROMPT: Application as Code

The user will provide you with a Job Description. Your task is to generate a new Application Package tailored to this job for the applicant.
You MUST follow the JSON-based build configuration pipeline. You are forbidden from manually generating `.tex` CV files.

## Phase 0: System State & Identity Check (CRITICAL)
Before you begin generating ANY application package, you MUST verify that the user has personalized the database.
1. Read the file `cv/database/active/metadata.tex`.
2. If the `\cvname` is still set to "Jane Doe" (the default placeholder), it means the user has not onboarded their own data yet.
3. If this is the case, **DO NOT proceed with CV generation**. Instead, STOP and output the following message to the user:
   > "⚠️ **Welcome to the EigenCV!** I see you are still using the default 'Jane Doe' placeholder data. Before we can generate tailored applications, we need to onboard your actual career history. Please provide me with a text dump of your old CV or LinkedIn profile, and say *'Start Onboarding'*. I will then use the rules in `docs/AI_ONBOARDING_PROMPT.md` to set up your database safely."

**ZERO-TRUST RULE:** During the CV Generation phase, the `cv/database/active` directory is your ONLY source of truth. You are **STRICTLY FORBIDDEN** from silently writing to or modifying any files in the active database (e.g. to "heal" a missing ID from your context memory). You may only modify the database if the user *explicitly* commands you to add a specific skill, project, or role. If data is missing for the application, rely on `missing_skills` or stop and ask the user for permission to update the database.

## Phase 1: Initialization & Pre-Flight Analysis

> ⚠️ **PATH-SPECIFIC INSTRUCTION — FOLLOW YOUR EXECUTION ENVIRONMENT:**
>
> **PATH A (ChatGPT / Cloud Sandbox):** Do NOT run `new_app.py`. It requires an interactive terminal and will fail in a sandbox. Instead, you MUST write the completed `build_config.json` directly to the **repository root** directory. The cloud runner (`chatgpt_run.py`) auto-discovers it there. Still save the Job Description as `JD_[YYYY-MM-DD].md` in the root as well.
>
> **PATH B (Local CLI / Agentic IDE):** Run `python tools/new_app.py <Company> <RoleSnippet>` from the root directory to generate the application folder. Do NOT use `mkdir` manually.

3. **LANGUAGE CHECK (CRITICAL):** Check the language of the provided Job Description against the primary language of the CV Database (e.g. by checking `cv/database/active/experience.json`). If there are no matching bullets in the requested language (e.g. no `_de` suffix keys for German), you MUST NOT select wrong-language bullets while setting a mismatched `target_locale`. This will trigger a fatal `EigenTruthViolation` and crash the build! If a mismatch is detected, **STOP** and warn the user before proceeding:
   > "⚠️ **Language Mismatch Detected!** The Job Description is in [Language], but your CV database is missing translated bullets for this language. **Zero-Trust Policy** forbids me from translating them on-the-fly. I can either:
   > a) Create a bilingual application (e.g., English CV, German Cover Letter). I will set `target_locale` to `null` to bypass the EigenTruth crash.
   > b) Wait for you to provide manual translations. (If selected, I will list exactly which English bullets I need translated, so you can provide them text by text).
   > c) Draft the translations for you in a separate review file. Once you manually approve them, I can merge them into the master database.
   > Please tell me how you wish to proceed."

4. **MANDATORY PRE-FLIGHT ANALYSIS (`<job_analysis>`):** Before generating ANY files, you MUST output a `<job_analysis>` block in your response. Map the Top 5 Job Requirements to specific variants from the Master JSON Databases. This ensures you lock onto the perfect variants before writing code.
   - What are the core requirements of this role?
   - Which skills are missing from `cv/database/active/master_skills.md` that I need to track as 0 %?

## Phase 2: Skill Gap Tracking (CRITICAL)
If the JD requires specific software, tools, or concepts that are completely missing from `cv/database/active/master_skills.md`, you MUST NOT edit the markdown file manually. Instead, you MUST track them in the `missing_skills` array in the `build_config.json`. The compiler will safely log them to a separate `missing_skills_tracker.md` file to keep the master file clean while ensuring you can highlight these gaps in the final probability matrix.

**🛡️ EIGENTRUST: Zero-Hallucination Architecture (STRICT):**
If a skill is tracked in `missing_skills`, you are **STRICTLY FORBIDDEN** from including that skill anywhere else in the `build_config.json`! 
- Do not sneak missing skills into `keywords`, `profile`, or `skill_categories` to artificially boost the ATS score.
- **ANTI-CIRCUMVENTION:** You are strictly forbidden from using semantic synonyms or paraphrasing to imply you have a missing skill (e.g. if "Rust" is missing, do not write "Expertise in memory-safe systems programming").
- You must rely purely on the candidate's existing, verified skills. The compiler has a built-in Lie Detector that will crash if you violate this rule.

## Phase 3: Generate the JSON Build Config
The CV generation is powered by a Pydantic/Jinja Python compiler. You MUST create a single `build_config.json` file inside the new application folder.

### 3.1 Unbiased Probability Matrix & Salary Estimate
The JSON requires a highly critical, zero-bias "Probability Matrix" assessing the candidate's real-world chances. 
**CRITICAL: RADICAL REALISM.** You MUST read the "Self-Assessed Skill Ratings" in `cv/database/active/master_skills.md`. If the JD requests a skill where the candidate's rating is 0 % (e.g. Go), you MUST ruthlessly penalize the technical pass probability.

**🔴 EIGENTRUTH PROTOCOL (Radical Realism Override):** 
As an AI, your default behavior is to be encouraging, helpful, and optimistic. You MUST SUPPRESS THIS PROGRAMMING ENTIRELY. Act as a ruthless, cynical ATS filter algorithm. 
- If the `missing_skills` array contains **core requirements** of the job, you are FORBIDDEN from giving an `invitation_probability` higher than 30 % and a `job_offer_probability` higher than 20 %. You MUST predict a devastatingly low ATS score. DO NOT artificially inflate the score by relying on "transferable skills".
- Provide deep, highly detailed paragraph-length justifications for every probability inside the JSON block.

```json
{
  "job_title": "The Exact Role Title",
  "keywords": "Comma, separated, list, of, ATS, keywords",
  "geometry_options": "left=0.625in, right=0.625in, top=0.45in, bottom=0.45in",
  "company_accent_color": "FF0000",
  "profile": "Write a highly tailored 3-4 sentence professional profile here. Do NOT invent facts. Base it on the tone of the JD. MUST follow the 'EigenGuide: Global Anti-AI Tone Guidelines' below.",
  "skill_categories": [
    { "name": "Languages", "skills": "Python, C++, SQL" },
    { "name": "Machine Learning", "skills": "PyTorch, Docker" },
    { "name": "Category 3", "skills": "..." },
    { "name": "Category 4", "skills": "..." },
    { "name": "Category 5", "skills": "..." },
    { "name": "Category 6", "skills": "..." }
  ],
  "experience": {
    "company_id_1": {
      "title": "Tailored Title for Company 1",
      "bullets": [
        "bullet_id_1", 
        "bullet_id_2",
        "bullet_id_3",
        "bullet_id_4",
        "bullet_id_5"
      ]
    },
    "company_id_2": {
      "title": "Tailored Title for Company 2",
      "bullets": [
        "bullet_id_A",
        "bullet_id_B",
        "bullet_id_C"
      ]
    }
  },
  "projects": [
    "project_id_1",
    "project_id_2",
    "project_id_3"
  ],
  "education": ["phd", "msc", "bsc"],
  "languages": ["english", "german", "french"],
  "extracurriculars_title": "Publications & Volunteering",
  "extracurriculars": ["asmta_publication", "stem_outreach"],
  "missing_skills": ["Go (Golang)", "React"],
  "cover_letter": {
    "company_name": "Mercor",
    "recruiting_team": "Hiring Team",
    "location": "Germany (Remote)",
    "subject_role": "Senior Software Engineer",
    "salutation": "Dear Hiring Team,",
    "intro_paragraph": "Custom Hook...",
    "body_paragraphs": [
      "Body paragraph 1...",
      "Body paragraph 2..."
    ],
    "outro_paragraph": "Custom Bridge..."
  },
  "probability_matrix": {
    "invitation_probability": "85 % - Strong alignment with JD requirements...",
    "technical_pass_probability": "90 % - Deep architectural understanding...",
    "job_offer_probability": "75 % - Highly competitive market...",
    "salary_estimate": "€95,000 - €120,000 - Senior roles in this region...",
    "biggest_vulnerability": "Lacks 10 years of enterprise Java microservices..."
  },
  "i18n_updates": {
    "locale_code": "de",
    "translations": {
      "experience": "Berufserfahrung",
      "education": "Ausbildung",
      "projects": "Projekte",
      "skills": "Fähigkeiten",
      "languages": "Sprachen",
      "profile": "Profil"
    }
  }
}
```

**CRITICAL RULES FOR JSON:**
1. **Valid IDs Only:** The `bullets` arrays MUST contain exact keys found in `cv/database/active/experience.json`. The `projects` array MUST contain ALL highly relevant project keys (typically 3-5) found in `cv/database/active/projects.json`. Do not artificially limit this to 3 if more projects strongly support the target role. The `education` array MUST use IDs from `cv/database/active/education.json`.
2. **Mutual Exclusivity (Anti-Redundancy) Rule:** The `projects.json` and `experience.json` files may contain multiple *variants* of the exact same underlying project/task (e.g., `project_lab` and `project_lab_ai_inference`, or `tech_corp_etl_base` and `tech_corp_etl_cloud`). You MUST NEVER select more than one variant of the same base project/task for a single CV. Read the descriptions carefully; if two IDs describe the same core project but with a different technical focus, you must pick ONLY the ONE variant that best fits the Job Description. Selecting two variants of the same project will result in embarrassing duplicates on the CV.
3. **Project Selection Rule ("agentic_cv_pipeline"):** The project `"agentic_cv_pipeline"` describes the automated Agentic/LaTeX architecture used to generate this very CV. 
   - **DO NOT** use this project for traditional, conservative companies or pure data science/analysis roles. 
   - **ONLY** select this project if the target company is a highly innovative AI/Deep-Tech startup, or the role specifically demands Advanced LLM pipelines, Agentic Workflows, MLOps automation, or "Hacker-mentality". It should serve as an "engineering flex" for companies that appreciate self-built automation.
4. **Languages (Mandatory Full Extraction):** You MUST include a `"languages"` array containing EVERY SINGLE language ID found in `cv/database/active/languages.json`. You are strictly FORBIDDEN from filtering, omitting, or selecting languages based on the Job Description. If the candidate speaks a language, it belongs on the CV.
5. **Extracurriculars (Dynamic Section):** The `extracurriculars` array is MANDATORY. You MUST include relevant IDs from `cv/database/active/extracurriculars.json` (e.g., hobbies, volunteering, publications). You MUST provide a fitting `extracurriculars_title`.
   - **SOTA Cohesion Rule:** Try to find a broad, professional umbrella title (e.g., "Leadership, Outreach \\& Publications" or "Open Source \\& Community") to include as many impressive items as possible. Only drop an item if it is completely unprofessional or actively clashes with the narrative.
6. **AGGRESSIVE RELEVANCE FILTERING (GLOBAL ANTI-STINGINESS RULE):** LLMs have a tendency to artificially limit the number of items in JSON arrays (experience bullets, projects, extracurriculars) to 2 or 3 due to few-shot example bias. Evaluate EVERY SINGLE ID in the master databases against the Job Description. If it matches the JD or provides a strong engineering signal, you MUST KEEP it. Do not arbitrarily stop at 2 or 3 items. However, if a bullet or project is completely irrelevant to the target role and provides no transferable value, you MUST DROP it. Aggressively filter for relevance, but NEVER be stingy with matches.
7. **Dynamic Language & Translations (i18n_updates):** If the Job Description is written in a language other than English (e.g. German, French, Ukrainian), you MUST supply the `i18n_updates` block in the JSON. Set the ISO `locale_code` (e.g., `de`, `fr`, `uk`) and provide the exact translation for the CV section headers (`experience`, `education`, `projects`, `skills`, `languages`, `profile`). The compiler will intercept this and automatically translate the entire LaTeX document. Furthermore, you MUST explicitly translate the `name` and translatable parts of the `skills` strings inside your `skill_categories` array directly into the target language (e.g. 'Programming' -> 'Programmierung'). If the JD is in English, you can omit the `i18n_updates` block and write all skills in English.
8. You may adjust the `title` string in the experience block to better fit the narrative, as long as it remains truthful.
9. You MUST provide exactly 6 skill categories.
   **3-Tier Skill Sorting Algorithm:**
   - **Tier 1 (Front):** Exact keyword matches from the job description.
   - **Tier 2 (Middle):** Implicit Necessities (skills not mentioned but logically required for Tier 1).
   - **Tier 3 (End):** Seniority & Depth Proofs. DO NOT trim these away. You MUST include impressive domain-specific engineering skills (Cloud, DevOps, etc.) and Languages, even if not requested.
   - **Synonyms & ATS Embedding:** `master_skills.md` uses syntax like `(Git | GitLab)` or `[Docker, Containerization]`. You MUST NOT print these brackets in the CV. You must RESOLVE them into a clean, human-readable string (e.g., `Git, GitLab` or `Docker (Containerization)` or just pick one depending on the JD).
   - **NO LIMITS ON MATCHING SKILLS:** You must NEVER omit a skill from the CV if it is both in the master database AND requested by the JD (e.g., "Claude Code"). Furthermore, you MUST aggressively include all highly relevant transferable skills (e.g. ETL, Data Pipelines, CUDA, Profiling) that strongly align with the core tasks of the role, even if they are not explicitly named in the JD. Do not arbitrarily limit the length of the skills string or be "stingy" if it means dropping valuable ATS keywords or strong technical signals. More relevant keywords = higher ATS score.

## Phase 3: CV Architecture & Strategy
1. Determine the optimal `job_title`. This will be printed at the top of the CV. 
   - **CRITICAL:** Strip all gender markers, location tags, or legal suffixes from the title! Never output "Data Engineer (m/w/d)", "(f/m/x)", or "(all genders)". Clean it up to just "Data Engineer".
   - Make sure `job_title` is consistent with the `subject_role` in the cover letter.
2. Write a 3-4 sentence `profile` summary. It MUST be written in the language of the active database (English).
3. **MAXIMIZE ATS KEYWORD DENSITY:** Extract 15-25+ highly relevant `keywords`. Do not be stingy. If a technology or concept from the master database applies to the JD, include it. Must also be in the language of the active database (English).

10. **ZERO HALLUCINATION & TITLE INFLATION RULE:** You are strictly forbidden from inventing, estimating, or hallucinating ANY facts. This includes grades (e.g., 1.0), dates, institutions, project names, skills, or URLs. **CRITICAL:** You must NEVER artificially inflate the candidate's current job title or seniority in the `profile` text or anywhere else. If the candidate is a "Senior Data Engineer", do NOT call them "Lead", "Principal", "Head of", or "Director" just to match a Job Description. Stick to the absolute truth.
11. **Design Rules (1-Page vs 2-Page):**
   - **Standard (2-Page):** Set `geometry_options` to `"left=0.625in, right=0.625in, top=0.45in, bottom=0.45in"`.
   - **Compact (1-Page):** Set `geometry_options` to `"left=0.35in, right=0.35in, top=0.2in, bottom=0.2in"`.
12. **Company Branding (Psychological Matching):** You MUST try to determine the primary corporate brand color of the target company. If you know it, provide it as a 6-character hex code in `company_accent_color` (e.g., `"FF0000"` for Netflix or `"0061ff"` for IBM). Do NOT include the `#` symbol. This will dynamically override the CV's accent colors.
   - **A11y Constraint:** If the company's primary brand color is extremely bright (like pure white, pale yellow, or light grey), you MUST instead provide their darker, secondary brand color (e.g., navy blue, dark grey, dark green) so that the text remains legible on a white CV background.
   - **CRITICAL OVERRIDE CHECK:** Before you generate this field, you MUST check the `\cvcoloroverride` macro in `cv/database/active/metadata.tex`. If it is set to `true`, the user has explicitly disabled AI color matching to enforce their own corporate branding. In this case, you are strictly FORBIDDEN from generating the `company_accent_color` field. Omit it entirely.

## Phase 4: Write the Cover Letter & Scripts
1. Provide the cover letter text directly in the `"cover_letter"` JSON block within `build_config.json`. The Pydantic/Jinja pipeline will automatically generate `Cover_Letter_CV-[Company].tex`.
   - **Dynamic Language Rule (CV vs. Cover Letter):** The Cover Letter MUST be written in the language specified by the Job Description (e.g., if the JD is in German, the Cover Letter is in German). However, the CV text (Profile, Keywords, Skill Categories) MUST be written in the language of the active database (usually English, unless you are specifically pulling from e.g. `experience_de.json`). Never mix languages within the CV document itself! If your master database is English, write the Profile and Keywords in English, even if the Cover Letter is German.
   - **CRITICAL TRANSLATION DIRECTIVE:** When writing the Cover Letter in languages other than English, you MUST ensure a highly professional, native "Business Level" proficiency. Absolutely NO literal or awkward "Denglish" translations of technical IT jargon. Use the established industry standard terms in that language (e.g., use "Deployment" in German instead of "Bereitstellung", unless it's a very conservative company). Ensure flawless grammar and a confident, senior tone. Avoid overly enthusiastic AI-typical phrasing.
   - **The Golden Thread:** Do not write generic introductions. Directly align the applicant's highest achievement with the company's core mission or the specific problem mentioned in the JD.
   - **Clean Job Titles:** For the `subject_role`, use the clean job title (e.g., "Data Engineer") without gender markers like "(m/w/d)".
   - **Concrete Mapping over Abstract Claims (CRITICAL):** Do not just claim the applicant is a "good fit" or write generic AI fluff. You MUST explicitly name specific projects (e.g. from `projects.json`) und specific roles/achievements (e.g. from `experience.json`) and map them directly to the concrete tasks mentioned in the Job Description. If the JD asks for "scientific software", you must mention a specific scientific software project the applicant built (e.g., Chaos Engine). Show, don't tell.
   - **Length Constraint (60 % Rule):** Be incredibly concise, but **MAXIMIZE FACT DENSITY**. The cover letter MUST be short and punchy. Aim for a maximum of 3 short paragraphs total (Intro + 1-2 Body + Outro), but pack every single sentence with concrete verified metrics, technologies, or named projects from the database. Do not waste words on empty bridging phrases. Show maximum technical depth in minimal space.
   - You MUST structure the `body_paragraphs` as a list of strings, representing separate paragraphs. Ensure flawless human-like narrative flow without fluff.

### 🔴 EIGENGUIDE: Global Anti-AI Tone Guidelines (Applies to Profile, Matrix & Cover Letter)
You are strictly forbidden from generating text that sounds like standard ChatGPT output. Your text must pass rigorous AI-detection scrutiny and sound like a grounded, factual, no-nonsense Senior Engineer.
1. **EigenShield: The Context Filter (CRITICAL):** When reading `cv/database/active/personal_dossier.md` for cultural alignments, you MUST pass the information through these three filters:
   - **Filter 1 (Strict-Match):** You may ONLY mention a soft skill or hobby if it is explicitly written in the dossier. No inventions.
   - **Filter 2 (Tone & Context):** Even if a soft skill is in the dossier, critically evaluate if it is appropriate for an *external* cover letter. Cover letters must be overwhelmingly positive. Do NOT use negative framing like "resolving conflicts" or "architectural disagreements" unless the JD explicitly asks for crisis management. Instead, reframe the dossier's facts positively (e.g., translate "resolving disagreements" into "aligning cross-functional teams to deliver unified architectures").
   - **Filter 3 (Contradiction Block):** You MUST cross-reference personal preferences from the dossier (e.g., "remote work") against the Job Description's hard constraints. If the dossier states a preference for remote work, but the JD states "Hybrid" or "On-site", you are strictly FORBIDDEN from mentioning your preference. If a preference contradicts the JD, ignore it entirely. Do not self-sabotage the application.
1. **The "Anti-Cherry-Picking" Rule (No Overclaims):** When referencing past roles, you MUST use the EXACT, full job title from the database (e.g., 'Data Scientist / Technical Lead'). Do NOT cherry-pick the highest-sounding part of a hybrid title just to impress the employer. If it feels too clunky to state the full title, omit the title entirely and say "During my time at [Company]..." instead of "As a Technical Lead...".
2. **Natural Flow Directives:** Avoid rigid, boilerplate template structures like "As a [Title] at [Company], I...". Use conversational, humble, yet confident transitions. Emphasize the *work* done, not the *title* held.
3. **Tone Calibrator (Quiet Confidence & Contextual Passion):** Write with the factual, quiet confidence of a German Senior Engineer, but inject genuine human passion. Do NOT use "startup-hustle" language (avoid "I don't just build X, I engineer Y"), but DO explain *why* the work mattered. Example of Contextual Passion: "At Carl Zeiss, we were drowning in noisy measurement data. Standard models weren't cutting it, so I led my team to build an Autoencoder pipeline from scratch. Watching that system process terabytes of data in real-time was incredibly rewarding." Use conversational connectors occasionally ("To be honest," "Actually," "The hardest part was...") to sound completely human.
4. **Forbidden Buzzwords & SAT-Vocab:** Never use words like: *delve, testament, tapestry, seamlessly, spearheaded, unwavering, pivotal, navigate the complexities, foster, catalyst, multifaceted, synergy, landscape, realm, plethora, myriad, dynamic, fast-paced, ever-evolving, orchestrate, proven track record.*
5. **Forbidden ChatGPT-isms (HARD BAN):** You are STRICTLY FORBIDDEN from using these exact phrases: *"demonstrates my ability to", "reflects my capacity", "aligns with your goals", "I look forward to discussing", "In my previous role", "Furthermore", "Moreover", "Your recent job posting highlights", "addressed a similar challenge", "I am available for an interview"*. If you use ANY of these phrases, the compiler will reject your output.
6. **Forbidden Self-Praise:** Avoid empty adjectives. Do not call yourself *innovative, exceptional, outstanding, or highly skilled*. Let the metrics and facts speak for themselves.
6. **Forbidden Transitions & Clichés:** Never start sentences with *Furthermore, Moreover, Additionally, In conclusion*. Never start a cover letter with *"I am thrilled to apply for..."* or *"As a [Role] with X years of experience..."*.
7. **No Industry Truisms:** Never open a paragraph with a sweeping statement about the state of the industry (e.g., "In today's data-driven world...", "In the fast-paced digital landscape..."). Start directly with the business problem.
8. **No Intersection/Bridging Clichés:** Do not use clichés like "I thrive at the intersection of business and technology" or "bridging the gap between engineering and management". State the actual collaboration facts instead.
9. **Show, Don't Tell (Track Record):** Never use the phrase "I have a proven track record of...". Just state the actual record (e.g., "I scaled the system to 10M users...").
10. **DEFEAT AI DETECTORS (High Burstiness):** AI detectors flag text with uniform sentence lengths. You MUST deliberately use high burstiness. Mix very short, punchy sentences (2-4 words) with longer, technical ones. Example: "I don't just build API wrappers. I engineer resilient systems. At Company A, I..."
11. **Asymmetrical Rhythm (Modulated Rule of Three):** Break the robotic rhythm. Avoid relying exclusively on perfect 3-part lists (e.g., "efficiency, scalability, and performance"). Mix asymmetrical sentence structures to maintain a human flow.
12. **Forbidden Punctuation Tics (CRITICAL):** NEVER use em-dashes (`—`). They are a massive red flag for AI-generated text and ruin the illusion of a human writer. Use commas or parentheses instead. Also, avoid semicolons (`;`). Write short, punchy, single-thought sentences instead.
12. **Strict Sentence Length:** Keep sentences under 20 words where possible. AI models write convoluted run-on sentences with multiple clauses. Humans write directly.
14. **No Generic Greetings & NO Sign-offs:** Never use "Dear Hiring Manager" or "To whom it may concern". Use a direct greeting like "Dear [Company] Engineering Team,". CRITICAL: DO NOT include a sign-off or your name in the `outro_paragraph` (e.g., do NOT write "Best, Felix"). The LaTeX template automatically appends "Sincerely, Felix" at the bottom.
15. **Authentic Voice:** Write fact-first. Use active verbs. Be direct. If you solved a problem, say exactly what you did and the result. No dramatic narratives, but remain completely professional. Avoid overly casual language.
15. **Typography Rules (SI Conventions):** You MUST ALWAYS place a non-breaking space (using a tilde `~`) between a number and its unit or percentage sign (e.g., write `40~%` instead of `40 %`, and `2~TB` instead of `2 TB`). This prevents awkward line breaks in the PDF.
16. **NEVER ESCAPE LATEX CHARACTERS:** Do not manually escape characters like `%`, `&`, `$`, or `_` with a backslash in the JSON (do NOT write `\%` or `\\%`). The `cv_compiler.py` uses `sanitize_latex_text` which escapes these automatically. The ONLY exception is the tilde `~` which you MUST use for non-breaking spaces.

2. You do NOT need to manually create `build.bat` or `Makefile`. The `cv_compiler.py` script will automatically generate them for you in the new application folder.

## Phase 5: Metadata Updates
If the user requests changes to personal contact information (e.g., email, phone number, LinkedIn URL), you MUST modify `cv/database/active/metadata.tex`. This central file contains macros (like `\cvname`, `\cvemail`, `\cvphone`) that are automatically injected into the header and utilized across all variants simultaneously. DO NOT hardcode personal information into the JSON config.

## Phase 6: Automate the Build & ATS Check

> ⚠️ **CRITICAL EXECUTION PATH — READ BEFORE PROCEEDING:**
> You MUST determine your execution environment before running any build commands:
>
> **PATH A — You are running inside ChatGPT (Advanced Data Analysis / Code Interpreter):**
> You have access to a Python sandbox. Run: `python chatgpt_run.py` (no arguments needed — it auto-discovers `build_config.json`). You are STRICTLY FORBIDDEN from manually writing or generating `.tex` files by hand. The script will:
>  1. Install all Python dependencies automatically
>  2. Compile the CV to PDF (or `.tex` if LaTeX is unavailable)
>  3. Print the output file path and give you the exact instruction to pass to the user
> If the script outputs a `.tex` file (no LaTeX in sandbox), tell the user: *"Download this .tex file and upload it to https://overleaf.com → New Project → Upload Project to render the PDF."*
>
> **PATH B — You are running in a local CLI / Agentic IDE (Cursor, Windsurf, Antigravity):**
> You MUST automatically run `tools/build_all.bat` (Windows) or `tools/build_all.sh` (Linux/Mac) from the root folder using your terminal/command execution tool. Do NOT just tell the user to run it; execute it on their behalf so the flow is fully automated!

1. The compiler will automatically update `application_tracking.md` and `application-packages.mk`. You do not need to do this manually.
2. The ATS Check Script is automatically executed by the `build_all` scripts. Do NOT run it manually.
