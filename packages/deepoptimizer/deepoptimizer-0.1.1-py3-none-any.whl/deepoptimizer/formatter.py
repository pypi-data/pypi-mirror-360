"""
Beautiful output formatting for CLI.
"""
import json
import sys
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from .utils import safe_print

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False


class OutputFormatter:
    """Format analysis results for different output types."""
    
    # Use ASCII alternatives on Windows
    SEVERITY_ICONS = {
        'error': '[ERROR]',
        'warning': '[WARN]',
        'info': '[INFO]'
    } if sys.platform == 'win32' else {
        'error': '🚨',
        'warning': '⚠️ ',
        'info': 'ℹ️ '
    }
    
    SEVERITY_COLORS = {
        'error': 'red',
        'warning': 'yellow',
        'info': 'blue'
    }
    
    # Category icons with ASCII fallbacks for Windows
    CATEGORY_ICONS = {
        'bug': '[BUG]',
        'performance': '[PERF]',
        'best_practice': '[TIP]',
        'anti-pattern': '[ANTI]',
        'optimization': '[OPT]',
        'compatibility': '[COMPAT]',
        'analysis_error': '[ERR]'
    } if sys.platform == 'win32' else {
        'bug': '🐛',
        'performance': '⚡',
        'best_practice': '💡',
        'anti-pattern': '🚫',
        'optimization': '🚀',
        'compatibility': '🔗',
        'analysis_error': '❌'
    }
    
    def __init__(self, style: str = 'rich', no_color: bool = False):
        """
        Initialize formatter.
        
        Args:
            style: Output style ('rich', 'simple', 'json', 'markdown')
            no_color: Disable colored output
        """
        self.style = style
        self.no_color = no_color or not HAS_CLICK
    
    def format_file_results(self, results: Dict[str, Any], show_code: bool = True) -> str:
        """Format results for a single file."""
        if self.style == 'json':
            return json.dumps(results, indent=2)
        elif self.style == 'markdown':
            return self._format_markdown(results)
        elif self.style == 'simple':
            return self._format_simple(results)
        else:
            return self._format_rich(results, show_code)
    
    def format_project_results(self, results: Dict[str, Any]) -> str:
        """Format results for an entire project."""
        if self.style == 'json':
            return json.dumps(results, indent=2)
        elif self.style == 'markdown':
            return self._format_project_markdown(results)
        else:
            return self._format_project_rich(results)
    
    def _format_rich(self, results: Dict[str, Any], show_code: bool) -> str:
        """Rich formatting with colors and icons."""
        output = []
        
        # Header
        file_path = results.get('file', 'code')
        issues = results.get('issues', [])
        summary = results.get('summary', {})
        
        output.append(self._echo("\n🔍 DeepOptimizer Analysis Results", bold=True))
        output.append("=" * 80)
        
        # File info
        output.append(safe_print(f"\n📄 File: {file_path}"))
        
        # Summary
        if summary:
            output.append(self._format_summary(summary))
        
        # Issues by severity
        if issues:
            errors = [i for i in issues if i.get('severity') == 'error']
            warnings = [i for i in issues if i.get('severity') == 'warning']
            info = [i for i in issues if i.get('severity') == 'info']
            
            # Critical issues
            if errors:
                output.append(self._echo(f"\n{self.SEVERITY_ICONS['error']} CRITICAL ISSUES (Must Fix)", 
                                       fg='red', bold=True))
                output.append("-" * 80)
                for i, issue in enumerate(errors, 1):
                    output.append(self._format_issue(issue, i, show_code))
            
            # Warnings
            if warnings:
                output.append(self._echo(f"\n{self.SEVERITY_ICONS['warning']} PERFORMANCE WARNINGS", 
                                       fg='yellow', bold=True))
                output.append("-" * 80)
                for i, issue in enumerate(warnings, 1):
                    output.append(self._format_issue(issue, i, show_code))
            
            # Info
            if info:
                output.append(self._echo(f"\n{self.SEVERITY_ICONS['info']} SUGGESTIONS", 
                                       fg='blue', bold=True))
                output.append("-" * 80)
                for i, issue in enumerate(info, 1):
                    output.append(self._format_issue(issue, i, show_code))
        else:
            output.append(self._echo("\n✅ No issues found! Your code looks great!", fg='green'))
        
        # Analysis methods used
        methods = results.get('analysis_methods', [])
        if methods:
            output.append(safe_print(f"\n📊 Analysis methods: {', '.join(methods)}"))
        
        return '\n'.join(output)
    
    def _format_issue(self, issue: Dict[str, Any], index: int, show_code: bool) -> str:
        """Format a single issue."""
        output = []
        
        severity = issue.get('severity', 'info')
        color = self.SEVERITY_COLORS.get(severity, 'white')
        category_icon = self.CATEGORY_ICONS.get(issue.get('category', ''), '•')
        
        # Title with line numbers
        title = f"{index}. {category_icon} {issue.get('title', 'Unknown issue')}"
        if issue.get('line_numbers'):
            lines = issue['line_numbers']
            if len(lines) == 1:
                title += f" (Line {lines[0]})"
            else:
                title += f" (Lines {lines[0]}-{lines[-1]})"
        
        output.append(self._echo(title, fg=color, bold=True))
        
        # Description
        if issue.get('description'):
            wrapped = self._wrap_text(issue['description'], indent=3)
            output.append(wrapped)
        
        # Suggestion with code
        if issue.get('suggestion'):
            output.append(self._echo("   📝 Fix:", fg='green'))
            
            # Check if suggestion contains code
            if '```' in issue['suggestion'] or '\n' in issue['suggestion']:
                output.append(self._format_code_block(issue['suggestion'], indent=3))
            else:
                wrapped = self._wrap_text(issue['suggestion'], indent=6)
                output.append(wrapped)
        
        # Confidence score
        if 'confidence' in issue and issue['confidence'] < 0.8:
            confidence_pct = int(issue['confidence'] * 100)
            output.append(safe_print(f"   🎯 Confidence: {confidence_pct}%"))
        
        # References
        if issue.get('references'):
            output.append(safe_print("   📚 References:"))
            for ref in issue['references']:
                output.append(f"      • {ref}")
        
        output.append("")  # Empty line between issues
        
        return '\n'.join(output)
    
    def _format_summary(self, summary: Dict[str, Any]) -> str:
        """Format the summary section."""
        output = []
        
        output.append(safe_print(f"\n📊 Summary: {summary.get('total', 0)} issues found"))
        
        # By severity
        by_severity = summary.get('by_severity', {})
        if by_severity:
            parts = []
            for sev in ['error', 'warning', 'info']:
                count = by_severity.get(sev, 0)
                if count > 0:
                    icon = self.SEVERITY_ICONS[sev]
                    parts.append(f"{icon} {count} {sev}{'s' if count != 1 else ''}")
            
            if parts:
                output.append(f"   {' '.join(parts)}")
        
        # Estimated impact
        impact = summary.get('estimated_impact', {})
        if any(v != 'minimal' for v in impact.values()):
            output.append(safe_print("\n⚡ Potential Performance Gains:"))
            if impact.get('speed') != 'minimal':
                output.append(f"   🏃 Speed: {impact['speed']}")
            if impact.get('memory') != 'minimal':
                output.append(f"   💾 Memory: {impact['memory']}")
            if impact.get('accuracy') != 'minimal':
                output.append(safe_print(f"   🎯 Accuracy: {impact['accuracy']}"))
        
        return '\n'.join(output)
    
    def _format_project_rich(self, results: Dict[str, Any]) -> str:
        """Format project-wide results."""
        output = []
        
        output.append(self._echo("\n🔍 DeepOptimizer Project Analysis", bold=True))
        output.append("=" * 80)
        
        # Project info
        output.append(safe_print(f"\n📁 Project: {results.get('project_path', 'Unknown')}"))
        output.append(safe_print(f"📄 Files analyzed: {results.get('files_analyzed', 0)}"))
        output.append(safe_print(f"📊 Total issues: {results.get('total_issues', 0)}"))
        
        # Issues by severity
        by_severity = results.get('issues_by_severity', {})
        if by_severity:
            output.append("\n📈 Issues by Severity:")
            for sev in ['error', 'warning', 'info']:
                count = by_severity.get(sev, 0)
                if count > 0:
                    icon = self.SEVERITY_ICONS[sev]
                    color = self.SEVERITY_COLORS[sev]
                    bar = self._create_bar(count, results.get('total_issues', 1))
                    output.append(self._echo(f"   {icon} {sev:8}: {bar} {count}", fg=color))
        
        # Top issues
        top_issues = results.get('top_issues', [])
        if top_issues:
            output.append(self._echo(f"\n🔝 Most Common Issues:", bold=True))
            for i, issue_info in enumerate(top_issues[:5], 1):
                count = issue_info.get('count', 0)
                example = issue_info.get('example', {})
                severity = example.get('severity', 'info')
                color = self.SEVERITY_COLORS[severity]
                title = example.get('title', 'Unknown')
                
                output.append(self._echo(f"   {i}. {title} ({count} occurrences)", fg=color))
        
        # Optimization opportunities
        opportunities = results.get('optimization_opportunities', [])
        if opportunities:
            output.append(self._echo(f"\n💡 Quick Wins:", bold=True))
            for opp in opportunities[:3]:
                output.append(f"   • {opp.get('title', '')} - {opp.get('impact', '')}")
        
        # Files with most issues
        if results.get('issues_by_file'):
            files_with_issues = [
                (path, len(data.get('issues', []))) 
                for path, data in results['issues_by_file'].items()
                if isinstance(data, dict) and data.get('issues')
            ]
            files_with_issues.sort(key=lambda x: x[1], reverse=True)
            
            if files_with_issues:
                output.append(self._echo(f"\n📁 Files with Most Issues:", bold=True))
                for path, count in files_with_issues[:5]:
                    rel_path = Path(path).name
                    output.append(f"   • {rel_path}: {count} issues")
        
        return '\n'.join(output)
    
    def _format_markdown(self, results: Dict[str, Any]) -> str:
        """Format results as Markdown."""
        output = []
        
        output.append("# DeepOptimizer Analysis Report")
        output.append(f"\n**File:** {results.get('file', 'Unknown')}")
        output.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        issues = results.get('issues', [])
        if issues:
            # Group by severity
            for severity in ['error', 'warning', 'info']:
                severity_issues = [i for i in issues if i.get('severity') == severity]
                if severity_issues:
                    icon = self.SEVERITY_ICONS[severity]
                    output.append(f"\n## {icon} {severity.title()}s\n")
                    
                    for issue in severity_issues:
                        output.append(f"### {issue.get('title', 'Unknown')}")
                        
                        if issue.get('line_numbers'):
                            output.append(f"**Location:** Lines {', '.join(map(str, issue['line_numbers']))}")
                        
                        if issue.get('description'):
                            output.append(f"\n{issue['description']}")
                        
                        if issue.get('suggestion'):
                            output.append(f"\n**Fix:**")
                            if '```' in issue['suggestion']:
                                output.append(issue['suggestion'])
                            else:
                                output.append(f"```python\n{issue['suggestion']}\n```")
                        
                        output.append("")
        else:
            output.append(safe_print("\n✅ **No issues found!**"))
        
        return '\n'.join(output)
    
    def _format_simple(self, results: Dict[str, Any]) -> str:
        """Simple text format without colors."""
        output = []
        
        for issue in results.get('issues', []):
            severity = issue.get('severity', 'info').upper()
            title = issue.get('title', 'Unknown')
            line_info = ""
            
            if issue.get('line_numbers'):
                line_info = f" (Line {issue['line_numbers'][0]})"
            
            output.append(f"{severity}: {title}{line_info}")
            
            if issue.get('suggestion'):
                output.append(f"  Fix: {issue['suggestion']}")
            
            output.append("")
        
        return '\n'.join(output)
    
    def _echo(self, text: str, fg: str = None, bold: bool = False) -> str:
        """Echo with optional color."""
        # Apply safe_print to handle Windows encoding issues
        text = safe_print(text)
        
        if self.no_color or not HAS_CLICK:
            return text
        
        return click.style(text, fg=fg, bold=bold)
    
    def _wrap_text(self, text: str, width: int = 80, indent: int = 0) -> str:
        """Wrap text to specified width with indentation."""
        import textwrap
        
        wrapper = textwrap.TextWrapper(
            width=width,
            initial_indent=' ' * indent,
            subsequent_indent=' ' * indent,
            break_long_words=False,
            break_on_hyphens=False
        )
        
        return wrapper.fill(text)
    
    def _format_code_block(self, code: str, indent: int = 0) -> str:
        """Format a code block with proper indentation."""
        lines = []
        indent_str = ' ' * indent
        
        # Check if code already has markdown code blocks
        if '```' in code:
            for line in code.split('\n'):
                lines.append(indent_str + line)
        else:
            lines.append(indent_str + '```python')
            for line in code.split('\n'):
                lines.append(indent_str + line)
            lines.append(indent_str + '```')
        
        return '\n'.join(lines)
    
    def _create_bar(self, value: int, total: int, width: int = 20) -> str:
        """Create a simple text progress bar."""
        if total == 0:
            return '-' * width
        
        filled = int(width * value / total)
        return '#' * filled + '-' * (width - filled)
    
    def _format_project_markdown(self, results: Dict[str, Any]) -> str:
        """Format project results as Markdown."""
        output = []
        
        output.append("# DeepOptimizer Project Analysis Report")
        output.append(f"\n**Project:** {results.get('project_path', 'Unknown')}")
        output.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Files Analyzed:** {results.get('files_analyzed', 0)}")
        output.append(f"**Total Issues:** {results.get('total_issues', 0)}")
        
        # Summary statistics
        by_severity = results.get('issues_by_severity', {})
        if by_severity:
            output.append("\n## Summary by Severity\n")
            output.append("| Severity | Count |")
            output.append("|----------|-------|")
            for sev in ['error', 'warning', 'info']:
                count = by_severity.get(sev, 0)
                output.append(f"| {sev.title()} | {count} |")
        
        # Top issues
        top_issues = results.get('top_issues', [])
        if top_issues:
            output.append("\n## Most Common Issues\n")
            for i, issue_info in enumerate(top_issues[:10], 1):
                example = issue_info.get('example', {})
                count = issue_info.get('count', 0)
                output.append(f"{i}. **{example.get('title', 'Unknown')}** ({count} occurrences)")
        
        # Optimization opportunities
        opportunities = results.get('optimization_opportunities', [])
        if opportunities:
            output.append("\n## Optimization Opportunities\n")
            for opp in opportunities:
                output.append(f"### {opp.get('title', '')}")
                output.append(f"- **Impact:** {opp.get('impact', '')}")
                output.append(f"- **Effort:** {opp.get('effort', '')}")
                output.append(f"- **Description:** {opp.get('description', '')}")
                output.append("")
        
        return '\n'.join(output)