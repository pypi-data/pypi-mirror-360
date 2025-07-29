"""
Smart prompt building for ML code analysis.
"""
import re
from typing import Dict, Any, List


class PromptBuilder:
    """Builds context-aware prompts for LLM analysis."""
    
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
    
    def build_analysis_prompt(self, code: str, file_path: str = None, project_context: Dict[str, Any] = None) -> str:
        """Build a comprehensive analysis prompt with context."""
        # Detect code characteristics
        framework = self._detect_framework(code)
        task_type = self._infer_task_type(code)
        architecture = self._detect_architecture(code)
        has_training = self._has_training_code(code)
        has_validation = self._has_validation_code(code)
        
        # Get relevant techniques from knowledge base
        relevant_techniques = self._get_relevant_techniques(code, framework)
        technique_conflicts = self._get_technique_conflicts()
        
        # Build the prompt
        prompt_parts = [
            self._system_prompt(),
            self._context_section(file_path, framework, task_type, architecture),
            self._code_section(code),
            self._knowledge_base_section(relevant_techniques, technique_conflicts),
            self._analysis_instructions(has_training, has_validation),
            self._few_shot_examples(),
            self._output_format_instructions()
        ]
        
        return "\n\n".join(prompt_parts)
    
    def _system_prompt(self) -> str:
        """System prompt establishing the AI's role."""
        return """You are an expert ML engineer reviewing code for bugs, performance issues, and optimization opportunities. You have deep knowledge of PyTorch, TensorFlow, JAX, and modern ML best practices.

Your analysis should be:
- Specific and actionable (not generic advice)
- Severity-appropriate (don't flag everything as critical)
- Context-aware (understand framework-specific patterns)
- Research-backed (cite papers when relevant)"""
    
    def _context_section(self, file_path: str, framework: str, task_type: str, architecture: str) -> str:
        """Build context section of the prompt."""
        context = "## Project Context\n"
        
        if file_path:
            context += f"- File: {file_path}\n"
        
        context += f"""- Framework: {framework}
- Task Type: {task_type}
- Architecture: {architecture}"""
        
        return context
    
    def _code_section(self, code: str) -> str:
        """Format the code section."""
        return f"""## Code to Analyze
```python
{code}
```"""
    
    def _knowledge_base_section(self, techniques: List[Dict], conflicts: List[Dict]) -> str:
        """Include relevant knowledge from the knowledge base."""
        section = "## Relevant ML Knowledge\n\n"
        
        if techniques:
            section += "### Applicable Optimization Techniques:\n"
            for tech in techniques[:5]:  # Limit to top 5 relevant techniques
                section += f"- **{tech['name']}**: {tech['benefit']}\n"
                if tech.get('warning'):
                    section += f"  [WARNING] {tech['warning']}\n"
        
        if conflicts:
            section += "\n### Technique Compatibility Rules:\n"
            for conflict in conflicts[:5]:
                section += f"- {conflict['rule']}\n"
        
        return section
    
    def _analysis_instructions(self, has_training: bool, has_validation: bool) -> str:
        """Specific instructions based on code type."""
        instructions = "## Analysis Focus\n\nAnalyze this code for:\n\n"
        
        # Always check for these
        instructions += """### 1. Critical Bugs (severity: error)
- Missing model.eval() in validation/inference
- Memory leaks (not using .item() on accumulated losses)
- Wrong loss functions for the task type
- Data leakage between train/test sets
- Gradient accumulation without loss scaling
"""
        
        if has_training:
            instructions += """- Training-specific: learning rate issues, optimizer bugs
- Missing gradient clipping for RNNs/Transformers
"""
        
        if has_validation:
            instructions += """- Validation-specific: missing torch.no_grad()
- Incorrect metric calculations
"""
        
        instructions += """
### 2. Performance Issues (severity: warning)
- Batch size = 1 or very small batch sizes
- Missing GPU optimizations (pin_memory, non_blocking)
- Inefficient tensor operations in loops
- Not using mixed precision when available
- Creating tensors on CPU then moving to GPU

### 3. Best Practices (severity: info)
- No explicit weight initialization
- Could benefit from modern optimizers
- Missing data augmentation for vision tasks
- Suboptimal hyperparameters for the architecture
- Could use advanced techniques from knowledge base"""
        
        return instructions
    
    def _few_shot_examples(self) -> str:
        """Provide examples of good analysis."""
        return '''## Example Analysis

For code like this:
```python
def validate(model, val_loader):
    total_loss = 0
    for data, target in val_loader:
        output = model(data)
        loss = F.cross_entropy(output, target)
        total_loss += loss
```

You should identify:
1. ERROR: Missing model.eval() - validation runs in training mode
2. ERROR: Memory leak - accumulating loss tensor instead of scalar
3. WARNING: Missing torch.no_grad() - computing unnecessary gradients

With specific fixes for each issue.'''
    
    def _output_format_instructions(self) -> str:
        """Instructions for output format."""
        return """## Output Format

Return ONLY a valid JSON array of issues. Each issue must have:
```json
[
  {
    "severity": "error|warning|info",
    "category": "bug|performance|best_practice|compatibility",
    "title": "Brief descriptive title (max 100 chars)",
    "description": "Clear explanation of why this is an issue",
    "line_numbers": [45, 67],  // Optional, if you can identify specific lines
    "suggestion": "Specific fix with code example",
    "confidence": 0.95,  // 0-1 score of how confident you are
    "references": ["https://arxiv.org/abs/..."]  // Optional research papers
  }
]
```

Focus on actionable, specific issues. Don't include generic advice like "consider using a different optimizer" without strong justification."""
    
    def _detect_framework(self, code: str) -> str:
        """Detect which ML framework is being used."""
        if 'import torch' in code or 'from torch' in code:
            return 'PyTorch'
        elif 'import tensorflow' in code or 'from tensorflow' in code:
            return 'TensorFlow'
        elif 'import jax' in code or 'from jax' in code:
            return 'JAX'
        elif 'import sklearn' in code or 'from sklearn' in code:
            return 'scikit-learn'
        else:
            return 'Unknown'
    
    def _infer_task_type(self, code: str) -> str:
        """Infer the ML task type from code."""
        code_lower = code.lower()
        
        # Classification indicators
        if any(term in code_lower for term in ['crossentropy', 'classification', 'logits', 'num_classes']):
            if 'binary' in code_lower or 'sigmoid' in code_lower or 'bce' in code_lower:
                return 'Binary Classification'
            return 'Multi-class Classification'
        
        # Regression indicators
        if any(term in code_lower for term in ['mse', 'mae', 'regression', 'mean_squared']):
            return 'Regression'
        
        # NLP indicators
        if any(term in code_lower for term in ['embedding', 'tokenizer', 'vocab', 'transformer', 'bert', 'gpt']):
            return 'NLP/Text'
        
        # Vision indicators
        if any(term in code_lower for term in ['conv2d', 'maxpool2d', 'image', 'resnet', 'vgg']):
            return 'Computer Vision'
        
        # RL indicators
        if any(term in code_lower for term in ['reward', 'episode', 'gym', 'policy', 'q_value']):
            return 'Reinforcement Learning'
        
        return 'General ML'
    
    def _detect_architecture(self, code: str) -> str:
        """Detect the model architecture type."""
        architectures = []
        
        # Check for specific architectures
        if re.search(r'class.*transformer|transformer', code, re.I):
            architectures.append('Transformer')
        if 'Conv2d' in code or 'conv2d' in code:
            architectures.append('CNN')
        if 'LSTM' in code or 'GRU' in code or 'RNN' in code:
            architectures.append('RNN')
        if re.search(r'ResNet|resnet|Residual|residual', code):
            architectures.append('ResNet')
        if 'Linear' in code and 'Conv' not in code and 'LSTM' not in code:
            architectures.append('MLP')
        
        if architectures:
            return ', '.join(architectures)
        return 'Custom Architecture'
    
    def _has_training_code(self, code: str) -> bool:
        """Check if code contains training logic."""
        training_indicators = [
            'optimizer', '.backward()', 'train_loader', 'training_step',
            'epochs', '.train()', 'zero_grad()'
        ]
        return any(indicator in code for indicator in training_indicators)
    
    def _has_validation_code(self, code: str) -> bool:
        """Check if code contains validation logic."""
        validation_indicators = [
            'val_loader', 'validation', 'evaluate', 'test_loader',
            'valid_', 'val_', '.eval()'
        ]
        return any(indicator in code for indicator in validation_indicators)
    
    def _get_relevant_techniques(self, code: str, framework: str) -> List[Dict]:
        """Get relevant optimization techniques from knowledge base."""
        techniques = []
        
        # Get techniques based on detected patterns
        if 'attention' in code.lower():
            techniques.extend(self.knowledge_base.get_techniques_by_category('attention'))
        
        if 'Conv2d' in code:
            techniques.extend(self.knowledge_base.get_techniques_by_category('convolution'))
        
        if 'optimizer' in code.lower():
            techniques.extend(self.knowledge_base.get_techniques_by_category('optimization'))
        
        # Filter by framework
        techniques = [t for t in techniques if t.get('framework') in [framework, 'any']]
        
        # Format for prompt
        formatted = []
        for tech in techniques[:5]:  # Limit to top 5
            formatted.append({
                'name': tech.get('name', ''),
                'benefit': tech.get('expected_benefits', ''),
                'warning': tech.get('compatibility_notes', '')
            })
        
        return formatted
    
    def _get_technique_conflicts(self) -> List[Dict]:
        """Get technique conflict rules from knowledge base."""
        conflicts = self.knowledge_base.get_all_conflicts()
        
        # Format for prompt
        formatted = []
        for conflict in conflicts[:5]:  # Limit to top 5
            rule = f"{conflict['technique_a']} + {conflict['technique_b']} = {conflict['evidence_description']}"
            formatted.append({'rule': rule})
        
        return formatted