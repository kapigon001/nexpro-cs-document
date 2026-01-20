"""LLM Agent - AI-powered content generation using Claude API"""
from typing import Any, Dict, List, Optional
import os
import json
from .base_agent import BaseAgent
from ..core.task import Task

# Try to import anthropic, but make it optional
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class LLMAgent(BaseAgent):
    """
    LLM Agent: AI-powered content generation using Claude API.

    Responsibilities:
    - Generate presentation content from topics
    - Improve and refine existing content
    - Create speaker notes
    - Translate content
    - Summarize research data into key points
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        super().__init__(
            name="LLMAgent",
            role="AI Content Generation",
            description="Generates and improves content using Claude API"
        )
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None

        if HAS_ANTHROPIC and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.log("Claude API client initialized")
        else:
            self.log("Running in offline mode (no API key or anthropic not installed)", "yellow")

    async def execute_task(self, task: Task) -> Any:
        """Execute LLM-related tasks"""
        task_type = task.input_data.get("type", "generate_content") if task.input_data else "generate_content"

        if task_type == "generate_content":
            return await self._generate_content(task.input_data)
        elif task_type == "generate_slides":
            return await self._generate_slides(task.input_data)
        elif task_type == "improve_content":
            return await self._improve_content(task.input_data)
        elif task_type == "generate_speaker_notes":
            return await self._generate_speaker_notes(task.input_data)
        elif task_type == "summarize_data":
            return await self._summarize_data(task.input_data)
        elif task_type == "translate":
            return await self._translate(task.input_data)
        else:
            return await self._generate_content(task.input_data)

    def _call_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
        """Call Claude API with given prompts"""
        if not self.client:
            self.log("API client not available, using fallback", "yellow")
            return self._fallback_response(user_prompt)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            self.log(f"API call failed: {e}", "red")
            return self._fallback_response(user_prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Provide fallback response when API is not available"""
        return json.dumps({
            "note": "Generated offline - API not available",
            "prompt_received": prompt[:100] + "..." if len(prompt) > 100 else prompt
        })

    async def _generate_content(self, input_data: Dict) -> Dict:
        """Generate presentation content from a topic"""
        topic = input_data.get("topic", "")
        context = input_data.get("context", "")
        audience = input_data.get("audience", "ビジネスプロフェッショナル")
        tone = input_data.get("tone", "professional")
        num_slides = input_data.get("num_slides", 5)

        self.log(f"Generating content for: {topic}")

        system_prompt = """あなたはプレゼンテーション資料の専門家です。
与えられたトピックに基づいて、構造化されたプレゼンテーションコンテンツを生成してください。
出力は必ずJSON形式で、以下の構造に従ってください：

{
    "title": "プレゼンテーションのタイトル",
    "slides": [
        {
            "type": "title|agenda|content|two_column|conclusion",
            "title": "スライドタイトル",
            "body": ["箇条書き1", "箇条書き2", ...],
            "notes": "スピーカーノート"
        }
    ]
}"""

        user_prompt = f"""以下の条件でプレゼンテーションコンテンツを生成してください：

トピック: {topic}
追加コンテキスト: {context}
対象者: {audience}
トーン: {tone}
スライド数: {num_slides}枚

JSONのみを出力してください。"""

        response = self._call_claude(system_prompt, user_prompt)

        try:
            # Try to parse JSON from response
            content = json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, create structured content
            content = self._create_fallback_content(topic, num_slides)

        self.log(f"Generated content with {len(content.get('slides', []))} slides")
        return content

    async def _generate_slides(self, input_data: Dict) -> Dict:
        """Generate detailed slide content from outline"""
        outline = input_data.get("outline", {})
        research_data = input_data.get("research_data", {})
        insights = input_data.get("insights", [])

        self.log("Generating detailed slides from outline...")

        system_prompt = """あなたはプレゼンテーション資料の専門家です。
アウトラインとリサーチデータから、詳細なスライドコンテンツを生成してください。
各スライドには具体的なデータや洞察を含めてください。

出力は必ずJSON形式で、各スライドに以下を含めてください：
- title: スライドタイトル
- type: スライドタイプ
- body: 本文（配列）
- key_points: 重要ポイント（配列）
- data_reference: 参照データ（あれば）
- notes: スピーカーノート"""

        user_prompt = f"""以下のアウトラインを詳細なスライドに展開してください：

アウトライン:
{json.dumps(outline, ensure_ascii=False, indent=2)}

リサーチデータ:
{json.dumps(research_data, ensure_ascii=False, indent=2) if research_data else "なし"}

インサイト:
{json.dumps(insights, ensure_ascii=False, indent=2) if insights else "なし"}

JSONのみを出力してください。"""

        response = self._call_claude(system_prompt, user_prompt)

        try:
            content = json.loads(response)
        except json.JSONDecodeError:
            content = outline  # Fallback to outline

        return content

    async def _improve_content(self, input_data: Dict) -> Dict:
        """Improve existing content"""
        content = input_data.get("content", {})
        instructions = input_data.get("instructions", "より説得力のある内容に改善してください")

        self.log("Improving content...")

        system_prompt = """あなたはプレゼンテーション資料の専門家です。
既存のコンテンツを改善し、より効果的なプレゼンテーションにしてください。
元の構造を維持しながら、内容を向上させてください。"""

        user_prompt = f"""以下のコンテンツを改善してください：

改善指示: {instructions}

現在のコンテンツ:
{json.dumps(content, ensure_ascii=False, indent=2)}

改善されたJSON形式のコンテンツを出力してください。"""

        response = self._call_claude(system_prompt, user_prompt)

        try:
            improved = json.loads(response)
        except json.JSONDecodeError:
            improved = content

        return improved

    async def _generate_speaker_notes(self, input_data: Dict) -> Dict:
        """Generate speaker notes for slides"""
        slides = input_data.get("slides", [])

        self.log("Generating speaker notes...")

        system_prompt = """あなたはプレゼンテーションのコーチです。
各スライドに対して、効果的なスピーカーノートを生成してください。
ノートには話すべきポイント、強調点、時間配分のヒントを含めてください。"""

        user_prompt = f"""以下のスライドにスピーカーノートを追加してください：

{json.dumps(slides, ensure_ascii=False, indent=2)}

各スライドにnotesフィールドを追加したJSONを出力してください。"""

        response = self._call_claude(system_prompt, user_prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Add default notes
            result = {"slides": slides}
            for slide in result.get("slides", []):
                if "notes" not in slide:
                    slide["notes"] = f"【{slide.get('title', 'スライド')}】について説明"

        return result

    async def _summarize_data(self, input_data: Dict) -> Dict:
        """Summarize research data into key points"""
        data = input_data.get("data", {})
        focus = input_data.get("focus", "")

        self.log("Summarizing data...")

        system_prompt = """あなたはデータアナリストです。
与えられたデータを分析し、プレゼンテーションで使える形式にまとめてください。"""

        user_prompt = f"""以下のデータを分析し、重要なポイントをまとめてください：

フォーカス: {focus}

データ:
{json.dumps(data, ensure_ascii=False, indent=2)}

以下のJSON形式で出力してください：
{{
    "summary": "概要",
    "key_findings": ["発見1", "発見2", ...],
    "recommendations": ["推奨1", "推奨2", ...],
    "data_highlights": [{{}}]
}}"""

        response = self._call_claude(system_prompt, user_prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {
                "summary": "データ分析結果",
                "key_findings": ["データを確認してください"],
                "recommendations": [],
                "data_highlights": []
            }

        return result

    async def _translate(self, input_data: Dict) -> Dict:
        """Translate content to another language"""
        content = input_data.get("content", {})
        target_language = input_data.get("target_language", "English")

        self.log(f"Translating to {target_language}...")

        system_prompt = f"""あなたは翻訳の専門家です。
プレゼンテーションコンテンツを{target_language}に翻訳してください。
ビジネス文書として適切な表現を使用し、元の構造を維持してください。"""

        user_prompt = f"""以下のコンテンツを{target_language}に翻訳してください：

{json.dumps(content, ensure_ascii=False, indent=2)}

翻訳されたJSONを出力してください。"""

        response = self._call_claude(system_prompt, user_prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = content

        return result

    def _create_fallback_content(self, topic: str, num_slides: int) -> Dict:
        """Create fallback content when API is not available"""
        slides = [
            {
                "type": "title",
                "title": topic,
                "subtitle": "プレゼンテーション資料",
                "notes": "タイトルスライド - 挨拶から始める"
            },
            {
                "type": "agenda",
                "title": "アジェンダ",
                "body": ["背景・目的", "現状分析", "提案内容", "まとめ"],
                "notes": "今日の流れを説明"
            }
        ]

        # Add content slides
        for i in range(num_slides - 3):
            slides.append({
                "type": "content",
                "title": f"ポイント {i + 1}",
                "body": [
                    "重要なポイント1",
                    "重要なポイント2",
                    "重要なポイント3"
                ],
                "notes": f"セクション{i + 1}の説明"
            })

        slides.append({
            "type": "conclusion",
            "title": "まとめ",
            "body": [
                "本日の要約",
                "次のステップ",
                "お問い合わせ先"
            ],
            "notes": "まとめと次のアクションを伝える"
        })

        return {
            "title": topic,
            "slides": slides
        }
