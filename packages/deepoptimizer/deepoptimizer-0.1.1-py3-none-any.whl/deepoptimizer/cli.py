"""
Command-line interface for DeepOptimizer.
"""
import os
import sys
from pathlib import Path
from typing import Optional

import click

from .analyzer import DeepOptimizer
from .formatter import OutputFormatter
from .knowledge_base import KnowledgeBase
from .utils import safe_print


@click.group()
@click.version_option(version='0.1.1', prog_name='DeepOptimizer')
def cli():
    """
    DeepOptimizer - AI-powered ML code analysis and optimization suggestions.
    
    Analyzes your ML code for bugs, performance issues, and optimization
    opportunities using both rule-based detection and LLM-powered insights.
    """
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--no-llm', is_flag=True, help='Use only rule-based analysis (no LLM)')
@click.option('--output', '-o', type=click.Choice(['rich', 'simple', 'json', 'markdown']), 
              default='rich', help='Output format')
@click.option('--export', '-e', type=click.Path(), help='Export results to file')
@click.option('--no-code', is_flag=True, help='Hide code snippets in output')
@click.option('--severity', type=click.Choice(['all', 'error', 'warning', 'info']), 
              default='all', help='Filter by severity level')
def analyze(path: str, api_key: Optional[str], no_llm: bool, output: str, 
           export: Optional[str], no_code: bool, severity: str):
    """
    Analyze a Python file or project for ML-specific issues.
    
    Examples:
    
        # Analyze a single file
        deepoptimizer analyze model.py
        
        # Analyze entire project
        deepoptimizer analyze ./src
        
        # Export results as markdown
        deepoptimizer analyze model.py --output markdown --export report.md
        
        # Quick rule-based analysis only
        deepoptimizer analyze model.py --no-llm
    """
    path = Path(path)
    
    # Initialize analyzer
    try:
        analyzer = DeepOptimizer(api_key=api_key, use_llm=not no_llm)
    except ValueError as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        if not no_llm:
            click.echo("\nTip: Use --no-llm for rule-based analysis without API key", err=True)
        sys.exit(1)
    
    # Initialize formatter
    formatter = OutputFormatter(style=output, no_color=False)
    
    # Analyze based on path type
    with click.progressbar(length=100, label='Analyzing', show_eta=False) as bar:
        bar.update(10)
        
        if path.is_file():
            # Single file analysis
            results = analyzer.analyze_file(path, include_llm=not no_llm)
            bar.update(90)
        else:
            # Project analysis
            results = analyzer.analyze_project(path, include_llm=not no_llm)
            bar.update(90)
    
    # Filter by severity if requested
    if severity != 'all' and 'issues' in results:
        if path.is_file():
            results['issues'] = [
                i for i in results.get('issues', [])
                if i.get('severity') == severity
            ]
        else:
            # For project results, filter each file
            for file_path, file_results in results.get('issues_by_file', {}).items():
                if isinstance(file_results, dict) and 'issues' in file_results:
                    file_results['issues'] = [
                        i for i in file_results['issues']
                        if i.get('severity') == severity
                    ]
    
    # Format output
    if path.is_file():
        formatted = formatter.format_file_results(results, show_code=not no_code)
    else:
        formatted = formatter.format_project_results(results)
    
    # Display or export
    if export:
        export_path = Path(export)
        export_path.write_text(formatted)
        click.echo(f"\n[SUCCESS] Results exported to {export_path}")
    else:
        # Apply safe_print to handle Windows encoding
        click.echo(safe_print(formatted))
    
    # Exit with appropriate code
    if path.is_file():
        error_count = sum(1 for i in results.get('issues', []) if i.get('severity') == 'error')
    else:
        error_count = results.get('issues_by_severity', {}).get('error', 0)
    
    if error_count > 0:
        sys.exit(1)  # Non-zero exit for CI/CD integration


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key')
@click.option('--interactive', '-i', is_flag=True, help='Interactive fix mode')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without making changes')
def fix(path: str, api_key: Optional[str], interactive: bool, dry_run: bool):
    """
    Interactively fix issues in your code (experimental).
    
    This command analyzes your code and offers to apply fixes for detected issues.
    Always review changes before committing!
    """
    click.echo(click.style("[WARNING] Fix command is experimental. Always review changes!", fg='yellow'))
    click.echo("This feature is coming soon...")
    
    # TODO: Implement interactive fix mode
    # 1. Analyze file
    # 2. For each issue with a concrete fix:
    #    - Show the issue and proposed fix
    #    - Ask user to accept/reject
    #    - Apply fix if accepted
    # 3. Save backup of original file


@cli.command()
@click.option('--category', '-c', type=click.Choice(['all', 'optimization', 'training', 
              'architecture', 'attention', 'quantization', 'augmentation']), 
              default='all', help='Filter techniques by category')
@click.option('--search', '-s', help='Search techniques by name or description')
@click.option('--framework', '-f', type=click.Choice(['all', 'pytorch', 'tensorflow', 'jax']), 
              default='all', help='Filter by framework')
def techniques(category: str, search: Optional[str], framework: str):
    """
    Browse the knowledge base of ML optimization techniques.
    
    Examples:
    
        # List all techniques
        deepoptimizer techniques
        
        # Search for attention techniques
        deepoptimizer techniques --search attention
        
        # Show only PyTorch optimizations
        deepoptimizer techniques --framework pytorch
    """
    kb = KnowledgeBase()
    
    # Get techniques based on filters
    if search:
        techniques = kb.search_techniques(search)
        click.echo(f"\n[SEARCH] Results for '{search}':\n")
    elif category != 'all':
        techniques = kb.get_techniques_by_category(category)
        click.echo(f"\n[CATEGORY] {category.title()} Techniques:\n")
    else:
        techniques = kb.get_all_techniques()
        click.echo("\n[ALL TECHNIQUES] ML Optimization Techniques:\n")
    
    # Filter by framework
    if framework != 'all':
        techniques = [
            t for t in techniques 
            if t.get('framework', '').lower() in [framework, 'any']
        ]
    
    # Display techniques
    if not techniques:
        click.echo("No techniques found matching your criteria.")
        return
    
    for i, tech in enumerate(techniques, 1):
        # Title
        name = tech.get('name', 'Unknown')
        category = tech.get('category', 'general')
        framework = tech.get('framework', 'any')
        
        click.echo(click.style(f"{i}. {name}", fg='cyan', bold=True))
        click.echo(f"   Category: {category} | Framework: {framework}")
        
        # Description
        desc = tech.get('description', '')
        if desc:
            # Truncate long descriptions
            if len(desc) > 200:
                desc = desc[:197] + "..."
            click.echo(f"   {desc}")
        
        # Benefits
        benefits = tech.get('expected_benefits', '')
        if benefits:
            click.echo(click.style(f"   [BENEFITS] {benefits}", fg='green'))
        
        # Compatibility notes
        compat = tech.get('compatibility_notes', '')
        if compat:
            click.echo(click.style(f"   [NOTE] {compat}", fg='yellow'))
        
        click.echo()  # Empty line
    
    # Show total count
    click.echo(f"Total: {len(techniques)} techniques")


@cli.command()
@click.argument('technique_name')
def technique_info(technique_name: str):
    """
    Show detailed information about a specific technique.
    
    Example:
        deepoptimizer technique-info "Mixed Precision Training"
    """
    kb = KnowledgeBase()
    
    # Find technique
    technique = kb.get_technique_by_name(technique_name)
    
    if not technique:
        # Try searching
        results = kb.search_techniques(technique_name)
        if results:
            click.echo(f"Exact match not found. Did you mean one of these?")
            for t in results[:5]:
                click.echo(f"  - {t.get('name', 'Unknown')}")
        else:
            click.echo(f"Technique '{technique_name}' not found.")
        return
    
    # Display detailed info
    click.echo(click.style(f"\n{technique.get('name', 'Unknown')}", fg='cyan', bold=True))
    click.echo("=" * 50)
    
    # Basic info
    click.echo(f"\nCategory: {technique.get('category', 'general')}")
    click.echo(f"Framework: {technique.get('framework', 'any')}")
    
    # Description
    desc = technique.get('description', 'No description available.')
    click.echo(f"\n[DESCRIPTION]\n{desc}")
    
    # Benefits
    benefits = technique.get('expected_benefits', '')
    if benefits:
        click.echo(click.style(f"\n[EXPECTED BENEFITS]\n{benefits}", fg='green'))
    
    # Implementation
    impl = technique.get('implementation_code', '')
    if impl:
        click.echo(f"\n[IMPLEMENTATION EXAMPLE]")
        click.echo(click.style(impl, fg='blue'))
    
    # Compatibility
    compat = technique.get('compatibility_notes', '')
    if compat:
        click.echo(click.style(f"\n[COMPATIBILITY NOTES]\n{compat}", fg='yellow'))
    
    # Research papers
    papers = technique.get('paper_url', '')
    if papers:
        click.echo(f"\n📚 Research Papers:\n{papers}")
    
    # Show conflicts
    conflicts = kb.get_conflicts_for_technique(technique_name)
    if conflicts:
        click.echo(click.style("\n⚔️  Conflicts with:", fg='red'))
        for conflict in conflicts:
            # Get the other technique name
            tech_a_id = conflict.get('technique_a')
            tech_b_id = conflict.get('technique_b')
            tech_id = technique.get('id')
            
            other_id = tech_b_id if tech_a_id == tech_id else tech_a_id
            
            # Find the other technique name
            for t in kb.get_all_techniques():
                if t.get('id') == other_id:
                    click.echo(f"  - {t.get('name', 'Unknown')}: {conflict.get('evidence_description', '')}")
                    break


@cli.command()
def init():
    """
    Initialize DeepOptimizer configuration.
    
    Creates a .deepoptimizer config file in the current directory.
    """
    config_path = Path('.deepoptimizer')
    
    if config_path.exists():
        if not click.confirm("Configuration file already exists. Overwrite?"):
            return
    
    # Create config
    config_content = """# DeepOptimizer Configuration

# Gemini API Key (or set GEMINI_API_KEY environment variable)
# api_key = your-api-key-here

# Default analysis options
[analysis]
# Include LLM analysis by default
use_llm = true

# Output format (rich, simple, json, markdown)
output_format = rich

# File patterns to include
include_patterns = ["**/*.py"]

# File patterns to exclude
exclude_patterns = ["**/venv/**", "**/__pycache__/**", "**/test_*.py"]

# Severity filter (all, error, warning, info)
severity_filter = all

[performance]
# Maximum workers for parallel analysis
max_workers = 4

# Timeout for LLM requests (seconds)
llm_timeout = 30
"""
    
    config_path.write_text(config_content)
    click.echo(f"[SUCCESS] Created configuration file: {config_path}")
    click.echo("\nNext steps:")
    click.echo("1. Add your Gemini API key to .deepoptimizer or set GEMINI_API_KEY")
    click.echo("2. Run 'deepoptimizer analyze .' to analyze your project")


@cli.command()
def doctor():
    """
    Check DeepOptimizer setup and dependencies.
    
    Verifies that everything is configured correctly.
    """
    click.echo("DeepOptimizer Doctor\n" + "=" * 50)
    
    issues = []
    
    # Check Python version
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor >= 9:
        click.echo("[OK] Python version: " + click.style(f"{py_version.major}.{py_version.minor}", fg='green'))
    else:
        click.echo("[FAIL] Python version: " + click.style(f"{py_version.major}.{py_version.minor}", fg='red'))
        issues.append("Python 3.9+ is required")
    
    # Check Gemini API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        # Mask the key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        click.echo("[OK] Gemini API key: " + click.style(f"Found ({masked_key})", fg='green'))
    else:
        click.echo("[WARN] Gemini API key: " + click.style("Not found", fg='yellow'))
        click.echo("   Set GEMINI_API_KEY environment variable for LLM analysis")
    
    # Check imports
    try:
        import google.generativeai
        click.echo("[OK] Google GenAI: " + click.style("Installed", fg='green'))
    except ImportError:
        click.echo("[FAIL] Google GenAI: " + click.style("Not installed", fg='red'))
        issues.append("Run: pip install google-generativeai")
    
    # Check knowledge base
    kb = KnowledgeBase()
    technique_count = len(kb.get_all_techniques())
    if technique_count > 0:
        click.echo("[OK] Knowledge base: " + click.style(f"{technique_count} techniques loaded", fg='green'))
    else:
        click.echo("[WARN] Knowledge base: " + click.style("No techniques loaded", fg='yellow'))
        click.echo("   Knowledge base fixtures may be missing")
    
    # Summary
    click.echo("\n" + "-" * 50)
    if not issues:
        click.echo(click.style("\n[SUCCESS] All checks passed! DeepOptimizer is ready to use.", fg='green', bold=True))
    else:
        click.echo(click.style("\n[ERRORS] Issues found:", fg='red', bold=True))
        for issue in issues:
            click.echo(f"  - {issue}")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()