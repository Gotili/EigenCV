import pytest
import os
import sys
from jinja2 import Environment, FileSystemLoader

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'cv', 'scripts'))

from cv_compiler import sanitize_latex_text

def test_template_rendering_preserves_latex_bullets():
    template_dir = os.path.join(base_dir, 'cv', 'template')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )
    env.filters['sanitize_latex_text'] = sanitize_latex_text
    
    template = env.get_template('eigencv_resume.tex.j2')
    
    # Dummy data
    test_context = {
        'job_title': '**Data Engineer**',
        'profile': 'Test profile with **bold** and 100%!',
        'skill_categories': [
            {'name': 'Data', 'skills': 'Python, SQL'},
            {'name': 'Data', 'skills': 'Python, SQL'},
            {'name': 'Data', 'skills': 'Python, SQL'},
            {'name': 'Data', 'skills': 'Python, SQL'},
            {'name': 'Data', 'skills': 'Python, SQL'},
            {'name': 'Data', 'skills': 'Python, SQL'},
        ],
        'experience': [
            {
                'title': 'Test Role',
                'dates': '2020-2021',
                'company': 'Test Corp',
                'location': 'Remote',
                'bullets': [r'\textbf{Raw LaTeX Bullet} with 100\%']
            }
        ],
        'projects': [r'\textbf{Raw Project}'],
        'education': [r'\textbf{Raw Edu}'],
        'extracurriculars_title': 'Extras',
        'extracurriculars': [r'\textbf{Raw Extra}'],
        'languages': [r'\textbf{Raw Lang}'],
        'company_accent_color': '000000',
        'i18n': {
            'experience': 'Exp', 'education': 'Edu', 'projects': 'Proj',
            'skills': 'Skills', 'languages': 'Lang', 'profile': 'Prof'
        },
        'section_order': ['Profile', 'Skills', 'Experience', 'Projects', 'Education', 'Extracurriculars', 'Languages']
    }
    
    rendered = template.render(**test_context)
    
    # 1. Verify that Markdown was converted in the profile
    assert r'\textbf{bold}' in rendered
    assert r'100\%!' in rendered
    assert r'\textbf{Data Engineer}' in rendered
    
    # 2. Verify that RAW LaTeX bullets were NOT double-escaped
    assert r'\textbf{Raw LaTeX Bullet} with 100\%' in rendered
    assert r'\textbackslash{}textbf' not in rendered
