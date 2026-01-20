"""CEO Agent - The Orchestrator that manages all other agents"""
from typing import Any, Dict, List, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import asyncio
import uuid
from enum import Enum

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .content_agent import ContentAgent
from .design_agent import DesignAgent
from .builder_agent import BuilderAgent
from .llm_agent import LLMAgent
from .chart_agent import ChartAgent
from ..core.task import Task, TaskStatus
from ..core.workflow import Workflow
from ..core.message import Message, MessageType
from ..core.templates import PresentationTemplate


console = Console()


class ExecutionMode(Enum):
    """Execution mode for the orchestrator"""
    SEQUENTIAL = "sequential"  # Run phases one by one
    PARALLEL = "parallel"      # Run independent tasks in parallel
    ADAPTIVE = "adaptive"      # Automatically choose based on task


class CEOAgent(BaseAgent):
    """
    CEO Agent: The Orchestrator that coordinates all other agents.

    Responsibilities:
    - Receive user requirements and create project plan
    - Delegate tasks to appropriate agents
    - Monitor progress and handle issues
    - Ensure quality and approve deliverables
    - Coordinate inter-agent communication
    - Support parallel execution of independent tasks
    - Integrate LLM for AI-powered content generation
    """

    def __init__(
        self,
        output_dir: str = "output",
        execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE,
        use_llm: bool = True,
        llm_api_key: Optional[str] = None,
    ):
        super().__init__(
            name="CEOAgent",
            role="Orchestrator",
            description="Coordinates all agents and manages the presentation creation workflow"
        )

        self.output_dir = output_dir
        self.execution_mode = execution_mode
        self.use_llm = use_llm

        # Initialize sub-agents
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.design_agent = DesignAgent()
        self.builder_agent = BuilderAgent(output_dir=output_dir)
        self.chart_agent = ChartAgent(output_dir=f"{output_dir}/charts")

        # LLM Agent (optional)
        self.llm_agent = None
        if use_llm:
            self.llm_agent = LLMAgent(api_key=llm_api_key)

        # Track all agents
        self.agents = {
            "research": self.research_agent,
            "content": self.content_agent,
            "design": self.design_agent,
            "builder": self.builder_agent,
            "chart": self.chart_agent,
        }
        if self.llm_agent:
            self.agents["llm"] = self.llm_agent

        # Template manager
        self.template_manager = PresentationTemplate()

        # Current workflow
        self.workflow: Optional[Workflow] = None

        # Project context
        self.project_context: Dict = {}

        # Event hooks
        self.hooks: Dict[str, List[Callable]] = {
            "on_phase_start": [],
            "on_phase_complete": [],
            "on_task_complete": [],
            "on_error": [],
        }

    def log(self, message: str, style: str = ""):
        """Override log with CEO styling"""
        console.print(f"[bold magenta][CEO][/bold magenta] {message}", style=style)

    def register_hook(self, event: str, callback: Callable):
        """Register a hook for an event"""
        if event in self.hooks:
            self.hooks[event].append(callback)

    async def _trigger_hooks(self, event: str, **kwargs):
        """Trigger all hooks for an event"""
        for callback in self.hooks.get(event, []):
            if asyncio.iscoroutinefunction(callback):
                await callback(**kwargs)
            else:
                callback(**kwargs)

    async def execute_task(self, task: Task) -> Any:
        """Execute orchestration tasks"""
        task_type = task.input_data.get("type", "create_presentation") if task.input_data else "create_presentation"

        if task_type == "create_presentation":
            return await self.create_presentation(task.input_data)
        elif task_type == "create_presentation_advanced":
            return await self.create_presentation_advanced(task.input_data)
        elif task_type == "create_from_template":
            return await self.create_from_template(task.input_data)
        else:
            return await self.create_presentation(task.input_data)

    async def create_presentation(self, requirements: Dict) -> Dict:
        """
        Main orchestration method: Create a complete presentation.

        This method coordinates all agents through the following phases:
        1. Research Phase: Gather and analyze data
        2. Content Phase: Create presentation structure and content
        3. Design Phase: Apply visual design and layouts
        4. Build Phase: Generate the actual PowerPoint file
        """
        topic = requirements.get("topic", "Presentation")
        data_file = requirements.get("data_file")
        theme = requirements.get("theme", "corporate")
        output_filename = requirements.get("output_filename", "presentation.pptx")
        presentation_type = requirements.get("presentation_type")
        include_charts = requirements.get("include_charts", True)

        # Display project start
        self._show_project_start(topic, data_file, theme, output_filename)

        # Initialize workflow
        self.workflow = Workflow(
            name=f"Presentation: {topic}",
            description=f"Create presentation about {topic}"
        )

        results = {
            "research": None,
            "insights": None,
            "outline": None,
            "content": None,
            "design": None,
            "charts": None,
            "build": None,
        }

        try:
            # ============================================
            # Phase 1: Research
            # ============================================
            await self._trigger_hooks("on_phase_start", phase="research")
            self.log("📊 Phase 1: リサーチフェーズを開始します")

            results["research"], results["insights"] = await self._execute_research_phase(
                data_file, topic
            )

            await self._trigger_hooks("on_phase_complete", phase="research", results=results["research"])
            self._show_phase_complete("Research", "✅")

            # ============================================
            # Phase 2: Content Creation (with optional LLM)
            # ============================================
            await self._trigger_hooks("on_phase_start", phase="content")
            self.log("📝 Phase 2: コンテンツ作成フェーズを開始します")

            results["outline"], results["content"] = await self._execute_content_phase(
                topic, results, requirements, presentation_type
            )

            await self._trigger_hooks("on_phase_complete", phase="content", results=results["content"])
            self._show_phase_complete("Content", "✅")

            # ============================================
            # Phase 3: Design & Charts (Parallel)
            # ============================================
            await self._trigger_hooks("on_phase_start", phase="design")
            self.log("🎨 Phase 3: デザイン＆チャートフェーズを開始します")

            if self.execution_mode in [ExecutionMode.PARALLEL, ExecutionMode.ADAPTIVE]:
                # Run design and chart generation in parallel
                design_coro = self._execute_design_phase(results["content"], theme)
                chart_coro = self._execute_chart_phase(results["research"], include_charts)

                design_result, charts_result = await asyncio.gather(
                    design_coro, chart_coro, return_exceptions=True
                )

                results["design"] = design_result if not isinstance(design_result, Exception) else None
                results["charts"] = charts_result if not isinstance(charts_result, Exception) else None
            else:
                results["design"] = await self._execute_design_phase(results["content"], theme)
                results["charts"] = await self._execute_chart_phase(results["research"], include_charts)

            await self._trigger_hooks("on_phase_complete", phase="design", results=results["design"])
            self._show_phase_complete("Design & Charts", "✅")

            # ============================================
            # Phase 4: Build
            # ============================================
            await self._trigger_hooks("on_phase_start", phase="build")
            self.log("🔨 Phase 4: ビルドフェーズを開始します")

            results["build"] = await self._execute_build_phase(
                results["content"],
                results["design"],
                results.get("charts"),
                output_filename
            )

            await self._trigger_hooks("on_phase_complete", phase="build", results=results["build"])
            self._show_phase_complete("Build", "✅")

            # ============================================
            # Final Summary
            # ============================================
            self._show_final_summary(results)

            return {
                "success": True,
                "file_path": results["build"].get("file_path"),
                "slide_count": results["build"].get("slide_count"),
                "phases_completed": ["research", "content", "design", "build"],
                "charts_generated": len(results.get("charts", {}).get("charts", [])) if results.get("charts") else 0,
            }

        except Exception as e:
            await self._trigger_hooks("on_error", error=str(e))
            self.log(f"❌ エラーが発生しました: {str(e)}", "red")
            return {
                "success": False,
                "error": str(e),
                "partial_results": results,
            }

    async def _execute_research_phase(self, data_file: Optional[str], topic: str) -> tuple:
        """Execute research phase"""
        research_result = None
        insights_result = None

        if data_file:
            # Read and analyze data file
            research_task = Task(
                id=str(uuid.uuid4())[:8],
                name="データ分析",
                description=f"Analyze data from {data_file}",
                input_data={
                    "type": "read_excel" if data_file.endswith(('.xlsx', '.xls')) else "read_csv",
                    "file_path": data_file,
                }
            )
            self.research_agent.receive_task(research_task)
            research_result = await self.research_agent.run()

            # Extract insights
            if research_result:
                sheets = research_result.get("sheets", {})
                if sheets:
                    first_sheet_name = list(sheets.keys())[0]
                    sample_data = sheets[first_sheet_name].get("sample", {})

                    insight_task = Task(
                        id=str(uuid.uuid4())[:8],
                        name="インサイト抽出",
                        description="Extract insights from analyzed data",
                        input_data={
                            "type": "analyze_data",
                            "data": sample_data,
                        }
                    )
                    self.research_agent.receive_task(insight_task)
                    analysis = await self.research_agent.run()

                    insight_extract_task = Task(
                        id=str(uuid.uuid4())[:8],
                        name="インサイト整理",
                        description="Organize insights",
                        input_data={
                            "type": "extract_insights",
                            "analysis": analysis,
                            "context": topic,
                        }
                    )
                    self.research_agent.receive_task(insight_extract_task)
                    insights_result = await self.research_agent.run()

        return research_result, insights_result

    async def _execute_content_phase(
        self,
        topic: str,
        results: Dict,
        requirements: Dict,
        presentation_type: Optional[str]
    ) -> tuple:
        """Execute content creation phase"""

        # Use LLM for content generation if available
        if self.llm_agent and self.use_llm:
            self.log("🤖 LLM Agentを使用してコンテンツを生成します")

            llm_task = Task(
                id=str(uuid.uuid4())[:8],
                name="AIコンテンツ生成",
                description="Generate content using AI",
                input_data={
                    "type": "generate_content",
                    "topic": topic,
                    "context": str(results.get("insights", [])),
                    "audience": requirements.get("audience", "ビジネスプロフェッショナル"),
                    "tone": requirements.get("tone", "professional"),
                    "num_slides": requirements.get("num_slides", 5),
                }
            )
            self.llm_agent.receive_task(llm_task)
            content_result = await self.llm_agent.run()

            outline_result = {
                "title": topic,
                "slides": [{"title": s.get("title"), "type": s.get("type")} for s in content_result.get("slides", [])]
            }

            return outline_result, content_result

        # Use template-based content generation
        if presentation_type:
            ptype = self.template_manager.get_presentation_type(presentation_type)
            if ptype:
                self.log(f"📋 テンプレート「{ptype['name']}」を使用します")

        # Create outline
        outline_task = Task(
            id=str(uuid.uuid4())[:8],
            name="アウトライン作成",
            description="Create presentation outline",
            input_data={
                "type": "create_outline",
                "topic": topic,
                "insights": results.get("insights", []),
                "num_slides": requirements.get("num_slides", 5),
                "presentation_type": presentation_type,
            }
        )
        self.content_agent.receive_task(outline_task)
        outline_result = await self.content_agent.run()

        # Create full content
        content_task = Task(
            id=str(uuid.uuid4())[:8],
            name="コンテンツ作成",
            description="Create full presentation content",
            input_data={
                "type": "create_full_content",
                "outline": outline_result,
                "research_data": results.get("research", {}),
                "insights": results.get("insights", []),
            }
        )
        self.content_agent.receive_task(content_task)
        content_result = await self.content_agent.run()

        return outline_result, content_result

    async def _execute_design_phase(self, content: Dict, theme: str) -> Dict:
        """Execute design phase"""
        design_task = Task(
            id=str(uuid.uuid4())[:8],
            name="プレゼンテーションデザイン",
            description="Design presentation styling",
            input_data={
                "type": "design_presentation",
                "content": content,
                "theme": theme,
            }
        )
        self.design_agent.receive_task(design_task)
        return await self.design_agent.run()

    async def _execute_chart_phase(self, research_data: Optional[Dict], include_charts: bool) -> Dict:
        """Execute chart generation phase"""
        if not include_charts or not research_data:
            return {"charts": [], "count": 0}

        self.log("📈 チャートを生成中...")

        chart_task = Task(
            id=str(uuid.uuid4())[:8],
            name="チャート生成",
            description="Generate charts from data",
            input_data={
                "type": "analyze_and_visualize",
                "data": research_data.get("sheets", {}),
                "title": "データ分析",
            }
        )
        self.chart_agent.receive_task(chart_task)
        return await self.chart_agent.run()

    async def _execute_build_phase(
        self,
        content: Dict,
        design: Dict,
        charts: Optional[Dict],
        filename: str
    ) -> Dict:
        """Execute build phase"""
        build_task = Task(
            id=str(uuid.uuid4())[:8],
            name="PowerPoint生成",
            description="Generate PowerPoint file",
            input_data={
                "type": "build_presentation",
                "content": content,
                "design": design,
                "charts": charts,
                "filename": filename,
            }
        )
        self.builder_agent.receive_task(build_task)
        return await self.builder_agent.run()

    async def create_presentation_advanced(self, requirements: Dict) -> Dict:
        """
        Advanced presentation creation with more control.

        Supports:
        - Custom slide ordering
        - Specific chart requests
        - Speaker notes generation
        - Multi-language support
        """
        # Enhanced version with more options
        base_result = await self.create_presentation(requirements)

        if not base_result.get("success"):
            return base_result

        # Generate speaker notes if requested
        if requirements.get("generate_speaker_notes") and self.llm_agent:
            self.log("📝 スピーカーノートを生成中...")
            notes_task = Task(
                id=str(uuid.uuid4())[:8],
                name="スピーカーノート生成",
                description="Generate speaker notes",
                input_data={
                    "type": "generate_speaker_notes",
                    "slides": base_result.get("content", {}).get("slides", []),
                }
            )
            self.llm_agent.receive_task(notes_task)
            await self.llm_agent.run()

        return base_result

    async def create_from_template(self, requirements: Dict) -> Dict:
        """Create presentation from a predefined template"""
        template_name = requirements.get("template", "business_proposal")

        template = self.template_manager.get_presentation_type(template_name)
        if not template:
            return {"success": False, "error": f"Template not found: {template_name}"}

        self.log(f"📋 テンプレート「{template['name']}」から作成します")

        # Merge template requirements with user requirements
        merged_requirements = {
            **requirements,
            "presentation_type": template_name,
            "theme": requirements.get("theme", template.get("recommended_theme", "corporate")),
        }

        return await self.create_presentation(merged_requirements)

    def _show_project_start(self, topic: str, data_file: Optional[str], theme: str, filename: str):
        """Display project start panel"""
        mode_str = f"実行モード: {self.execution_mode.value}"
        llm_str = "LLM: 有効" if self.use_llm and self.llm_agent else "LLM: 無効"

        console.print(Panel(
            f"[bold]プロジェクト開始[/bold]\n\n"
            f"トピック: {topic}\n"
            f"データファイル: {data_file or 'なし'}\n"
            f"テーマ: {theme}\n"
            f"出力ファイル: {filename}\n"
            f"{mode_str}\n"
            f"{llm_str}",
            title="[magenta]CEO Agent - プロジェクト概要[/magenta]",
            border_style="magenta"
        ))

    def _show_phase_complete(self, phase_name: str, status: str):
        """Show phase completion status"""
        console.print(f"  {status} {phase_name} フェーズ完了")

    def _show_final_summary(self, results: Dict):
        """Show final project summary"""
        table = Table(title="プロジェクト完了サマリー")
        table.add_column("フェーズ", style="cyan")
        table.add_column("ステータス", style="green")
        table.add_column("詳細", style="white")

        # Research
        if results.get("research"):
            sheets = results["research"].get("summary", {}).get("total_sheets", 0)
            table.add_row("Research", "✅ 完了", f"{sheets} シート分析済み")
        else:
            table.add_row("Research", "⏭️ スキップ", "データファイルなし")

        # Content
        if results.get("content"):
            slides = len(results["content"].get("slides", []))
            table.add_row("Content", "✅ 完了", f"{slides} スライド作成")

        # Design
        if results.get("design"):
            theme = results["design"].get("theme", {}).get("name", "default")
            table.add_row("Design", "✅ 完了", f"テーマ: {theme}")

        # Charts
        if results.get("charts"):
            chart_count = results["charts"].get("count", 0)
            table.add_row("Charts", "✅ 完了", f"{chart_count} チャート生成")

        # Build
        if results.get("build"):
            file_path = results["build"].get("file_path", "")
            table.add_row("Build", "✅ 完了", f"出力: {file_path}")

        console.print()
        console.print(table)
        console.print()

    def get_all_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            name: agent.get_status()
            for name, agent in self.agents.items()
        }

    def list_available_templates(self) -> List[Dict]:
        """List all available presentation templates"""
        return self.template_manager.list_presentation_types()

    def list_available_themes(self) -> List[Dict]:
        """List all available themes"""
        return self.template_manager.list_themes()

    async def run_interactive(self):
        """Run in interactive mode"""
        console.print(Panel(
            "[bold]Multi-Agent PowerPoint Orchestrator[/bold]\n\n"
            "CEOエージェントとして、複数のサブエージェントを\n"
            "統括してプレゼンテーションを自動生成します。\n\n"
            f"利用可能なエージェント: {', '.join(self.agents.keys())}\n"
            f"実行モード: {self.execution_mode.value}\n"
            f"LLM: {'有効' if self.llm_agent else '無効'}",
            title="[magenta]Welcome[/magenta]",
            border_style="magenta"
        ))
