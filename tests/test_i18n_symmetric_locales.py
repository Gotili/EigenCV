import json
import sys
from pathlib import Path

import pytest

base_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(base_dir / "cv" / "scripts"))


def _i18n():
    import cv_i18n

    return cv_i18n


def _loc(de, en):
    return {"de-DE": de, "en-US": en}


def _write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_db(tmp_path, mode):
    db = tmp_path / f"db_{mode}"
    db.mkdir()

    if mode == "scalar":
        company = "Example Corp"
        bullet = "Architected a platform."
        project = "Built a deterministic compiler."
        i18n = {
            "experience": "Experience",
            "education": "Education",
            "projects": "Projects",
            "skills": "Skills",
            "languages": "Languages",
            "profile": "Profile",
        }
    elif mode == "missing_de":
        company = _loc("Beispiel GmbH", "Example Corp")
        bullet = {"en-US": "Architected a platform."}
        project = _loc(
            "Baute einen deterministischen Compiler.",
            "Built a deterministic compiler.",
        )
        i18n = {"experience": _loc("Berufserfahrung", "Experience")}
    else:
        company = "Shared Corp" if mode == "mixed" else _loc("Beispiel GmbH", "Example Corp")
        bullet = _loc("Architektur einer Plattform.", "Architected a platform.")
        project = _loc(
            "Baute einen deterministischen Compiler.",
            "Built a deterministic compiler.",
        )
        i18n = {
            "experience": _loc("Berufserfahrung", "Experience"),
            "education": _loc("Ausbildung", "Education"),
            "projects": _loc("Projekte", "Projects"),
            "skills": _loc("Faehigkeiten", "Skills"),
            "languages": _loc("Sprachen", "Languages"),
            "profile": _loc("Profil", "Profile"),
        }

    _write_json(
        db / "experience.json",
        {
            "tech_corp": {
                "company": company,
                "location": "Berlin",
                "dates": "2021 - 2024",
                "bullets": {"platform": bullet},
            }
        },
    )
    _write_json(db / "projects.json", {"compiler": project})
    _write_json(db / "education.json", {"msc": "MSc Computer Science"})
    _write_json(db / "extracurriculars.json", {"mentoring": "Mentored junior engineers."})
    _write_json(db / "languages.json", {"english": "English (Fluent)"})
    _write_json(db / "i18n.json", i18n)
    (db / "metadata.tex").write_text(r"\newcommand{\cvlocale}{en}" + "\n", encoding="utf-8")
    return db


def _config(mode="scalar", target_locale="de-DE"):
    localized = mode in {"localized", "mixed", "missing_de"}
    text = _loc if localized else lambda de, en: en
    title = text("Technischer Leiter", "Technical Lead")

    return {
        "target_locale": target_locale,
        "job_title": text("Senior Softwareentwickler", "Senior Software Engineer"),
        "keywords": text("Compiler, Tests", "Compiler, tests"),
        "geometry_options": "left=0.625in",
        "profile": text("Profiltext.", "Profile text."),
        "skill_categories": [
            {"name": text("Sprachen", "Languages"), "skills": "Python"},
            {"name": "Frameworks", "skills": "Pydantic"},
            {"name": "Daten", "skills": "JSON"},
            {"name": "Cloud", "skills": "AWS"},
            {"name": "Tools", "skills": "Git"},
            {"name": "Soft Skills", "skills": "Mentoring"},
        ],
        "experience": {
            "tech_corp": {
                "title": title,
                "bullets": ["platform"],
            }
        },
        "projects": ["compiler"],
        "education": ["msc"],
        "extracurriculars_title": text("Engagement", "Activities"),
        "extracurriculars": ["mentoring"],
        "languages": ["english"],
        "missing_skills": [],
        "cover_letter": {
            "company_name": "Example Corp",
            "recruiting_team": text("Engineering Team", "Engineering Team"),
            "location": "Berlin",
            "subject_role": title,
            "salutation": text("Dear Engineering Team,", "Dear Engineering Team,"),
            "intro_paragraph": text("Kurzer Einstieg.", "Short intro."),
            "body_paragraphs": [text("Kernargument.", "Core argument.")],
            "outro_paragraph": text("Kurzer Abschluss.", "Short outro."),
        },
        "probability_matrix": {
            "invitation_probability": text("80 % - Stark.", "80 % - Strong."),
            "technical_pass_probability": text("75 % - Solide.", "75 % - Solid."),
            "job_offer_probability": text("60 % - Realistisch.", "60 % - Realistic."),
            "salary_estimate": text("90k - 110k.", "90k - 110k."),
            "biggest_vulnerability": text("Keine.", "None."),
        },
    }


@pytest.fixture
def scalar_db(tmp_path):
    return _write_db(tmp_path, "scalar")


@pytest.fixture
def localized_db(tmp_path):
    return _write_db(tmp_path, "localized")


@pytest.fixture
def mixed_db(tmp_path):
    return _write_db(tmp_path, "mixed")


@pytest.fixture
def missing_de_db(tmp_path):
    return _write_db(tmp_path, "missing_de")


def test_allowed_locales_are_regex_valid_and_allowlisted():
    m = _i18n()

    assert m.validate_locale_code("de-DE") == "de-DE"
    assert m.validate_locale_code("en-US") == "en-US"


@pytest.mark.parametrize("bad_locale", ["en", "de", "english", "de_DE", "en-us", "EN-US", "pt-BR", ""])
def test_malformed_or_unsupported_target_locale_raises_clear_error(bad_locale):
    m = _i18n()

    with pytest.raises(m.LocaleValidationError) as exc_info:
        m.validate_locale_code(bad_locale)

    assert bad_locale in str(exc_info.value)
    assert "de-DE" in str(exc_info.value)
    assert "en-US" in str(exc_info.value)


def test_locale_map_with_unsupported_key_raises_path_key_and_supported_locales():
    m = _i18n()

    with pytest.raises(m.LocaleValidationError) as exc_info:
        m.resolve_localized(
            {"de-DE": "Text", "pt-BR": "Texto"},
            "de-DE",
            "profile",
        )

    message = str(exc_info.value)
    assert "profile" in message
    assert "pt-BR" in message
    assert "de-DE" in message
    assert "en-US" in message


def test_legacy_metadata_en_is_bridge_only_without_explicit_target_locale():
    m = _i18n()
    metadata = r"\newcommand{\cvlocale}{en}"

    assert m.resolve_target_locale({}, metadata_text=metadata) == "en-US"

    with pytest.raises(m.LocaleValidationError):
        m.resolve_target_locale({"target_locale": "en"}, metadata_text=metadata)


def test_explicit_build_config_target_locale_wins_over_metadata():
    m = _i18n()
    metadata = r"\newcommand{\cvlocale}{en}"

    assert m.resolve_target_locale({"target_locale": "de-DE"}, metadata_text=metadata) == "de-DE"


def test_scalar_field_renders_identically_for_any_requested_locale(scalar_db):
    m = _i18n()

    de_context = m.resolve_application_context(_config("scalar", "de-DE"), scalar_db)
    en_context = m.resolve_application_context(_config("scalar", "en-US"), scalar_db)

    de_context.pop("target_locale", None)
    en_context.pop("target_locale", None)
    assert de_context == en_context


def test_locale_map_with_requested_locale_present_resolves_that_locale():
    m = _i18n()
    value = {"de-DE": "Berufserfahrung", "en-US": "Experience"}

    assert m.resolve_localized(value, "de-DE", "i18n.experience") == "Berufserfahrung"
    assert m.resolve_localized(value, "en-US", "i18n.experience") == "Experience"


def test_locale_map_with_requested_locale_absent_raises_path_and_locale():
    m = _i18n()

    with pytest.raises(m.LocaleResolutionError) as exc_info:
        m.resolve_localized({"en-US": "Experience"}, "de-DE", "i18n.experience")

    assert "i18n.experience" in str(exc_info.value)
    assert "de-DE" in str(exc_info.value)


def test_en_us_is_not_privileged_in_new_resolver_path():
    m = _i18n()

    with pytest.raises(m.LocaleResolutionError) as exc_info:
        m.resolve_localized({"de-DE": "Berufserfahrung"}, "en-US", "i18n.experience")

    assert "i18n.experience" in str(exc_info.value)
    assert "en-US" in str(exc_info.value)


def test_fully_localized_sample_record_round_trips_in_de_de_and_en_us(localized_db):
    m = _i18n()

    de_context = m.resolve_application_context(_config("localized", "de-DE"), localized_db)
    en_context = m.resolve_application_context(_config("localized", "en-US"), localized_db)

    assert de_context["job_title"] == "Senior Softwareentwickler"
    assert en_context["job_title"] == "Senior Software Engineer"
    assert de_context["i18n"]["experience"] == "Berufserfahrung"
    assert en_context["i18n"]["experience"] == "Experience"
    assert de_context["experience"][0]["bullets"] == ["Architektur einer Plattform."]
    assert en_context["experience"][0]["bullets"] == ["Architected a platform."]


def test_mixed_scalar_and_localized_fields_resolve_correctly(mixed_db):
    m = _i18n()

    context = m.resolve_application_context(_config("mixed", "de-DE"), mixed_db)

    assert context["experience"][0]["company"] == "Shared Corp"
    assert context["experience"][0]["title"] == "Technischer Leiter"
    assert context["languages"] == ["English (Fluent)"]


def test_selected_record_missing_target_locale_fails_loud_before_rendering(missing_de_db):
    m = _i18n()

    with pytest.raises(m.LocaleResolutionError) as exc_info:
        m.resolve_application_context(_config("missing_de", "de-DE"), missing_de_db)

    assert "de-DE" in str(exc_info.value)
    assert "experience.tech_corp.bullets.platform" in str(exc_info.value)


def test_resolve_localized_tree_resolves_nested_maps_and_preserves_plain_values():
    m = _i18n()
    value = {
        "title": _loc("Titel", "Title"),
        "metadata": {"kind": "normal", "de-DE": "plain key"},
        "items": [
            _loc("Eins", "One"),
            "plain",
            {"label": _loc("Etikett", "Label")},
        ],
    }

    resolved = m.resolve_localized_tree(value, "de-DE", "build_config")

    assert resolved == {
        "title": "Titel",
        "metadata": {"kind": "normal", "de-DE": "plain key"},
        "items": ["Eins", "plain", {"label": "Etikett"}],
    }


def test_resolve_localized_tree_missing_locale_raises_path_and_locale():
    m = _i18n()
    value = {
        "cover_letter": {
            "body_paragraphs": [
                {"en-US": "Core argument."},
            ],
        },
    }

    with pytest.raises(m.LocaleResolutionError) as exc_info:
        m.resolve_localized_tree(value, "de-DE", "build_config")

    message = str(exc_info.value)
    assert "de-DE" in message
    assert "build_config.cover_letter.body_paragraphs.0" in message


def _write_schema_active_db(tmp_path):
    fake_repo = tmp_path / "repo"
    scripts_dir = fake_repo / "cv" / "scripts"
    active_dir = fake_repo / "cv" / "database" / "active"
    scripts_dir.mkdir(parents=True)
    active_dir.mkdir(parents=True)

    _write_json(
        active_dir / "experience.json",
        {
            "tech_corp": {
                "company": "Example Corp",
                "location": "Berlin",
                "dates": "2021 - 2024",
                "bullets": {"platform": "Architected a platform."},
            },
        },
    )
    _write_json(active_dir / "projects.json", {"compiler": "Built a deterministic compiler."})
    _write_json(active_dir / "education.json", {"msc": "MSc Computer Science"})
    _write_json(active_dir / "extracurriculars.json", {"mentoring": "Mentored junior engineers."})
    _write_json(active_dir / "languages.json", {"english": "English (Fluent)"})
    return scripts_dir


def test_compiler_render_config_resolves_build_config_prose_maps(tmp_path, monkeypatch):
    import cv_schema

    scripts_dir = _write_schema_active_db(tmp_path)
    monkeypatch.setattr(cv_schema, "__file__", str(scripts_dir / "cv_schema.py"))
    import cv_compiler
    payload = _config("localized", "de-DE")
    payload["cover_letter"]["recruiting_team"] = "Engineering Team"
    payload["cover_letter"]["salutation"] = "Dear Engineering Team,"
    payload["probability_matrix"]["technical_pass_probability"] = "75 % - Solid."
    payload["probability_matrix"]["job_offer_probability"] = "60 % - Realistic."
    payload["probability_matrix"]["salary_estimate"] = "90k - 110k."

    config = cv_schema.BuildConfig.model_validate(payload)
    render_config = cv_compiler._resolve_config_for_render(config, "en")

    assert render_config.job_title == "Senior Softwareentwickler"
    assert render_config.keywords == "Compiler, Tests"
    assert render_config.profile == "Profiltext."
    assert render_config.skill_categories[0].name == "Sprachen"
    assert render_config.experience["tech_corp"].title == "Technischer Leiter"
    assert render_config.extracurriculars_title == "Engagement"
    assert render_config.cover_letter.subject_role == "Technischer Leiter"
    assert render_config.cover_letter.body_paragraphs == ["Kernargument."]
    assert render_config.probability_matrix.invitation_probability == "80 % - Stark."
    assert render_config.probability_matrix.biggest_vulnerability == "Keine."


def test_compiler_rendered_latex_has_resolved_build_config_prose_maps(tmp_path, monkeypatch):
    import jinja2
    import cv_schema

    scripts_dir = _write_schema_active_db(tmp_path)
    monkeypatch.setattr(cv_schema, "__file__", str(scripts_dir / "cv_schema.py"))
    import cv_compiler

    payload = _config("localized", "de-DE")
    payload["cover_letter"]["recruiting_team"] = "Engineering Team"
    payload["cover_letter"]["salutation"] = "Dear Engineering Team,"
    payload["probability_matrix"]["technical_pass_probability"] = "75 % - Solid."
    payload["probability_matrix"]["job_offer_probability"] = "60 % - Realistic."
    payload["probability_matrix"]["salary_estimate"] = "90k - 110k."

    config = cv_schema.BuildConfig.model_validate(payload)
    render_config = cv_compiler._resolve_config_for_render(config, "en")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(base_dir / "cv" / "template")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["sanitize_latex_text"] = cv_compiler.sanitize_latex_text

    rendered = env.get_template("eigencv_resume.tex.j2").render(
        geometry_options=config.geometry_options,
        keywords=render_config.keywords,
        cvcolor="awesome-emerald",
        section_order=["Profile", "Skills", "Experience", "Extracurriculars"],
        user_first_name="Test",
        user_last_name="User",
        job_title=render_config.job_title,
        profile=render_config.profile,
        skill_categories=[cat.model_dump() for cat in render_config.skill_categories],
        experience=[
            {
                "company": "Example Corp",
                "location": "Berlin",
                "dates": "2021 - 2024",
                "title": render_config.experience["tech_corp"].title,
                "bullets": ["Architected a platform."],
            }
        ],
        projects=[],
        education=[],
        extracurriculars_title=render_config.extracurriculars_title,
        extracurriculars=["Mentored junior engineers."],
        languages=[],
        company_accent_color=None,
        i18n={
            "experience": "Berufserfahrung",
            "skills": "Faehigkeiten",
            "profile": "Profil",
        },
    )

    assert "Senior Softwareentwickler" in rendered
    assert "Profiltext." in rendered
    assert "Sprachen" in rendered
    assert "Technischer Leiter" in rendered
    assert "Engagement" in rendered
    assert "{'de-DE'" not in rendered
    assert "\"de-DE\"" not in rendered
    assert "en-US" not in rendered
