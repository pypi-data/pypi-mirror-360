"""
Main CLI entry point for AI Safety Guardrails.
"""

import asyncio
from pathlib import Path
from typing import List, Optional

import click

from ..core.detector_config import SafetyConfig
from ..core.safety_guard import SafetyGuard
from ..utils.logger import get_logger
from .config import config_command
from .create import create_command
from .models import models_command

logger = get_logger(__name__)


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.pass_context
def cli(ctx, verbose, config):
    """AI Safety Guardrails - Comprehensive AI safety for LLM applications."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    if verbose:
        import os

        os.environ["AI_SAFETY_LOG_LEVEL"] = "DEBUG"


@cli.command()
@click.option(
    "--detectors", "-d", multiple=True, help="Detectors to test (default: all)"
)
@click.option("--text", "-t", default="Hello world", help="Test text")
@click.pass_context
def test(ctx, detectors, text):
    """Test AI safety detectors."""

    async def _test():
        try:
            # Load configuration
            config_path = ctx.obj.get("config")
            config = (
                SafetyConfig.from_file(config_path) if config_path else SafetyConfig()
            )

            # Create SafetyGuard
            detector_list = list(detectors) if detectors else None
            guard = SafetyGuard(detectors=detector_list, config=config)

            click.echo(f"Testing detectors with text: '{text}'")
            click.echo()

            # Analyze text
            results = await guard.analyze_text(text)

            # Display results
            for name, result in results.items():
                status = "🚫 BLOCKED" if result.blocked else "✅ SAFE"
                confidence = f"{result.confidence:.2f}"

                click.echo(f"{status} {name}: confidence={confidence}")
                if result.reason:
                    click.echo(f"  Reason: {result.reason}")
                if result.processing_time:
                    click.echo(f"  Time: {result.processing_time:.3f}s")
                click.echo()

            # Overall result
            blocked_count = sum(1 for r in results.values() if r.blocked)
            if blocked_count > 0:
                click.echo(f"❌ Overall: BLOCKED by {blocked_count} detector(s)")
            else:
                click.echo("✅ Overall: SAFE")

            await guard.cleanup()

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return 1

    return asyncio.run(_test())


@cli.command()
@click.pass_context
def health(ctx):
    """Check system health."""

    async def _health():
        try:
            config_path = ctx.obj.get("config")
            config = (
                SafetyConfig.from_file(config_path) if config_path else SafetyConfig()
            )

            guard = SafetyGuard(config=config)
            health_info = await guard.health_check()

            # Display health status
            status = "✅ HEALTHY" if health_info["overall_healthy"] else "❌ UNHEALTHY"
            click.echo(f"System Status: {status}")
            click.echo()

            # Detector health
            click.echo("Detector Health:")
            for name, health in health_info["detectors"].items():
                detector_status = "✅" if health["healthy"] else "❌"
                click.echo(f"  {detector_status} {name}: {health['status']}")

            click.echo()

            # Metrics
            metrics = health_info["metrics"]
            click.echo("Metrics:")
            click.echo(f"  Total requests: {metrics['total_requests']}")
            click.echo(f"  Blocked requests: {metrics['blocked_requests']}")
            click.echo(f"  Success rate: {metrics['success_rate']:.2%}")
            click.echo(f"  Avg processing time: {metrics['avg_processing_time']:.3f}s")

            await guard.cleanup()

        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            return 1

    return asyncio.run(_health())


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def init_config(ctx, output):
    """Create a default configuration file."""
    try:
        config = SafetyConfig()

        if output:
            output_path = Path(output)
        else:
            output_path = Path.cwd() / "ai_safety_config.yml"

        config.save(output_path)
        click.echo(f"✅ Created configuration file: {output_path}")

        # Validate the config
        issues = config.validate()
        if issues:
            click.echo("⚠️  Configuration issues found:")
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("✅ Configuration is valid")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        return 1


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate_config(config_file):
    """Validate a configuration file."""
    try:
        config = SafetyConfig.from_file(config_file)
        issues = config.validate()

        if issues:
            click.echo(f"❌ Configuration file {config_file} has issues:")
            for issue in issues:
                click.echo(f"  - {issue}")
            return 1
        else:
            click.echo(f"✅ Configuration file {config_file} is valid")

    except Exception as e:
        click.echo(f"❌ Error validating {config_file}: {e}", err=True)
        return 1


# Add sub-commands
cli.add_command(create_command, name="create")
cli.add_command(models_command, name="models")
cli.add_command(config_command, name="config")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
