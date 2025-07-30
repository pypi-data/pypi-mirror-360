#!/usr/bin/env python3
"""Rich-based Progress Tracking System for SocialMapper.

Key Features:
- Beautiful Rich progress bars with real-time metrics
- Professional console output with colors and formatting
- Status indicators with spinners for long operations
- Optimized for CLI usage with Rich console
- Memory and performance monitoring
- Rich tracebacks for better error reporting
- Tables for summary data
"""

import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

import psutil
from rich import box

# Rich imports
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.status import Status
from rich.table import Table
from rich.traceback import install as install_rich_traceback

if TYPE_CHECKING:
    from rich.live import Live

# Always use Rich console output

# Install Rich tracebacks globally
install_rich_traceback(show_locals=True)

# Global console for SocialMapper
console = Console()


class ProcessingStage(Enum):
    """Enumeration of main processing stages in the SocialMapper pipeline."""

    SETUP = "setup"
    POI_PROCESSING = "poi_processing"
    ISOCHRONE_GENERATION = "isochrone_generation"
    CENSUS_INTEGRATION = "census_integration"
    EXPORT_VISUALIZATION = "export_visualization"


@dataclass
class RichProgressMetrics:
    """Performance metrics for Rich progress tracking."""

    stage: ProcessingStage
    start_time: float = field(default_factory=time.time)
    items_processed: int = 0
    total_items: int | None = None
    throughput_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    estimated_time_remaining: float | None = None

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time

    def update_throughput(self):
        """Update throughput calculation."""
        elapsed = self.get_elapsed_time()
        if elapsed > 0:
            self.throughput_per_second = self.items_processed / elapsed

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024


class RichProgressTracker:
    """Rich-based progress tracker for SocialMapper.

    Provides beautiful progress bars, status indicators, and console output
    using the Rich library for an excellent user experience.
    """

    def __init__(self, enable_performance_metrics: bool = True):
        """Initialize the Rich progress tracker.

        Args:
            enable_performance_metrics: Whether to track performance metrics
        """
        self.console = console
        self.enable_performance_metrics = enable_performance_metrics
        self.current_stage: ProcessingStage | None = None
        self.stage_metrics: dict[ProcessingStage, RichProgressMetrics] = {}
        self.progress: Progress | None = None
        self.current_task_id: int | None = None
        self.live: Live | None = None
        self._lock = threading.Lock()

        # Stage configurations with emojis and descriptions
        self.stage_configs = {
            ProcessingStage.SETUP: {
                "emoji": "⚙️",
                "description": "Setting up analysis environment",
                "color": "cyan",
            },
            ProcessingStage.POI_PROCESSING: {
                "emoji": "🗺️",
                "description": "Processing points of interest",
                "color": "yellow",
            },
            ProcessingStage.ISOCHRONE_GENERATION: {
                "emoji": "🕐",
                "description": "Generating travel time areas",
                "color": "green",
            },
            ProcessingStage.CENSUS_INTEGRATION: {
                "emoji": "📊",
                "description": "Integrating census data",
                "color": "blue",
            },
            ProcessingStage.EXPORT_VISUALIZATION: {
                "emoji": "📈",
                "description": "Exporting results and visualizations",
                "color": "magenta",
            },
        }

        # Substage descriptions
        self.substage_configs = {
            "poi_query": {"emoji": "🔍", "description": "Querying OpenStreetMap"},
            "poi_validation": {"emoji": "✅", "description": "Validating POI data"},
            "clustering": {"emoji": "🔗", "description": "Optimizing POI clusters"},
            "network_download": {"emoji": "🌐", "description": "Downloading road networks"},
            "isochrone_calculation": {"emoji": "⏱️", "description": "Calculating travel areas"},
            "block_group_intersection": {"emoji": "🏘️", "description": "Finding census areas"},
            "distance_calculation": {"emoji": "📏", "description": "Calculating travel distances"},
            "census_data_fetch": {"emoji": "📋", "description": "Retrieving census statistics"},
            "data_export": {"emoji": "💾", "description": "Exporting data files"},
            "map_generation": {"emoji": "🗺️", "description": "Creating visualizations"},
        }

    def print_banner(self, title: str, subtitle: str | None = None):
        """Print a beautiful banner using Rich."""
        if subtitle:
            banner_text = f"[bold cyan]{title}[/bold cyan]\n[dim]{subtitle}[/dim]"
        else:
            banner_text = f"[bold cyan]{title}[/bold cyan]"

        panel = Panel(
            banner_text,
            title="🏘️ SocialMapper",
            subtitle=f"v{self._get_version()}",
            box=box.DOUBLE,
            padding=(1, 2),
        )
        self.console.print(panel)

    def _get_version(self) -> str:
        """Get SocialMapper version."""
        try:
            from .. import __version__

            return __version__
        except:
            return "dev"

    def start_stage(
        self, stage: ProcessingStage, total_items: int | None = None
    ) -> RichProgressMetrics:
        """Start tracking a new processing stage with Rich progress.

        Args:
            stage: The processing stage to start
            total_items: Optional total number of items to process

        Returns:
            RichProgressMetrics object for this stage
        """
        with self._lock:
            # Stop any existing progress
            if self.progress:
                self.progress.stop()
                self.progress = None

            self.current_stage = stage
            metrics = RichProgressMetrics(stage=stage, total_items=total_items)
            self.stage_metrics[stage] = metrics

            # Get stage configuration
            config = self.stage_configs.get(
                stage, {"emoji": "🔄", "description": str(stage), "color": "white"}
            )

            # Create Rich progress bar
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
                transient=False,
            )

            task_description = f"{config['emoji']} {config['description']}"
            self.current_task_id = self.progress.add_task(task_description, total=total_items)

            self.progress.start()

            # Print stage start message
            self.console.print(
                f"\n[{config['color']}]Starting: {config['description']}[/{config['color']}]"
            )

            return metrics

    def update_progress(
        self, advance: int = 1, substage: str | None = None, description: str | None = None
    ) -> None:
        """Update progress for the current stage.

        Args:
            advance: Number of items to advance
            substage: Optional substage identifier
            description: Optional custom description override
        """
        if not self.current_stage:
            return

        with self._lock:
            metrics = self.stage_metrics.get(self.current_stage)
            if not metrics:
                return

            # Update metrics
            metrics.items_processed += advance
            if self.enable_performance_metrics:
                metrics.memory_usage_mb = metrics.get_memory_usage()
                metrics.update_throughput()

            # Update progress display
            if self.progress and self.current_task_id is not None:
                # Build description with substage if provided
                task_description = description
                if not task_description and substage:
                    substage_config = self.substage_configs.get(
                        substage, {"emoji": "⚡", "description": substage}
                    )
                    task_description = (
                        f"{substage_config['emoji']} {substage_config['description']}"
                    )

                self.progress.update(
                    self.current_task_id, advance=advance, description=task_description
                )

    def complete_stage(self, stage: ProcessingStage) -> None:
        """Complete a processing stage and show summary."""
        if stage not in self.stage_metrics:
            return

        metrics = self.stage_metrics[stage]
        elapsed = metrics.get_elapsed_time()
        config = self.stage_configs.get(
            stage, {"emoji": "✅", "description": str(stage), "color": "green"}
        )

        # Stop progress
        if self.progress:
            self.progress.stop()
            self.progress = None

        # Show completion message
        if self.enable_performance_metrics and metrics.throughput_per_second > 0:
            self.console.print(
                f"[green]✅ Completed: {config['description']} "
                f"({elapsed:.1f}s, {metrics.throughput_per_second:.1f} items/s)[/green]"
            )
        else:
            self.console.print(
                f"[green]✅ Completed: {config['description']} ({elapsed:.1f}s)[/green]"
            )

    @contextmanager
    def status(self, message: str, spinner: str = "dots"):
        """Context manager for showing a status spinner."""
        with Status(message, spinner=spinner, console=self.console) as status:
            yield status

    def print_summary(self) -> None:
        """Print a beautiful summary table of all stages."""
        if not self.stage_metrics:
            return

        # Create summary table
        table = Table(title="🏘️ SocialMapper Pipeline Summary", box=box.ROUNDED)
        table.add_column("Stage", style="cyan", no_wrap=True)
        table.add_column("Items", justify="right", style="green")
        table.add_column("Duration", justify="right", style="blue")
        table.add_column("Throughput", justify="right", style="yellow")
        table.add_column("Memory", justify="right", style="magenta")

        total_time = 0
        total_items = 0

        for stage, metrics in self.stage_metrics.items():
            config = self.stage_configs.get(stage, {"emoji": "🔄", "description": str(stage)})
            elapsed = metrics.get_elapsed_time()
            total_time += elapsed
            total_items += metrics.items_processed

            table.add_row(
                f"{config['emoji']} {config['description']}",
                f"{metrics.items_processed:,}",
                f"{elapsed:.1f}s",
                (
                    f"{metrics.throughput_per_second:.1f}/s"
                    if metrics.throughput_per_second > 0
                    else "-"
                ),
                f"{metrics.memory_usage_mb:.1f}MB" if metrics.memory_usage_mb > 0 else "-",
            )

        # Add total row
        table.add_section()
        table.add_row(
            "[bold]Total Pipeline[/bold]",
            f"[bold]{total_items:,}[/bold]",
            f"[bold]{total_time:.1f}s[/bold]",
            (
                f"[bold]{total_items / total_time:.1f}/s[/bold]"
                if total_time > 0
                else "[bold]-[/bold]"
            ),
            "[bold]-[/bold]",
        )

        self.console.print(table)


# Global tracker instance
_global_tracker: RichProgressTracker | None = None


def get_rich_tracker(enable_performance_metrics: bool = True) -> RichProgressTracker:
    """Get the global Rich progress tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = RichProgressTracker(enable_performance_metrics=enable_performance_metrics)
    return _global_tracker


def reset_rich_tracker():
    """Reset the global Rich progress tracker."""
    global _global_tracker
    _global_tracker = None


# Convenience context managers
@contextmanager
def track_stage(stage: ProcessingStage, total_items: int | None = None):
    """Context manager for tracking a processing stage."""
    tracker = get_rich_tracker()
    tracker.start_stage(stage, total_items)
    try:
        yield tracker
    finally:
        tracker.complete_stage(stage)


def track_poi_processing(total_pois: int | None = None):
    """Context manager for POI processing stage."""
    return track_stage(ProcessingStage.POI_PROCESSING, total_pois)


def track_isochrone_generation(total_pois: int | None = None):
    """Context manager for isochrone generation stage."""
    return track_stage(ProcessingStage.ISOCHRONE_GENERATION, total_pois)


def track_census_integration(total_block_groups: int | None = None):
    """Context manager for census integration stage."""
    return track_stage(ProcessingStage.CENSUS_INTEGRATION, total_block_groups)


def track_export_visualization(total_outputs: int | None = None):
    """Context manager for export and visualization stage."""
    return track_stage(ProcessingStage.EXPORT_VISUALIZATION, total_outputs)
