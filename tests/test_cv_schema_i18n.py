import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

base_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(base_dir / "cv" / "scripts"))

import cv_schema
from cv_schema import BuildConfig


def _loc(de, en):
    return {"de-DE": de, "en-US": en}


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def schema_fixture_db(tmp_path, monkeypatch):
    fake_repo = tmp_path / "repo"
    scripts_dir = fake_repo / "cv" / "scripts"
    active_dir = fake_repo / "cv" / "database" / "active"
    scripts_dir.mkdir(parents=True)
    active_dir.mkdir(parents=True)

    monkeypatch.setattr(cv_schema, "__file__", str(scripts_dir / "cv_schema.py"))

    _write_json(
        active_dir / "experience.json",
        {
            "tech_corp": {
                "company": "Example Corp",
                "location": "Berlin",
                "dates": "2021 - 2024",
                "bullets": {
                    "platform": "Architected a platform.",
                },
            }
        },
    )
    _write_json(active_dir / "projects.json", {"compiler": "Built a deterministic compiler."})
    _write_json(active_dir / "education.json", {"msc": "MSc Computer Science"})
    _write_json(active_dir / "extracurriculars.json", {"mentoring": "Mentored junior engineers."})
    _write_json(active_dir / "languages.json", {"english": "English (Fluent)"})

    return active_dir


def _valid_payload():
    return {
        "job_title": "Senior Software Engineer",
        "keywords": "Compiler, tests",
        "geometry_options": "left=0.625in",
        "company_accent_color": "4285F4",
        "profile": "Profile text.",
        "skill_categories": [
            {"name": "Languages", "skills": "Python"},
            {"name": "Frameworks", "skills": "Pydantic"},
            {"name": "Data", "skills": "JSON"},
            {"name": "Cloud", "skills": "AWS"},
            {"name": "Tools", "skills": "Git"},
            {"name": "Soft Skills", "skills": "Mentoring"},
        ],
        "experience": {
            "tech_corp": {
                "title": "Technical Lead",
                "bullets": ["platform"],
            }
        },
        "projects": ["compiler"],
        "education": ["msc"],
        "extracurriculars_title": "Activities",
        "extracurriculars": ["mentoring"],
        "languages": ["english"],
        "missing_skills": [],
        "cover_letter": {
            "company_name": "Example Corp",
            "recruiting_team": "Engineering Team",
            "location": "Berlin",
            "subject_role": "Senior Software Engineer",
            "salutation": "Dear Engineering Team,",
            "intro_paragraph": "Short intro.",
            "body_paragraphs": ["Core argument."],
            "outro_paragraph": "Short outro.",
        },
        "probability_matrix": {
            "invitation_probability": "80 % - Strong.",
            "technical_pass_probability": "75 % - Solid.",
            "job_offer_probability": "60 % - Realistic.",
            "salary_estimate": "90k - 110k.",
            "biggest_vulnerability": "None.",
        },
    }


def test_scalar_legacy_payload_without_target_locale_still_validates(schema_fixture_db):
    config = BuildConfig.model_validate(_valid_payload())

    assert config.job_title == "Senior Software Engineer"


def test_explicit_allowed_target_locale_validates(schema_fixture_db):
    payload = _valid_payload()
    payload["target_locale"] = "de-DE"

    config = BuildConfig.model_validate(payload)

    assert config.target_locale == "de-DE"


@pytest.mark.parametrize("bad_locale", ["en", "pt-BR"])
def test_explicit_target_locale_rejects_short_or_unsupported_values(schema_fixture_db, bad_locale):
    payload = _valid_payload()
    payload["target_locale"] = bad_locale

    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(payload)

    message = str(exc_info.value)
    assert "target_locale" in message
    assert bad_locale in message


def test_top_level_build_config_prose_accepts_localizable_maps(schema_fixture_db):
    payload = _valid_payload()
    payload["target_locale"] = "de-DE"
    payload["job_title"] = _loc("Senior Softwareentwickler", "Senior Software Engineer")
    payload["keywords"] = _loc("Compiler, Tests", "Compiler, tests")
    payload["profile"] = _loc("Profiltext.", "Profile text.")
    payload["extracurriculars_title"] = _loc("Engagement", "Activities")

    config = BuildConfig.model_validate(payload)

    assert config.job_title["de-DE"] == "Senior Softwareentwickler"
    assert config.profile["en-US"] == "Profile text."


def test_localizable_map_rejects_unsupported_locale_key(schema_fixture_db):
    payload = _valid_payload()
    payload["job_title"] = {"de-DE": "Text", "pt-BR": "Texto"}

    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(payload)

    message = str(exc_info.value)
    assert "job_title" in message
    assert "pt-BR" in message


def test_nested_localizable_skill_category_fields_validate(schema_fixture_db):
    payload = _valid_payload()
    payload["skill_categories"][0]["name"] = _loc("Sprachen", "Languages")
    payload["skill_categories"][0]["skills"] = _loc("Python, SQL", "Python, SQL")

    config = BuildConfig.model_validate(payload)

    assert config.skill_categories[0].name["de-DE"] == "Sprachen"


def test_nested_localizable_experience_title_validates(schema_fixture_db):
    payload = _valid_payload()
    payload["experience"]["tech_corp"]["title"] = _loc("Technischer Leiter", "Technical Lead")

    config = BuildConfig.model_validate(payload)

    assert config.experience["tech_corp"].title["en-US"] == "Technical Lead"


def test_nested_localizable_cover_letter_fields_validate(schema_fixture_db):
    payload = _valid_payload()
    payload["cover_letter"]["company_name"] = _loc("Beispiel GmbH", "Example Corp")
    payload["cover_letter"]["subject_role"] = _loc("Senior Softwareentwickler", "Senior Software Engineer")
    payload["cover_letter"]["intro_paragraph"] = _loc("Kurzer Einstieg.", "Short intro.")
    payload["cover_letter"]["body_paragraphs"] = [_loc("Kernargument.", "Core argument.")]
    payload["cover_letter"]["outro_paragraph"] = _loc("Kurzer Abschluss.", "Short outro.")

    config = BuildConfig.model_validate(payload)

    assert config.cover_letter.subject_role["de-DE"] == "Senior Softwareentwickler"
    assert config.cover_letter.body_paragraphs[0]["en-US"] == "Core argument."


def test_nested_localizable_probability_matrix_fields_validate(schema_fixture_db):
    payload = _valid_payload()
    payload["probability_matrix"]["invitation_probability"] = _loc("80 % - Stark.", "80 % - Strong.")
    payload["probability_matrix"]["biggest_vulnerability"] = _loc("Keine.", "None.")

    config = BuildConfig.model_validate(payload)

    assert config.probability_matrix.invitation_probability["de-DE"] == "80 % - Stark."


def test_skill_cluster_validator_checks_localized_skill_values(schema_fixture_db):
    payload = _valid_payload()
    payload["skill_categories"][0]["skills"] = {
        "de-DE": "[Python, Java]",
        "en-US": "Python",
    }

    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(payload)

    assert "Unresolved skill cluster" in str(exc_info.value)


def test_profile_length_validator_checks_localized_profile_values(schema_fixture_db):
    payload = _valid_payload()
    payload["profile"] = {
        "de-DE": "A" * 1001,
        "en-US": "Short profile.",
    }

    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(payload)

    message = str(exc_info.value)
    assert "profile" in message
    assert "at most 1000" in message


def test_cover_letter_length_validator_checks_localized_text_values(schema_fixture_db):
    payload = _valid_payload()
    payload["cover_letter"]["intro_paragraph"] = {
        "de-DE": "word " * 401,
        "en-US": "Short intro.",
    }
    payload["cover_letter"]["body_paragraphs"] = [
        {
            "de-DE": "body",
            "en-US": "body",
        }
    ]
    payload["cover_letter"]["outro_paragraph"] = {
        "de-DE": "outro",
        "en-US": "outro",
    }

    with pytest.raises(ValidationError) as exc_info:
        BuildConfig.model_validate(payload)

    assert "Cover letter is too long" in str(exc_info.value)
