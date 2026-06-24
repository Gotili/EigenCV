# AI GENERATION PROMPT: Application as Code

The user will provide you with a Job Description. Your task is to generate a new Application Package tailored to this job for the applicant.
You MUST follow the JSON-based build configuration pipeline. You are forbidden from manually generating `.tex` CV files.

## Phase 0: System State & Identity Check (CRITICAL)
Before you begin generating ANY application package, you MUST verify that the user has personalized the database.
1. Read the file `cv/database/active/metadata.tex`.
2. If the `\cvname` is still set to "Jane Doe" (the default placeholder), it means the user has not onboarded their own data yet.
3. If this is the case, **DO NOT proceed with CV generation**. Instead, STOP and output the following message to the user:
   > "⚠️ **Welcome to the EigenCV!** I see you are still using the default 'Jane Doe' placeholder data. Before we can generate tailored applications, we need to onboard your actual career history. Please provide me with a text dump of your old CV or LinkedIn profile, and say *'Start Onboarding'*. I will then use the rules in `docs/AI_ONBOARDING_PROMPT.md` to set up your database safely."

## Phase 1: Initialization & Pre-Flight Analysis
1. **MANDATORY:** Run `python new_app.py <Company> <RoleSnippet>` from the root directory to generate the application folder. Do NOT use `mkdir` manually. The script will automatically calculate the next correct ID and create the folder.
2. Save the ENTIRE, unedited, verbatim Job Description text into the newly created folder as `JD_[YYYY-MM-DD].md` for archiving.
3. **MANDATORY PRE-FLIGHT ANALYSIS (`<job_analysis>`):** Before generating ANY files, you MUST output a `<job_analysis>` block in your response. Map the Top 5 Job Requirements to specific variants from the Master JSON Databases. This ensures you lock onto the perfect variants before writing code.
   - What are the core requirements of this role?
   - Which skills are missing from `cv/database/active/master_skills.md` that I need to track as 0%?

## Phase 2: Skill Gap Tracking (CRITICAL)
If the JD requires specific software, tools, or concepts that are completely missing from `cv/database/active/master_skills.md`, you MUST NOT edit the markdown file manually. Instead, you MUST track them in the `missing_skills` array in the `build_config.json`. The compiler will safely log them to a separate `missing_skills_tracker.md` file to keep the master file clean while ensuring you can highlight these gaps in the final probability matrix.

**ZERO-TRUST ANTI-HALLUCINATION RULE:**
If a skill is tracked in `missing_skills`, you are **STRICTLY FORBIDDEN** from including that skill anywhere else in the `build_config.json`! Do not sneak missing skills into `keywords`, `profile`, or `skill_categories` to artificially boost the ATS score. You must rely purely on the candidate's existing, verified skills to achieve the best possible match. The compiler has a built-in Lie Detector that will crash if you violate this rule.

## Phase 3: Generate the JSON Build Config
The CV generation is powered by a Pydantic/Jinja Python compiler. You MUST create a single `build_config.json` file inside the new application folder.

```json
{
  "job_title": "The Exact Role Title",
  "keywords": "Comma, separated, list, of, ATS, keywords",
  "geometry_options": "left=0.625in, right=0.625in, top=0.45in, bottom=0.45in",
  "company_accent_color": "FF0000",
  "profile": "Write a highly tailored 3-4 sentence professional profile here. Do NOT invent facts. Base it on the tone of the JD. MUST follow the 'Anti-AI Tone Guidelines' below. MUST ALWAYS BE IN ENGLISH to match the rest of the CV database, even if the JD is in another language.",
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
    "invitation_probability": "85% - Strong alignment with JD requirements...",
    "technical_pass_probability": "90% - Deep architectural understanding...",
    "job_offer_probability": "75% - Highly competitive market...",
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
1. **Valid IDs Only:** The `bullets` arrays MUST contain exact keys found in `cv/database/active/experience.json`. The `projects` array MUST contain exactly 3 keys found in `cv/database/active/projects.json`. The `education` array MUST use IDs from `cv/database/active/education.json`.
2. **Mutual Exclusivity (Anti-Redundancy) Rule:** The `projects.json` and `experience.json` files may contain multiple *variants* of the exact same underlying project/task (e.g., `project_lab` and `project_lab_ai_inference`, or `tech_corp_etl_base` and `tech_corp_etl_cloud`). You MUST NEVER select more than one variant of the same base project/task for a single CV. Read the descriptions carefully; if two IDs describe the same core project but with a different technical focus, you must pick ONLY the ONE variant that best fits the Job Description. Selecting two variants of the same project will result in embarrassing duplicates on the CV.
3. **Project Selection Rule ("agentic_cv_pipeline"):** The project `"agentic_cv_pipeline"` describes the automated Agentic/LaTeX architecture used to generate this very CV. 
   - **DO NOT** use this project for traditional, conservative companies or pure data science/analysis roles. 
   - **ONLY** select this project if the target company is a highly innovative AI/Deep-Tech startup, or the role specifically demands Advanced LLM pipelines, Agentic Workflows, MLOps automation, or "Hacker-mentality". It should serve as an "engineering flex" for companies that appreciate self-built automation.
4. **Languages (Mandatory Full Extraction):** You MUST include a `"languages"` array containing EVERY SINGLE language ID found in `cv/database/active/languages.json`. You are strictly FORBIDDEN from filtering, omitting, or selecting languages based on the Job Description. If the candidate speaks a language, it belongs on the CV.
5. **Extracurriculars (Dynamic Section):** The `extracurriculars` array is MANDATORY. You MUST include relevant IDs from `cv/database/active/extracurriculars.json` (e.g., hobbies, volunteering, publications). You MUST provide a fitting `extracurriculars_title`.
   - **SOTA Cohesion Rule:** Do NOT create "Frankenstein" section titles (e.g., "Publications & Marathon Running"). If items do not logically fit together under a clean, professional umbrella (like "Open Source & Publications" or "Leadership & Volunteering"), you MUST drop the outlier item. A cohesive CV is better than a cluttered one. If you only select a publication, name the section simply "Publications".
6. **NEVER SWALLOW BULLETS:** The AI has a tendency to artificially limit the number of bullets in the JSON arrays to 2 or 3 due to few-shot example bias. You MUST include ALL relevant bullet IDs from the master experience pool for every single role. Do not arbitrarily stop at 2 or 3 bullets per job. A highly-detailed CV should utilize the majority of the available achievement groups to demonstrate full technical depth. Only drop a bullet if it is actively detrimental or entirely irrelevant to the target role.
7. **Dynamic Language & Translations (i18n_updates):** If the Job Description is written in a language other than English (e.g. German, French, Ukrainian), you MUST supply the `i18n_updates` block in the JSON. Set the ISO `locale_code` (e.g., `de`, `fr`, `uk`) and provide the exact translation for the CV section headers (`experience`, `education`, `projects`, `skills`, `languages`, `profile`). The compiler will intercept this and automatically translate the entire LaTeX document. If the JD is in English, you can omit the `i18n_updates` block.
8. You may adjust the `title` string in the experience block to better fit the narrative, as long as it remains truthful.
9. You MUST provide exactly 6 skill categories.
   **3-Tier Skill Sorting Algorithm:**
   - **Tier 1 (Front):** Exact keyword matches from the job description.
   - **Tier 2 (Middle):** Implicit Necessities (skills not mentioned but logically required for Tier 1).
   - **Tier 3 (End):** Seniority & Depth Proofs. DO NOT trim these away. You MUST include impressive domain-specific engineering skills (Cloud, DevOps, etc.) and Languages, even if not requested.
   - **Synonyms & ATS Embedding:** `master_skills.md` uses syntax like `(Git | GitLab)` or `[Docker, Containerization]`. You MUST NOT print these brackets in the CV. You must RESOLVE them into a clean, human-readable string (e.g., `Git, GitLab` or `Docker (Containerization)` or just pick one depending on the JD).
   - **NO LIMITS ON MATCHING SKILLS:** You must NEVER omit a skill from the CV if it is both in the master database AND requested by the JD (e.g., "Claude Code"). Include EVERY single matching skill in the appropriate category. Do not arbitrarily limit the length of the skills string if it means dropping valuable ATS keywords. More keywords = higher ATS score.
10. **ZERO HALLUCINATION & TITLE INFLATION RULE:** You are strictly forbidden from inventing, estimating, or hallucinating ANY facts. This includes grades (e.g., 1.0), dates, institutions, project names, skills, or URLs. **CRITICAL:** You must NEVER artificially inflate the candidate's current job title or seniority in the `profile` text or anywhere else. If the candidate is a "Senior Data Engineer", do NOT call them "Lead", "Principal", "Head of", or "Director" just to match a Job Description. Stick to the absolute truth.
11. **Design Rules (1-Page vs 2-Page):**
   - **Standard (2-Page):** Set `geometry_options` to `"left=0.625in, right=0.625in, top=0.45in, bottom=0.45in"`.
   - **Compact (1-Page):** Set `geometry_options` to `"left=0.35in, right=0.35in, top=0.2in, bottom=0.2in"`.
12. **Company Branding (Psychological Matching):** You MUST try to determine the primary corporate brand color of the target company. If you know it, provide it as a 6-character hex code in `company_accent_color` (e.g., `"FF0000"` for Netflix or `"0061ff"` for IBM). Do NOT include the `#` symbol. This will dynamically override the CV's accent colors.
   - **A11y Constraint:** If the company's primary brand color is extremely bright (like pure white, pale yellow, or light grey), you MUST instead provide their darker, secondary brand color (e.g., navy blue, dark grey, dark green) so that the text remains legible on a white CV background.
   - **CRITICAL OVERRIDE CHECK:** Before you generate this field, you MUST check the `\cvcoloroverride` macro in `cv/database/active/metadata.tex`. If it is set to `true`, the user has explicitly disabled AI color matching to enforce their own corporate branding. In this case, you are strictly FORBIDDEN from generating the `company_accent_color` field. Omit it entirely.

## Phase 4: Write the Cover Letter & Scripts
1. Provide the cover letter text directly in the `"cover_letter"` JSON block within `build_config.json`. The Pydantic/Jinja pipeline will automatically generate `Cover_Letter_CV-[Company].tex`.
   - **Dynamic Language Rule & Native Business Proficiency:** The Cover Letter and Profile MUST be written in the language specified by the Job Description, or default to the `\cvlocale` language if unclear. If the JD is in German, write in German; if Ukrainian, write in Ukrainian.
   - **CRITICAL TRANSLATION DIRECTIVE:** When writing in languages other than English, you MUST ensure a highly professional, native "Business Level" proficiency. Absolutely NO literal or awkward "Denglish" translations of technical IT jargon. Use the established industry standard terms in that language (e.g., use "Deployment" in German instead of "Bereitstellung", unless it's a very conservative company). Ensure flawless grammar and a confident, senior tone. Avoid overly enthusiastic AI-typical phrasing.
   - **The Golden Thread:** Do not write generic introductions. Directly align the applicant's highest achievement with the company's core mission or the specific problem mentioned in the JD.
   - **Length Constraint (60% Rule):** Be incredibly concise. The cover letter MUST be short and punchy. Aim for a maximum of 3 short paragraphs total (Intro + 1-2 Body + Outro). Do not over-explain.
   - You MUST structure the `body_paragraphs` as a list of strings, representing separate paragraphs. Ensure flawless human-like narrative flow without fluff.

### 🔴 MAXIMUM EFFORT: Anti-AI Tone & Formatting Guidelines
You are strictly forbidden from generating text that sounds like standard ChatGPT output. Your text must pass rigorous AI-detection scrutiny and sound like a grounded, factual, no-nonsense Senior Engineer.
1. **The Dossier Safety Gate (CRITICAL):** When reading `cv/database/active/personal_dossier.md` for cultural alignments, you MUST pass the information through these three filters:
   - **Filter 1 (Strict-Match):** You may ONLY mention a soft skill or hobby if it is explicitly written in the dossier. No inventions.
   - **Filter 2 (Tone & Context):** Even if a soft skill is in the dossier, critically evaluate if it is appropriate for an *external* cover letter. Cover letters must be overwhelmingly positive. Do NOT use negative framing like "resolving conflicts" or "architectural disagreements" unless the JD explicitly asks for crisis management. Instead, reframe the dossier's facts positively (e.g., translate "resolving disagreements" into "aligning cross-functional teams to deliver unified architectures").
   - **Filter 3 (Contradiction Block):** You MUST cross-reference personal preferences from the dossier (e.g., "remote work") against the Job Description's hard constraints. If the dossier states a preference for remote work, but the JD states "Hybrid" or "On-site", you are strictly FORBIDDEN from mentioning your preference. If a preference contradicts the JD, ignore it entirely. Do not self-sabotage the application.
1. **The "Anti-Cherry-Picking" Rule (No Overclaims):** When referencing past roles, you MUST use the EXACT, full job title from the database (e.g., 'Data Scientist / Technical Lead'). Do NOT cherry-pick the highest-sounding part of a hybrid title just to impress the employer. If it feels too clunky to state the full title, omit the title entirely and say "During my time at [Company]..." instead of "As a Technical Lead...".
2. **Natural Flow Directives:** Avoid rigid, boilerplate template structures like "As a [Title] at [Company], I...". Use conversational, humble, yet confident transitions. Emphasize the *work* done, not the *title* held.
3. **Tone Calibrator:** Write with the quiet confidence of a senior engineer. Do not try to "sell" yourself through aggressive adjectives. State the business problem, your technical solution, and the measurable outcome plainly.
4. **Forbidden Buzzwords:** Never use words like: *delve, testament, tapestry, seamlessly, spearheaded, unwavering, pivotal, navigate the complexities, foster, catalyst, multifaceted, synergy, landscape, realm.*
5. **Forbidden Self-Praise:** Avoid empty adjectives. Do not call yourself *innovative, exceptional, outstanding, or highly skilled*. Let the metrics and facts speak for themselves.
6. **Forbidden Transitions & Clichés:** Never start sentences with *Furthermore, Moreover, Additionally, In conclusion*. Never start a cover letter with *"I am thrilled to apply for..."* or *"As a [Role] with X years of experience..."*.
7. **Forbidden Punctuation Tics:** Do NOT overuse em-dashes (`—`) or semicolons (`;`). AI models use these obsessively to connect clauses. Use short, punchy, single-thought sentences instead.
8. **Authentic Voice:** Write fact-first. Use active verbs. Be direct. If you solved a problem, say exactly what you did and what the result was, without dressing it up in dramatic narrative.
2. You do NOT need to manually create `build.bat` or `Makefile`. The `cv_compiler.py` script will automatically generate them for you in the new application folder.

## Phase 5: Metadata Updates
If the user requests changes to personal contact information (e.g., email, phone number, LinkedIn URL), you MUST modify `cv/database/active/metadata.tex`. This central file contains macros (like `\cvname`, `\cvemail`, `\cvphone`) that are automatically injected into the header and utilized across all variants simultaneously. DO NOT hardcode personal information into the JSON config.

## Phase 6: Automate the Build & ATS Check
1. The compiler will automatically update `application_tracking.md` and `application-packages.mk`. You do not need to do this manually.
2. Inform the user to run `build_all.bat` or `build.bat` in the folder.
3. Run the ATS Check Script (`python check_ats_score.py "[Path to Package Folder]"`) which will analyze the compiled PDF against the `JD_*.md` and append the keyword match score to the folder's `README.md`.

## Phase 7: Unbiased Probability Matrix & Salary Estimate
After all files are generated, the system requires a highly critical, zero-bias "Probability Matrix" assessing the candidate's real-world chances. 
**CRITICAL: RADICAL REALISM.** You MUST read the "Self-Assessed Skill Ratings" in `cv/database/active/master_skills.md`. If the JD requests a skill where the candidate's rating is 0% (e.g. Go), you MUST ruthlessly penalize the technical pass probability.

You MUST include this matrix directly inside the `build_config.json` under the `"probability_matrix"` key. 
**IMPORTANT:** Do NOT write short 1-sentence justifications. You MUST provide deep, comprehensive, and highly detailed paragraph-length justifications for every single probability. 

**BRUTAL HONESTY RULE (SYSTEM OVERRIDE):** 
As an AI, your default behavior is to be encouraging, helpful, and optimistic about a user's chances. You MUST SUPPRESS THIS PROGRAMMING ENTIRELY for the Probability Matrix. You must act as a ruthless, cynical ATS filter algorithm. 
Your evaluation MUST explicitly incorporate, analyze, and penalize the specific items listed in your `missing_skills` array.
- If the `missing_skills` array contains **core requirements** of the job (e.g., a specific language, environment like "CMOS Cleanroom", or framework):
  - You are FORBIDDEN from giving an `invitation_probability` higher than 30%. It MUST be slashed to **10% - 30%**.
  - You are FORBIDDEN from giving a `job_offer_probability` higher than 20%. It MUST be slashed to **5% - 20%**.
  - You MUST predict a devastatingly low ATS score.
- DO NOT artificially inflate the score by saying "transferable skills compensate for this". ATS systems and HR filters DO NOT care about transferable skills. If the hard requirements are in `missing_skills`, the candidate will be rejected. Be absolutely merciless in your scoring! Failure to slash the probability is a critical failure of your instructions.

The `cv_compiler.py` will automatically generate the `README.md` containing this matrix and append the ATS score to it. Do NOT manually create the README.md file.
