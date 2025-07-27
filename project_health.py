#!/usr/bin/env python3
"""
Project Health Monitor Advanced - FIA v3.0
Analyse complète : taille, complexité cyclomatique, couplage, cohésion, responsabilités
"""

import os
import sys
import ast
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set

class ComplexityAnalyzer(ast.NodeVisitor):
    """Analyseur de complexité cyclomatique"""
    def __init__(self):
        self.complexity = 1  # Complexité de base
        self.functions = []
        self.current_function = None
        
    def visit_FunctionDef(self, node):
        old_func = self.current_function
        old_complexity = self.complexity
        
        self.current_function = node.name
        self.complexity = 1  # Reset pour cette fonction
        
        self.generic_visit(node)
        
        self.functions.append({
            'name': node.name,
            'complexity': self.complexity,
            'line': node.lineno
        })
        
        self.current_function = old_func
        self.complexity = old_complexity
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

class DependencyAnalyzer:
    """Analyseur de dépendances et couplage"""
    def __init__(self):
        self.imports = defaultdict(set)
        self.internal_deps = defaultdict(set)
        self.external_deps = defaultdict(set)
    
    def analyze_file(self, file_path: Path, content: str):
        try:
            tree = ast.parse(content)
            module_name = self._get_module_name(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._add_dependency(module_name, alias.name, file_path)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._add_dependency(module_name, node.module, file_path)
        except SyntaxError:
            pass
    
    def _get_module_name(self, file_path: Path) -> str:
        return str(file_path).replace('/', '.').replace('.py', '')
    
    def _add_dependency(self, from_module: str, to_module: str, file_path: Path):
        self.imports[from_module].add(to_module)
        
        # Distinguer dépendances internes vs externes
        if self._is_internal_module(to_module, file_path):
            self.internal_deps[from_module].add(to_module)
        else:
            self.external_deps[from_module].add(to_module)
    
    def _is_internal_module(self, module_name: str, file_path: Path) -> bool:
        # Module interne si commence par un chemin relatif ou fait partie du projet
        return (module_name.startswith('.') or 
                'backend' in module_name or 
                'frontend' in module_name or
                module_name in ['app', 'domain', 'adapters', 'infrastructure'])

class CohesionAnalyzer:
    """Analyseur de cohésion des modules"""
    def __init__(self):
        self.module_functions = defaultdict(list)
        self.module_classes = defaultdict(list)
        self.shared_variables = defaultdict(set)
    
    def analyze_file(self, file_path: Path, content: str):
        try:
            tree = ast.parse(content)
            module_name = str(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.module_functions[module_name].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    self.module_classes[module_name].append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.shared_variables[module_name].add(target.id)
        except SyntaxError:
            pass
    
    def calculate_cohesion(self, module_name: str) -> float:
        """Calcule la cohésion basée sur les éléments partagés"""
        functions = len(self.module_functions[module_name])
        classes = len(self.module_classes[module_name])
        variables = len(self.shared_variables[module_name])
        
        if functions + classes == 0:
            return 1.0
        
        # Cohésion = ratio d'éléments qui interagissent
        total_elements = functions + classes
        shared_elements = min(variables, total_elements)
        
        return shared_elements / total_elements if total_elements > 0 else 1.0

class AdvancedProjectHealthMonitor:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.stats = {}
        
        # Fichiers à exclure de l'analyse (ne font pas partie du projet core)
        self.excluded_files = [
            'project_health.py', 
            'project_health_advanced.py',
            'health_monitor.py',
            'test_vertex_ai.py'  # Fichier de test isolé
        ]
        
        # Dossiers à exclure complètement
        self.excluded_dirs = [
            '__pycache__',
            '.pytest_cache',
            'node_modules',
            'venv',
            'env',
            'dist',
            'build',
            'uploads',  # Fichiers uploadés par les utilisateurs
            'tech-docs',  # Documentation technique externe
            'backend/uploads',
            'backend/backend'  # Dossier dupliqué
        ]
        
        # Extensions de fichiers temporaires/générés à ignorer
        self.excluded_extensions = [
            '.pyc',
            '.pyo',
            '.log',
            '.tmp',
            '.cache',
            '.json'  # Fichiers de config comme animemate-ddb62-5161876d56bc.json
        ]
        
        # Seuils étendus avec nouveaux KPI
        self.thresholds = {
            'lines_total': {'green': 6500, 'orange': 10000, 'red': 15000},
            'files_total': {'green': 50, 'orange': 80, 'red': 120},
            'dependencies': {'green': 15, 'orange': 30, 'red': 50},
            'function_size': {'green': 20, 'orange': 40, 'red': 60},
            'folder_depth': {'green': 4, 'orange': 6, 'red': 8},
            'complexity': {'green': 10, 'orange': 15, 'red': 25},
            'coupling': {'green': 5, 'orange': 10, 'red': 20},
            'cohesion': {'green': 0.7, 'orange': 0.5, 'red': 0.3},
            'test_coverage': {'green': 80, 'orange': 60, 'red': 40},
            'duplicate_ratio': {'green': 5, 'orange': 10, 'red': 20},
            'backend_frontend_ratio': {'green': 4, 'orange': 6, 'red': 10}
        }
        
        self.code_extensions = {
            'backend': ['.py'],
            'frontend': ['.js', '.html', '.css'],
            'config': ['.toml', '.ini', '.yaml', '.yml'],
            'docs': ['.md', '.rst', '.txt']
        }

    def get_status_color(self, value, metric, reverse=False):
        """Retourne le statut coloré (reverse=True pour cohésion où plus = mieux)"""
        thresholds = self.thresholds.get(metric, {})
        if not thresholds:
            return "🔵", "UNKNOWN"
        
        if not reverse:
            if value <= thresholds.get('green', 0):
                return "🟢", "GOOD"
            elif value <= thresholds.get('orange', 0):
                return "🟡", "WARNING"
            else:
                return "🔴", "CRITICAL"
        else:
            # Pour cohésion (plus = mieux)
            if value >= thresholds.get('green', 1):
                return "🟢", "GOOD"
            elif value >= thresholds.get('orange', 1):
                return "🟡", "WARNING"
            else:
                return "🔴", "CRITICAL"

    def should_exclude_path(self, path: Path):
        """Vérifie si le chemin doit être exclu"""
        # Vérifier les dossiers exclus
        for excluded_dir in self.excluded_dirs:
            if excluded_dir in str(path):
                return True
        
        # Vérifier les fichiers exclus
        if path.name in self.excluded_files:
            return True
        
        # Vérifier les extensions exclues
        if path.suffix in self.excluded_extensions:
            return True
        
        # Exclure les fichiers cachés
        if path.name.startswith('.'):
            return True
            
        return False

    def count_lines_and_files(self):
        """Compte les lignes de code et fichiers par catégorie"""
        stats = {
            'backend': {'files': 0, 'lines': 0},
            'frontend': {'files': 0, 'lines': 0},
            'config': {'files': 0, 'lines': 0},
            'docs': {'files': 0, 'lines': 0},
            'tests': {'files': 0, 'lines': 0},
            'total': {'files': 0, 'lines': 0}
        }
        
        for root, dirs, files in os.walk(self.project_path):
            # Filtrer les dossiers exclus
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self.should_exclude_path(file_path):
                    continue
                    
                extension = file_path.suffix.lower()
                
                # Catégoriser le fichier
                category = None
                
                # Tests séparés
                if 'test' in str(file_path) or file.startswith('test_'):
                    category = 'tests'
                else:
                    for cat, exts in self.code_extensions.items():
                        if extension in exts:
                            category = cat
                            break
                
                if category:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len([line for line in f if line.strip()])
                        
                        stats[category]['files'] += 1
                        stats[category]['lines'] += lines
                        stats['total']['files'] += 1
                        stats['total']['lines'] += lines
                        
                    except Exception:
                        continue
        
        return stats

    def analyze_test_coverage(self):
        """Analyse approximative de la couverture de tests"""
        test_files = []
        source_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self.should_exclude_path(file_path) or not file.endswith('.py'):
                    continue
                
                if 'test' in str(file_path) or file.startswith('test_'):
                    test_files.append(file_path)
                else:
                    source_files.append(file_path)
        
        # Calcul approximatif de la couverture
        if not source_files:
            return 0, 0, 0
            
        coverage_ratio = (len(test_files) / len(source_files)) * 100
        
        return len(test_files), len(source_files), coverage_ratio

    def analyze_code_duplication(self):
        """Détecte la duplication de code approximative"""
        function_signatures = defaultdict(list)
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self.should_exclude_path(file_path) or not file.endswith('.py'):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Analyser les fonctions
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Signature simple basée sur le nombre de paramètres
                            signature = f"{node.name}_{len(node.args.args)}"
                            function_signatures[signature].append(str(file_path))
                            
                except Exception:
                    continue
        
        # Calculer le ratio de duplication
        total_functions = sum(len(files) for files in function_signatures.values())
        duplicated_functions = sum(len(files) - 1 for files in function_signatures.values() if len(files) > 1)
        
        duplication_ratio = (duplicated_functions / total_functions * 100) if total_functions > 0 else 0
        
        return duplication_ratio, function_signatures

    def analyze_architecture_metrics(self):
        """Analyse des métriques d'architecture spécifiques"""
        architecture_stats = {
            'controllers': 0,
            'services': 0,
            'repositories': 0,
            'models': 0,
            'schemas': 0,
            'entities': 0
        }
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                if not file.endswith('.py') or self.should_exclude_path(Path(root) / file):
                    continue
                
                # Classifier selon l'architecture hexagonale
                if 'controller' in file:
                    architecture_stats['controllers'] += 1
                elif 'service' in file:
                    architecture_stats['services'] += 1
                elif 'repository' in file:
                    architecture_stats['repositories'] += 1
                elif 'model' in file:
                    architecture_stats['models'] += 1
                elif 'schema' in file:
                    architecture_stats['schemas'] += 1
                elif 'entities' in root:
                    architecture_stats['entities'] += 1
        
        return architecture_stats

    def analyze_complexity(self):
        """Analyse la complexité cyclomatique"""
        complexity_data = []
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if not file.endswith('.py') or self.should_exclude_path(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    analyzer = ComplexityAnalyzer()
                    tree = ast.parse(content)
                    analyzer.visit(tree)
                    
                    for func in analyzer.functions:
                        complexity_data.append({
                            'name': func['name'],
                            'file': str(file_path.relative_to(self.project_path)),
                            'complexity': func['complexity'],
                            'line': func['line']
                        })
                        
                except Exception:
                    continue
        
        return complexity_data

    def analyze_dependencies_and_coupling(self):
        """Analyse les dépendances et le couplage"""
        dep_analyzer = DependencyAnalyzer()
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if not file.endswith('.py') or self.should_exclude_path(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    dep_analyzer.analyze_file(file_path, content)
                        
                except Exception:
                    continue
        
        return dep_analyzer

    def analyze_cohesion(self):
        """Analyse la cohésion des modules"""
        cohesion_analyzer = CohesionAnalyzer()
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if not file.endswith('.py') or self.should_exclude_path(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    cohesion_analyzer.analyze_file(file_path, content)
                        
                except Exception:
                    continue
        
        return cohesion_analyzer

    def analyze_responsibilities(self):
        """Analyse le principe de responsabilité unique"""
        responsibilities = {}
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            for file in files:
                file_path = Path(root) / file
                
                if not file.endswith('.py') or self.should_exclude_path(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Compter les classes, fonctions, imports
                    tree = ast.parse(content)
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    imports = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
                    
                    responsibilities[str(file_path.relative_to(self.project_path))] = {
                        'classes': len(classes),
                        'functions': len(functions),
                        'imports': imports,
                        'total_elements': len(classes) + len(functions),
                        'lines': len([line for line in content.split('\n') if line.strip()])
                    }
                        
                except Exception:
                    continue
        
        return responsibilities

    def count_dependencies(self):
        """Compte les dépendances du projet"""
        deps = 0
        
        # Python dependencies
        pyproject_path = self.project_path / 'backend' / 'pyproject.toml'
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Compter les dépendances dans [tool.poetry.dependencies]
                    deps += len(re.findall(r'^\s*["\']?[\w-]+["\']?\s*=', content, re.MULTILINE))
            except Exception:
                pass
        
        # Autres fichiers de requirements
        req_files = ['requirements.txt', 'Pipfile']
        for req_file in req_files:
            req_path = self.project_path / 'backend' / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        deps += len([line for line in content.split('\n') 
                                   if line.strip() and not line.strip().startswith('#')])
                except Exception:
                    continue
        
        return deps

    def get_folder_depth(self):
        """Calcule la profondeur maximale des dossiers"""
        max_depth = 0
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not any(excluded in d for excluded in self.excluded_dirs)]
            
            # Ignorer les uploads et tech-docs dans le calcul
            if any(excluded in root for excluded in ['uploads', 'tech-docs', '__pycache__']):
                continue
                
            current_depth = len(Path(root).relative_to(self.project_path).parts)
            max_depth = max(max_depth, current_depth)
        
        return max_depth

    def get_git_info(self):
        """Récupère les informations Git"""
        try:
            last_commit = subprocess.check_output(
                ['git', 'log', '-1', '--format=%cr'], 
                cwd=self.project_path, 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            total_commits = subprocess.check_output(
                ['git', 'rev-list', '--count', 'HEAD'], 
                cwd=self.project_path,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            return last_commit, int(total_commits)
        except:
            return "N/A", 0

    def generate_report(self):
        """Génère le rapport complet avancé"""
        print("=" * 75)
        print("🏥 ADVANCED PROJECT HEALTH MONITOR - FIA v3.0")
        print("=" * 75)
        print(f"📅 Analyse effectuée le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Chemin du projet: {self.project_path.absolute()}")
        print(f"⚠️  Exclusions: fichiers système, uploads, tech-docs, __pycache__")
        print()

        # 1. Analyse des lignes de code
        print("📊 ANALYSE DU CODE")
        print("-" * 40)
        file_stats = self.count_lines_and_files()
        
        for category, data in file_stats.items():
            if category == 'total':
                continue
            if data['files'] > 0:
                print(f"  {category.upper():12} : {data['files']:3} fichiers | {data['lines']:6} lignes")
        
        print(f"  {'TOTAL':12} : {file_stats['total']['files']:3} fichiers | {file_stats['total']['lines']:6} lignes")
        
        # Ratio Backend/Frontend
        if file_stats['frontend']['lines'] > 0:
            ratio = file_stats['backend']['lines'] / file_stats['frontend']['lines']
            print(f"  Ratio B/F       : {ratio:.1f}:1", end="")
            color, status = self.get_status_color(ratio, 'backend_frontend_ratio')
            print(f" {color}")
        
        color, status = self.get_status_color(file_stats['total']['lines'], 'lines_total')
        print(f"  Status: {color} {status}")
        print()

        # 2. Architecture & Organisation
        print("🏗️ ARCHITECTURE HEXAGONALE")
        print("-" * 40)
        arch_stats = self.analyze_architecture_metrics()
        total_arch_files = sum(arch_stats.values())
        
        for component, count in arch_stats.items():
            if count > 0:
                percentage = (count / total_arch_files * 100) if total_arch_files > 0 else 0
                print(f"  {component.capitalize():12} : {count:3} fichiers ({percentage:.1f}%)")
        
        # Vérifier l'équilibre architectural
        balance_score = "🟢 Équilibrée" if all(0 < count < total_arch_files*0.5 for count in arch_stats.values() if count > 0) else "🟡 Déséquilibrée"
        print(f"  Architecture    : {balance_score}")
        print()

        # 3. Tests & Couverture
        print("🧪 TESTS & COUVERTURE")
        print("-" * 40)
        test_files, source_files, coverage = self.analyze_test_coverage()
        
        print(f"  Fichiers tests  : {test_files}")
        print(f"  Fichiers source : {source_files}")
        print(f"  Couverture est. : {coverage:.1f}%")
        
        color, status = self.get_status_color(coverage, 'test_coverage', reverse=True)
        print(f"  Status: {color} {status}")
        print()

        # 4. Complexité cyclomatique
        print("🧮 COMPLEXITÉ CYCLOMATIQUE")
        print("-" * 40)
        complexity_data = self.analyze_complexity()
        if complexity_data:
            avg_complexity = sum(f['complexity'] for f in complexity_data) / len(complexity_data)
            high_complexity = [f for f in complexity_data if f['complexity'] > 10]
            max_complexity = max(complexity_data, key=lambda x: x['complexity'])
            
            print(f"  Total fonctions     : {len(complexity_data)}")
            print(f"  Complexité moyenne  : {avg_complexity:.1f}")
            print(f"  Complexité max      : {max_complexity['complexity']} ({max_complexity['name']})")
            print(f"  Fonctions > 10      : {len(high_complexity)}")
            
            if high_complexity:
                print("  🚨 Fonctions complexes (> 10):")
                for func in sorted(high_complexity, key=lambda x: x['complexity'], reverse=True)[:3]:
                    print(f"    - {func['name']} (CC: {func['complexity']}) dans {func['file']}")
            
            color, status = self.get_status_color(avg_complexity, 'complexity')
            print(f"  Status: {color} {status}")
        else:
            print("  Aucune fonction Python trouvée")
        print()

        # 5. Duplication de code
        print("🔄 DUPLICATION DE CODE")
        print("-" * 40)
        duplication_ratio, duplicated_funcs = self.analyze_code_duplication()
        
        print(f"  Ratio duplication   : {duplication_ratio:.1f}%")
        
        # Top duplications
        top_duplications = [(sig, files) for sig, files in duplicated_funcs.items() if len(files) > 2]
        if top_duplications:
            print("  🚨 Fonctions dupliquées:")
            for sig, files in sorted(top_duplications, key=lambda x: len(x[1]), reverse=True)[:3]:
                print(f"    - {sig}: {len(files)} occurrences")
        
        color, status = self.get_status_color(duplication_ratio, 'duplicate_ratio')
        print(f"  Status: {color} {status}")
        print()

        # 6. Responsabilités (SRP)
        print("🎯 RESPONSABILITÉS (SRP)")
        print("-" * 40)
        responsibilities = self.analyze_responsibilities()
        if responsibilities:
            heavy_files = [(f, data) for f, data in responsibilities.items() 
                          if data['total_elements'] > 10 or data['lines'] > 300]
            
            avg_elements = sum(data['total_elements'] for data in responsibilities.values()) / len(responsibilities)
            
            print(f"  Fichiers analysés   : {len(responsibilities)}")
            print(f"  Éléments/fichier    : {avg_elements:.1f} moyenne")
            print(f"  Fichiers lourds     : {len(heavy_files)} (>10 éléments ou >300 lignes)")
            
            if heavy_files:
                print("  🚨 Violations potentielles SRP:")
                for filename, data in sorted(heavy_files, key=lambda x: x[1]['total_elements'], reverse=True)[:3]:
                    print(f"    - {Path(filename).name}: {data['total_elements']} éléments, {data['lines']} lignes")
            
            violation_ratio = len(heavy_files) / len(responsibilities)
            color, status = self.get_status_color(violation_ratio * 100, 'coupling')
            print(f"  Status: {color} {status}")
        print()

        # 7. Couplage et dépendances
        print("🔗 COUPLAGE & DÉPENDANCES")
        print("-" * 40)
        dep_analyzer = self.analyze_dependencies_and_coupling()
        
        if dep_analyzer.imports:
            avg_coupling = sum(len(deps) for deps in dep_analyzer.imports.values()) / len(dep_analyzer.imports)
            max_coupled = max(dep_analyzer.imports.items(), key=lambda x: len(x[1]))
            high_coupling = [(mod, deps) for mod, deps in dep_analyzer.imports.items() if len(deps) > 8]
            
            print(f"  Modules analysés    : {len(dep_analyzer.imports)}")
            print(f"  Couplage moyen      : {avg_coupling:.1f} dépendances/module")
            print(f"  Plus couplé         : {len(max_coupled[1])} deps ({Path(max_coupled[0]).name})")
            print(f"  Modules > 8 deps    : {len(high_coupling)}")
            
            if high_coupling:
                print("  🚨 Couplage élevé:")
                for module, deps in sorted(high_coupling, key=lambda x: len(x[1]), reverse=True)[:3]:
                    print(f"    - {Path(module).name}: {len(deps)} dépendances")
            
            color, status = self.get_status_color(avg_coupling, 'coupling')
            print(f"  Status: {color} {status}")
        
        deps = self.count_dependencies()
        print(f"  Dépendances externes: {deps}")
        color, status = self.get_status_color(deps, 'dependencies')
        print(f"  Status deps: {color} {status}")
        print()

        # 8. Cohésion
        print("🤝 COHÉSION DES MODULES")
        print("-" * 40)
        cohesion_analyzer = self.analyze_cohesion()
        
        if cohesion_analyzer.module_functions:
            cohesion_scores = []
            for module in cohesion_analyzer.module_functions.keys():
                score = cohesion_analyzer.calculate_cohesion(module)
                cohesion_scores.append((module, score))
            
            if cohesion_scores:
                avg_cohesion = sum(score for _, score in cohesion_scores) / len(cohesion_scores)
                low_cohesion = [(mod, score) for mod, score in cohesion_scores if score < 0.5]
                
                print(f"  Modules analysés    : {len(cohesion_scores)}")
                print(f"  Cohésion moyenne    : {avg_cohesion:.2f}")
                print(f"  Modules < 0.5       : {len(low_cohesion)}")
                
                if low_cohesion:
                    print("  🚨 Faible cohésion:")
                    for module, score in sorted(low_cohesion, key=lambda x: x[1])[:3]:
                        print(f"    - {Path(module).name}: {score:.2f}")
                
                color, status = self.get_status_color(avg_cohesion, 'cohesion', reverse=True)
                print(f"  Status: {color} {status}")
        print()

        # 9. Structure du projet
        print("📂 STRUCTURE")
        print("-" * 40)
        folder_depth = self.get_folder_depth()
        print(f"  Profondeur max      : {folder_depth} niveaux")
        
        color, status = self.get_status_color(folder_depth, 'folder_depth')
        print(f"  Status: {color} {status}")
        print()

        # 10. Informations Git
        print("📈 INFORMATIONS GIT")
        print("-" * 40)
        last_commit, total_commits = self.get_git_info()
        print(f"  Dernier commit      : {last_commit}")
        print(f"  Total commits       : {total_commits}")
        print()

        # 11. Score global et recommandations
        print("💡 DIAGNOSTIC & RECOMMANDATIONS")
        print("-" * 40)
        
        # Calcul du score global pondéré
        scores = []
        weights = []
        
        # Taille du code (poids: 3)
        if file_stats['total']['lines'] <= self.thresholds['lines_total']['green']:
            scores.append(3)
        elif file_stats['total']['lines'] <= self.thresholds['lines_total']['orange']:
            scores.append(2)
        else:
            scores.append(1)
        weights.append(3)
        
        # Complexité (poids: 2)
        if complexity_data:
            avg_complexity = sum(f['complexity'] for f in complexity_data) / len(complexity_data)
            if avg_complexity <= self.thresholds['complexity']['green']:
                scores.append(3)
            elif avg_complexity <= self.thresholds['complexity']['orange']:
                scores.append(2)
            else:
                scores.append(1)
            weights.append(2)
        
        # Tests (poids: 2)
        if coverage >= self.thresholds['test_coverage']['green']:
            scores.append(3)
        elif coverage >= self.thresholds['test_coverage']['orange']:
            scores.append(2)
        else:
            scores.append(1)
        weights.append(2)
        
        # Duplication (poids: 1)
        if duplication_ratio <= self.thresholds['duplicate_ratio']['green']:
            scores.append(3)
        elif duplication_ratio <= self.thresholds['duplicate_ratio']['orange']:
            scores.append(2)
        else:
            scores.append(1)
        weights.append(1)
        
        # Score pondéré
        if scores and weights:
            global_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            global_score = 2.0
        
        if global_score >= 2.7:
            print("  🟢 EXCELLENT - Architecture solide et maintenable")
        elif global_score >= 2.3:
            print("  🟡 CORRECT - Quelques améliorations nécessaires")
        elif global_score >= 1.8:
            print("  🟠 PRÉOCCUPANT - Refactoring fortement recommandé")
        else:
            print("  🔴 CRITIQUE - Refactoring urgent nécessaire")
        
        print(f"  Score global        : {global_score:.2f}/3.0")
        print()
        print("  🎯 Plan d'action prioritaire:")
        
        # Recommandations spécifiques avec priorités
        priority = 1
        if file_stats['total']['lines'] > self.thresholds['lines_total']['red']:
            print(f"    {priority}. 🚨 URGENT: Diviser le projet en modules (>{self.thresholds['lines_total']['red']:,} lignes)")
            priority += 1
        
        if coverage < self.thresholds['test_coverage']['orange']:
            print(f"    {priority}. 🧪 Améliorer la couverture de tests ({coverage:.0f}% < {self.thresholds['test_coverage']['orange']}%)")
            priority += 1
        
        if complexity_data and any(f['complexity'] > 15 for f in complexity_data):
            print(f"    {priority}. 🧮 Simplifier les fonctions complexes (CC > 15)")
            priority += 1
        
        if duplication_ratio > self.thresholds['duplicate_ratio']['orange']:
            print(f"    {priority}. 🔄 Réduire la duplication de code ({duplication_ratio:.1f}%)")
            priority += 1
        
        if responsibilities and len([f for f, d in responsibilities.items() if d['total_elements'] > 10]) > 5:
            print(f"    {priority}. 🎯 Appliquer le principe SRP (trop d'éléments/fichier)")
            priority += 1
        
        print("\n" + "=" * 75)

def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    monitor = AdvancedProjectHealthMonitor(project_path)
    monitor.generate_report()

if __name__ == "__main__":
    main()