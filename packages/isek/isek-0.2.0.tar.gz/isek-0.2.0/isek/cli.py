#!/usr/bin/env python
import click
import importlib.util
import subprocess
import sys
from pathlib import Path


def load_module(script_path: Path):
    """Dynamically load module"""
    try:
        module_name = script_path.stem
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        click.secho(f"Module load error: {e}", fg="red")
        sys.exit(1)


def get_available_examples(ctx, args, incomplete):
    """Get available example scripts"""
    examples_dir = Path(__file__).parent.parent / "examples"
    return [
        f.stem
        for f in examples_dir.glob("*.py")
        if f.name != "__init__.py"
        and not f.name.startswith("_")
        and f.stem.startswith(incomplete)
    ]


@click.group()
def cli():
    """ISEK Distributed Multi-Agent Framework CLI"""


@cli.command()
def clean():
    """Run system cleanup script"""
    script_path = Path(__file__).parent.parent / "scripts" / "clean.py"
    module = load_module(script_path)
    module.main()
    click.secho("✓ Cleanup completed", fg="green")


@cli.command()
def registry():
    """Start local development registry"""
    from isek.isek_center import main

    main()


@cli.command()
def setup():
    """Install ISEK Python and JavaScript dependencies"""
    project_root = Path(__file__).parent.parent
    p2p_dir = project_root / "isek" / "protocol" / "p2p"

    click.secho("🚀 Setting up ISEK dependencies...", fg="blue")

    # Step 1: Install Python dependencies
    click.secho("📦 Installing Python dependencies...", fg="yellow")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", str(project_root)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        click.secho("✓ Python dependencies installed", fg="green")
    except subprocess.CalledProcessError as e:
        click.secho(f"✗ Python dependency installation failed: {e}", fg="red")
        sys.exit(e.returncode)

    # Step 2: Check if Node.js is installed
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.secho(
            "⚠️  Node.js and npm are required for P2P functionality", fg="yellow"
        )
        click.secho("   Please install Node.js from https://nodejs.org/", fg="yellow")
        click.secho("   Then run 'isek setup' again", fg="yellow")
        return

    # Step 3: Install JavaScript dependencies
    if p2p_dir.exists() and (p2p_dir / "package.json").exists():
        click.secho("📦 Installing JavaScript dependencies for P2P...", fg="yellow")
        try:
            subprocess.check_call(
                ["npm", "install"],
                cwd=p2p_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            click.secho("✓ JavaScript dependencies installed", fg="green")
        except subprocess.CalledProcessError as e:
            click.secho(f"✗ JavaScript dependency installation failed: {e}", fg="red")
            click.secho("   P2P functionality may not work correctly", fg="yellow")

    click.secho("🎉 ISEK setup completed successfully!", fg="green")
    click.secho("   You can now run examples with 'isek example run <name>'", fg="blue")

@cli.group()
def example():
    """Example script management"""


@example.command()
def list():
    """List available example scripts"""
    examples_dir = Path(__file__).parent.parent / "examples"
    examples = [
        f.stem
        for f in examples_dir.glob("*.py")
        if f.name != "__init__.py" and not f.name.startswith("_")
    ]

    click.echo("Available examples:")
    for name in sorted(examples):
        click.echo(f"  • {name}")


@example.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.argument("name", type=click.STRING, shell_complete=get_available_examples)
@click.pass_context
def run(ctx, name: str):
    """Execute specific example script"""
    script_path = Path(__file__).parent.parent / "examples" / f"{name}.py"

    module = load_module(script_path)
    if hasattr(module, "main"):
        extra_args = ctx.args
        module.main(*extra_args) if extra_args else module.main()
        click.secho(f"✓ Example '{name}' completed", fg="green")
    else:
        click.secho(f"✗ Example '{name}' lacks main() function", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
