"""Content Agent - Responsible for content structure and text generation"""
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent
from ..core.task import Task


class ContentAgent(BaseAgent):
    """
    Content Agent: Creates and structures presentation content.

    Responsibilities:
    - Design presentation outline and structure
    - Write slide titles and body text
    - Create bullet points and key messages
    - Ensure logical flow between slides
    """

    def __init__(self):
        super().__init__(
            name="ContentAgent",
            role="Content Creation & Structure",
            description="Designs presentation structure, writes content, and ensures logical flow"
        )

    async def execute_task(self, task: Task) -> Any:
        """Execute content-related tasks"""
        task_type = task.input_data.get("type", "create_outline") if task.input_data else "create_outline"

        if task_type == "create_outline":
            return await self._create_outline(task.input_data)
        elif task_type == "write_slide":
            return await self._write_slide(task.input_data)
        elif task_type == "create_full_content":
            return await self._create_full_content(task.input_data)
        else:
            return await self._create_outline(task.input_data)

    async def _create_outline(self, input_data: Dict) -> Dict:
        """Create presentation outline"""
        topic = input_data.get("topic", "Presentation")
        insights = input_data.get("insights", [])
        num_slides = input_data.get("num_slides", 5)

        self.log(f"Creating outline for: {topic}")

        outline = {
            "title": topic,
            "slides": [
                {
                    "slide_number": 1,
                    "type": "title",
                    "title": topic,
                    "subtitle": "プレゼンテーション資料",
                },
                {
                    "slide_number": 2,
                    "type": "agenda",
                    "title": "アジェンダ",
                    "items": ["背景・目的", "分析結果", "提案内容", "まとめ"],
                },
            ]
        }

        # Add content slides based on insights
        slide_num = 3
        if insights:
            # Group insights for slides
            outline["slides"].append({
                "slide_number": slide_num,
                "type": "content",
                "title": "分析結果",
                "items": [ins.get("description", "") for ins in insights[:4]],
            })
            slide_num += 1

        # Add conclusion slide
        outline["slides"].append({
            "slide_number": slide_num,
            "type": "conclusion",
            "title": "まとめ",
            "items": ["主要なポイント", "次のステップ", "お問い合わせ"],
        })

        self.log(f"Created outline with {len(outline['slides'])} slides")
        return outline

    async def _write_slide(self, input_data: Dict) -> Dict:
        """Write content for a single slide"""
        slide_type = input_data.get("slide_type", "content")
        title = input_data.get("title", "")
        key_points = input_data.get("key_points", [])

        self.log(f"Writing slide: {title}")

        slide_content = {
            "title": title,
            "type": slide_type,
            "body": [],
            "notes": "",
        }

        if slide_type == "title":
            slide_content["subtitle"] = input_data.get("subtitle", "")
        elif slide_type == "content":
            slide_content["body"] = key_points if key_points else [
                "ポイント1",
                "ポイント2",
                "ポイント3",
            ]
        elif slide_type == "comparison":
            slide_content["left"] = input_data.get("left_items", [])
            slide_content["right"] = input_data.get("right_items", [])

        return slide_content

    async def _create_full_content(self, input_data: Dict) -> Dict:
        """Create complete presentation content"""
        outline = input_data.get("outline", {})
        research_data = input_data.get("research_data", {})
        insights = input_data.get("insights", [])

        self.log("Creating full presentation content...")

        presentation = {
            "title": outline.get("title", "Presentation"),
            "slides": [],
            "metadata": {
                "total_slides": 0,
                "has_data": bool(research_data),
                "insight_count": len(insights),
            }
        }

        # Process each slide from outline
        for slide_def in outline.get("slides", []):
            slide = await self._write_slide({
                "slide_type": slide_def.get("type", "content"),
                "title": slide_def.get("title", ""),
                "key_points": slide_def.get("items", []),
                "subtitle": slide_def.get("subtitle", ""),
            })
            slide["slide_number"] = slide_def.get("slide_number", len(presentation["slides"]) + 1)
            presentation["slides"].append(slide)

        presentation["metadata"]["total_slides"] = len(presentation["slides"])

        self.log(f"Created full content with {len(presentation['slides'])} slides")
        return presentation
