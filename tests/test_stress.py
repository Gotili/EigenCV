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
        "carl_zeiss": {
          "title": "Senior Data Engineer",
          "bullets": [
            "zeiss_tech_lead",
            "zeiss_etl_pipelines",
            "zeiss_ml_anomaly",
            "i_made_this_up",
            "zeiss_evaluation_workflows"
          ]
        }
      },
      "projects": ["llm_workflow_orchestrator"],
      "education": ["phd_chemistry"],
      "extracurriculars_title": "Open Source",
      "extracurriculars": ["invited_speaker"],
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
        "carl_zeiss": {
          "title": "Senior Data Engineer",
          "bullets": [
            "zeiss_tech_lead",
            "zeiss_etl_pipelines",
            "zeiss_ml_anomaly",
            "zeiss_spc_drift",
            "zeiss_evaluation_workflows"
          ]
        }
      },
      "projects": ["llm_workflow_orchestrator"],
      "education": ["phd_chemistry"],
      "extracurriculars_title": "Open Source",
      "extracurriculars": ["invited_speaker"],
      "languages": ["english", "german"],
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

