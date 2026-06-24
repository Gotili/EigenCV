import pytest
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'cv', 'scripts'))

from cv_compiler import sanitize_latex_text, hex_to_rgb, adjust_color_for_contrast

def test_hex_to_rgb():
    assert hex_to_rgb("FF0000") == (255, 0, 0)
    assert hex_to_rgb("00FF00") == (0, 255, 0)
    assert hex_to_rgb("0000FF") == (0, 0, 255)
    assert hex_to_rgb("FFFFFF") == (255, 255, 255)
    assert hex_to_rgb("000000") == (0, 0, 0)

def test_darken_hex():
    # Should darken white
    darkened_white = adjust_color_for_contrast("FFFFFF")
    rgb = hex_to_rgb(darkened_white)
    assert rgb[0] < 255 and rgb[1] < 255 and rgb[2] < 255
    
    # Should not darken a color that is already dark enough
    assert adjust_color_for_contrast("000000") == "000000"
    assert adjust_color_for_contrast("102030") == "102030"

def test_sanitize_latex_markdown_bold():
    res = sanitize_latex_text("This is **bold** text")
    assert r"\textbf{bold}" in res
    assert "**" not in res

def test_sanitize_latex_markdown_italic():
    res = sanitize_latex_text("This is *italic* text")
    assert r"\textit{italic}" in res
    
def test_sanitize_latex_markdown_link():
    res = sanitize_latex_text("A [Google](https://google.com) link")
    assert r"\href{https://google.com}{Google}" in res

def test_sanitize_latex_dangerous_chars():
    res = sanitize_latex_text("100% & $100 #tag _test {group}")
    assert r"\%" in res
    assert r"\&" in res
    assert r"\$" in res
    assert r"\#" in res
    assert r"\_" in res
    assert r"\{" in res
    assert r"\}" in res

def test_sanitize_latex_combined():
    # A complex string with both markdown and dangerous characters
    res = sanitize_latex_text("**100% Match** for [Role_Name](https://link.com/?q=1&b=2)")
    assert r"\textbf{100\% Match}" in res
    assert r"\href{https://link.com/?q=1&b=2}{Role\_Name}" in res

def test_sanitize_latex_preserves_backslash():
    res = sanitize_latex_text(r"\textbf{Already Escaped}")
    # Current behavior escapes \ to \textbackslash{}
    assert r"\textbackslash{}textbf\{Already Escaped\}" in res
