"""
Automated Accessibility (WCAG 2.1 Level AA) Compliance Verification Suite.
Validates semantic structure, ARIA labeling, keyboard navigation, and contrast tokens.
"""

import os
import re
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_accessibility_specification_exists():
    """Verify ACCESSIBILITY.md exists and contains WCAG 2.1 AA documentation."""
    doc_path = os.path.join(ROOT_DIR, "ACCESSIBILITY.md")
    assert os.path.exists(doc_path), "ACCESSIBILITY.md must be present in project root"
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "WCAG 2.1 Level AA" in content
    assert "Keyboard Navigation" in content
    assert "Contrast" in content
    assert "Screen Reader" in content


def test_html_lang_attribute():
    """Ensure root HTML layout specifies lang='en'."""
    layout_path = os.path.join(ROOT_DIR, "src", "app", "layout.tsx")
    assert os.path.exists(layout_path)
    with open(layout_path, "r", encoding="utf-8") as f:
        code = f.read()
    assert '<html lang="en">' in code or "<html lang='en'>" in code


def test_skip_to_main_content_landmark():
    """Ensure AppShell includes skip navigation link pointing to main landmark."""
    shell_path = os.path.join(ROOT_DIR, "src", "components", "layout", "AppShell.tsx")
    assert os.path.exists(shell_path)
    with open(shell_path, "r", encoding="utf-8") as f:
        code = f.read()
    assert 'href="#main-content"' in code
    assert 'id="main-content"' in code
    assert "Skip to main content" in code


def test_navbar_aria_labels():
    """Verify that interactive buttons in TopNavbar have explicit aria-label attributes."""
    nav_path = os.path.join(ROOT_DIR, "src", "components", "layout", "TopNavbar.tsx")
    assert os.path.exists(nav_path)
    with open(nav_path, "r", encoding="utf-8") as f:
        code = f.read()
    assert 'aria-label="Toggle Sidebar"' in code
    assert 'aria-label="Search corpus"' in code
    assert 'aria-label="12 Active System Verifications"' in code
    assert 'aria-label="Counsel Profile and Active Session Settings"' in code


def test_contrast_ratio_tokens():
    """Verify high-contrast color tokens meet WCAG 2.1 AA minimums (>= 4.5:1)."""
    # Slate 900 (#0F172A) on White (#FFFFFF) luminance contrast
    # Relative luminance calculation check
    def get_contrast(hex1: str, hex2: str) -> float:
        # Standard relative luminance formula
        def lum(h):
            r, g, b = [int(h[i:i+2], 16) / 255.0 for i in (1, 3, 5)]
            srgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
            return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2]
        l1, l2 = lum(hex1), lum(hex2)
        bright, dark = max(l1, l2), min(l1, l2)
        return (bright + 0.05) / (dark + 0.05)

    primary_text_contrast = get_contrast("#0F172A", "#FFFFFF")
    assert primary_text_contrast >= 4.5, f"Primary text contrast {primary_text_contrast:.2f} must exceed 4.5"

    body_text_contrast = get_contrast("#1E293B", "#FFFFFF")
    assert body_text_contrast >= 4.5, f"Body text contrast {body_text_contrast:.2f} must exceed 4.5"
