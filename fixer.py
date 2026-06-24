import os

with open('cv/scripts/cv_compiler.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I want to extract the code for auto_update_tracking and compile PDFs and just append it inline.
# Let's just find the index of "    # Auto-Update Tracking and Makefiles\n    update_tracking_and_make(config_path, config)"
# and replace everything after it with the correct inline code.

start_idx = content.find("    # Auto-Update Tracking and Makefiles\n    update_tracking_and_make(config_path, config)")

if start_idx != -1:
    content = content[:start_idx]
    
    inline_code = """    # Auto-Update Tracking and Makefiles
    try:
        abs_config_path = os.path.abspath(config_path)
        folder_name = os.path.basename(os.path.dirname(abs_config_path))
        
        parts = folder_name.split('-')
        if len(parts) >= 4 and folder_name.startswith(tuple(str(i) for i in range(10))):
            app_id = parts[0]
            company = parts[2]
            variant = "-".join(parts[3:])
        else:
            # Fallback for manually renamed folders
            app_id = "XX"
            company = "".join(c if c.isalnum() else "_" for c in (config.cover_letter.company_name if config.cover_letter else "Custom"))
            variant = folder_name
            
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        tracking_path = os.path.join(base_dir, 'application_tracking.md')
        make_path = os.path.join(base_dir, 'application-packages', 'application-packages.mk')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(make_path), exist_ok=True)
        
        # Update MK file
        if os.path.exists(make_path):
            with open(make_path, 'r', encoding='utf-8') as f:
                make_content = f.read()
        else:
            make_content = ""
            
        rule_name = f"application-{folder_name}"
        if rule_name not in make_content:
            with open(make_path, 'a', encoding='utf-8') as f:
                f.write(f"\\n{rule_name}:\\n\\t$(MAKE) -C application-packages/{folder_name}\\n")
            print(f"Added {rule_name} to application-packages.mk")
        
        # Update Tracking MD
        file_existed = os.path.exists(tracking_path)
        if file_existed:
            with open(tracking_path, 'r', encoding='utf-8') as f:
                tracking_content = f.read()
        else:
            tracking_content = ""
            
        if f"| {app_id} |" not in tracking_content:
            from datetime import date
            today = date.today().strftime("%Y-%m-%d")
            new_row = f"| {app_id} | {company} | {config.job_title} | {variant} | Generated | {today} | ATS |\\n"
            with open(tracking_path, 'a', encoding='utf-8') as f:
                if not file_existed:
                    f.write("# Application Tracking\\n\\n| ID | Company | Role | Variant | Status | Date | ATS Score |\\n|---|---|---|---|---|---|---|\\n")
                f.write(new_row)
            console.print(f"[bold green]Appended tracking row to application_tracking.md[/bold green]")
            
        # Automatically compile the PDFs using pdflatex
        console.print("[bold cyan]Auto-compiling PDFs with pdflatex...[/bold cyan]")
        import subprocess
        tex_files = [output_path]
        if config.cover_letter:
            cl_output_path = os.path.join(os.path.dirname(config_path), cl_filename)
            tex_files.append(cl_output_path)
            
        for tex_file in tex_files:
            try:
                # Run pdflatex twice for cross-references/geometry
                for _ in range(2):
                    subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", os.path.basename(tex_file)],
                        cwd=os.path.dirname(abs_config_path),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True
                    )
                console.print(f"[bold green]Successfully compiled {os.path.basename(tex_file).replace('.tex', '.pdf')}[/bold green]")
            except subprocess.CalledProcessError:
                console.print(f"[bold red]Failed to compile {os.path.basename(tex_file)}. Check the .log file.[/bold red]")
            except FileNotFoundError:
                console.print("[bold red]pdflatex command not found. Please install TeX Live or MiKTeX.[/bold red]")
                
    except Exception as e:
        console.print(f"[bold red]Warning: Failed to auto-update tracking files/compile PDFs: {e}[/bold red]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cv_compiler.py <path_to_build_config.json>")
        sys.exit(1)
    main(sys.argv[1])
"""
    content += inline_code

    with open('cv/scripts/cv_compiler.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed cv_compiler.py")
