"""
Rule-based ML bug detection for common patterns and anti-patterns.
"""
import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DetectedIssue:
    """Represents a detected issue in the code."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'bug', 'anti-pattern', 'optimization', 'best_practice'
    title: str
    description: str
    line_numbers: Optional[List[int]] = None
    file_path: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = 0.9
    references: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}


class RuleBasedDetector:
    """Fast rule-based detection of common ML bugs and anti-patterns."""
    
    def __init__(self):
        self.issues = []
        self.file_path = None
    
    def detect_all(self, code: str, file_path: str = None) -> List[Dict[str, Any]]:
        """Run all detectors on the code."""
        self.issues = []
        self.file_path = file_path
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        
        # Run all detectors
        self._detect_train_eval_mode_issues(code, tree)
        self._detect_missing_no_grad(code, tree)
        self._detect_data_leakage(code, tree)
        self._detect_gradient_accumulation_bugs(code, tree)
        self._detect_loss_function_issues(code, tree)
        self._detect_memory_leaks(code, tree)
        self._detect_batch_norm_issues(code, tree)
        self._detect_optimizer_issues(code, tree)
        self._detect_tensor_operation_issues(code, tree)
        self._detect_batch_size_issues(code, tree)
        self._detect_dataloader_optimization(code, tree)
        self._detect_initialization_issues(code, tree)
        
        # Convert to dict format
        return [issue.to_dict() for issue in self.issues]
    
    def _detect_train_eval_mode_issues(self, code: str, tree: ast.AST):
        """Detect missing model.eval() or model.train() calls."""
        validation_patterns = r'(val|valid|test|eval|inference)'
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if re.search(validation_patterns, node.name, re.I):
                    # Check if model.eval() is called
                    has_eval = any(
                        isinstance(n, ast.Call) and 
                        isinstance(n.func, ast.Attribute) and 
                        n.func.attr == 'eval'
                        for n in ast.walk(node)
                    )
                    
                    if not has_eval:
                        self.issues.append(DetectedIssue(
                            severity='error',
                            category='bug',
                            title='Missing model.eval() in validation/test function',
                            description=f'Function "{node.name}" appears to be for validation/testing but doesn\'t call model.eval()',
                            line_numbers=[node.lineno],
                            file_path=self.file_path,
                            suggestion='Add "model.eval()" at the beginning of the function and use "with torch.no_grad():" for inference'
                        ))
    
    def _detect_missing_no_grad(self, code: str, tree: ast.AST):
        """Detect validation/inference without torch.no_grad()."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name.lower()
                # Check if it's likely a validation/inference function
                if any(pattern in func_name for pattern in ['val', 'test', 'eval', 'infer', 'predict']):
                    # Check if it has backward pass (if so, it's training)
                    has_backward = any(
                        isinstance(n, ast.Attribute) and n.attr == 'backward'
                        for n in ast.walk(node)
                    )
                    
                    if not has_backward:
                        # Check for no_grad usage
                        has_no_grad = any(
                            isinstance(n, ast.With) and 
                            any(isinstance(item.context_expr, ast.Call) and 
                                'no_grad' in ast.unparse(item.context_expr)
                                for item in n.items)
                            for n in ast.walk(node)
                        )
                        
                        # Also check for decorator
                        has_no_grad_decorator = any(
                            isinstance(dec, ast.Name) and 'no_grad' in dec.id or
                            isinstance(dec, ast.Attribute) and dec.attr == 'no_grad'
                            for dec in node.decorator_list
                        )
                        
                        if not has_no_grad and not has_no_grad_decorator:
                            self.issues.append(DetectedIssue(
                                severity='warning',
                                category='performance',
                                title=f'Missing torch.no_grad() in {node.name} function',
                                description='Inference code should use torch.no_grad() to save memory and improve speed',
                                line_numbers=[node.lineno],
                                file_path=self.file_path,
                                suggestion='Wrap inference code with "with torch.no_grad():" or use @torch.no_grad() decorator'
                            ))
    
    def _detect_data_leakage(self, code: str, tree: ast.AST):
        """Detect potential data leakage issues."""
        normalization_patterns = [
            (r'(train|test).*\.mean\(\)', 'Using dataset-wide statistics'),
            (r'StandardScaler.*fit.*test', 'Fitting scaler on test data'),
            (r'normalize.*entire.*dataset', 'Normalizing entire dataset together')
        ]
        
        for pattern, issue in normalization_patterns:
            if re.search(pattern, code, re.I):
                self.issues.append(DetectedIssue(
                    severity='error',
                    category='bug',
                    title='Potential data leakage detected',
                    description=f'{issue} - this can leak test set information into training',
                    file_path=self.file_path,
                    suggestion='Compute normalization statistics only on training data, then apply to validation/test sets'
                ))
    
    def _detect_gradient_accumulation_bugs(self, code: str, tree: ast.AST):
        """Detect incorrect gradient accumulation implementations."""
        if 'accumulation_steps' in code or 'gradient_accumulation' in code:
            # Check if loss is being scaled
            loss_scaled = bool(re.search(r'loss\s*/\s*\w*accumulation', code))
            
            if not loss_scaled:
                self.issues.append(DetectedIssue(
                    severity='error',
                    category='bug',
                    title='Gradient accumulation without loss scaling',
                    description='When using gradient accumulation, loss must be divided by accumulation steps',
                    file_path=self.file_path,
                    suggestion='Scale loss by dividing by accumulation_steps: loss = loss / accumulation_steps'
                ))
    
    def _detect_loss_function_issues(self, code: str, tree: ast.AST):
        """Detect incorrect loss function usage."""
        # MSE for classification
        if 'MSELoss' in code and ('classification' in code.lower() or 'classify' in code.lower()):
            self.issues.append(DetectedIssue(
                severity='error',
                category='bug',
                title='Using MSE loss for classification',
                description='MSELoss is inappropriate for classification tasks',
                file_path=self.file_path,
                suggestion='Use CrossEntropyLoss for multi-class or BCEWithLogitsLoss for binary classification'
            ))
        
        # CrossEntropyLoss with binary
        if 'CrossEntropyLoss' in code and 'binary' in code.lower():
            self.issues.append(DetectedIssue(
                severity='warning',
                category='bug',
                title='Using CrossEntropyLoss for binary classification',
                description='CrossEntropyLoss is typically used for multi-class classification',
                file_path=self.file_path,
                suggestion='Use BCEWithLogitsLoss for binary classification tasks'
            ))
        
        # BCE without sigmoid
        if 'BCELoss' in code and ('logits' in code.lower() or ('sigmoid' not in code and 'BCEWithLogitsLoss' not in code)):
            self.issues.append(DetectedIssue(
                severity='warning',
                category='bug',
                title='BCELoss without sigmoid activation',
                description='BCELoss expects inputs in range [0,1], usually from sigmoid',
                file_path=self.file_path,
                suggestion='Either add sigmoid to model output or use BCEWithLogitsLoss which includes sigmoid'
            ))
    
    def _detect_memory_leaks(self, code: str, tree: ast.AST):
        """Detect potential memory leaks in training loops."""
        # Look for loss accumulation without .item()
        if re.search(r'(total_loss|running_loss)\s*\+=\s*loss(?!\.item)', code):
            self.issues.append(DetectedIssue(
                severity='error',
                category='bug',
                title='Memory leak: accumulating loss without .item()',
                description='Accumulating loss tensors keeps computation graph in memory',
                file_path=self.file_path,
                suggestion='Use loss.item() when accumulating losses: total_loss += loss.item()'
            ))
    
    def _detect_batch_norm_issues(self, code: str, tree: ast.AST):
        """Detect batch normalization issues."""
        # BatchNorm with batch_size=1 - use AST for better detection
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check for batch_size = 1
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'batch_size':
                        if isinstance(node.value, ast.Constant) and node.value.value == 1:
                            if 'BatchNorm' in code:
                                self.issues.append(DetectedIssue(
                                    severity='error',
                                    category='bug',
                                    title='BatchNorm with batch_size=1',
                                    description='BatchNorm doesn\'t work properly with batch_size=1',
                                    line_numbers=[node.lineno],
                                    file_path=self.file_path,
                                    suggestion='Use GroupNorm, LayerNorm, or InstanceNorm for small batch sizes'
                                ))
    
    def _detect_optimizer_issues(self, code: str, tree: ast.AST):
        """Detect optimizer-related issues."""
        # Use AST to find optimizer instantiations
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    optimizer_name = node.func.attr
                    
                    # Extract learning rate
                    lr = None
                    for keyword in node.keywords:
                        if keyword.arg == 'lr':
                            if isinstance(keyword.value, ast.Constant):
                                lr = keyword.value.value
                    
                    if lr:
                        # Check learning rate ranges based on optimizer
                        if 'SGD' in optimizer_name:
                            if lr < 1e-5:
                                severity = 'warning'
                                suggestion = 'SGD typically uses learning rates between 0.01 and 0.1'
                            elif lr < 1e-3:
                                severity = 'info'
                                suggestion = 'SGD typically uses learning rates between 0.01 and 0.1'
                            else:
                                continue
                                
                            self.issues.append(DetectedIssue(
                                severity=severity,
                                category='optimization',
                                title=f'Small learning rate for SGD optimizer',
                                description=f'Learning rate {lr} is small for SGD',
                                line_numbers=[node.lineno],
                                file_path=self.file_path,
                                suggestion=suggestion
                            ))
                        
                        elif 'Adam' in optimizer_name:
                            if lr < 1e-5:
                                self.issues.append(DetectedIssue(
                                    severity='warning',
                                    category='optimization',
                                    title=f'Very small learning rate for Adam',
                                    description=f'Learning rate {lr} is very small and may prevent convergence',
                                    line_numbers=[node.lineno],
                                    file_path=self.file_path,
                                    suggestion='Adam typically uses learning rates between 1e-4 and 1e-3'
                                ))
                            elif lr > 1e-2:
                                self.issues.append(DetectedIssue(
                                    severity='info',
                                    category='optimization',
                                    title=f'Large learning rate for Adam',
                                    description=f'Learning rate {lr} is large for Adam and may cause instability',
                                    line_numbers=[node.lineno],
                                    file_path=self.file_path,
                                    suggestion='Adam typically uses learning rates between 1e-4 and 1e-3'
                                ))
    
    def _detect_tensor_operation_issues(self, code: str, tree: ast.AST):
        """Detect inefficient tensor operations."""
        # .cpu().numpy() in loops
        if re.search(r'for.*\.cpu\(\)\.numpy\(\)', code, re.S):
            self.issues.append(DetectedIssue(
                severity='warning',
                category='performance',
                title='CPU transfer inside loop',
                description='Calling .cpu().numpy() inside loops is inefficient',
                file_path=self.file_path,
                suggestion='Batch operations and move to CPU once after the loop'
            ))
        
        # Creating tensors on wrong device
        if 'torch.tensor' in code and 'cuda' in code and 'device=' not in code:
            self.issues.append(DetectedIssue(
                severity='warning',
                category='performance',
                title='Creating tensors without specifying device',
                description='Creating tensors on CPU then moving to GPU is inefficient',
                file_path=self.file_path,
                suggestion='Create tensors directly on target device: torch.tensor(..., device=device)'
            ))
    
    def _detect_batch_size_issues(self, code: str, tree: ast.AST):
        """Detect batch size issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and 'batch' in target.id.lower():
                        if isinstance(node.value, ast.Constant):
                            batch_size = node.value.value
                            if batch_size == 1:
                                self.issues.append(DetectedIssue(
                                    severity='warning',
                                    category='performance',
                                    title='Batch size of 1 detected',
                                    description='Batch size of 1 is inefficient for training',
                                    line_numbers=[node.lineno],
                                    file_path=self.file_path,
                                    suggestion='Use larger batch sizes (16-128) for better GPU utilization'
                                ))
                            elif batch_size < 16:
                                self.issues.append(DetectedIssue(
                                    severity='info',
                                    category='performance',
                                    title=f'Small batch size ({batch_size}) detected',
                                    description='Small batch sizes may not fully utilize GPU',
                                    line_numbers=[node.lineno],
                                    file_path=self.file_path,
                                    suggestion='Consider using batch sizes of 16 or larger for better GPU utilization'
                                ))
    
    def _detect_dataloader_optimization(self, code: str, tree: ast.AST):
        """Detect missing DataLoader optimizations."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id == 'DataLoader':
                    # Check for missing optimizations
                    has_num_workers = any(kw.arg == 'num_workers' for kw in node.keywords)
                    has_pin_memory = any(kw.arg == 'pin_memory' for kw in node.keywords)
                    has_shuffle = any(kw.arg == 'shuffle' for kw in node.keywords)
                    
                    if not has_num_workers:
                        self.issues.append(DetectedIssue(
                            severity='info',
                            category='performance',
                            title='DataLoader without num_workers',
                            description='Using default num_workers=0 means no parallel data loading',
                            line_numbers=[node.lineno],
                            file_path=self.file_path,
                            suggestion='Set num_workers=4 (or number of CPU cores) for faster data loading'
                        ))
                    
                    if not has_pin_memory and 'cuda' in code:
                        self.issues.append(DetectedIssue(
                            severity='info',
                            category='performance',
                            title='DataLoader without pin_memory for GPU training',
                            description='pin_memory=True can speed up GPU data transfer',
                            line_numbers=[node.lineno],
                            file_path=self.file_path,
                            suggestion='Add pin_memory=True when training on GPU'
                        ))
    
    def _detect_initialization_issues(self, code: str, tree: ast.AST):
        """Detect missing weight initialization."""
        # Look for custom nn.Module classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's likely a neural network module
                inherits_module = any(
                    (isinstance(base, ast.Name) and 'Module' in base.id) or
                    (isinstance(base, ast.Attribute) and base.attr == 'Module')
                    for base in node.bases
                )
                
                if inherits_module:
                    # Check if there's any initialization
                    has_init = any(
                        'init' in ast.unparse(n).lower() and 
                        any(init_func in ast.unparse(n) for init_func in 
                            ['xavier', 'kaiming', 'normal_', 'uniform_', 'orthogonal'])
                        for n in ast.walk(node)
                    )
                    
                    if not has_init:
                        self.issues.append(DetectedIssue(
                            severity='info',
                            category='best_practice',
                            title=f'No explicit weight initialization in {node.name}',
                            description='Custom models benefit from proper weight initialization',
                            line_numbers=[node.lineno],
                            file_path=self.file_path,
                            suggestion='Consider using kaiming_uniform_ or xavier_uniform_ initialization'
                        ))


class AntiPatternDetector:
    """Detects ML anti-patterns and suboptimal implementations."""
    
    def detect_architecture_issues(self, model_code: str) -> List[Dict[str, Any]]:
        """Detect architecture-specific anti-patterns."""
        issues = []
        
        # Deep network without skip connections
        conv_count = len(re.findall(r'Conv2d', model_code))
        linear_count = len(re.findall(r'Linear\(|nn\.Linear', model_code))
        total_layers = conv_count + linear_count
        
        if total_layers > 10:
            # Check for residual connections
            has_residual = any(pattern in model_code for pattern in 
                              ['x +', '+ x', 'residual =', 'skip', 'identity'])
            
            if not has_residual:
                issues.append({
                    'severity': 'warning',
                    'category': 'anti-pattern',
                    'title': 'Deep network without skip connections',
                    'description': f'Network has {total_layers} layers but no apparent residual connections',
                    'suggestion': 'Consider adding skip connections for better gradient flow in deep networks'
                })
        
        # Sigmoid/tanh in deep networks
        if total_layers > 5 and ('sigmoid' in model_code.lower() or 'tanh' in model_code.lower()):
            issues.append({
                'severity': 'warning',
                'category': 'anti-pattern',
                'title': 'Sigmoid/Tanh activation in deep network',
                'description': 'Sigmoid/Tanh can cause vanishing gradients in deep networks',
                'suggestion': 'Use ReLU, LeakyReLU, or GELU for better gradient flow'
            })
        
        # No normalization in deep networks
        if conv_count > 3 and not any(norm in model_code for norm in ['BatchNorm', 'LayerNorm', 'GroupNorm']):
            issues.append({
                'severity': 'warning',
                'category': 'anti-pattern',
                'title': 'No normalization layers in deep network',
                'description': 'Deep networks typically benefit from normalization layers',
                'suggestion': 'Add BatchNorm2d after convolutional layers for training stability'
            })
        
        return issues