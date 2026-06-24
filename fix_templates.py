import glob

files = glob.glob("cv/template/*.j2")

replacements = [
    ("{{ bullet | sanitize_latex_text }}", "{{ bullet }}"),
    ("{{ project | sanitize_latex_text }}", "{{ project }}"),
    ("{{ edu | sanitize_latex_text }}", "{{ edu }}"),
    ("{{ extra | sanitize_latex_text }}", "{{ extra }}"),
    ("{{ lang | sanitize_latex_text }}", "{{ lang }}"),
    ("{{- bullet | sanitize_latex_text -}}", "{{- bullet -}}"),
    ("{{- proj | sanitize_latex_text -}}", "{{- proj -}}"),
    ("{{- edu | sanitize_latex_text -}}", "{{- edu -}}"),
    ("{{- extra | sanitize_latex_text -}}", "{{- extra -}}"),
    ("{{- lang | sanitize_latex_text -}}", "{{- lang -}}")
]

for f in files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
        
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(f, "w", encoding="utf-8") as file:
        file.write(content)
