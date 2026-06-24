# ☁️ The "Zero-Click" Cloud Prompt

**How to use:**
If you don't want to install LaTeX or Python on your computer, you can run the entire EigenCV pipeline inside ChatGPT (requires Plus/Advanced Data Analysis).

1. Download this entire repository as a ZIP file.
2. Drag and drop the ZIP file into ChatGPT.
3. If you want to migrate old resumes, drop them in too.
4. Copy and paste the exact prompt below into ChatGPT, and paste your target Job Description where indicated.

---

### 👉 Copy & Paste this into ChatGPT:

```text
I have uploaded the EigenCV system as a ZIP file. Please unzip it.

TASK 1: Extract my career facts from my provided old resumes into the JSON database format found in `cv/database/active/`. (If I did not upload old resumes, assume the database is already filled).

TASK 2: Analyze this Job Description:
[ PASTE YOUR JOB DESCRIPTION HERE ]

TASK 3: Generate the `build_config.json` in the root directory by selecting the best matching bullet points from the database. Strictly follow the instructions in `docs/AI_GENERATION_PROMPT.md`. Do not invent any skills.

TASK 4: Run the `chatgpt_run.py` script in the root directory to generate my PDF. 
If the script throws an EigenTruthViolationError, DO NOT try to fix the python code. Just tell me what skill I am missing.
If successful, provide me with the direct download link for the PDF.
```
