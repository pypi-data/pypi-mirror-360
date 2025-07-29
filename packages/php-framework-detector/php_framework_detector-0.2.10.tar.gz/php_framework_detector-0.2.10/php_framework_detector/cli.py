"""
Modern CLI interface for PHP Framework Detector.

This module provides a clean, async-aware command-line interface with structured logging,
comprehensive error handling, and user-friendly output formatting.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import structlog

from .core.detector import FrameworkDetector
from .core.factory import FrameworkDetectorFactory
from .core.models import DetectionResult, FrameworkInfo
from .core.exceptions import DetectionError, InvalidPathError

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
app = typer.Typer(
    name="php-framework-detector",
    help="Detect PHP frameworks in project directories",
    add_completion=False,
)
console = Console()





async def detect_frameworks_async(project_path: Path) -> DetectionResult:
    """
    Asynchronously detect frameworks in the given project path.
    
    Args:
        project_path: Path to the PHP project directory
        
    Returns:
        DetectionResult containing detection scores and results
        
    Raises:
        InvalidPathError: If the project path is invalid
        DetectionError: If detection fails
    """
    try:
        if not project_path.exists():
            raise InvalidPathError(f"Project path does not exist: {project_path}")
        
        if not project_path.is_dir():
            raise InvalidPathError(f"Project path is not a directory: {project_path}")
        
        logger.debug("Starting framework detection", project_path=str(project_path))
        
        # Get all available detectors
        detectors = FrameworkDetectorFactory.get_all_detectors(str(project_path))
        framework_names = FrameworkDetectorFactory.get_framework_names()
        
        scores: Dict[str, int] = {}
        detected_framework: Optional[str] = None
        
        # Process each detector
        for detector in detectors:
            try:
                score = await detector.detect_async()
                scores[detector.name] = score
                
                if score == 100 and detected_framework is None:
                    detected_framework = detector.name
                    logger.debug(
                        "Framework detected",
                        framework=detector.name,
                        display_name=detector.display_name
                    )
                    
            except Exception as e:
                logger.warning(
                    "Detection failed for framework",
                    framework=detector.name,
                    error=str(e)
                )
                scores[detector.name] = 0
        
        # Determine final result
        detected_framework = detected_framework or "na"
        detected_name = framework_names.get(detected_framework, "Unknown")
        
        result = DetectionResult(
            detected_framework=detected_framework,
            detected_name=detected_name,
            scores=scores,
            project_path=str(project_path)
        )
        
        logger.debug(
            "Detection completed",
            detected_framework=detected_framework,
            detected_name=detected_name
        )
        
        return result
        
    except Exception as e:
        logger.error("Framework detection failed", error=str(e))
        raise DetectionError(f"Detection failed: {e}") from e


def display_results(result: DetectionResult, show_all: bool = False, json_output: bool = False) -> None:
    """
    Display detection results in the specified format.
    
    Args:
        result: Detection result to display
        show_all: Whether to show all frameworks or only detected ones
        json_output: Whether to output in JSON format
    """
    if json_output:
        console.print(JSON(result.model_dump_json(indent=2)))
        return
    
    # Create results table
    table = Table(
        title="PHP Framework Detection Results",
        show_lines=True,
        header_style="bold magenta"
    )
    table.add_column("Framework Code", style="cyan", no_wrap=True)
    table.add_column("Framework Name", style="magenta")
    table.add_column("Score", style="green", justify="right")
    
    framework_names = FrameworkDetectorFactory.get_framework_names()
    
    for code, name in framework_names.items():
        if code == "na":
            continue
            
        score = result.scores.get(code, 0)
        if not show_all and score == 0:
            continue
            
        # Highlight detected framework
        if code == result.detected_framework:
            table.add_row(
                f"[bold green]{code}[/bold green]",
                f"[bold green]{name}[/bold green]",
                f"[bold green]{score}[/bold green]"
            )
        else:
            table.add_row(code, name, str(score))
    
    console.print(table)
    
    # Display final result
    status_style = "bold green" if result.detected_framework != "na" else "bold yellow"
    result_text = Text(f"{result.detected_name} ({result.detected_framework})", style=status_style)
    
    panel = Panel(
        result_text,
        title="Detection Result",
        border_style="green" if result.detected_framework != "na" else "yellow"
    )
    console.print(panel)


@app.command()
def detect(
    path: str = typer.Argument(
        ...,
        help="Path to the PHP project directory to analyze"
    ),
    json: bool = typer.Option(
        False,
        "--json",
        "-j",
        help="Output results in JSON format"
    ),
    show_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all frameworks, including those with zero scores"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    )
) -> None:
    """
    Detect PHP frameworks in the specified project directory.
    
    This command analyzes the given directory to identify which PHP framework
    (if any) is being used. It examines composer files, directory structures,
    and other framework-specific indicators to make its determination.
    
    Examples:
        php-framework-detector /path/to/php/project
        php-framework-detector /path/to/php/project --json
        php-framework-detector /path/to/php/project --all --verbose
    """
    try:
        # Configure logging level
        if verbose:
            structlog.stdlib.get_logger().setLevel("DEBUG")
        
        project_path = Path(path).resolve()
        
        # Run detection
        result = asyncio.run(detect_frameworks_async(project_path))
        
        # Display results
        display_results(result, show_all=show_all, json_output=json)
        
    except InvalidPathError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except DetectionError as e:
        console.print(f"[red]Detection failed: {e}[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Detection cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_frameworks() -> None:
    """
    List all supported PHP frameworks.
    
    Displays a table of all frameworks that can be detected by this tool,
    along with their display names and detection capabilities.
    """
    try:
        frameworks = FrameworkDetectorFactory.get_all_detectors("")
        framework_names = FrameworkDetectorFactory.get_framework_names()
        
        table = Table(
            title="Supported PHP Frameworks",
            show_lines=True,
            header_style="bold magenta"
        )
        table.add_column("Code", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="white")
        
        for detector in frameworks:
            description = getattr(detector, 'description', 'No description available')
            table.add_row(detector.name, detector.display_name, description)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing frameworks: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Display version information."""
    console.print("PHP Framework Detector v0.2.0")


if __name__ == "__main__":
    app() 