"""
Main analyzer that combines rule-based and LLM analysis.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .llm_analyzer import GeminiAnalyzer
from .rule_detector import RuleBasedDetector, AntiPatternDetector
from .knowledge_base import KnowledgeBase


class DeepOptimizer:
    """Main analyzer that orchestrates rule-based and LLM analysis."""
    
    def __init__(self, api_key: Optional[str] = None, use_llm: bool = True):
        """
        Initialize DeepOptimizer.
        
        Args:
            api_key: Gemini API key (uses GEMINI_API_KEY env var if not provided)
            use_llm: Whether to use LLM analysis in addition to rules
        """
        self.rule_detector = RuleBasedDetector()
        self.antipattern_detector = AntiPatternDetector()
        self.knowledge_base = KnowledgeBase()
        
        self.llm_analyzer = None
        if use_llm:
            try:
                self.llm_analyzer = GeminiAnalyzer(api_key)
            except ValueError:
                # LLM analysis disabled - continue with rule-based only
                pass
    
    def analyze_file(self, file_path: Union[str, Path], include_llm: bool = True) -> Dict[str, Any]:
        """
        Analyze a single Python file.
        
        Args:
            file_path: Path to the Python file
            include_llm: Whether to include LLM analysis
            
        Returns:
            Dictionary with analysis results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'file': str(file_path),
                'error': f'File not found: {file_path}',
                'issues': []
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {
                'file': str(file_path),
                'error': f'Error reading file: {e}',
                'issues': []
            }
        
        return self.analyze_code(code, str(file_path), include_llm=include_llm)
    
    def analyze_code(self, code: str, file_path: Optional[str] = None, 
                     include_llm: bool = True, project_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze Python code for ML-specific issues.
        
        Args:
            code: Python code to analyze
            file_path: Optional file path for context
            include_llm: Whether to include LLM analysis
            project_context: Additional context (framework, hardware, etc.)
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            'file': file_path or 'code_snippet',
            'issues': [],
            'summary': {},
            'analysis_methods': []
        }
        
        # Run rule-based detection (fast)
        try:
            rule_issues = self.rule_detector.detect_all(code, file_path)
            antipattern_issues = self.antipattern_detector.detect_architecture_issues(code)
            
            all_rule_issues = rule_issues + antipattern_issues
            result['issues'].extend(all_rule_issues)
            result['analysis_methods'].append('rule-based')
        except Exception as e:
            result['issues'].append({
                'severity': 'error',
                'category': 'analysis_error',
                'title': 'Rule-based analysis failed',
                'description': str(e)
            })
        
        # Run LLM analysis if enabled and available
        if include_llm and self.llm_analyzer:
            try:
                # Build context with detected issues for LLM
                enhanced_context = {
                    **(project_context or {}),
                    'rule_based_issues': all_rule_issues
                }
                
                llm_issues = self.llm_analyzer.analyze(code, file_path, enhanced_context)
                
                # Merge issues, avoiding duplicates
                merged_issues = self._merge_issues(result['issues'], llm_issues)
                result['issues'] = merged_issues
                result['analysis_methods'].append('llm-enhanced')
            except Exception as e:
                result['issues'].append({
                    'severity': 'warning',
                    'category': 'analysis_error',
                    'title': 'LLM analysis failed',
                    'description': str(e),
                    'suggestion': 'Results shown are from rule-based analysis only'
                })
        
        # Generate summary
        result['summary'] = self._generate_summary(result['issues'])
        
        return result
    
    def analyze_project(self, project_path: Union[str, Path], 
                       include_patterns: List[str] = None,
                       exclude_patterns: List[str] = None,
                       include_llm: bool = True,
                       max_workers: int = 4) -> Dict[str, Any]:
        """
        Analyze an entire project.
        
        Args:
            project_path: Root directory of the project
            include_patterns: Glob patterns for files to include (default: ['**/*.py'])
            exclude_patterns: Glob patterns for files to exclude
            include_llm: Whether to include LLM analysis
            max_workers: Maximum parallel workers for analysis
            
        Returns:
            Dictionary with project-wide analysis results
        """
        project_path = Path(project_path)
        
        if not project_path.exists():
            return {'error': f'Project path not found: {project_path}'}
        
        # Default patterns
        if include_patterns is None:
            include_patterns = ['**/*.py']
        
        if exclude_patterns is None:
            exclude_patterns = ['**/venv/**', '**/env/**', '**/__pycache__/**', 
                              '**/node_modules/**', '**/.git/**']
        
        # Find all files
        files_to_analyze = []
        for pattern in include_patterns:
            for file_path in project_path.glob(pattern):
                # Check exclusions
                if not any(file_path.match(excl) for excl in exclude_patterns):
                    files_to_analyze.append(file_path)
        
        # Analyze files in parallel
        results = {
            'project_path': str(project_path),
            'files_analyzed': 0,
            'total_issues': 0,
            'issues_by_severity': {'error': 0, 'warning': 0, 'info': 0},
            'issues_by_file': {},
            'top_issues': [],
            'analysis_methods': []
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.analyze_file, file_path, include_llm): file_path
                for file_path in files_to_analyze
            }
            
            # Process results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_result = future.result()
                    
                    if file_result.get('issues'):
                        results['files_analyzed'] += 1
                        results['issues_by_file'][str(file_path)] = file_result
                        results['total_issues'] += len(file_result['issues'])
                        
                        # Update severity counts
                        for issue in file_result['issues']:
                            severity = issue.get('severity', 'info')
                            results['issues_by_severity'][severity] += 1
                        
                        # Update analysis methods
                        for method in file_result.get('analysis_methods', []):
                            if method not in results['analysis_methods']:
                                results['analysis_methods'].append(method)
                                
                except Exception as e:
                    results['issues_by_file'][str(file_path)] = {
                        'error': f'Analysis failed: {e}',
                        'issues': []
                    }
        
        # Generate project-wide insights
        results['top_issues'] = self._get_top_issues(results['issues_by_file'])
        results['optimization_opportunities'] = self._identify_optimization_opportunities(results)
        
        return results
    
    def _merge_issues(self, rule_issues: List[Dict], llm_issues: List[Dict]) -> List[Dict]:
        """Merge rule-based and LLM issues, avoiding duplicates."""
        merged = list(rule_issues)
        
        for llm_issue in llm_issues:
            # Check if similar issue already exists
            is_duplicate = False
            for rule_issue in rule_issues:
                if self._issues_similar(rule_issue, llm_issue):
                    # Enhance rule issue with LLM insights if available
                    if llm_issue.get('references') and not rule_issue.get('references'):
                        rule_issue['references'] = llm_issue['references']
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                merged.append(llm_issue)
        
        # Sort by severity and confidence
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        merged.sort(key=lambda x: (
            severity_order.get(x.get('severity', 'info'), 3),
            -x.get('confidence', 0)
        ))
        
        return merged
    
    def _issues_similar(self, issue1: Dict, issue2: Dict) -> bool:
        """Check if two issues are similar enough to be considered duplicates."""
        # Same title is a strong indicator
        if issue1.get('title', '').lower() == issue2.get('title', '').lower():
            return True
        
        # Check for similar key terms
        title1 = issue1.get('title', '').lower()
        title2 = issue2.get('title', '').lower()
        desc1 = issue1.get('description', '').lower()
        desc2 = issue2.get('description', '').lower()
        
        # Common duplicate patterns
        duplicate_patterns = [
            ('model.eval()', 'eval()'),
            ('torch.no_grad()', 'no_grad'),
            ('batch_size', 'batch size'),
            ('memory leak', 'loss.item()'),
            ('mse', 'classification')
        ]
        
        for pattern1, pattern2 in duplicate_patterns:
            if (pattern1 in title1 or pattern1 in desc1) and (pattern2 in title2 or pattern2 in desc2):
                return True
            if (pattern2 in title1 or pattern2 in desc1) and (pattern1 in title2 or pattern1 in desc2):
                return True
        
        return False
    
    def _generate_summary(self, issues: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for issues."""
        summary = {
            'total': len(issues),
            'by_severity': {'error': 0, 'warning': 0, 'info': 0},
            'by_category': {},
            'estimated_impact': self._estimate_impact(issues)
        }
        
        for issue in issues:
            # Count by severity
            severity = issue.get('severity', 'info')
            summary['by_severity'][severity] += 1
            
            # Count by category
            category = issue.get('category', 'general')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
        
        return summary
    
    def _estimate_impact(self, issues: List[Dict]) -> Dict[str, str]:
        """Estimate potential performance impact of fixing issues."""
        impact = {
            'speed': 'minimal',
            'memory': 'minimal',
            'accuracy': 'minimal'
        }
        
        # Check for high-impact issues
        for issue in issues:
            title_lower = issue.get('title', '').lower()
            
            # Speed impact
            if any(term in title_lower for term in ['batch size', 'mixed precision', 'gpu', 'dataloader']):
                impact['speed'] = '2-4x potential improvement'
            
            # Memory impact
            if any(term in title_lower for term in ['memory leak', 'gradient checkpoint', 'mixed precision']):
                impact['memory'] = '30-50% potential reduction'
            
            # Accuracy impact
            if any(term in title_lower for term in ['loss function', 'eval()', 'data leak']):
                impact['accuracy'] = 'critical - may affect results'
        
        return impact
    
    def _get_top_issues(self, issues_by_file: Dict) -> List[Dict]:
        """Get the most common issues across all files."""
        issue_counts = {}
        
        for file_result in issues_by_file.values():
            if isinstance(file_result, dict) and 'issues' in file_result:
                for issue in file_result['issues']:
                    title = issue.get('title', '')
                    if title:
                        if title not in issue_counts:
                            issue_counts[title] = {
                                'count': 0,
                                'severity': issue.get('severity', 'info'),
                                'example': issue
                            }
                        issue_counts[title]['count'] += 1
        
        # Sort by count and severity
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        top_issues = sorted(
            issue_counts.values(),
            key=lambda x: (-x['count'], severity_order.get(x['severity'], 3))
        )
        
        return top_issues[:10]
    
    def _identify_optimization_opportunities(self, results: Dict) -> List[Dict]:
        """Identify project-wide optimization opportunities."""
        opportunities = []
        
        # Check for common patterns
        total_files = results['files_analyzed']
        issues_by_file = results['issues_by_file']
        
        # Missing mixed precision
        mixed_precision_count = sum(
            1 for file_result in issues_by_file.values()
            if any('mixed precision' in issue.get('title', '').lower() 
                  for issue in file_result.get('issues', []))
        )
        
        if mixed_precision_count > total_files * 0.3:
            opportunities.append({
                'title': 'Enable Mixed Precision Training',
                'impact': '2x speedup, 50% memory reduction',
                'effort': 'Low',
                'description': 'Many files could benefit from automatic mixed precision'
            })
        
        # Batch size issues
        batch_size_issues = sum(
            1 for file_result in issues_by_file.values()
            if any('batch size' in issue.get('title', '').lower() 
                  for issue in file_result.get('issues', []))
        )
        
        if batch_size_issues > 0:
            opportunities.append({
                'title': 'Optimize Batch Sizes',
                'impact': 'Up to 10x training speedup',
                'effort': 'Low',
                'description': 'Small batch sizes are limiting GPU utilization'
            })
        
        return opportunities