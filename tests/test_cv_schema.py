import pytest
import os
import json
from pydantic import ValidationError
import sys

# Add the cv/scripts folder to sys.path so we can import cv_schema
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'cv', 'scripts'))

from cv_schema import BuildConfig

def get_valid_payload():
    def load_db(name):
        with open(os.path.join(base_dir, 'cv', 'database', 'active', name), 'r', encoding='utf-8') as f:
            return json.load(f)

    exp = load_db('experience.json')
    proj = load_db('projects.json')
    edu = load_db('education.json')
    ext = load_db('extracurriculars.json')
    lang = load_db('languages.json')

    c_id = list(exp.keys())[0]
    b_ids = list(exp[c_id]['bullets'].keys())

    return {
        "job_title": "Test Engineer",
        "keywords": "Test",
        "geometry_options": "margin=1in",
        "profile": "Test profile",
        "skill_categories": [
            {"name": "Languages", "skills": "Python"},
            {"name": "ML", "skills": "PyTorch"},
            {"name": "Data", "skills": "SQL"},
            {"name": "Cloud", "skills": "AWS"},
            {"name": "DevOps", "skills": "Docker"},
            {"name": "Soft", "skills": "Agile"}
        ],
        "experience": {
            c_id: {
                "title": "Technical Lead",
                "bullets": b_ids
            }
        },
        "projects": list(proj.keys())[:1],
        "education": list(edu.keys())[:1],
        "extracurriculars_title": "Activities",
        "extracurriculars": list(ext.keys())[:1],
        "languages": list(lang.keys())[:1],
        "probability_matrix": {
            "invitation_probability": "90%",
            "technical_pass_probability": "90%",
            "job_offer_probability": "90%",
            "salary_estimate": "100k",
            "biggest_vulnerability": "none"
        }
    }

def test_valid_config():
    payload = get_valid_payload()
    config = BuildConfig(**payload)
    assert config.job_title == "Test Engineer"

def test_invalid_company_id():
    payload = get_valid_payload()
    payload["experience"]["fake_company"] = {
        "title": "Fake Title",
        "bullets": ["fake_bullet"]
    }
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig(**payload)
    assert "not found in experience.json" in str(exc_info.value)

def test_invalid_bullet_id():
    payload = get_valid_payload()
    c_id = list(payload["experience"].keys())[0]
    payload["experience"][c_id]["bullets"].append("fake_bullet_123")
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig(**payload)
    assert "not found under company" in str(exc_info.value)

def test_below_60_percent_bullets():
    payload = get_valid_payload()
    c_id = list(payload["experience"].keys())[0]
    # Keep only the first 10% (less than 60%) to guarantee failure
    total_bullets = len(payload["experience"][c_id]["bullets"])
    payload["experience"][c_id]["bullets"] = payload["experience"][c_id]["bullets"][:1]
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig(**payload)
    assert "You MUST provide AT LEAST" in str(exc_info.value)

def test_invalid_project_id():
    payload = get_valid_payload()
    payload["projects"].append("fake_project_999")
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig(**payload)
    assert "not found in projects.json" in str(exc_info.value)

def test_invalid_skill_cluster():
    payload = get_valid_payload()
    payload["skill_categories"][0]["skills"] = "[Python, Java]"
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig(**payload)
    assert "Unresolved skill cluster or synonym detected" in str(exc_info.value)

def test_cover_letter_too_long():
    payload = get_valid_payload()
    long_text = "word " * 500
    payload["cover_letter"] = {
        "company_name": "Test",
        "location": "Remote",
        "subject_role": "Role",
        "intro_paragraph": long_text,
        "body_paragraphs": ["body"],
        "outro_paragraph": "outro"
    }
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig(**payload)
    assert "Cover letter is too long" in str(exc_info.value)
