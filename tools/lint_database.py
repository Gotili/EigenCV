"""
LaTeX Database Linter.

This script scans the active JSON database files for unescaped characters 
(e.g., %, &, $, #) that would crash the pdflatex compiler.
"""
import os
import json
import re

def lint_database(active_dir=None):
    if active_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        active_dir = os.path.join(base_dir, 'cv', 'database', 'active')
        
    if not os.path.exists(active_dir):
        return
        
    # Regex to find unescaped %, &, $, #. 
    # It looks for characters that are NOT preceded by a backslash.
    # Note: This is a simplistic check and won't catch everything, but helps with common mistakes.
    unescaped_pattern = re.compile(r'(?<!\\)([%&$#_])')
    
    warnings = []
    
    for filename in os.listdir(active_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(active_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            def check_dict(d, path=""):
                if isinstance(d, dict):
                    for k, v in d.items():
                        check_dict(v, f"{path}.{k}" if path else k)
                elif isinstance(d, list):
                    for i, v in enumerate(d):
                        check_dict(v, f"{path}[{i}]")
                elif isinstance(d, str):
                    matches = unescaped_pattern.findall(d)
                    if matches:
                        warnings.append(f"File: {filename} | Key: {path} | Suspicious unescaped characters: {', '.join(set(matches))}")
                        
            check_dict(data)
            
        except Exception as e:
            warnings.append(f"Could not parse {filename}: {e}")
            
    if warnings:
        print("\n--- LaTeX Linter Warnings in cv/database/active/ ---")
        for w in warnings:
            print(f"   - {w}")
        print("   (Ensure characters like % or & are escaped as \\% or \\& if they are meant as literal text.)\n")
        
if __name__ == "__main__":
    lint_database()
