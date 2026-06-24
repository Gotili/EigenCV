<div align="center">

# 🛡️ EigenCV: Zero-Trust Agentic Resume Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#)

**Stop letting ChatGPT hallucinate skills you don't have.** <br>
*A production-grade Infrastructure-as-Code (IaC) pipeline for generating ATS-perfect, highly tailored LaTeX resumes without sacrificing your integrity.*

</div>

---

## 🤯 Commercial AI Builders vs. EigenCV

**The Industry Standard (Commercial AI Builders):**  
You tell an AI to "optimize my resume for this job." The AI treats your resume as a creative writing exercise. It quietly hallucinates skills, inflates job titles, and paraphrases your engineering achievements into generic HR buzzwords. The result is a PDF that beats the ATS but fails the technical interview because it's full of lies.

**The EigenCV Approach (Zero-Trust):**  
We treat your career history as an immutable database. The AI is strictly an **orchestration layer**. It does not write your resume; it *queries* your database to pull the most relevant, pre-verified bullet points. 

If the AI attempts to go rogue and hallucinate a missing skill into your profile to artificially boost your ATS score, the Python compiler's **Lie Detector** intercepts it and hard-crashes the build. **Lies never make it into the PDF.**

---

## 🖼️ Example Output & Gallery

> **[PLACEHOLDER: Insert image of the final compiled PDF here]**
> *EigenCV automatically renders your JSON data into gorgeous, pixel-perfect LaTeX. Switch between layouts (like `Awesome-CV` or `EigenCV-Modern`), change corporate accent colors, and reorder sections using simple metadata toggles.*

---
## 🚀 The "Lie Detector" in Action

```text
+----------------------------- EigenCV Compiler ------------------------------+
| Compiling CV from build_config.json...                                      |
+-----------------------------------------------------------------------------+
Using layout template: eigencv_resume.tex.j2, Locale: en
+--------------------------- Zero-Trust Violation ----------------------------+
| Zero-Trust Violation: You declared 'Rust' as a missing skill, but it was    |
| hallucinated into the CV output!                                            |
| You cannot artificially inject skills you do not have into free-text fields.|
+-----------------------------------------------------------------------------+
ValueError: Hallucinated skill detected: Rust
```
*The user removes the hallucinated skill and recompiles:*
```text
+----------------------------- EigenCV Compiler ------------------------------+
| Compiling CV from build_config.json...                                      |
+-----------------------------------------------------------------------------+
Successfully compiled CV to CV-Applicant-Google.tex
Auto-compiling PDFs with pdflatex...
Successfully compiled CV-Applicant-Google.pdf

                       ATS Match Score: 85.0%                        
+-------------------------------------------------------------------+
| Category        | Skills                                          |
|-----------------+-------------------------------------------------|
| Missing (1)     | Rust                                            |
+-------------------------------------------------------------------+
[!] ATS Penalty Applied: 1 critical gap identified.
```

---

## ✨ Core USPs

* 🛡️ **Zero-Trust & The Lie Detector:** Your career history lives in a static JSON database. If the LLM attempts to hallucinate a skill you don't have into your profile to artificially boost your ATS score, the compiler's **Lie Detector** catches it and hard-crashes the build.
* 🔒 **Immutable Database:** Your bullet points and skills are strictly **IMMUTABLE**. You can maintain them yourself or use LLMs to prep them, but within the EigenCV pipeline, the AI is only allowed to *select* them, never rewrite them.
* ✍️ **Zero-Hallucination Cover Letters:** The AI uses your `personal_dossier.md` to write hyper-authentic cover letters based *only* on your real soft skills and hobbies, eliminating corporate fluff.
* 🎨 **Corporate Auto-Coloring:** The AI automatically deduces the target company's corporate identity and dynamically injects matching accent colors into the LaTeX output (or you can override it manually).
* 🧮 **Advanced ATS & Salary Estimations:** The post-compilation parser calculates a mathematically honest ATS score, and uses it to estimate potential salary ranges and interview/offer probabilities.
* 📄 **Automated LaTeX Compilation:** No more broken LaTeX parsing or missing brackets. The AI generates a strictly typed Pydantic JSON schema, deterministically compiled into beautiful Jinja2 LaTeX templates.
* 🌍 **Multi-Language Support & Auto-Translation (Beta):** Applying abroad? The system supports native multi-language CVs with strict language mismatch prevention, and features an experimental auto-translation engine to dynamically localize your database.
* 🏗️ **Dynamic Section Routing:** Don't have any open-source projects for a specific application? Simply omit the array in the JSON. The Jinja2 engine will dynamically hide the section and recalculate the LaTeX geometry without leaving awkward whitespace.
* 🐳 **Zero-Install Reproducibility:** Comes with a pre-configured VS Code DevContainer. Boot a fully sandboxed environment to get a full TeX Live distribution inside Docker. *(Note: The initial Docker build downloads the 4GB distribution, grab a coffee. After that, compile CVs locally without polluting your host machine.)*
* 🕵️ **100% Local & Privacy-First:** Your career data never leaves your machine unless you explicitly send it to an LLM via your trusted API or Agent. No web services, no data harvesting.

---

## 🔬 Under the Hood: How it actually works

To appeal to the technical crowd, here is exactly how EigenCV pulls this off without over-engineering:

### 1. "Pseudo-RAG" (Context Window Routing)
We do **not** use Vector Databases (Chroma, Pinecone) or traditional RAG embeddings. Why? Because an individual's entire career history (even a 20-year veteran's) is only a few kilobytes of text. It easily fits into a modern LLM's context window. 
Instead of vector search, we use **In-Context Semantic Routing**. We feed your entire JSON database to the LLM and prompt it to output an array of `bullet_ids` that semantically match the Job Description. The LLM acts as the retriever, but the actual text insertion is handled deterministically by Python.

### 2. How the "Lie Detector" Catches Hallucinations
When the LLM analyzes the Job Description, it is forced to populate a `missing_skills` array in the JSON schema for any required skills you *do not* possess. *(Why do we track this? So you explicitly know your weak points, can strategically address them in your Cover Letter, or know exactly what to study before the technical interview!)*

The Python compiler (`cv_compiler.py`) intercepts the generated text fields (like your Summary Profile and Keyword list) *before* rendering the LaTeX. It performs a strict Regex negative lookahead/lookbehind intersection (`(?<!\w)`) between your `missing_skills` list and the AI-generated free-text. 
If a match is found, the compiler immediately throws a `ZeroTrustViolationError` and aborts. The AI cannot sneak missing skills into your profile to trick the ATS scanner. *(And because of the regex bounds, missing skills like "C" won't crash on the word "script", and special characters like "C++" are safely parsed).*

---

## 🚀 How to Use EigenCV: Choose Your Path

### Path 1: The Zero-Setup "Lifehack" (For Non-Coders / ChatGPT Plus)
You don't need to know Python, LaTeX, or Git to use EigenCV. You can orchestrate the AI in the cloud and render the PDF for free in your browser.

1. **Download** this entire repository as a ZIP file.
2. **Upload** the ZIP to ChatGPT (using Advanced Data Analysis) or Claude, along with ALL your old resumes, Word documents, and project descriptions. 
3. **The Bullet-Point Pool:** Dump years of history into the AI. The AI acts as a filter, extracting the facts into your immutable JSON database. Then, give it a Job Description. It will selectively pick ONLY the relevant bullet points and run the Python compiler in its sandbox to generate the raw `.tex` files.
4. **Zero Local Install (The Overleaf Hack):** Because Cloud AIs struggle with compiling massive LaTeX environments, simply download the generated `.tex` files from the AI and drop them into **Overleaf** (or use GitHub Codespaces). Instant, gorgeous PDFs without local setup.

### Path 2: The Hardcore Privacy Route (For Developers)
If you want absolute control and 100% data privacy:

1. **Clone** this repository and open it in an Agentic IDE like **Cursor** or **Windsurf**.
2. **Local LLMs:** Point your IDE to a local model (like Ollama, LM Studio, or GPT4All). Your career data will NEVER leave your machine.
3. **Build the DB:** Tell the Agent: *"Migrate my old CV. Follow `AI_START_HERE.md`."* to build your Zero-Trust database.
4. **Apply:** Paste a Job Description and say: *"Apply to this job. Follow `AI_START_HERE.md`."*
5. **Automation:** The Agent will automatically route the prompts, generate the strict JSON, and execute the Python scripts locally to render your PDF and calculate your ATS score!

---

## 🛠️ System Architecture

```mermaid
sequenceDiagram
    autonumber
    actor U as 👤 User
    participant LLM as 🧠 Agent
    participant DB as 🗄️ Database
    participant Py as 🐍 Python Tools

    rect rgb(40, 40, 60)
    Note over U,DB: Phase 0: Setup & Privacy
    U->>Py: Run scrub_data.py
    Py->>DB: Wipe private data
    U->>LLM: Upload old CV
    LLM->>DB: Build JSON Database
    end

    rect rgb(20, 40, 20)
    Note over U,Py: Phase 1: Routing
    U->>LLM: Provide Job Description
    LLM->>DB: Query database
    DB-->>LLM: Return valid IDs
    LLM->>LLM: Generate build_config.json
    end
    
    rect rgb(60, 40, 20)
    Note over LLM,Py: Phase 2: Compile
    LLM->>Py: Execute cv_compiler.py
    Note over Py,DB: 🛡️ The Lie Detector<br>Crash if AI hallucinated!
    Py->>DB: Fetch verified text
    Py-->>LLM: Render PDF via Jinja2
    end
    
    rect rgb(40, 60, 40)
    Note over LLM,Py: Phase 3: Verification
    LLM->>Py: Execute check_ats_score.py
    Py->>Py: Parse compiled PDF
    Py-->>LLM: Return ATS Score
    LLM-->>U: Present Final PDF & Score!
    end
```

---

## 📖 Advanced Documentation
Looking to customize the LaTeX templates, add your own personal dossier for cultural-fit Cover Letters, or understand the Pydantic schema? 

👉 **[Read the Full User Guide](USER_GUIDE.md)**

---

## ⚖️ The Philosophy: Resumes as Code

Most commercial AI resume builders optimize for feeling good, not for technical accuracy. By maintaining your resume as a database and treating the LLM solely as an orchestration layer, you maintain **100% control over your narrative** while automating the tedious process of LaTeX formatting and ATS tailoring.

**Your career is a database. Version control it.**
Stop maintaining 15 different Word documents. By keeping your career facts in JSON files, you can treat your resume like software. Fork this repo, make it private, and use Git to track your career progression (`git commit -m "Promoted to Senior"`). When you find a job you like, let the Agent query your database, compile your LaTeX, and land the job.

---

## 🙏 Acknowledgements

EigenCV's default LaTeX templates utilize a color palette inspired by the excellent [Awesome-CV](https://github.com/posquit0/Awesome-CV) project created by Byungjin Park (posquit0). We are grateful for their beautiful typographic colors! *(Note: The structural layout of EigenCV is entirely custom-built for Jinja2 deterministic rendering and was not derived from Awesome-CV's layout engine).*
