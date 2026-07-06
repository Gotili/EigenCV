"""
Pydantic Schema Definitions for EigenCV.

This module defines the strict JSON structure expected from the LLM. 
It uses Pydantic to validate the input and enforces business logic such as 
RapidFuzz-based ID healing and data integrity checks against the master databases.
"""
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Dict, Optional, Union
import json
import os
import math
from cv_i18n import validate_locale_code

LocalizedText = Union[str, Dict[str, str]]


def validate_localized_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for locale, text in value.items():
            validate_locale_code(locale)
            if not isinstance(text, str):
                raise ValueError(f"Localized value for '{locale}' must be a string.")
        return value
    return value


def localized_text_values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return list(value.values())
    return []


def localized_text_locales(value):
    if isinstance(value, dict):
        return set(value.keys())
    return set()


def localized_text_for_locale(value, locale):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get(locale, "")
    return ""

class SkillCategory(BaseModel):
    name: LocalizedText = Field(..., description="Name of the skill category (e.g., 'Languages', 'Machine Learning' )")
    skills: LocalizedText = Field(..., description="Comma-separated list of skills belonging to this category")

    @field_validator('name', 'skills', mode='before')
    @classmethod
    def validate_localized_fields(cls, v):
        return validate_localized_text(v)

    @field_validator('skills')
    @classmethod
    def prevent_unresolved_skill_clusters(cls, v: LocalizedText) -> LocalizedText:
        for text in localized_text_values(v):
            if '[' in text or ']' in text or '|' in text:
                raise ValueError(
                    "Unresolved skill cluster or synonym detected. You must NOT output literal square brackets '[' or unresolved synonyms containing '|'. "
                    "Resolve them by picking exactly one synonym from (A | B) or picking specific relevant items from [A, B] as per the AI_GENERATION_PROMPT."
                )
        return v

class JobExperience(BaseModel):
    title: LocalizedText = Field(..., description="Job title customized for the specific application narrative")
    bullets: List[str] = Field(..., description="List of exact bullet IDs from the master experience.json database")

    @field_validator('title', mode='before')
    @classmethod
    def validate_localized_title(cls, v):
        return validate_localized_text(v)

class CoverLetterConfig(BaseModel):
    company_name: LocalizedText = Field(..., description="Name of the company")
    recruiting_team: str = Field("Hiring Team", description="Name of the team or 'Hiring Team'")
    location: str = Field(..., description="Location of the company or 'Remote'")
    subject_role: LocalizedText = Field(..., description="The role name for the subject line")
    salutation: str = Field("Dear Hiring Team,", description="Salutation, e.g. 'Dear Hiring Team,'")
    intro_paragraph: LocalizedText = Field(..., description="The custom intro paragraph (The Hook)")
    body_paragraphs: List[LocalizedText] = Field(..., description="List of body paragraphs (tailored core arguments)")
    outro_paragraph: LocalizedText = Field(..., description="The custom outro paragraph (The Bridge)")

    @field_validator('company_name', 'subject_role', 'intro_paragraph', 'outro_paragraph', mode='before')
    @classmethod
    def validate_localized_fields(cls, v):
        return validate_localized_text(v)

    @field_validator('body_paragraphs', mode='before')
    @classmethod
    def validate_localized_body_paragraphs(cls, v):
        if isinstance(v, list):
            return [validate_localized_text(item) for item in v]
        return v

    @model_validator(mode='after')
    def check_length(self):
        locales = set()
        locales.update(localized_text_locales(self.intro_paragraph))
        locales.update(localized_text_locales(self.outro_paragraph))
        for paragraph in self.body_paragraphs:
            locales.update(localized_text_locales(paragraph))

        if not locales:
            locales = {None}

        for locale in locales:
            parts = [
                localized_text_for_locale(self.intro_paragraph, locale),
                *[localized_text_for_locale(paragraph, locale) for paragraph in self.body_paragraphs],
                localized_text_for_locale(self.outro_paragraph, locale),
            ]
            total_text = " ".join(part for part in parts if part)
            word_count = len(total_text.split())
            if word_count > 400:
                raise ValueError(f"Cover letter is too long ({word_count} words). Keep it under 400 words to fit on one page.")
        return self

class ProbabilityMatrix(BaseModel):
    invitation_probability: LocalizedText = Field(..., description="E.g., '85 % - Justification...'")
    technical_pass_probability: str = Field(..., description="E.g., '90 % - Justification...'")
    job_offer_probability: str = Field(..., description="E.g., '75 % - Justification...'")
    salary_estimate: str = Field(..., description="E.g., '€95,000 - €120,000 - Justification...'")
    biggest_vulnerability: LocalizedText = Field(..., description="The single weakest point in the profile")

    @field_validator('invitation_probability', 'biggest_vulnerability', mode='before')
    @classmethod
    def validate_localized_fields(cls, v):
        return validate_localized_text(v)

class I18nUpdate(BaseModel):
    locale_code: str = Field(..., description="ISO language code (e.g., 'fr', 'uk', 'de')")
    translations: Dict[str, str] = Field(..., description="Dictionary containing exactly these keys: experience, education, projects, skills, languages, profile")

class BuildConfig(BaseModel):
    target_locale: Optional[str] = Field(None, description="Optional explicit output locale, e.g. 'de-DE' or 'en-US'")
    job_title: LocalizedText = Field(..., description="The exact title of the job applied for")
    keywords: LocalizedText = Field("", description="Comma-separated list of ATS keywords for PDF metadata")
    geometry_options: str = Field("left=0.625in, right=0.625in, top=0.45in, bottom=0.45in", description="LaTeX geometry package options")
    company_accent_color: Optional[str] = Field(None, pattern=r'^[0-9a-fA-F]{6}$', description="A 6-character HEX color code representing the target company's primary brand color (e.g., 'FF0000'). Do NOT include the '#' symbol.")
    profile: LocalizedText = Field(..., description="Highly tailored 3-4 sentence professional profile")
    skill_categories: List[SkillCategory] = Field(..., min_length=6, max_length=6, description="Exactly 6 skill categories")
    experience: Dict[str, JobExperience] = Field(..., min_length=1, description="Dictionary mapping company IDs (e.g., 'tech_corp') to their tailored experience block")
    projects: List[str] = Field(..., min_length=1, description="List of project IDs from the master projects.json database")
    education: List[str] = Field(..., min_length=1, description="List of education IDs to include")
    extracurriculars_title: LocalizedText = Field(..., description="Dynamic title for the section (e.g., 'Publications & Leadership', 'Volunteering & Hobbies')")
    extracurriculars: List[str] = Field(..., min_length=1, description="List of extracurricular IDs to include")
    languages: List[str] = Field(default_factory=list, description="List of language IDs to include from the master languages.json database")
    missing_skills: List[str] = Field(default_factory=list, description="List of skills required by JD but missing from master_skills.md")
    cover_letter: Optional[CoverLetterConfig] = Field(None, description="Optional cover letter configuration")
    probability_matrix: ProbabilityMatrix = Field(..., description="Strictly required probability matrix evaluating candidate chances")
    i18n_updates: Optional[I18nUpdate] = Field(None, description="Provide this if the JD is not in English. The compiler will use these translations and save them to the database.")

    @field_validator('job_title', 'keywords', 'profile', 'extracurriculars_title', mode='before')
    @classmethod
    def validate_localized_fields(cls, v):
        return validate_localized_text(v)

    @field_validator('profile')
    @classmethod
    def check_profile_length(cls, v: LocalizedText) -> LocalizedText:
        for text in localized_text_values(v):
            if len(text) > 1000:
                raise ValueError('String should have at most 1000 characters')
        return v

    @field_validator('target_locale')
    @classmethod
    def validate_target_locale(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_locale_code(v)

    @model_validator(mode='after')
    def validate_databases(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        active_dir = os.path.join(base_dir, 'database', 'active')
        
        def load_db(filename):
            try:
                with open(os.path.join(active_dir, filename), 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}

        master_exp = load_db('experience.json')
        master_proj = load_db('projects.json')
        master_edu = load_db('education.json')
        master_ext = load_db('extracurriculars.json')
        master_lang = load_db('languages.json')

        errors = []

        if not master_exp:
            return self  # Skip if we can't load DBs

        def heal_id(candidate, valid_choices, category):
            try:
                from rapidfuzz import process, fuzz
            except ImportError:
                return candidate
                
            if candidate in valid_choices:
                return candidate
            if not valid_choices:
                return candidate
            match = process.extractOne(candidate, valid_choices, scorer=fuzz.ratio)
            if match and match[1] >= 90:
                print(f"[Healer] Auto-corrected '{candidate}' to '{match[0]}' in {category}.")
                return match[0]
            return candidate


        healed_experience = {}
        for comp_id, exp_data in self.experience.items():
            healed_comp_id = heal_id(comp_id, list(master_exp.keys()), "experience company")
            
            if healed_comp_id not in master_exp:
                errors.append(f"Company ID '{healed_comp_id}' not found in experience.json.")
                healed_experience[healed_comp_id] = exp_data
            else:
                valid_bullets = master_exp[healed_comp_id].get('bullets', {})
                healed_bullets = []
                for b_id in exp_data.bullets:
                    healed_b_id = heal_id(b_id, list(valid_bullets.keys()), f"bullets for {healed_comp_id}")
                    if healed_b_id not in valid_bullets:
                        errors.append(f"Bullet ID '{healed_b_id}' not found under company '{healed_comp_id}' in experience.json.")
                    healed_bullets.append(healed_b_id)
                
                exp_data.bullets = healed_bullets
                healed_experience[healed_comp_id] = exp_data
                
                # Enforce bullet counts
                total_available = len(valid_bullets)
                if total_available > 0:
                    min_required = math.ceil(total_available * 0.6)
                    if len(exp_data.bullets) < min_required:
                        errors.append(f"You only provided {len(exp_data.bullets)} bullets for '{healed_comp_id}'. You MUST provide AT LEAST {min_required} bullets (60 % of available {total_available}).")
        
        self.experience = healed_experience

        self.projects = [heal_id(p, list(master_proj.keys()), "projects") for p in self.projects]
        for p_id in self.projects:
            if p_id not in master_proj:
                errors.append(f"Project ID '{p_id}' not found in projects.json.")

        self.education = [heal_id(e, list(master_edu.keys()), "education") for e in self.education]
        for e_id in self.education:
            if e_id not in master_edu:
                errors.append(f"Education ID '{e_id}' not found in education.json.")

        self.extracurriculars = [heal_id(ex, list(master_ext.keys()), "extracurriculars") for ex in self.extracurriculars]
        for ex_id in self.extracurriculars:
            if ex_id not in master_ext:
                errors.append(f"Extracurricular ID '{ex_id}' not found in extracurriculars.json.")

        self.languages = [heal_id(lang, list(master_lang.keys()), "languages") for lang in self.languages]
        for lang_id in self.languages:
            if lang_id not in master_lang:
                errors.append(f"Language ID '{lang_id}' not found in languages.json.")

        if errors:
            raise ValueError("Database Validation Failed:\n- " + "\n- ".join(errors))
            
        return self
