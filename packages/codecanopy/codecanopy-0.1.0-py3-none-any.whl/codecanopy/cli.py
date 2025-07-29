"""Main CLI interface for CodeCanopy."""

import click
import sys
from pathlib import Path

from .config import Config
from .tree import TreeGenerator
from .cat import CatGenerator


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """CodeCanopy - Give LLMs perfect context about your codebase."""
    if ctx.invoked_subcommand is None:
        click.echo("CodeCanopy - Give LLMs perfect context about your codebase")
        click.echo("\nCommands:")
        click.echo("  tree    Show directory structure")
        click.echo("  cat     Show file contents")
        click.echo("\nUse --help with any command for more information.")


@main.command()
@click.option(
    "--focus",
    multiple=True,
    help="Focus directories (full depth). Can be used multiple times.",
)
@click.option(
    "--ignore",
    multiple=True,
    help="Ignore directories/files. Can be used multiple times.",
)
@click.option("--depth", type=int, help="Global depth limit (default: 3)")
@click.option("--no-files", is_flag=True, help="Hide files, show only directories")
@click.option("--config", help="Config file path (default: .codecanopy.json)")
@click.argument("path", required=False, default=".")
def tree(focus, ignore, depth, no_files, config, path):
    """Show directory structure with selective depth control.

    PATH: Directory to analyze (default: current directory)

    Examples:
      codecanopy tree --focus src --ignore node_modules
      codecanopy tree --depth 2 --no-files
      codecanopy tree /path/to/project --focus src,lib
    """

    try:
        # Validate path
        root_path = Path(path).resolve()
        if not root_path.exists():
            click.echo(f"Error: Path '{path}' does not exist.", err=True)
            sys.exit(1)
        if not root_path.is_dir():
            click.echo(f"Error: Path '{path}' is not a directory.", err=True)
            sys.exit(1)

        # Load configuration
        cfg = Config(config)

        # Generate tree
        generator = TreeGenerator(cfg)

        ignore_patterns = list(ignore) if ignore else None
        focus_dirs = list(focus) if focus else None

        result = generator.generate(
            root_path=root_path,
            focus_dirs=focus_dirs,
            ignore_patterns=ignore_patterns,
            global_depth=depth,
            show_files=not no_files,
        )

        click.echo(result)

    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("patterns", nargs=-1, required=True)
@click.option(
    "--exclude",
    multiple=True,
    help="Exclude file patterns. Can be used multiple times.",
)
@click.option(
    "--header", help="Header format template. Available: {path}, {filename}, {dir}"
)
@click.option("--no-headers", is_flag=True, help="Skip file headers")
@click.option("--max-size", help="Skip files larger than size (e.g., 100KB, 1MB)")
@click.option("--config", help="Config file path (default: .codecanopy.json)")
@click.option(
    "--base-path", help="Base path for relative file paths (default: current directory)"
)
def cat(patterns, exclude, header, no_headers, max_size, config, base_path):
    """Show file contents with headers.

    PATTERNS: File patterns to include (supports glob patterns)

    Examples:
      codecanopy cat "src/**/*.py"
      codecanopy cat "*.js" "*.ts" --exclude "*test*"
      codecanopy cat file1.py file2.py --header "// {filename}"
      codecanopy cat "**/*.md" --max-size 50KB --no-headers
    """

    try:
        # Validate base path
        if base_path:
            base_path = Path(base_path).resolve()
            if not base_path.exists() or not base_path.is_dir():
                click.echo(
                    f"Error: Base path '{base_path}' does not exist or is not a directory.",
                    err=True,
                )
                sys.exit(1)
        else:
            base_path = Path.cwd()

        # Validate patterns
        if not patterns:
            click.echo("Error: No file patterns specified.", err=True)
            sys.exit(1)

        # Load configuration
        cfg = Config(config)

        # Generate output
        generator = CatGenerator(cfg)

        exclude_patterns = list(exclude) if exclude else None

        result = generator.generate(
            patterns=list(patterns),
            exclude_patterns=exclude_patterns,
            header_format=header,
            show_headers=not no_headers,
            max_file_size=max_size,
            base_path=base_path,
        )

        click.echo(result)

    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def version():
    """Show version information."""
    from . import __version__

    click.echo(f"CodeCanopy version {__version__}")


if __name__ == "__main__":
    main()
