# EigenCV: User Guide

Welcome to the User Guide! This document provides an in-depth look at how the database is structured, best practices for adding your personal data, and how to customize the visual design of your LaTeX resumes.

---

## 🤖 Cheat-Sheet: How to talk to the AI Agent
If you are using Cursor, Windsurf, or Copilot, use these exact prompts to trigger the correct internal routing logic without confusing the AI:

*   **To initialize the project:** *"Migrate my old CV to the database. Follow `AI_START_HERE.md`."*
*   **To generate an application:** *"Apply to this job [Paste JD]. Follow `AI_START_HERE.md`."*
*   **To update your history:** *"I learned a new skill / got a new job. Please update my history. Follow `AI_START_HERE.md`."*

---

## 🗄️ The Database Structure (`cv/database/active/`)

To use this for yourself, you just need to replace the contents of the files in `cv/database/active/` with your own career info. The architecture uses a simple Key-Value store:

* **`experience.json`**: Store every bullet point you've ever achieved here. Use a unique key for each (e.g., `"data_pipelines": "Architected distributed ETL pipelines..."`). The LLM will pick the keys that match the job. **Note:** Text in this database is injected directly into LaTeX. You must manually escape LaTeX characters (e.g., `%` as `\%`) and you may use LaTeX formatting (e.g., `\textbf{}`).
* **`projects.json`**: Store your technical portfolio. The keys are the project IDs, the values are the LaTeX-formatted descriptions.
* **`education.json` & `extracurriculars.json`**: Standard ID-to-Text mappings for your degrees and extracurriculars.
* **`languages.json`**: Simple mappings for your spoken languages and proficiencies.
* **`master_skills.md`**: A plain markdown file where you dump every tool, framework, and language you know. The LLM will scan this to build the `skills` array.
* **`personal_dossier.md`**: A markdown file storing your soft skills, work philosophy, and hobbies. The LLM will strictly reference this file to weave authentic, non-hallucinated cultural fit arguments into your cover letters.

### 🌍 Multi-Language Support (Locale Fallback)
The system supports Zero-Trust multi-language CV generation natively. 
If you request a specific language for your CV (e.g., setting `\cvlocale{es}` or generating a Spanish Cover Letter), the compiler will first look for locale-specific databases like `experience_es.json` or `projects_es.json`.
- If the file exists, it loads your translated bullets.
- If the file does **not** exist, it falls back to the default `experience.json` (English). 
- **Important:** If it falls back, the internal *Lie Detector* will immediately crash the build with a `Language Mismatch Error` to prevent you from accidentally sending out a bilingual Frankenstein-CV! You MUST provide translated database files if you intend to apply in a different language.

### 💡 Best Practices for `personal_dossier.md`
The EigenCV uses a strict anti-hallucination engine. If you want a compelling cover letter, you must provide compelling facts in your dossier.
- **Avoid Fluff:** Do not write "I am a strong team player." Instead, write an anecdote: "Successfully mediated architectural disagreements between Data Science and Data Engineering teams."
- **Concrete Hobbies:** Instead of "I like programming", use "Active Open-Source Contributor to Rust networking libraries." This gives the AI hard facts to use as proof of your cultural fit.

### 🧹 The "Clean Sweep" (Starting Over)
If you ever accidentally corrupt the JSON schema, delete a critical file, or want to wipe your data to start completely fresh, you can perform an automated **Clean Sweep**. 
Simply run the destructive script `python scripts/scrub_data.py`.
When prompted, type `WIPE`. This will:
1. Delete everything inside `cv/database/active/` (including `application_tracking.md` and `missing_skills_tracker.md`).
2. Copy all files from the safe `cv/database/blank_slate/` template into `cv/database/active/`.
This will safely restore EigenCV to its default factory state.

### 📂 Advanced Repository Structure
Beyond the database, the repository is modularized into several functional directories:
* **`cv/scripts/`**: Contains the core pipeline logic (`cv_compiler.py` and `cv_schema.py`).
* **Root Directory**: Contains the entry-point scripts (`tools/new_app.py` and `check_ats_score.py`) for easy command-line execution.
* **`cv/template/`**: Houses all visual presentation logic. This includes the Jinja2 LaTeX templates (`eigencv_resume.tex.j2`, `eigencv_cover_letter.tex.j2`), the `preamble.tex`, and your static `header.tex` (contact info & links).
* **`application-packages/`**: The generated output folder where all your finished applications live.

---

## 🧠 The Agentic Output (Pydantic Schema)

When the LLM reads your Job Description, it generates a `build_config.json`. This file is strictly validated by Pydantic (`cv/scripts/cv_schema.py`). You don't need to know Python to understand it, but you should understand its structure:

* **No Raw Text for History (Self-Healing IDs):** The schema forces the AI to output *arrays of string IDs*, not raw text. For example, under `experience`, the AI outputs `["data_pipelines", "aws_migration"]`. The compiler uses these IDs to fetch the real text from your database. If the AI makes a slight typo in an ID, an internal "Healer" uses RapidFuzz to auto-correct it (>90% accuracy match) to ensure your build doesn't crash over a missing underscore.
* **The `skills` Array:** The AI extracts a curated list of skills from your `master_skills.md` that match the job.
* **The `missing_skills` Array:** If the job requires a skill you do not have, the AI MUST put it here. The Lie Detector uses this array to ensure the AI didn't hallucinate that skill into your `profile` or `keywords`.
* **Dynamic Generation:** Only the `profile` (your summary paragraph) and `keywords` (ATS SEO terms) are generated dynamically as free-text by the AI, because these must be heavily tailored to the specific company's mission statement.

---

## 🎨 Customizing the Design

Because the pipeline strictly separates Data (JSON) from Presentation (LaTeX), overhauling the visual design is incredibly easy. You don't have to touch your career history at all.

### The Metadata System (`metadata.tex`)
The most powerful way to customize your CV is through `cv/database/active/metadata.tex`. This file controls global variables:
* **Template Switching (`\cvtemplate`)**: Choose between `eigencv_resume.tex.j2` and `awesomecv_resume.tex.j2`.
* **Accent Colors (`\cvcolor`)**: Change the primary color (e.g. `awesome-red`, `awesome-emerald`, or custom hex).
* **Color Override (`\cvcoloroverride`)**: By default, the AI will try to deduce the target company's brand color and dynamically inject it (e.g., Netflix Red). If you want to force the system to always use your chosen `\cvcolor`, set `\cvcoloroverride{true}`. This instructs both the AI and the Compiler to ignore corporate colors.
* **Section Ordering (`\cvorder`)**: Dynamically reorder your layout (e.g. `Profile, Experience, Skills, Projects, Education, Languages, Extracurriculars`). Any section omitted from this list, or missing data in `build_config.json`, will be dynamically hidden without breaking the layout.

### Advanced LaTeX Tweaking
1. **Fonts & Margins**: Edit `cv/template/preamble.tex` (for EigenCV) or `cv/template/awesome-cv.cls` (for Awesome-CV) to change font sizes or document geometry.
2. **Jinja Logic**: Edit `cv/template/eigencv_resume.tex.j2` or `awesomecv_resume.tex.j2`. These Jinja files determine the overarching layout loops. You can alter how specific sections render here.

---

## 🕵️ Deep Dive: The Cover Letter "Dossier Hack"

Commercial AI builders write terrible, generic cover letters because they don't know who you are as a person. EigenCV solves this with the `personal_dossier.md`.

**How it works:**
1. The AI reads the Job Description to understand the company's culture (e.g., "fast-paced startup", "enterprise governance").
2. It then reads your `personal_dossier.md` to find real, factual anecdotes that prove you fit that culture.
3. It generates the `cover_letter` object in `build_config.json`.

**How to exploit it:**
Don't just write "I like coding." Write highly specific, verifiable facts in your dossier:
* *"Open-source philosophy: I maintain a homelab with Proxmox and Kubernetes to test distributed systems."*
* *"Leadership: I mentored 3 junior developers who subsequently were promoted to mid-level engineers within 12 months."*
* *"Conflict Resolution: I successfully navigated a cross-departmental dispute between Data Engineering and Sales by presenting data-backed infrastructure costs."*

When you provide hard facts, the AI weaves them into a highly persuasive, non-hallucinated narrative.

---

## 🧮 The ATS & Probability Engine Explained

The pipeline provides actionable intelligence through a split approach (Determinism vs. Heuristics).

1. **The Python Keyword Matcher (Deterministic):** The `check_ats_score.py` script extracts raw text from your compiled PDF and compares it against lemmatized keywords from the Job Description (using NLTK & RapidFuzz). If a mandatory skill is missing, it applies a mathematically defined penalty to your ATS score.
2. **Probability & Salary Matrix (AI Heuristics):** Prior to compiling the PDF, the AI Agent assesses your factual database against the Job Description. It acts as a ruthless filter to estimate a realistic salary range and calculates your statistical chance of receiving an interview invite or job offer based strictly on your verified skills.
*Note: To improve these metrics, you must acquire the missing skills or re-write your immutable database bullet points to better reflect your true experience. The AI is strictly instructed to penalize your probabilities if core skills are tracked as missing.*

---

## 🔌 Local LLM Integration (100% Privacy)

EigenCV was built for the paranoid. You can run the entire semantic routing pipeline offline.

1. Install [Ollama](https://ollama.ai/) or [LM Studio](https://lmstudio.ai/).
2. Pull a high-context model (e.g., `llama3.1:8b` or `phi-3-mini`).
3. If using an Agentic IDE like Cursor, point the Custom OpenAI URL setting to your local host (e.g., `http://localhost:11434/v1`).
4. Execute the same prompts (`AI_START_HERE.md`). The local model will read your JSON database and output the `build_config.json`.

Your career data never touches the internet.

---

## 📜 Advanced LaTeX & Jinja2 Templating

If you are a LaTeX power user, you can build entirely new resume designs.

1. **Create your template:** Create a `custom_resume.tex.j2` file in `cv/template/`.
2. **Use Jinja tags:** The Python compiler passes the entire `build_config.json` schema to Jinja. 
   * Example: `\cvprofile{ {{ profile }} }`
   * Example Loop: 
     ```latex
     {% for item in experience %}
     \cvexperience{ {{ item.title }} }{ {{ item.company }} }{ {{ item.date }} }
     {% endfor %}
     ```
3. **Set the Metadata:** Open `cv/database/active/metadata.tex` and change `\cvtemplate` to `custom_resume`.

Because the data (JSON) and presentation (LaTeX) are strictly decoupled, you can swap between a highly conservative McKinsey-style template and a flashy Tech-Startup template just by changing one line of code, without ever rewriting your bullet points.
