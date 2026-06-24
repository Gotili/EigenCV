import pytest
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from check_ats_score import is_skill_in_text
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string

lemmatizer = WordNetLemmatizer()

def get_lemmatized_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t not in string.punctuation]
    return [lemmatizer.lemmatize(t) for t in tokens]

def test_is_skill_in_text_exact_match():
    text = "We are looking for a python developer."
    lemmatized = get_lemmatized_text(text)
    assert is_skill_in_text("python", text, lemmatized) == True

def test_is_skill_in_text_stem_match():
    # WordNetLemmatizer handles basic pluralization
    text = "We write many languages"
    lemmatized = get_lemmatized_text(text)
    assert is_skill_in_text("language", text, lemmatized) == True

def test_is_skill_in_text_fuzzy_match():
    # Minor typo in text
    text = "Experience with tensorflw is required."
    lemmatized = get_lemmatized_text(text)
    assert is_skill_in_text("tensorflow", text, lemmatized) == True

def test_is_skill_in_text_no_match():
    text = "Looking for a C++ developer."
    lemmatized = get_lemmatized_text(text)
    assert is_skill_in_text("python", text, lemmatized) == False
    assert is_skill_in_text("rust", text, lemmatized) == False

def test_is_skill_in_text_multi_word():
    text = "Experience in machine learning is required."
    lemmatized = get_lemmatized_text(text)
    assert is_skill_in_text("machine learning", text, lemmatized) == True
