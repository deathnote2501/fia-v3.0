"""
FIA v3.0 - Plan Validator Service
Pure domain service for validating generated training plans
"""

import logging
import json
from typing import Dict, Any, List, Optional

# Configure logger
logger = logging.getLogger(__name__)


class PlanValidationError(Exception):
    """Exception for plan validation errors"""
    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []


class PlanValidator:
    """Pure domain service for training plan validation"""
    
    # Required stage structure (exact names and order)
    REQUIRED_STAGES = {
        1: "Mise en contexte",
        2: "Acquisition des fondamentaux", 
        3: "Construction progressive",
        4: "Maîtrise",
        5: "Validation"
    }
    
    # Validation constraints
    CONSTRAINTS = {
        "stages_count": 5,
        "max_modules_per_stage": 3,
        "max_submodules_per_module": 4,
        "min_slides_per_submodule": 2,
        "max_slides_per_submodule": 8,
        "min_module_name_length": 5,
        "min_submodule_name_length": 5
    }
    
    def __init__(self):
        """Initialize plan validator"""
        logger.info("✅ PLAN [VALIDATOR] initialized")
    
    def get_json_schema(self) -> Dict[str, Any]:
        """Get strict JSON schema for plan validation"""
        return {
            "type": "object",
            "required": ["training_plan"],
            "properties": {
                "training_plan": {
                    "type": "object",
                    "required": ["stages"],
                    "properties": {
                        "stages": {
                            "type": "array",
                            "minItems": 5,
                            "maxItems": 5,
                            "items": {
                                "type": "object",
                                "required": ["stage_number", "title", "modules"],
                                "properties": {
                                    "stage_number": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 5
                                    },
                                    "title": {
                                        "type": "string",
                                        "enum": list(self.REQUIRED_STAGES.values())
                                    },
                                    "modules": {
                                        "type": "array",
                                        "minItems": 1,
                                        "maxItems": 3,
                                        "items": {
                                            "type": "object",
                                            "required": ["module_name", "submodules"],
                                            "properties": {
                                                "module_name": {
                                                    "type": "string",
                                                    "minLength": 5
                                                },
                                                "submodules": {
                                                    "type": "array",
                                                    "minItems": 1,
                                                    "maxItems": 4,
                                                    "items": {
                                                        "type": "object",
                                                        "required": ["submodule_name", "slide_count", "slide_titles"],
                                                        "properties": {
                                                            "submodule_name": {
                                                                "type": "string",
                                                                "minLength": 5
                                                            },
                                                            "slide_count": {
                                                                "type": "integer",
                                                                "minimum": 2,
                                                                "maximum": 8
                                                            },
                                                            "slide_titles": {
                                                                "type": "array",
                                                                "minItems": 2,
                                                                "maxItems": 8,
                                                                "items": {
                                                                    "type": "string",
                                                                    "minLength": 3
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def validate_basic_structure(self, plan: Dict[str, Any]) -> List[str]:
        """Validate basic JSON structure"""
        errors = []
        
        # Check root structure
        if not isinstance(plan, dict):
            errors.append("Plan must be a dictionary")
            return errors
        
        if "training_plan" not in plan:
            errors.append("Missing 'training_plan' key")
            return errors
        
        training_plan = plan["training_plan"]
        if not isinstance(training_plan, dict):
            errors.append("'training_plan' must be a dictionary")
            return errors
        
        if "stages" not in training_plan:
            errors.append("Missing 'stages' key in training_plan")
            return errors
        
        stages = training_plan["stages"]
        if not isinstance(stages, list):
            errors.append("'stages' must be a list")
            return errors
        
        return errors
    
    def validate_stages_structure(self, stages: List[Dict[str, Any]]) -> List[str]:
        """Validate stages structure and content"""
        errors = []
        
        # Check stages count
        if len(stages) != self.CONSTRAINTS["stages_count"]:
            errors.append(f"Must have exactly {self.CONSTRAINTS['stages_count']} stages, got {len(stages)}")
            return errors
        
        found_stage_numbers = set()
        
        for stage_idx, stage in enumerate(stages):
            if not isinstance(stage, dict):
                errors.append(f"Stage {stage_idx + 1} must be a dictionary")
                continue
            
            # Validate stage_number
            stage_number = stage.get("stage_number")
            if not isinstance(stage_number, int) or stage_number < 1 or stage_number > 5:
                errors.append(f"Stage {stage_idx + 1}: Invalid stage_number '{stage_number}', must be 1-5")
                continue
            
            if stage_number in found_stage_numbers:
                errors.append(f"Duplicate stage_number: {stage_number}")
                continue
            
            found_stage_numbers.add(stage_number)
            
            # Validate stage title
            stage_title = stage.get("title")
            expected_title = self.REQUIRED_STAGES[stage_number]
            if stage_title != expected_title:
                errors.append(f"Stage {stage_number}: Title '{stage_title}' != expected '{expected_title}'")
            
            # Validate modules
            modules_errors = self.validate_modules(stage.get("modules", []), stage_number)
            errors.extend(modules_errors)
        
        # Check for missing stage numbers
        for required_number in self.REQUIRED_STAGES.keys():
            if required_number not in found_stage_numbers:
                errors.append(f"Missing stage_number: {required_number}")
        
        return errors
    
    def validate_modules(self, modules: List[Dict[str, Any]], stage_number: int) -> List[str]:
        """Validate modules within a stage"""
        errors = []
        
        if not isinstance(modules, list):
            errors.append(f"Stage {stage_number}: 'modules' must be a list")
            return errors
        
        if len(modules) == 0:
            errors.append(f"Stage {stage_number}: Must have at least 1 module")
            return errors
        
        if len(modules) > self.CONSTRAINTS["max_modules_per_stage"]:
            errors.append(f"Stage {stage_number}: Cannot have more than {self.CONSTRAINTS['max_modules_per_stage']} modules")
            return errors
        
        for module_idx, module in enumerate(modules):
            if not isinstance(module, dict):
                errors.append(f"Stage {stage_number}, Module {module_idx + 1}: Must be a dictionary")
                continue
            
            # Validate module_name
            module_name = module.get("module_name")
            if not isinstance(module_name, str):
                errors.append(f"Stage {stage_number}, Module {module_idx + 1}: 'module_name' must be a string")
                continue
            
            if len(module_name) < self.CONSTRAINTS["min_module_name_length"]:
                errors.append(f"Stage {stage_number}, Module {module_idx + 1}: Module name too short (min {self.CONSTRAINTS['min_module_name_length']} chars)")
            
            # Validate submodules
            submodules_errors = self.validate_submodules(
                module.get("submodules", []), 
                stage_number, 
                module_idx + 1
            )
            errors.extend(submodules_errors)
        
        return errors
    
    def validate_submodules(self, submodules: List[Dict[str, Any]], stage_number: int, module_number: int) -> List[str]:
        """Validate submodules within a module"""
        errors = []
        
        if not isinstance(submodules, list):
            errors.append(f"Stage {stage_number}, Module {module_number}: 'submodules' must be a list")
            return errors
        
        if len(submodules) == 0:
            errors.append(f"Stage {stage_number}, Module {module_number}: Must have at least 1 submodule")
            return errors
        
        if len(submodules) > self.CONSTRAINTS["max_submodules_per_module"]:
            errors.append(f"Stage {stage_number}, Module {module_number}: Cannot have more than {self.CONSTRAINTS['max_submodules_per_module']} submodules")
            return errors
        
        for sub_idx, submodule in enumerate(submodules):
            if not isinstance(submodule, dict):
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: Must be a dictionary")
                continue
            
            # Validate submodule_name
            submodule_name = submodule.get("submodule_name")
            if not isinstance(submodule_name, str):
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: 'submodule_name' must be a string")
                continue
            
            if len(submodule_name) < self.CONSTRAINTS["min_submodule_name_length"]:
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: Submodule name too short")
            
            # Validate slide_count
            slide_count = submodule.get("slide_count")
            if not isinstance(slide_count, int):
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: 'slide_count' must be an integer")
                continue
            
            if slide_count < self.CONSTRAINTS["min_slides_per_submodule"] or slide_count > self.CONSTRAINTS["max_slides_per_submodule"]:
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: slide_count must be {self.CONSTRAINTS['min_slides_per_submodule']}-{self.CONSTRAINTS['max_slides_per_submodule']}")
            
            # Validate slide_titles
            slide_titles = submodule.get("slide_titles")
            if not isinstance(slide_titles, list):
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: 'slide_titles' must be a list")
                continue
            
            if len(slide_titles) != slide_count:
                errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}: slide_titles length ({len(slide_titles)}) != slide_count ({slide_count})")
            
            # Validate each slide title
            for title_idx, title in enumerate(slide_titles):
                if not isinstance(title, str):
                    errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}, Slide {title_idx + 1}: Title must be a string")
                elif len(title.strip()) < 3:
                    errors.append(f"Stage {stage_number}, Module {module_number}, Submodule {sub_idx + 1}, Slide {title_idx + 1}: Title too short")
        
        return errors
    
    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate complete training plan structure
        
        Args:
            plan: Generated plan to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            PlanValidationError: If validation fails with detailed errors
        """
        logger.info("🔍 PLAN [VALIDATION] Starting validation...")
        
        all_errors = []
        
        # Basic structure validation
        basic_errors = self.validate_basic_structure(plan)
        all_errors.extend(basic_errors)
        
        if basic_errors:
            logger.error(f"❌ PLAN [VALIDATION] Basic structure errors: {basic_errors}")
            raise PlanValidationError("Basic structure validation failed", all_errors)
        
        # Stages validation
        stages = plan["training_plan"]["stages"]
        stages_errors = self.validate_stages_structure(stages)
        all_errors.extend(stages_errors)
        
        if all_errors:
            logger.error(f"❌ PLAN [VALIDATION] {len(all_errors)} errors found")
            for error in all_errors[:5]:  # Log first 5 errors
                logger.error(f"  - {error}")
            
            raise PlanValidationError("Plan validation failed", all_errors)
        
        logger.info("✅ PLAN [VALIDATION] Success - Plan is valid")
        return True
    
    def validate_and_fix_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate plan and attempt basic fixes
        
        Args:
            plan: Plan to validate and fix
            
        Returns:
            Fixed plan if possible
            
        Raises:
            PlanValidationError: If plan cannot be fixed
        """
        try:
            # Try validation first
            if self.validate_plan(plan):
                return plan
        except PlanValidationError as e:
            logger.info(f"🔧 PLAN [FIXING] Attempting to fix {len(e.validation_errors)} errors...")
            
            # Attempt basic fixes
            fixed_plan = self._attempt_basic_fixes(plan, e.validation_errors)
            
            # Validate fixed plan
            if self.validate_plan(fixed_plan):
                logger.info("✅ PLAN [FIXING] Successfully fixed plan")
                return fixed_plan
            else:
                raise PlanValidationError("Could not fix plan validation errors", e.validation_errors)
    
    def _attempt_basic_fixes(self, plan: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Attempt to fix basic validation errors"""
        # This is a simplified fix attempt - in practice, more sophisticated fixes could be implemented
        fixed_plan = json.loads(json.dumps(plan))  # Deep copy
        
        # Example: Fix missing slide_titles by generating placeholder titles
        try:
            stages = fixed_plan.get("training_plan", {}).get("stages", [])
            for stage in stages:
                for module in stage.get("modules", []):
                    for submodule in module.get("submodules", []):
                        slide_count = submodule.get("slide_count", 0)
                        slide_titles = submodule.get("slide_titles", [])
                        
                        # Fix slide_titles count mismatch
                        if len(slide_titles) != slide_count:
                            if len(slide_titles) < slide_count:
                                # Add missing titles
                                for i in range(len(slide_titles), slide_count):
                                    slide_titles.append(f"Slide {i + 1} - {submodule.get('submodule_name', 'Contenu')}")
                            else:
                                # Remove excess titles
                                slide_titles = slide_titles[:slide_count]
                            
                            submodule["slide_titles"] = slide_titles
        except Exception as e:
            logger.warning(f"⚠️ PLAN [FIXING] Error during fix attempt: {e}")
        
        return fixed_plan
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation configuration and statistics"""
        return {
            "constraints": self.CONSTRAINTS.copy(),
            "required_stages": self.REQUIRED_STAGES.copy(),
            "schema_available": True
        }