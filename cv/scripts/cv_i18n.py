import json
import re
from pathlib import Path


SUPPORTED_LOCALES = ("de-DE", "en-US")
LOCALE_PATTERN = r"^[a-z]{2,3}-[A-Z]{2}$"

_LOCALE_RE = re.compile(LOCALE_PATTERN)


class LocaleValidationError(ValueError):
    pass


class LocaleResolutionError(ValueError):
    pass


def _supported_locales_message() -> str:
    return ", ".join(SUPPORTED_LOCALES)


def validate_locale_code(locale: str) -> str:
    """Validate the repo-supported BCP-47-style locale subset."""
    if not isinstance(locale, str) or not _LOCALE_RE.fullmatch(locale):
        raise LocaleValidationError(
            f"Invalid locale '{locale}'. Expected pattern {LOCALE_PATTERN}. "
            f"Supported locales: {_supported_locales_message()}."
        )
    if locale not in SUPPORTED_LOCALES:
        raise LocaleValidationError(
            f"Unsupported locale '{locale}'. "
            f"Supported locales: {_supported_locales_message()}."
        )
    return locale


def _extract_metadata_locale(metadata_text: str | None) -> str | None:
    if not metadata_text:
        return None
    match = re.search(r"\\newcommand\{\\cvlocale\}\{([^}]+)\}", metadata_text)
    if not match:
        return None
    return match.group(1).strip()


def resolve_target_locale(build_config: dict, metadata_text: str | None = None) -> str:
    if "target_locale" in build_config:
        return validate_locale_code(build_config["target_locale"])

    metadata_locale = _extract_metadata_locale(metadata_text)
    if metadata_locale == "en":
        return "en-US"
    if metadata_locale:
        return validate_locale_code(metadata_locale)
    return "en-US"


def is_locale_map(value) -> bool:
    """Return True for dictionaries shaped entirely as locale keyed maps."""
    return (
        isinstance(value, dict)
        and bool(value)
        and all(isinstance(key, str) and _LOCALE_RE.fullmatch(key) for key in value)
    )


def _validate_locale_map_keys(value: dict, path: str) -> None:
    for key in value:
        try:
            validate_locale_code(key)
        except LocaleValidationError as exc:
            raise LocaleValidationError(
                f"{exc} Field path: {path}. Unsupported locale key: '{key}'."
            ) from exc


def resolve_localized(value, locale: str, path: str):
    validate_locale_code(locale)
    if is_locale_map(value):
        _validate_locale_map_keys(value, path)
        if locale not in value:
            available = ", ".join(value)
            raise LocaleResolutionError(
                f"Missing locale '{locale}' at {path}. "
                f"Available locales: {available}. "
                "No silent fallback by design."
            )
        return value[locale]
    return value


def resolve_localized_tree(value, locale: str, path: str):
    if is_locale_map(value):
        return resolve_localized(value, locale, path)
    if isinstance(value, dict):
        return {
            key: resolve_localized_tree(child, locale, f"{path}.{key}")
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [
            resolve_localized_tree(child, locale, f"{path}.{index}")
            for index, child in enumerate(value)
        ]
    return value


def _load_json(database_dir: Path, filename: str):
    with (database_dir / filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_metadata(database_dir: Path) -> str | None:
    metadata_path = database_dir / "metadata.tex"
    if not metadata_path.exists():
        return None
    return metadata_path.read_text(encoding="utf-8")


def _resolve_mapping_values(values: dict, locale: str, path: str) -> dict:
    return {key: resolve_localized(value, locale, f"{path}.{key}") for key, value in values.items()}


def _resolve_skill_categories(build_config: dict, locale: str) -> list[dict]:
    categories = []
    for index, category in enumerate(build_config["skill_categories"]):
        path = f"skill_categories.{index}"
        categories.append(
            {
                "name": resolve_localized(category["name"], locale, f"{path}.name"),
                "skills": resolve_localized(category["skills"], locale, f"{path}.skills"),
            }
        )
    return categories


def _resolve_cover_letter(build_config: dict, locale: str) -> dict | None:
    cover_letter = build_config.get("cover_letter")
    if cover_letter is None:
        return None

    resolved = {}
    for key, value in cover_letter.items():
        path = f"cover_letter.{key}"
        if key == "body_paragraphs":
            resolved[key] = [
                resolve_localized(paragraph, locale, f"{path}.{index}")
                for index, paragraph in enumerate(value)
            ]
        else:
            resolved[key] = resolve_localized(value, locale, path)
    return resolved


def _resolve_probability_matrix(build_config: dict, locale: str) -> dict:
    return _resolve_mapping_values(build_config["probability_matrix"], locale, "probability_matrix")


def _resolve_experience(build_config: dict, experience_db: dict, locale: str) -> list[dict]:
    resolved = []
    for job_id, job_config in build_config["experience"].items():
        master_job = experience_db[job_id]
        bullets = [
            resolve_localized(
                master_job["bullets"][bullet_id],
                locale,
                f"experience.{job_id}.bullets.{bullet_id}",
            )
            for bullet_id in job_config["bullets"]
        ]
        resolved.append(
            {
                "company": resolve_localized(master_job["company"], locale, f"experience.{job_id}.company"),
                "location": resolve_localized(master_job["location"], locale, f"experience.{job_id}.location"),
                "dates": resolve_localized(master_job["dates"], locale, f"experience.{job_id}.dates"),
                "title": resolve_localized(job_config["title"], locale, f"build_config.experience.{job_id}.title"),
                "bullets": bullets,
            }
        )
    return resolved


def resolve_application_context(build_config: dict, database_dir: Path | str) -> dict:
    """Resolve selected application data into locale-specific plain values."""
    database_dir = Path(database_dir)
    metadata_text = _read_metadata(database_dir)
    locale = resolve_target_locale(build_config, metadata_text=metadata_text)

    experience_db = _load_json(database_dir, "experience.json")
    projects_db = _load_json(database_dir, "projects.json")
    education_db = _load_json(database_dir, "education.json")
    extracurriculars_db = _load_json(database_dir, "extracurriculars.json")
    languages_db = _load_json(database_dir, "languages.json")
    i18n_db = _load_json(database_dir, "i18n.json")

    return {
        "target_locale": locale,
        "job_title": resolve_localized(build_config["job_title"], locale, "job_title"),
        "keywords": resolve_localized(build_config["keywords"], locale, "keywords"),
        "geometry_options": build_config.get("geometry_options", ""),
        "profile": resolve_localized(build_config["profile"], locale, "profile"),
        "skill_categories": _resolve_skill_categories(build_config, locale),
        "experience": _resolve_experience(build_config, experience_db, locale),
        "projects": [
            resolve_localized(projects_db[project_id], locale, f"projects.{project_id}")
            for project_id in build_config["projects"]
        ],
        "education": [
            resolve_localized(education_db[education_id], locale, f"education.{education_id}")
            for education_id in build_config["education"]
        ],
        "extracurriculars_title": resolve_localized(
            build_config["extracurriculars_title"],
            locale,
            "extracurriculars_title",
        ),
        "extracurriculars": [
            resolve_localized(extracurriculars_db[extra_id], locale, f"extracurriculars.{extra_id}")
            for extra_id in build_config["extracurriculars"]
        ],
        "languages": [
            resolve_localized(languages_db[language_id], locale, f"languages.{language_id}")
            for language_id in build_config.get("languages", [])
        ],
        "i18n": _resolve_mapping_values(i18n_db, locale, "i18n"),
        "missing_skills": list(build_config.get("missing_skills", [])),
        "cover_letter": _resolve_cover_letter(build_config, locale),
        "probability_matrix": _resolve_probability_matrix(build_config, locale),
    }
