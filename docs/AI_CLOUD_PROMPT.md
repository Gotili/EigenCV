# ☁️ EigenCV Cloud Prompt — Quick Start

> **Note:** This file (`AI_CLOUD_PROMPT.md`) is the legacy name. The full, authoritative system prompt is now in **`AI_GENERATION_PROMPT.md`**.
> When you tell the AI to "follow `docs/AI_GENERATION_PROMPT.md`", it will find the correct file.

---

## How to use ChatGPT (Advanced Data Analysis) — Copy & Paste

1. Download this repository as a ZIP (`Code → Download ZIP` on GitHub) or run `python tools/export_for_cloud.py` if you have your own data.
2. Upload the ZIP to **ChatGPT Plus** (requires Advanced Data Analysis tier).
3. Optionally upload your old CV/resume files alongside the ZIP.
4. Copy the prompt below, paste your Job Description where indicated, and send.

---

### 👉 Copy & Paste this into ChatGPT:

```text
I have uploaded the EigenCV system as a ZIP file. Please unzip it.

TASK 1 (only if I uploaded old resumes): Extract my career facts from my provided
old resumes into the JSON database format found in `cv/database/active/`.
If I did not upload old resumes, assume the database is already filled.

TASK 2: Read the file `VALID_IDS.md` in the repository root. This is your ONLY
reference for valid IDs. Do not use any ID that is not listed there.

TASK 3: Analyze this Job Description:
[ PASTE YOUR JOB DESCRIPTION HERE ]

TASK 4: Strictly follow ALL instructions in `docs/AI_GENERATION_PROMPT.md`.
Do not invent or hallucinate any skills or bullet points.
Only use IDs from `VALID_IDS.md`.

TASK 5: Run `python chatgpt_run.py` (no arguments) from the repository root.
The script will auto-discover the build_config.json and compile the CV.
If pdflatex is not available, it will produce a .tex file — provide me with
a download link and remind me to upload it to https://overleaf.com.
```
