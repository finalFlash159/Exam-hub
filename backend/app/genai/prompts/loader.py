import os
from typing import Any, Dict, Tuple

import yaml
from jinja2 import Template


PROVIDERS_DIR = os.path.join(os.path.dirname(__file__), "providers")
BASE_FILE = os.path.join(PROVIDERS_DIR, "base.yaml")


def _read_yaml(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"YAML not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def load_base() -> Dict[str, Any]:
    """Load base prompt configuration (templates, defaults)."""
    return _read_yaml(BASE_FILE)


def load_provider(name: str) -> Dict[str, Any]:
    """Load provider-specific configuration (model, params, overrides)."""
    path = os.path.join(PROVIDERS_DIR, f"{name}.yaml")
    return _read_yaml(path)


def render(
    template_key: str,
    provider: str,
    locale: str,
    variables: Dict[str, Any],
) -> Tuple[str, Dict[str, Any], Any]:
    """
    Render prompt from YAML templates.

    Returns: (rendered_prompt, provider_config, required_fields)
    """
    base_cfg = load_base()
    prv_cfg = load_provider(provider)

    # Validate minimal structure
    templates = (base_cfg.get("templates") or {})
    if template_key not in templates:
        raise KeyError(f"Template '{template_key}' not found in base.yaml")

    tpl_cfg = templates[template_key]
    locales = (tpl_cfg.get("locales") or {})
    required_fields = tpl_cfg.get("required_fields") or []
    if not isinstance(required_fields, list) or not required_fields:
        raise ValueError("required_fields must be a non-empty list")

    # Determine locale (fallback to base default)
    base_vars = base_cfg.get("variables") or {}
    language_default = base_vars.get("language_default", "vi")
    use_locale = locale or language_default
    if use_locale not in locales:
        # fallback to default
        use_locale = language_default
        if use_locale not in locales:
            raise KeyError(f"Locale '{use_locale}' not available and no valid default in base.yaml")

    # Provider validations
    prv = prv_cfg.get("provider") or {}
    if not prv.get("name") or not prv.get("model"):
        raise KeyError("provider.name and provider.model are required in provider YAML")

    mapping = prv_cfg.get("template_mapping") or {}
    mapped_key = mapping.get(template_key) or template_key
    # Ensure template exists in base
    if mapped_key not in templates:
        raise KeyError(
            f"Mapped template key '{mapped_key}' not found in base templates."
        )

    # Merge variables: base.defaults <- provider.variables <- runtime
    merged_vars: Dict[str, Any] = {}
    merged_vars.update(base_vars)
    merged_vars.update(prv_cfg.get("variables") or {})
    merged_vars.update(variables or {})

    # Ensure common placeholders
    if "question_count" not in merged_vars:
        merged_vars["question_count"] = base_vars.get("default_question_count", 10)
    if "max_content_length" not in merged_vars:
        merged_vars["max_content_length"] = base_vars.get("max_content_length", 10000)
    merged_vars.setdefault("required_fields", required_fields)

    # Render via Jinja2
    template_str: str = locales[use_locale]
    prompt = Template(template_str).render(**merged_vars)

    provider_config = {
        "name": prv["name"],
        "model": prv["model"],
        "params": prv_cfg.get("params") or {},
        "resolved_locale": use_locale,
        "resolved_variables": merged_vars,
    }

    return prompt.strip(), provider_config, required_fields


