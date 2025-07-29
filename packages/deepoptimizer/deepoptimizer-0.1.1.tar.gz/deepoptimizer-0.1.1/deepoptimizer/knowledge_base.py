"""
Knowledge base for ML optimization techniques and their relationships.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class KnowledgeBase:
    """Manages ML optimization techniques and their relationships."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize knowledge base from JSON fixtures."""
        if data_dir is None:
            # Use local fixtures directory
            data_dir = Path(__file__).parent / 'fixtures'
        
        self.data_dir = Path(data_dir)
        self.techniques = []
        self.relationships = []
        self.techniques_by_category = {}
        self.techniques_by_name = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load techniques and relationships from JSON files."""
        # Load technique files
        technique_files = [
            'optimizer_techniques.json',
            'distributed_techniques.json',
            'quantization_techniques.json',
            'attention_techniques.json',
            'normalization_techniques.json',
            'data_techniques.json',
            'architecture_techniques.json',
            'additional_techniques.json'
        ]
        
        for filename in technique_files:
            file_path = self.data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Handle both direct list and Django fixture format
                    if isinstance(data, list) and data and 'model' in data[0]:
                        # Django fixture format
                        for item in data:
                            if item['model'] == 'knowledge_base.mltechnique':
                                technique = item['fields']
                                technique['id'] = item.get('pk', len(self.techniques))
                                self._add_technique(technique)
                    else:
                        # Direct list of techniques
                        for technique in data:
                            self._add_technique(technique)
                            
                except Exception as e:
                    # Could not load fixture file
                    pass
        
        # Load relationships
        relationships_file = self.data_dir / 'technique_relationships.json'
        if relationships_file.exists():
            try:
                with open(relationships_file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and data and 'model' in data[0]:
                    # Django fixture format
                    for item in data:
                        if item['model'] == 'knowledge_base.techniquerelationship':
                            self.relationships.append(item['fields'])
                else:
                    # Direct list
                    self.relationships = data
                    
            except Exception as e:
                # Could not load relationships
                pass
    
    def _add_technique(self, technique: Dict[str, Any]):
        """Add a technique to the knowledge base."""
        self.techniques.append(technique)
        
        # Index by category
        category = technique.get('category', 'general')
        if category not in self.techniques_by_category:
            self.techniques_by_category[category] = []
        self.techniques_by_category[category].append(technique)
        
        # Index by name
        name = technique.get('name', '')
        if name:
            self.techniques_by_name[name.lower()] = technique
    
    def get_all_techniques(self) -> List[Dict[str, Any]]:
        """Get all techniques."""
        return self.techniques
    
    def get_techniques_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get techniques by category."""
        return self.techniques_by_category.get(category, [])
    
    def get_technique_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific technique by name."""
        return self.techniques_by_name.get(name.lower())
    
    def get_all_conflicts(self) -> List[Dict[str, Any]]:
        """Get all technique conflicts."""
        return [r for r in self.relationships if r.get('relationship_type') == 'conflicts']
    
    def get_all_synergies(self) -> List[Dict[str, Any]]:
        """Get all technique synergies."""
        return [r for r in self.relationships if r.get('relationship_type') == 'synergizes']
    
    def get_conflicts_for_technique(self, technique_name: str) -> List[Dict[str, Any]]:
        """Get conflicts for a specific technique."""
        conflicts = []
        technique_id = None
        
        # Find technique ID
        for tech in self.techniques:
            if tech.get('name', '').lower() == technique_name.lower():
                technique_id = tech.get('id')
                break
        
        if technique_id:
            for rel in self.relationships:
                if rel.get('relationship_type') == 'conflicts':
                    if rel.get('technique_a') == technique_id or rel.get('technique_b') == technique_id:
                        conflicts.append(rel)
        
        return conflicts
    
    def get_relevant_techniques_for_code(self, code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get techniques relevant to the given code."""
        relevant = []
        code_lower = code.lower()
        
        # Score techniques based on relevance
        for technique in self.techniques:
            score = 0
            
            # Check if technique name or keywords appear in code
            name = technique.get('name', '').lower()
            if name and any(word in code_lower for word in name.split()):
                score += 3
            
            # Check description
            description = technique.get('description', '').lower()
            if description:
                keyword_matches = sum(1 for word in description.split() if len(word) > 4 and word in code_lower)
                score += min(keyword_matches * 0.5, 2)
            
            # Check implementation code similarity
            impl_code = technique.get('implementation_code', '').lower()
            if impl_code and any(line in code_lower for line in impl_code.split('\n') if len(line) > 10):
                score += 2
            
            # Framework match
            framework = technique.get('framework', '').lower()
            if framework and framework != 'any':
                if f'import {framework}' in code_lower or f'from {framework}' in code_lower:
                    score += 1
            
            if score > 0:
                relevant.append({**technique, '_relevance_score': score})
        
        # Sort by relevance and return top N
        relevant.sort(key=lambda x: x['_relevance_score'], reverse=True)
        return relevant[:limit]
    
    def format_technique_for_prompt(self, technique: Dict[str, Any]) -> str:
        """Format a technique for inclusion in a prompt."""
        parts = [f"**{technique.get('name', 'Unknown')}**"]
        
        if technique.get('description'):
            parts.append(f"Description: {technique['description']}")
        
        if technique.get('expected_benefits'):
            parts.append(f"Benefits: {technique['expected_benefits']}")
        
        if technique.get('compatibility_notes'):
            parts.append(f"[WARNING] Compatibility: {technique['compatibility_notes']}")
        
        if technique.get('implementation_code'):
            parts.append(f"```python\n{technique['implementation_code']}\n```")
        
        return '\n'.join(parts)
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self.techniques_by_category.keys())
    
    def search_techniques(self, query: str) -> List[Dict[str, Any]]:
        """Search techniques by name or description."""
        query_lower = query.lower()
        results = []
        
        for technique in self.techniques:
            name = technique.get('name', '').lower()
            description = technique.get('description', '').lower()
            
            if query_lower in name or query_lower in description:
                results.append(technique)
        
        return results