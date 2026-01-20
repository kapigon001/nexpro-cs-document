"""Template management for PowerPoint presentations"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from enum import Enum


class SlideType(Enum):
    """Types of slides available in templates"""
    TITLE = "title"
    AGENDA = "agenda"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    COMPARISON = "comparison"
    CHART = "chart"
    IMAGE = "image"
    QUOTE = "quote"
    TIMELINE = "timeline"
    TEAM = "team"
    CONCLUSION = "conclusion"
    QA = "qa"
    THANK_YOU = "thank_you"


@dataclass
class ThemeColors:
    """Color scheme for a theme"""
    primary: str = "#1F4E79"
    secondary: str = "#2E75B6"
    accent: str = "#5B9BD5"
    text: str = "#333333"
    text_light: str = "#666666"
    background: str = "#FFFFFF"
    background_alt: str = "#F5F5F5"


@dataclass
class ThemeFonts:
    """Font settings for a theme"""
    title_name: str = "Yu Gothic UI"
    title_size: int = 36
    title_bold: bool = True
    body_name: str = "Yu Gothic UI"
    body_size: int = 18
    body_bold: bool = False
    caption_name: str = "Yu Gothic UI"
    caption_size: int = 12


@dataclass
class SlideTemplate:
    """Template for a single slide"""
    type: SlideType
    layout: Dict[str, Any]
    placeholders: List[str]
    default_content: Dict[str, Any]


class PresentationTemplate:
    """
    Manages presentation templates with predefined themes and layouts.
    """

    # Built-in themes
    THEMES = {
        "corporate": {
            "name": "Corporate",
            "description": "Professional business theme",
            "colors": ThemeColors(
                primary="#1F4E79",
                secondary="#2E75B6",
                accent="#5B9BD5",
                text="#333333",
                text_light="#666666",
                background="#FFFFFF",
                background_alt="#F8F9FA"
            ),
            "fonts": ThemeFonts(
                title_name="Yu Gothic UI",
                title_size=36,
                title_bold=True,
                body_name="Yu Gothic UI",
                body_size=18,
                body_bold=False
            )
        },
        "modern": {
            "name": "Modern",
            "description": "Clean and contemporary design",
            "colors": ThemeColors(
                primary="#2D3436",
                secondary="#636E72",
                accent="#00B894",
                text="#2D3436",
                text_light="#636E72",
                background="#FFFFFF",
                background_alt="#DFE6E9"
            ),
            "fonts": ThemeFonts(
                title_name="Yu Gothic UI",
                title_size=40,
                title_bold=True,
                body_name="Yu Gothic UI",
                body_size=16,
                body_bold=False
            )
        },
        "vibrant": {
            "name": "Vibrant",
            "description": "Bold and colorful theme",
            "colors": ThemeColors(
                primary="#E74C3C",
                secondary="#3498DB",
                accent="#F39C12",
                text="#2C3E50",
                text_light="#7F8C8D",
                background="#FFFFFF",
                background_alt="#ECF0F1"
            ),
            "fonts": ThemeFonts(
                title_name="Yu Gothic UI",
                title_size=38,
                title_bold=True,
                body_name="Yu Gothic UI",
                body_size=18,
                body_bold=False
            )
        },
        "minimal": {
            "name": "Minimal",
            "description": "Simple and elegant design",
            "colors": ThemeColors(
                primary="#000000",
                secondary="#333333",
                accent="#666666",
                text="#000000",
                text_light="#666666",
                background="#FFFFFF",
                background_alt="#FAFAFA"
            ),
            "fonts": ThemeFonts(
                title_name="Yu Gothic UI",
                title_size=44,
                title_bold=False,
                body_name="Yu Gothic UI",
                body_size=16,
                body_bold=False
            )
        },
        "tech": {
            "name": "Tech",
            "description": "Technology-focused theme",
            "colors": ThemeColors(
                primary="#6C5CE7",
                secondary="#A29BFE",
                accent="#00CEC9",
                text="#2D3436",
                text_light="#636E72",
                background="#FFFFFF",
                background_alt="#F8F9FA"
            ),
            "fonts": ThemeFonts(
                title_name="Yu Gothic UI",
                title_size=36,
                title_bold=True,
                body_name="Yu Gothic UI",
                body_size=16,
                body_bold=False
            )
        },
        "nature": {
            "name": "Nature",
            "description": "Organic and natural theme",
            "colors": ThemeColors(
                primary="#27AE60",
                secondary="#2ECC71",
                accent="#F1C40F",
                text="#2C3E50",
                text_light="#7F8C8D",
                background="#FFFFFF",
                background_alt="#E8F6EF"
            ),
            "fonts": ThemeFonts(
                title_name="Yu Gothic UI",
                title_size=36,
                title_bold=True,
                body_name="Yu Gothic UI",
                body_size=18,
                body_bold=False
            )
        }
    }

    # Presentation type templates
    PRESENTATION_TYPES = {
        "business_proposal": {
            "name": "Business Proposal",
            "description": "Template for business proposals and pitches",
            "recommended_theme": "corporate",
            "slide_structure": [
                {"type": SlideType.TITLE, "purpose": "Cover slide"},
                {"type": SlideType.AGENDA, "purpose": "Outline"},
                {"type": SlideType.CONTENT, "purpose": "Problem statement"},
                {"type": SlideType.CONTENT, "purpose": "Solution overview"},
                {"type": SlideType.TWO_COLUMN, "purpose": "Benefits"},
                {"type": SlideType.CHART, "purpose": "Market data"},
                {"type": SlideType.TIMELINE, "purpose": "Implementation plan"},
                {"type": SlideType.CONTENT, "purpose": "Pricing"},
                {"type": SlideType.CONCLUSION, "purpose": "Summary"},
                {"type": SlideType.QA, "purpose": "Q&A"}
            ]
        },
        "project_update": {
            "name": "Project Update",
            "description": "Template for project status updates",
            "recommended_theme": "modern",
            "slide_structure": [
                {"type": SlideType.TITLE, "purpose": "Title"},
                {"type": SlideType.AGENDA, "purpose": "Agenda"},
                {"type": SlideType.CONTENT, "purpose": "Progress summary"},
                {"type": SlideType.CHART, "purpose": "Metrics"},
                {"type": SlideType.TWO_COLUMN, "purpose": "Achievements vs Challenges"},
                {"type": SlideType.TIMELINE, "purpose": "Next steps"},
                {"type": SlideType.CONCLUSION, "purpose": "Key takeaways"}
            ]
        },
        "product_launch": {
            "name": "Product Launch",
            "description": "Template for product introductions",
            "recommended_theme": "vibrant",
            "slide_structure": [
                {"type": SlideType.TITLE, "purpose": "Product name"},
                {"type": SlideType.IMAGE, "purpose": "Product hero image"},
                {"type": SlideType.CONTENT, "purpose": "Problem we solve"},
                {"type": SlideType.CONTENT, "purpose": "Key features"},
                {"type": SlideType.COMPARISON, "purpose": "Competitive advantage"},
                {"type": SlideType.CHART, "purpose": "Market opportunity"},
                {"type": SlideType.CONTENT, "purpose": "Pricing"},
                {"type": SlideType.TIMELINE, "purpose": "Availability"},
                {"type": SlideType.THANK_YOU, "purpose": "Call to action"}
            ]
        },
        "training": {
            "name": "Training",
            "description": "Template for educational content",
            "recommended_theme": "modern",
            "slide_structure": [
                {"type": SlideType.TITLE, "purpose": "Course title"},
                {"type": SlideType.AGENDA, "purpose": "Learning objectives"},
                {"type": SlideType.CONTENT, "purpose": "Introduction"},
                {"type": SlideType.CONTENT, "purpose": "Topic 1"},
                {"type": SlideType.CONTENT, "purpose": "Topic 2"},
                {"type": SlideType.CONTENT, "purpose": "Topic 3"},
                {"type": SlideType.CONTENT, "purpose": "Best practices"},
                {"type": SlideType.CONCLUSION, "purpose": "Summary"},
                {"type": SlideType.QA, "purpose": "Questions"}
            ]
        },
        "quarterly_review": {
            "name": "Quarterly Review",
            "description": "Template for quarterly business reviews",
            "recommended_theme": "corporate",
            "slide_structure": [
                {"type": SlideType.TITLE, "purpose": "Quarter title"},
                {"type": SlideType.AGENDA, "purpose": "Agenda"},
                {"type": SlideType.CHART, "purpose": "Revenue metrics"},
                {"type": SlideType.CHART, "purpose": "Growth metrics"},
                {"type": SlideType.TWO_COLUMN, "purpose": "Wins and learnings"},
                {"type": SlideType.CONTENT, "purpose": "Key initiatives"},
                {"type": SlideType.TIMELINE, "purpose": "Next quarter goals"},
                {"type": SlideType.CONCLUSION, "purpose": "Summary"}
            ]
        },
        "comparison_analysis": {
            "name": "Comparison Analysis",
            "description": "Template for comparing options or competitors",
            "recommended_theme": "corporate",
            "slide_structure": [
                {"type": SlideType.TITLE, "purpose": "Analysis title"},
                {"type": SlideType.AGENDA, "purpose": "Overview"},
                {"type": SlideType.CONTENT, "purpose": "Background"},
                {"type": SlideType.COMPARISON, "purpose": "Feature comparison"},
                {"type": SlideType.CHART, "purpose": "Data comparison"},
                {"type": SlideType.TWO_COLUMN, "purpose": "Pros and cons"},
                {"type": SlideType.CONTENT, "purpose": "Recommendation"},
                {"type": SlideType.CONCLUSION, "purpose": "Summary"}
            ]
        }
    }

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = Path(template_dir) if template_dir else None
        self.custom_themes: Dict[str, Dict] = {}
        self.custom_templates: Dict[str, Dict] = {}

    def get_theme(self, theme_name: str) -> Dict:
        """Get theme by name"""
        if theme_name in self.custom_themes:
            return self.custom_themes[theme_name]
        if theme_name in self.THEMES:
            theme = self.THEMES[theme_name]
            return {
                "name": theme["name"],
                "description": theme["description"],
                "colors": asdict(theme["colors"]),
                "fonts": {
                    "title": {
                        "name": theme["fonts"].title_name,
                        "size": theme["fonts"].title_size,
                        "bold": theme["fonts"].title_bold
                    },
                    "body": {
                        "name": theme["fonts"].body_name,
                        "size": theme["fonts"].body_size,
                        "bold": theme["fonts"].body_bold
                    },
                    "caption": {
                        "name": theme["fonts"].caption_name,
                        "size": theme["fonts"].caption_size
                    }
                }
            }
        # Default to corporate
        return self.get_theme("corporate")

    def get_presentation_type(self, type_name: str) -> Dict:
        """Get presentation type template"""
        if type_name in self.custom_templates:
            return self.custom_templates[type_name]
        if type_name in self.PRESENTATION_TYPES:
            ptype = self.PRESENTATION_TYPES[type_name]
            return {
                "name": ptype["name"],
                "description": ptype["description"],
                "recommended_theme": ptype["recommended_theme"],
                "slide_structure": [
                    {
                        "type": s["type"].value,
                        "purpose": s["purpose"]
                    }
                    for s in ptype["slide_structure"]
                ]
            }
        return None

    def list_themes(self) -> List[Dict]:
        """List all available themes"""
        themes = []
        for name, theme in self.THEMES.items():
            themes.append({
                "id": name,
                "name": theme["name"],
                "description": theme["description"]
            })
        for name, theme in self.custom_themes.items():
            themes.append({
                "id": name,
                "name": theme.get("name", name),
                "description": theme.get("description", "Custom theme"),
                "custom": True
            })
        return themes

    def list_presentation_types(self) -> List[Dict]:
        """List all available presentation types"""
        types = []
        for name, ptype in self.PRESENTATION_TYPES.items():
            types.append({
                "id": name,
                "name": ptype["name"],
                "description": ptype["description"],
                "slide_count": len(ptype["slide_structure"])
            })
        return types

    def register_custom_theme(self, name: str, theme: Dict):
        """Register a custom theme"""
        self.custom_themes[name] = theme

    def register_custom_template(self, name: str, template: Dict):
        """Register a custom presentation template"""
        self.custom_templates[name] = template

    def generate_slide_content_template(self, slide_type: str) -> Dict:
        """Generate a template for slide content based on type"""
        templates = {
            "title": {
                "type": "title",
                "title": "[タイトルを入力]",
                "subtitle": "[サブタイトルを入力]",
                "author": "",
                "date": ""
            },
            "agenda": {
                "type": "agenda",
                "title": "アジェンダ",
                "items": ["項目1", "項目2", "項目3"]
            },
            "content": {
                "type": "content",
                "title": "[スライドタイトル]",
                "body": ["ポイント1", "ポイント2", "ポイント3"]
            },
            "two_column": {
                "type": "two_column",
                "title": "[スライドタイトル]",
                "left_title": "左側",
                "left": ["項目1", "項目2"],
                "right_title": "右側",
                "right": ["項目1", "項目2"]
            },
            "comparison": {
                "type": "comparison",
                "title": "比較",
                "items": [
                    {"name": "オプションA", "features": ["特徴1", "特徴2"]},
                    {"name": "オプションB", "features": ["特徴1", "特徴2"]}
                ]
            },
            "chart": {
                "type": "chart",
                "title": "[チャートタイトル]",
                "chart_type": "bar",
                "data": {}
            },
            "timeline": {
                "type": "timeline",
                "title": "タイムライン",
                "events": [
                    {"date": "Phase 1", "description": "説明"},
                    {"date": "Phase 2", "description": "説明"}
                ]
            },
            "conclusion": {
                "type": "conclusion",
                "title": "まとめ",
                "body": ["要点1", "要点2", "次のステップ"]
            },
            "qa": {
                "type": "qa",
                "title": "Q&A",
                "subtitle": "ご質問はありますか？"
            },
            "thank_you": {
                "type": "thank_you",
                "title": "ありがとうございました",
                "contact": "お問い合わせ先"
            }
        }
        return templates.get(slide_type, templates["content"])

    def save_theme(self, name: str, theme: Dict, path: Optional[Path] = None):
        """Save a theme to a JSON file"""
        save_path = path or (self.template_dir / f"theme_{name}.json" if self.template_dir else None)
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(theme, f, ensure_ascii=False, indent=2)

    def load_theme(self, path: Path) -> Dict:
        """Load a theme from a JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
