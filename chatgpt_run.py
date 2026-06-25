"""
EigenCV ChatGPT / AI Sandbox Runner
====================================
Entry point for executing the EigenCV pipeline inside a sandboxed AI
environment (ChatGPT Advanced Data Analysis).

Usage:
    python chatgpt_run.py                          # auto-discovers build_config.json
    python chatgpt_run.py path/to/build_config.json  # explicit path
"""
import os
import sys
import shutil
import subprocess

# --- Constants ---
REQUIREMENTS_FILE = "requirements.txt"
CV_COMPILER_REL   = os.path.join("cv", "scripts", "cv_compiler.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_build_config(root_dir: str) -> str | None:
    """
    Locate build_config.json.

    Search order:
      1. Root of the repository (simplest case for cloud AIs)
      2. Any direct subfolder of application-packages/ (standard local layout)
      3. Recursive search as last resort
    """
    # 1 — root
    candidate = os.path.join(root_dir, "build_config.json")
    if os.path.exists(candidate):
        return candidate

    # 2 — application-packages/* (one level deep, newest first)
    app_pkg = os.path.join(root_dir, "application-packages")
    if os.path.isdir(app_pkg):
        subdirs = sorted(
            [d for d in os.scandir(app_pkg) if d.is_dir()],
            key=lambda e: e.stat().st_mtime,
            reverse=True,
        )
        for entry in subdirs:
            candidate = os.path.join(entry.path, "build_config.json")
            if os.path.exists(candidate):
                return candidate

    # 3 — full recursive scan (safety net)
    for dirpath, _, filenames in os.walk(root_dir):
        # Skip hidden dirs and the blank_slate database
        if any(part.startswith(".") or part == "blank_slate" for part in dirpath.split(os.sep)):
            continue
        if "build_config.json" in filenames:
            return os.path.join(dirpath, "build_config.json")

    return None


def ensure_dependencies(root_dir: str) -> None:
    """
    Always install requirements in the sandbox.
    In a ChatGPT sandbox, pip install is safe and idempotent.
    """
    req_file = os.path.join(root_dir, REQUIREMENTS_FILE)
    if not os.path.exists(req_file):
        print("[WARNING] requirements.txt not found — skipping dependency install.")
        return

    print("[INFO] Installing / verifying Python dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", req_file],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[WARNING] pip install encountered issues:\n{result.stderr}")
        print("[INFO] Continuing anyway — required packages may already be installed.")
    else:
        print("[INFO] Dependencies OK.")


def latex_available() -> bool:
    """Return True if pdflatex (or xelatex) is available on PATH."""
    return shutil.which("pdflatex") is not None or shutil.which("xelatex") is not None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    root_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("  EigenCV — Cloud Compile Runner")
    print("=" * 60)

    # --- Resolve build_config.json ---
    if len(sys.argv) > 1:
        build_config_path = os.path.abspath(sys.argv[1])
        if not os.path.exists(build_config_path):
            print(f"[ERROR] Provided path does not exist: {build_config_path}")
            sys.exit(1)
    else:
        print("[INFO] No path provided — auto-discovering build_config.json...")
        build_config_path = find_build_config(root_dir)
        if build_config_path is None:
            print()
            print("[ERROR] Could not find build_config.json anywhere in the repository.")
            print()
            print("  AI INSTRUCTION: You must write the build_config.json file to the")
            print("  repository ROOT before calling this script. Example:")
            print("    with open('build_config.json', 'w') as f:")
            print("        f.write(json.dumps(config_dict, indent=2))")
            print()
            sys.exit(1)

    print(f"[INFO] Using config: {os.path.relpath(build_config_path, root_dir)}")

    # --- Pre-validate JSON before running compiler ---
    print("[INFO] Validating build_config.json syntax...")
    import json
    try:
        with open(build_config_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print("[INFO] JSON syntax OK.")
    except json.JSONDecodeError as e:
        print(f"[WARNING] Invalid JSON detected: {e}")
        print("[INFO] Attempting auto-repair with tolerant parser (json5)...")
        try:
            import json5
            with open(build_config_path, 'r', encoding='utf-8') as f:
                data = json5.load(f)
            with open(build_config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("[INFO] JSON auto-repaired and rewritten. Continuing...")
        except ImportError:
            print("[INFO] json5 not available. Continuing — compiler will report the exact error.")
        except Exception as repair_err:
            print(f"[ERROR] Could not auto-repair JSON: {repair_err}")
            print()
            print("  AI INSTRUCTION: Fix the JSON syntax error in build_config.json.")
            print("  Common causes: trailing commas, unescaped quotes, missing brackets.")
            print("  Correct the file and run chatgpt_run.py again.")
            sys.exit(1)

    ensure_dependencies(root_dir)

    # --- Check LaTeX availability ---
    has_latex = latex_available()
    if not has_latex:
        print()
        print("[WARNING] pdflatex / xelatex not found in this environment.")
        print("[INFO] Will compile to .tex source only — no PDF will be produced.")
        print("[INFO] The user can paste the .tex file into https://overleaf.com to render the PDF.")
        print()

    # --- Set cloud-safe env flags ---
    env = os.environ.copy()
    env["EIGENCV_FORCE_CLOUD_SAFE"] = "1"
    if not has_latex:
        env["EIGENCV_TEX_ONLY"] = "1"

    # --- Run the compiler ---
    cv_compiler_path = os.path.join(root_dir, CV_COMPILER_REL)
    if not os.path.exists(cv_compiler_path):
        print(f"[ERROR] Compiler not found at: {cv_compiler_path}")
        sys.exit(1)

    print()
    print("[INFO] Starting EigenCV compiler...")
    print("-" * 60)

    result = subprocess.run(
        [sys.executable, cv_compiler_path, build_config_path],
        env=env,
    )

    print("-" * 60)

    if result.returncode != 0:
        print()
        print("[ERROR] Compilation failed. Review the error output above.")
        print()
        print("  AI INSTRUCTION: If the error mentions a missing bullet/project ID,")
        print("  check that all IDs in your build_config.json exist in the database.")
        print("  Re-read docs/AI_GENERATION_PROMPT.md Phase 2 (Valid IDs Only).")
        sys.exit(1)

    # --- Success summary ---
    print()
    print("[OK] Compilation successful!")
    print()

    # Find and report the generated output files
    config_dir = os.path.dirname(build_config_path)
    output_files = [
        f for f in os.listdir(config_dir)
        if f.endswith(".pdf") or f.endswith(".tex")
    ]
    if output_files:
        print("  Generated files:")
        for fname in sorted(output_files):
            fpath = os.path.join(config_dir, fname)
            size_kb = os.path.getsize(fpath) / 1024
            print(f"    {fname}  ({size_kb:.1f} KB)")
        print()
        if any(f.endswith(".pdf") for f in output_files):
            print("  AI INSTRUCTION: Provide the user a download link to the .pdf file.")
        else:
            print("  AI INSTRUCTION: LaTeX was not available — provide the .tex file.")
            print("  Tell the user: 'Download this .tex file and upload it to")
            print("  https://overleaf.com — click New Project > Upload Project.'")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
