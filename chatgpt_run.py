import os
import sys
import subprocess

def is_venv():
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    cv_compiler_path = os.path.join(root_dir, "cv", "scripts", "cv_compiler.py")
    build_config_path = os.path.join(root_dir, "build_config.json")
    
    if not os.path.exists(build_config_path):
        print("ERROR: build_config.json not found in the root directory.")
        print("AI INSTRUCTION: You must generate the 'build_config.json' file first before running this script.")
        sys.exit(1)
        
    print("--- Starting ChatGPT Cloud Compile ---")
    
    if not is_venv() and not os.environ.get("EIGENCV_IN_CLOUD"):
        print("[INFO] You are not in a virtual environment. Skipping automatic 'pip install' to protect your global Python environment.")
        print("[INFO] If you are missing dependencies, please create a venv or run: pip install -r requirements.txt")
    else:
        print("Ensuring dependencies are installed (this may take a few seconds)...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", os.path.join(root_dir, "requirements.txt")], check=True)
        except Exception as e:
            print(f"[WARNING] Could not auto-install dependencies: {e}")
        
    print("Forcing cloud-safe template to avoid LaTeX font errors...")
    
    env = os.environ.copy()
    env["EIGENCV_FORCE_CLOUD_SAFE"] = "1"
    
    try:
        subprocess.run([sys.executable, cv_compiler_path, build_config_path], env=env, check=True)
    except subprocess.CalledProcessError:
        print("\n[FATAL ERROR] Compilation failed. See output above for AI instructions.")
        sys.exit(1)
        
    print("\n--- Compile Successful ---")
    print("PDF generation complete. Please provide the download link to the user.")

if __name__ == "__main__":
    main()
