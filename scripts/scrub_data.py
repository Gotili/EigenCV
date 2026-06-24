import os
import sys
import shutil

def scrub_data():
    print("="*60)
    print("🛑 WARNING: DESTRUCTIVE ACTION 🛑")
    print("You are about to perform a Clean Sweep. This will:")
    print("1. DELETE ALL your personal career history in cv/database/active/")
    print("2. DELETE your application_tracking.md history")
    print("3. Restore the 'Jane Doe' default configuration")
    print("This action CANNOT be undone.")
    print("="*60)
    
    confirmation = input("Type 'WIPE' to proceed with the deletion: ")
    
    if confirmation != "WIPE":
        print("Scrub aborted. Your data is safe.")
        sys.exit(0)
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    active_dir = os.path.join(base_dir, 'cv', 'database', 'active')
    blank_slate_dir = os.path.join(base_dir, 'cv', 'database', 'blank_slate')
    tracking_file = os.path.join(base_dir, 'application_tracking.md')
    
    print("\nStarting Clean Sweep...")
    
    # 1. Clear out active directory
    if os.path.exists(active_dir):
        for filename in os.listdir(active_dir):
            file_path = os.path.join(active_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(active_dir)
        
    # 2. Copy files from blank_slate to active
    if os.path.exists(blank_slate_dir):
        for filename in os.listdir(blank_slate_dir):
            src_file = os.path.join(blank_slate_dir, filename)
            dst_file = os.path.join(active_dir, filename)
            try:
                shutil.copy2(src_file, dst_file)
            except Exception as e:
                print(f"Failed to copy {filename}. Reason: {e}")
    else:
        print("Error: blank_slate directory not found. Cannot restore templates.")
        
    # 3. Clear application tracking file
    if os.path.exists(tracking_file):
        try:
            with open(tracking_file, 'w', encoding='utf-8') as f:
                f.write("# Application Tracking\n\n| ID | Company | Role | Variant | Status | Date | ATS Score |\n|---|---|---|---|---|---|---|\n")
            print("Cleared application_tracking.md")
        except Exception as e:
            print(f"Failed to clear tracking file. Reason: {e}")
            
    # 4. Clear build folder (Temp PDF collection)
    build_dir = os.path.join(base_dir, 'build')
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            print("Purged build/ directory (temporary PDFs)")
        except Exception as e:
            print(f"Failed to delete build directory. Reason: {e}")
            
    print("\nSUCCESS: Repository has been restored to factory 'Jane Doe' settings.")

if __name__ == "__main__":
    scrub_data()
