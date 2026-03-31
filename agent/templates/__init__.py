"""
Industry Templates for India SME Voice AI
Each template defines: system prompt, tools, greeting, FAQ patterns
SMEs pick a template → get a fully configured agent instantly
"""

from .clinic import CLINIC_TEMPLATE
from .restaurant import RESTAURANT_TEMPLATE
from .real_estate import REAL_ESTATE_TEMPLATE
from .ecommerce import ECOMMERCE_TEMPLATE
from .general import GENERAL_TEMPLATE

TEMPLATES = {
    "clinic": CLINIC_TEMPLATE,
    "restaurant": RESTAURANT_TEMPLATE,
    "real_estate": REAL_ESTATE_TEMPLATE,
    "realestate": REAL_ESTATE_TEMPLATE,
    "ecommerce": ECOMMERCE_TEMPLATE,
    "general": GENERAL_TEMPLATE,
}


def get_template(industry: str) -> dict:
    """Get template by industry. Falls back to general."""
    return TEMPLATES.get(industry.lower(), GENERAL_TEMPLATE)


def list_templates() -> list[dict]:
    """List all available templates for dashboard dropdown."""
    seen = set()
    result = []
    for key, tmpl in TEMPLATES.items():
        if tmpl["id"] not in seen:
            seen.add(tmpl["id"])
            result.append({
                "id": tmpl["id"],
                "name": tmpl["name"],
                "description": tmpl["description"],
                "icon": tmpl["icon"],
            })
    return result