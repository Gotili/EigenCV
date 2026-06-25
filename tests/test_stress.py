import pytest
from pydantic import ValidationError
import sys
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'cv', 'scripts'))

from cv_schema import BuildConfig
# Use a trick to import check_eigentruth even if we can't easily import everything from cv_compiler
# Alternatively, since cv_compiler is a script, we can just extract the function or import it.
import cv_compiler

def test_pydantic_id_validation_broken_id():
    """Test that pydantic catches invalid bullet IDs and throws ValidationError."""
    # A dummy config based on the one we used for stress testing
    bad_config = {
      "job_title": "Test Job",
      "keywords": "C++",
      "geometry_options": "left=0.625in, right=0.625in, top=0.45in, bottom=0.45in",
      "company_accent_color": "4285F4",
      "profile": "Test Profile",
      "skill_categories": [
        {"name": "Languages", "skills": "C/C++"},
        {"name": "Frameworks", "skills": "React"},
        {"name": "Databases", "skills": "PostgreSQL"},
        {"name": "DevOps", "skills": "Docker"},
        {"name": "Tools", "skills": "Git"},
        {"name": "Soft Skills", "skills": "Leadership"}
      ],
      "experience": {
        "acme_corp": {
          "title": "Senior Data Engineer",
          "bullets": [
            "acme_corp_lead",
            "acme_corp_ml",
            "acme_corp_arch",
            "i_made_this_up",
            "acme_corp_dummy2"
          ]
        }
      },
      "projects": ["project_alpha"],
      "education": ["msc_compsci"],
      "extracurriculars_title": "Open Source",
      "extracurriculars": ["open_source"],
      "languages": ["english", "german"],
      "probability_matrix": {
        "invitation_probability": "50%",
        "technical_pass_probability": "50%",
        "job_offer_probability": "50%",
        "salary_estimate": "€100k",
        "biggest_vulnerability": "None"
      }
    }
    
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(bad_config)
    
    error_msg = str(exc_info.value)
    assert "i_made_this_up" in error_msg
    assert "not found under company" in error_msg

def test_eigentruth_violation():
    """Test that the EigenTruth Lie Detector catches hallucinated skills."""
    # A fake config where the AI put 'Kubernetes' in missing_skills, but also sneaked it into the profile.
    config_dict = {
      "job_title": "Senior Cloud Developer",
      "keywords": "C++, Rust, Kubernetes, Docker",
      "geometry_options": "left=0.625in, right=0.625in, top=0.45in, bottom=0.45in",
      "company_accent_color": "4285F4",
      "profile": "Software Engineer specialized in Agentic Tooling. Passionate about building memory-safe infrastructure with Kubernetes and Docker.",
      "skill_categories": [
        {"name": "Languages", "skills": "C/C++"},
        {"name": "Frameworks", "skills": "React"},
        {"name": "Databases", "skills": "PostgreSQL"},
        {"name": "DevOps", "skills": "Docker"},
        {"name": "Tools", "skills": "Git"},
        {"name": "Soft Skills", "skills": "Leadership"}
      ],
      "experience": {
        "acme_corp": {
          "title": "Senior Data Engineer",
          "bullets": [
            "acme_corp_lead",
            "acme_corp_ml",
            "acme_corp_arch",
            "acme_corp_dummy1",
            "acme_corp_dummy2"
          ]
        }
      },
      "projects": ["project_alpha"],
      "education": ["msc_compsci"],
      "extracurriculars_title": "Open Source",
      "extracurriculars": ["open_source"],
      "languages": ["english", "spanish"],
      "missing_skills": ["Kubernetes"],
      "probability_matrix": {
        "invitation_probability": "50%",
        "technical_pass_probability": "50%",
        "job_offer_probability": "50%",
        "salary_estimate": "€100k",
        "biggest_vulnerability": "None"
      }
    }
    
    # Write to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(config_dict, tmp)
        tmp_path = tmp.name
        
    try:
        # It should fail the EigenTruth check when compiling
        with pytest.raises(cv_compiler.EigenTruthViolationError):
            cv_compiler.compile_cv(tmp_path)
    finally:
        os.unlink(tmp_path)


def test_pydantic_color_crash():
    """Test that invalid hex colors are caught by Pydantic before they crash the compiler."""
    # A valid config base
    config_dict = {
      "job_title": "Senior Cloud Developer",
      "keywords": "C++, Rust",
      "geometry_options": "left=0.625in",
      "company_accent_color": "red", # INVALID! Must be hex like 'FF0000'
      "profile": "Short profile.",
      "skill_categories": [
        {"name": "L", "skills": "C/C++"}, {"name": "F", "skills": "R"}, 
        {"name": "D", "skills": "P"}, {"name": "D", "skills": "D"}, 
        {"name": "T", "skills": "G"}, {"name": "S", "skills": "L"}
      ],
      "experience": {"acme_corp": {"title": "X", "bullets": ["acme_corp_lead"]}},
      "projects": ["project_alpha"],
      "education": ["msc_compsci"],
      "extracurriculars_title": "X",
      "extracurriculars": ["open_source"],
      "probability_matrix": {
        "invitation_probability": "50%", "technical_pass_probability": "50%",
        "job_offer_probability": "50%", "salary_estimate": "100k", "biggest_vulnerability": "None"
      }
    }
    
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(config_dict)
    
    error_msg = str(exc_info.value)
    assert "company_accent_color" in error_msg
    assert "String should match pattern" in error_msg


def test_pydantic_wall_of_text():
    """Test that extremely long profiles are blocked to prevent Layout DoS."""
    config_dict = {
      "job_title": "Senior Cloud Developer",
      "keywords": "C++, Rust",
      "geometry_options": "left=0.625in",
      "company_accent_color": "FF0000",
      "profile": "A" * 1500, # INVALID! Max length is 1000
      "skill_categories": [
        {"name": "L", "skills": "C/C++"}, {"name": "F", "skills": "R"}, 
        {"name": "D", "skills": "P"}, {"name": "D", "skills": "D"}, 
        {"name": "T", "skills": "G"}, {"name": "S", "skills": "L"}
      ],
      "experience": {"acme_corp": {"title": "X", "bullets": ["acme_corp_lead"]}},
      "projects": ["project_alpha"],
      "education": ["msc_compsci"],
      "extracurriculars_title": "X",
      "extracurriculars": ["open_source"],
      "probability_matrix": {
        "invitation_probability": "50%", "technical_pass_probability": "50%",
        "job_offer_probability": "50%", "salary_estimate": "100k", "biggest_vulnerability": "None"
      }
    }
    
    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(config_dict)
    
    error_msg = str(exc_info.value)
    assert "profile" in error_msg
    assert "String should have at most 1000 characters" in error_msg


def test_rapidfuzz_healer():
    """Test that slight typos in bullet IDs are auto-healed by RapidFuzz."""
    config_dict = {
      "job_title": "Test Job",
      "keywords": "C++",
      "geometry_options": "left=0.625in",
      "company_accent_color": "4285F4",
      "profile": "Short profile.",
      "skill_categories": [
        {"name": "L", "skills": "C/C++"}, {"name": "F", "skills": "R"}, 
        {"name": "D", "skills": "P"}, {"name": "D", "skills": "D"}, 
        {"name": "T", "skills": "G"}, {"name": "S", "skills": "L"}
      ],
      "experience": {
        "acme_corp": {
          "title": "Data Engineer",
          "bullets": [
            "acme_corp_ml", 
            "acme_corp_arch", 
            "acme_corp_dummy1", 
            "acme_corp_dummy2",
            "acme_corp_lea" # TYPO! Should be acme_corp_lead (close enough for RapidFuzz)
          ]
        }
      },
      "projects": ["project_alpha"],
      "education": ["msc_compsci"],
      "extracurriculars_title": "Open Source",
      "extracurriculars": ["open_source"],
      "probability_matrix": {
        "invitation_probability": "50%", "technical_pass_probability": "50%",
        "job_offer_probability": "50%", "salary_estimate": "100k", "biggest_vulnerability": "None"
      }
    }
    
    # Should not raise validation error because the typo is healed!
    config = BuildConfig.model_validate(config_dict)
    
    # Check that the ID was actually healed
    assert "acme_corp_lead" in config.experience["acme_corp"].bullets
    assert "acme_corp_lea" not in config.experience["acme_corp"].bullets


def test_locale_mismatch():
    """Test that requesting a foreign language CV crashes if the database is still in English."""
    config_dict = {
      "job_title": "Senior Cloud Developer",
      "keywords": "C++, Rust",
      "geometry_options": "left=0.625in",
      "company_accent_color": "4285F4",
      "profile": "Short profile.",
      "skill_categories": [
        {"name": "L", "skills": "C/C++"}, {"name": "F", "skills": "R"}, 
        {"name": "D", "skills": "P"}, {"name": "D", "skills": "D"}, 
        {"name": "T", "skills": "G"}, {"name": "S", "skills": "L"}
      ],
      "experience": {
        "acme_corp": {
          "title": "Senior Data Engineer",
          "bullets": [
            "acme_corp_lead",
            "acme_corp_ml",
            "acme_corp_arch",
            "acme_corp_dummy1",
            "acme_corp_dummy2"
          ]
        }
      },
      "projects": ["project_alpha"],
      "education": ["msc_compsci"],
      "extracurriculars_title": "X",
      "extracurriculars": ["open_source"],
      "probability_matrix": {
        "invitation_probability": "50%", "technical_pass_probability": "50%",
        "job_offer_probability": "50%", "salary_estimate": "100k", "biggest_vulnerability": "None"
      },
      "i18n_updates": {
        "locale_code": "de", # Trigger German locale check
        "translations": {}
      }
    }
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        json.dump(config_dict, tmp)
        tmp_path = tmp.name
        
    try:
        # cv_compiler should crash with a ValueError due to langdetect finding English text while locale='de'
        with pytest.raises(ValueError) as exc_info:
            cv_compiler.compile_cv(tmp_path)
            
        assert "Language mismatch" in str(exc_info.value)
    finally:
        os.unlink(tmp_path)
