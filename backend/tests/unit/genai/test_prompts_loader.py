import os
import sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.genai.prompts.loader import render


def test_render_openai_vi_minimal():
    prompt, cfg, required = render(
        template_key="exam_generation",
        provider="openai",
        locale="vi",
        variables={
            "content": "Nội dung kiểm thử",
            "question_count": 1,
        },
    )
    assert isinstance(prompt, str) and len(prompt) > 0
    assert cfg.get("name") == "openai"
    assert cfg.get("model")
    assert isinstance(required, list) and len(required) > 0
    # Ensure placeholders resolved
    assert "{{" not in prompt and "}}" not in prompt


def test_render_gemini_en_minimal():
    prompt, cfg, required = render(
        template_key="exam_generation",
        provider="gemini",
        locale="en",
        variables={
            "content": "Test content",
            "question_count": 1,
        },
    )
    assert cfg.get("name") == "gemini"
    assert isinstance(prompt, str) and len(prompt) > 0


def test_render_invalid_template_key():
    with pytest.raises(KeyError):
        render(
            template_key="unknown_template",
            provider="openai",
            locale="vi",
            variables={"content": "x"},
        )


