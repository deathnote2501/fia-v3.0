#!/usr/bin/env python3
"""
FIA v3.0 Project Health Monitor (KISS Version)
Simple, focused health check based on SPEC.md requirements
"""

import os
import sys
import ast
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

class FIAHealthMonitor:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        
        # Exclusions (KISS: simple lists)
        self.excluded_dirs = [
            '__pycache__', '.pytest_cache', 'node_modules', 'venv', 'env',
            'dist', 'build', 'uploads', 'tech-docs', 'backend/uploads', 'backend/backend',
            'tests'  # Exclude all test directories
        ]
        
        self.excluded_files = [
            'project_health.py', 'project_health_advanced.py', 'test_vertex_ai.py'
        ]
        
        # File extensions to exclude (not core app files)
        self.excluded_extensions = [
            '.pdf', '.ppt', '.pptx', '.doc', '.docx',  # Documents
            '.pyc', '.log', '.tmp', '.cache'           # Generated files
        ]
        
        # SPEC.md compliance thresholds
        self.thresholds = {
            'total_files': 100,        # Reasonable for phase-based development
            'total_lines': 8000,       # KISS principle
            'max_function_complexity': 10,  # Readable functions
            'max_file_lines': 300,     # Single responsibility
            'architecture_violations': 5   # Clean architecture
        }

    def should_exclude(self, path: Path) -> bool:
        """Simple exclusion check"""
        path_str = str(path)
        return (
            any(excluded in path_str for excluded in self.excluded_dirs) or
            path.name in self.excluded_files or
            path.name.startswith('.') or
            path.suffix in self.excluded_extensions or
            'test_' in path.name  # Exclude individual test files
        )

    def analyze_code_structure(self) -> Dict:
        """Analyze basic code structure"""
        stats = {
            'files_by_type': defaultdict(int),
            'lines_by_type': defaultdict(int),
            'total_files': 0,
            'total_lines': 0
        }
        
        extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.html': 'html',
            '.css': 'css',
            '.md': 'docs'
        }
        
        # Office documents to exclude from counting
        office_extensions = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'}
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(ex in d for ex in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                if self.should_exclude(file_path):
                    continue
                
                ext = file_path.suffix.lower()
                
                # Skip office documents entirely
                if ext in office_extensions:
                    continue
                
                file_type = extensions.get(ext, 'other')
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len([line for line in f if line.strip()])
                    
                    stats['files_by_type'][file_type] += 1
                    stats['lines_by_type'][file_type] += lines
                    stats['total_files'] += 1
                    stats['total_lines'] += lines
                    
                except Exception:
                    continue
        
        return stats

    def check_architecture_compliance(self) -> Dict:
        """Check hexagonal architecture compliance from SPEC.md"""
        compliance = {
            'has_domain_layer': False,
            'has_adapters_layer': False,
            'has_infrastructure_layer': False,
            'domain_purity': 0,
            'violations': []
        }
        
        backend_path = self.project_path / 'backend' / 'app'
        if not backend_path.exists():
            compliance['violations'].append("Missing backend/app structure")
            return compliance
        
        # Check required directories from SPEC.md
        required_dirs = ['domain', 'adapters', 'infrastructure']
        for dir_name in required_dirs:
            if (backend_path / dir_name).exists():
                compliance[f'has_{dir_name}_layer'] = True
        
        # Check domain purity (no infrastructure imports in domain)
        domain_path = backend_path / 'domain'
        if domain_path.exists():
            domain_violations = self._check_domain_purity(domain_path)
            compliance['domain_purity'] = max(0, 100 - len(domain_violations) * 20)
            compliance['violations'].extend(domain_violations)
        
        return compliance

    def _check_domain_purity(self, domain_path: Path) -> List[str]:
        """Check if domain layer is pure (no infrastructure dependencies)"""
        violations = []
        forbidden_imports = ['sqlalchemy', 'alembic', 'fastapi', 'uvicorn', 'psycopg']
        
        for py_file in domain_path.rglob('*.py'):
            if self.should_exclude(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        module_name = ''
                        if isinstance(node, ast.Import):
                            module_name = node.names[0].name if node.names else ''
                        elif isinstance(node, ast.ImportFrom):
                            module_name = node.module or ''
                        
                        if any(forbidden in module_name.lower() for forbidden in forbidden_imports):
                            violations.append(f"Domain layer imports infrastructure: {module_name} in {py_file.name}")
                            
            except Exception:
                continue
        
        return violations

    def check_naming_conventions(self) -> Dict:
        """Check SPEC.md English naming conventions"""
        conventions = {
            'english_compliance': 0,
            'violations': []
        }
        
        # Simple check for French words in code
        french_indicators = ['formateur', 'apprenant', 'formation', 'cours', 'module']
        total_checked = 0
        violations_count = 0
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(ex in d for ex in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                if not file.endswith('.py') or self.should_exclude(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                    
                    total_checked += 1
                    for french_word in french_indicators:
                        if french_word in content:
                            violations_count += 1
                            conventions['violations'].append(f"French word '{french_word}' in {file_path.name}")
                            break
                            
                except Exception:
                    continue
        
        if total_checked > 0:
            conventions['english_compliance'] = max(0, 100 - (violations_count / total_checked * 100))
        
        return conventions

    def check_file_sizes(self) -> Dict:
        """Check for oversized files (KISS principle)"""
        sizes = {
            'oversized_files': [],
            'average_size': 0,
            'max_size': 0
        }
        
        file_sizes = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(ex in d for ex in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                if not file.endswith('.py') or self.should_exclude(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len([line for line in f if line.strip()])
                    
                    file_sizes.append(lines)
                    
                    if lines > self.thresholds['max_file_lines']:
                        sizes['oversized_files'].append({
                            'file': str(file_path.relative_to(self.project_path)),
                            'lines': lines
                        })
                        
                except Exception:
                    continue
        
        if file_sizes:
            sizes['average_size'] = sum(file_sizes) / len(file_sizes)
            sizes['max_size'] = max(file_sizes)
        
        return sizes

    def analyze_complexity(self) -> Dict:
        """Simple complexity analysis"""
        complexity = {
            'complex_functions': [],
            'average_complexity': 0,
            'total_functions': 0
        }
        
        all_complexities = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(ex in d for ex in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                if not file.endswith('.py') or self.should_exclude(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Simple complexity: count control structures
                            func_complexity = 1  # Base complexity
                            for child in ast.walk(node):
                                if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                                    func_complexity += 1
                            
                            all_complexities.append(func_complexity)
                            complexity['total_functions'] += 1
                            
                            if func_complexity > self.thresholds['max_function_complexity']:
                                complexity['complex_functions'].append({
                                    'function': node.name,
                                    'file': file_path.name,
                                    'complexity': func_complexity
                                })
                                
                except Exception:
                    continue
        
        if all_complexities:
            complexity['average_complexity'] = sum(all_complexities) / len(all_complexities)
        
        return complexity

    def get_status_indicator(self, value: float, threshold: float, reverse: bool = False) -> Tuple[str, str]:
        """Simple status indicator"""
        if not reverse:
            if value <= threshold:
                return "🟢", "GOOD"
            elif value <= threshold * 1.5:
                return "🟡", "WARNING" 
            else:
                return "🔴", "CRITICAL"
        else:
            if value >= threshold:
                return "🟢", "GOOD"
            elif value >= threshold * 0.7:
                return "🟡", "WARNING"
            else:
                return "🔴", "CRITICAL"

    def generate_report(self):
        """Generate KISS health report"""
        print("=" * 60)
        print("🏥 FIA v3.0 PROJECT HEALTH MONITOR (KISS)")
        print("=" * 60)
        print(f"📅 Analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Project: {self.project_path.absolute()}")
        print()

        # 1. Code Structure
        print("📊 CODE STRUCTURE")
        print("-" * 30)
        structure = self.analyze_code_structure()
        
        for file_type, count in structure['files_by_type'].items():
            lines = structure['lines_by_type'][file_type]
            print(f"  {file_type:12}: {count:3} files | {lines:5} lines")
        
        print(f"  {'TOTAL':12}: {structure['total_files']:3} files | {structure['total_lines']:5} lines")
        
        # Status for total size
        size_status, size_text = self.get_status_indicator(
            structure['total_lines'], self.thresholds['total_lines']
        )
        print(f"  Status: {size_status} {size_text}")
        print()

        # 2. Architecture Compliance
        print("🏗️ ARCHITECTURE (SPEC.md)")
        print("-" * 30)
        arch = self.check_architecture_compliance()
        
        layers = ['domain', 'adapters', 'infrastructure']
        for layer in layers:
            has_layer = arch[f'has_{layer}_layer']
            status = "✅" if has_layer else "❌"
            print(f"  {layer.capitalize():12}: {status}")
        
        purity_status, purity_text = self.get_status_indicator(
            arch['domain_purity'], 80, reverse=True
        )
        print(f"  Domain purity   : {arch['domain_purity']:.0f}% {purity_status}")
        
        if arch['violations']:
            print("  🚨 Violations:")
            for violation in arch['violations'][:3]:  # Limit to 3
                print(f"    - {violation}")
        print()

        # 3. Naming Conventions
        print("🌐 NAMING (English First)")
        print("-" * 30)
        naming = self.check_naming_conventions()
        
        naming_status, naming_text = self.get_status_indicator(
            naming['english_compliance'], 90, reverse=True
        )
        print(f"  English compliance: {naming['english_compliance']:.0f}% {naming_status}")
        
        if naming['violations']:
            print("  🚨 French words found:")
            for violation in naming['violations'][:3]:
                print(f"    - {violation}")
        print()

        # 4. File Sizes (KISS)
        print("📏 FILE SIZES (KISS)")
        print("-" * 30)
        sizes = self.check_file_sizes()
        
        print(f"  Average size    : {sizes['average_size']:.0f} lines")
        print(f"  Largest file    : {sizes['max_size']} lines")
        print(f"  Oversized files : {len(sizes['oversized_files'])}")
        
        if sizes['oversized_files']:
            print("  🚨 Large files (>300 lines):")
            for file_info in sizes['oversized_files'][:3]:
                print(f"    - {file_info['file']}: {file_info['lines']} lines")
        
        size_status, size_text = self.get_status_indicator(
            len(sizes['oversized_files']), 5
        )
        print(f"  Status: {size_status} {size_text}")
        print()

        # 5. Complexity
        print("🧮 COMPLEXITY")
        print("-" * 30)
        complexity = self.analyze_complexity()
        
        print(f"  Total functions : {complexity['total_functions']}")
        print(f"  Avg complexity  : {complexity['average_complexity']:.1f}")
        print(f"  Complex funcs   : {len(complexity['complex_functions'])}")
        
        if complexity['complex_functions']:
            print("  🚨 Complex functions (>10):")
            for func in complexity['complex_functions'][:3]:
                print(f"    - {func['function']} ({func['complexity']}): {func['file']}")
        
        complexity_status, complexity_text = self.get_status_indicator(
            complexity['average_complexity'], self.thresholds['max_function_complexity']
        )
        print(f"  Status: {complexity_status} {complexity_text}")
        print()

        # 6. Overall Health Score
        print("💡 OVERALL HEALTH")
        print("-" * 30)
        
        # Simple scoring
        scores = []
        
        # Size score (30%)
        if structure['total_lines'] <= self.thresholds['total_lines']:
            scores.append(3)
        elif structure['total_lines'] <= self.thresholds['total_lines'] * 1.5:
            scores.append(2)
        else:
            scores.append(1)
        
        # Architecture score (25%)
        arch_score = sum([
            arch['has_domain_layer'],
            arch['has_adapters_layer'], 
            arch['has_infrastructure_layer']
        ])
        scores.append(arch_score)
        
        # Naming score (20%)
        if naming['english_compliance'] >= 90:
            scores.append(3)
        elif naming['english_compliance'] >= 70:
            scores.append(2)
        else:
            scores.append(1)
        
        # Complexity score (25%)
        if complexity['average_complexity'] <= self.thresholds['max_function_complexity']:
            scores.append(3)
        elif complexity['average_complexity'] <= self.thresholds['max_function_complexity'] * 1.5:
            scores.append(2)
        else:
            scores.append(1)
        
        # Weighted average
        weights = [0.3, 0.25, 0.2, 0.25]
        final_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        
        if final_score >= 2.5:
            health = "🟢 EXCELLENT"
            recommendation = "Architecture is solid and maintainable"
        elif final_score >= 2.0:
            health = "🟡 GOOD"
            recommendation = "Minor improvements recommended"
        elif final_score >= 1.5:
            health = "🟠 WARNING"
            recommendation = "Refactoring needed in some areas"
        else:
            health = "🔴 CRITICAL"
            recommendation = "Significant refactoring required"
        
        print(f"  Overall Health  : {health}")
        print(f"  Score          : {final_score:.2f}/3.0")
        print(f"  Recommendation : {recommendation}")
        print()

        # 7. Action Items
        print("🎯 PRIORITY ACTIONS")
        print("-" * 30)
        
        priority = 1
        
        if structure['total_lines'] > self.thresholds['total_lines'] * 1.5:
            print(f"  {priority}. 🚨 URGENT: Reduce codebase size ({structure['total_lines']} lines)")
            priority += 1
        
        if not all([arch['has_domain_layer'], arch['has_adapters_layer'], arch['has_infrastructure_layer']]):
            print(f"  {priority}. 🏗️ Complete hexagonal architecture structure")
            priority += 1
        
        if naming['english_compliance'] < 80:
            print(f"  {priority}. 🌐 Fix naming conventions (English first)")
            priority += 1
        
        if len(complexity['complex_functions']) > 5:
            print(f"  {priority}. 🧮 Simplify complex functions")
            priority += 1
        
        if len(sizes['oversized_files']) > 5:
            print(f"  {priority}. 📏 Break down large files (KISS principle)")
            priority += 1
        
        if priority == 1:
            print("  ✅ No critical actions needed!")
        
        print("\n" + "=" * 60)

def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    monitor = FIAHealthMonitor(project_path)
    monitor.generate_report()

if __name__ == "__main__":
    main()