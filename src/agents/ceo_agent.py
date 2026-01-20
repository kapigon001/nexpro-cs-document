"""CEO Agent - The Orchestrator that manages all other agents"""
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import asyncio
import uuid

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .content_agent import ContentAgent
from .design_agent import DesignAgent
from .builder_agent import BuilderAgent
from ..core.task import Task, TaskStatus
from ..core.workflow import Workflow
from ..core.message import Message, MessageType


console = Console()


class CEOAgent(BaseAgent):
    """
    CEO Agent: The Orchestrator that coordinates all other agents.

    Responsibilities:
    - Receive user requirements and create project plan
    - Delegate tasks to appropriate agents
    - Monitor progress and handle issues
    - Ensure quality and approve deliverables
    - Coordinate inter-agent communication
    """

    def __init__(self, output_dir: str = "output"):
        super().__init__(
            name="CEOAgent",
            role="Orchestrator",
            description="Coordinates all agents and manages the presentation creation workflow"
        )

        # Initialize sub-agents
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.design_agent = DesignAgent()
        self.builder_agent = BuilderAgent(output_dir=output_dir)

        # Track all agents
        self.agents = {
            "research": self.research_agent,
            "content": self.content_agent,
            "design": self.design_agent,
            "builder": self.builder_agent,
        }

        # Current workflow
        self.workflow: Optional[Workflow] = None

        # Project context
        self.project_context: Dict = {}

    def log(self, message: str, style: str = ""):
        """Override log with CEO styling"""
        console.print(f"[bold magenta][CEO][/bold magenta] {message}", style=style)

    async def execute_task(self, task: Task) -> Any:
        """Execute orchestration tasks"""
        task_type = task.input_data.get("type", "create_presentation") if task.input_data else "create_presentation"

        if task_type == "create_presentation":
            return await self.create_presentation(task.input_data)
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

        # Display project start
        console.print(Panel(
            f"[bold]プロジェクト開始[/bold]\n\n"
            f"トピック: {topic}\n"
            f"データファイル: {data_file or 'なし'}\n"
            f"テーマ: {theme}\n"
            f"出力ファイル: {output_filename}",
            title="[magenta]CEO Agent - プロジェクト概要[/magenta]",
            border_style="magenta"
        ))

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
            "build": None,
        }

        try:
            # ============================================
            # Phase 1: Research
            # ============================================
            self.log("📊 Phase 1: リサーチフェーズを開始します")

            if data_file:
                # Read and analyze data file
                research_task = Task(
                    id=str(uuid.uuid4())[:8],
                    name="データ分析",
                    description=f"Analyze data from {data_file}",
                    input_data={
                        "type": "read_excel",
                        "file_path": data_file,
                    }
                )
                self.research_agent.receive_task(research_task)
                results["research"] = await self.research_agent.run()

                # Extract insights
                if results["research"]:
                    insight_task = Task(
                        id=str(uuid.uuid4())[:8],
                        name="インサイト抽出",
                        description="Extract insights from analyzed data",
                        input_data={
                            "type": "analyze_data",
                            "data": results["research"].get("sheets", {}).get(
                                list(results["research"].get("sheets", {}).keys())[0], {}
                            ).get("sample", {}) if results["research"].get("sheets") else {},
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
                    results["insights"] = await self.research_agent.run()

            self._show_phase_complete("Research", "✅")

            # ============================================
            # Phase 2: Content Creation
            # ============================================
            self.log("📝 Phase 2: コンテンツ作成フェーズを開始します")

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
                }
            )
            self.content_agent.receive_task(outline_task)
            results["outline"] = await self.content_agent.run()

            # Create full content
            content_task = Task(
                id=str(uuid.uuid4())[:8],
                name="コンテンツ作成",
                description="Create full presentation content",
                input_data={
                    "type": "create_full_content",
                    "outline": results["outline"],
                    "research_data": results.get("research", {}),
                    "insights": results.get("insights", []),
                }
            )
            self.content_agent.receive_task(content_task)
            results["content"] = await self.content_agent.run()

            self._show_phase_complete("Content", "✅")

            # ============================================
            # Phase 3: Design
            # ============================================
            self.log("🎨 Phase 3: デザインフェーズを開始します")

            design_task = Task(
                id=str(uuid.uuid4())[:8],
                name="プレゼンテーションデザイン",
                description="Design presentation styling",
                input_data={
                    "type": "design_presentation",
                    "content": results["content"],
                    "theme": theme,
                }
            )
            self.design_agent.receive_task(design_task)
            results["design"] = await self.design_agent.run()

            self._show_phase_complete("Design", "✅")

            # ============================================
            # Phase 4: Build
            # ============================================
            self.log("🔨 Phase 4: ビルドフェーズを開始します")

            build_task = Task(
                id=str(uuid.uuid4())[:8],
                name="PowerPoint生成",
                description="Generate PowerPoint file",
                input_data={
                    "type": "build_presentation",
                    "content": results["content"],
                    "design": results["design"],
                    "filename": output_filename,
                }
            )
            self.builder_agent.receive_task(build_task)
            results["build"] = await self.builder_agent.run()

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
            }

        except Exception as e:
            self.log(f"❌ エラーが発生しました: {str(e)}", "red")
            return {
                "success": False,
                "error": str(e),
                "partial_results": results,
            }

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

    async def run_interactive(self):
        """Run in interactive mode (for future CLI interface)"""
        console.print(Panel(
            "[bold]Multi-Agent PowerPoint Orchestrator[/bold]\n\n"
            "CEOエージェントとして、複数のサブエージェントを\n"
            "統括してプレゼンテーションを自動生成します。",
            title="[magenta]Welcome[/magenta]",
            border_style="magenta"
        ))

        # This could be expanded for interactive CLI usage
        pass
