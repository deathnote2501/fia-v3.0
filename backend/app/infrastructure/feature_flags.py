"""
FIA v3.0 - Feature Flags for Safe Refactoring
Allows progressive activation of refactored components without breaking production
"""

import os
from typing import Optional


class FeatureFlags:
    """
    Feature flags for safe incremental refactoring.
    
    Usage:
        if FeatureFlags.NEW_NAMING_CONVENTION:
            # Use refactored code with English naming
        else:
            # Use legacy code (fallback)
    """
    
    # Phase 1: Safe changes (0% risk)
    NEW_NAMING_CONVENTION: bool = os.getenv('FEATURE_NEW_NAMING', 'false').lower() == 'true'
    NEW_PAGINATION: bool = os.getenv('FEATURE_NEW_PAGINATION', 'false').lower() == 'true'
    NEW_DATABASE_INDEXES: bool = os.getenv('FEATURE_NEW_DB_INDEXES', 'false').lower() == 'true'
    
    # Phase 2: Moderate changes (15% risk)
    NEW_DOMAIN_STRUCTURE: bool = os.getenv('FEATURE_NEW_DOMAIN', 'false').lower() == 'true'
    NEW_PORTS_ADAPTERS: bool = os.getenv('FEATURE_NEW_PORTS', 'false').lower() == 'true'
    
    # Phase 3: Risky changes (40-95% risk)
    NEW_SERVICES_STRUCTURE: bool = os.getenv('FEATURE_NEW_SERVICES', 'false').lower() == 'true'
    NEW_CONTROLLERS_STRUCTURE: bool = os.getenv('FEATURE_NEW_CONTROLLERS', 'false').lower() == 'true'
    
    # Emergency flags
    DISABLE_ALL_REFACTORING: bool = os.getenv('EMERGENCY_DISABLE_REFACTOR', 'false').lower() == 'true'
    
    @classmethod
    def is_refactoring_enabled(cls, flag_name: str) -> bool:
        """
        Check if a specific refactoring feature is enabled.
        Returns False if emergency disable is active.
        
        Args:
            flag_name: Name of the feature flag attribute
            
        Returns:
            bool: True if feature is enabled and not emergency disabled
        """
        if cls.DISABLE_ALL_REFACTORING:
            return False
            
        return getattr(cls, flag_name, False)
    
    @classmethod
    def get_active_flags(cls) -> dict:
        """
        Get all currently active feature flags.
        
        Returns:
            dict: Dictionary of active flag names and their values
        """
        active_flags = {}
        
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                value = getattr(cls, attr_name)
                if isinstance(value, bool) and value:
                    active_flags[attr_name] = value
                    
        return active_flags
    
    @classmethod
    def get_phase_status(cls) -> dict:
        """
        Get refactoring phase status.
        
        Returns:
            dict: Status of each refactoring phase
        """
        return {
            "phase1_safe": {
                "naming": cls.NEW_NAMING_CONVENTION,
                "pagination": cls.NEW_PAGINATION,
                "indexes": cls.NEW_DATABASE_INDEXES
            },
            "phase2_moderate": {
                "domain": cls.NEW_DOMAIN_STRUCTURE,
                "ports": cls.NEW_PORTS_ADAPTERS
            },
            "phase3_risky": {
                "services": cls.NEW_SERVICES_STRUCTURE,
                "controllers": cls.NEW_CONTROLLERS_STRUCTURE
            },
            "emergency": {
                "all_disabled": cls.DISABLE_ALL_REFACTORING
            }
        }


# Convenience functions for common checks
def is_safe_refactoring_enabled() -> bool:
    """Check if any Phase 1 (safe) refactoring is enabled"""
    return any([
        FeatureFlags.NEW_NAMING_CONVENTION,
        FeatureFlags.NEW_PAGINATION,
        FeatureFlags.NEW_DATABASE_INDEXES
    ]) and not FeatureFlags.DISABLE_ALL_REFACTORING


def is_risky_refactoring_enabled() -> bool:
    """Check if any Phase 3 (risky) refactoring is enabled"""
    return any([
        FeatureFlags.NEW_SERVICES_STRUCTURE,
        FeatureFlags.NEW_CONTROLLERS_STRUCTURE
    ]) and not FeatureFlags.DISABLE_ALL_REFACTORING


# Environment variable documentation
ENVIRONMENT_VARIABLES = {
    "FEATURE_NEW_NAMING": "Enable new English naming conventions (Phase 1)",
    "FEATURE_NEW_PAGINATION": "Enable repository pagination (Phase 1)",
    "FEATURE_NEW_DB_INDEXES": "Enable new database indexes (Phase 1)",
    "FEATURE_NEW_DOMAIN": "Enable new domain structure (Phase 2)",
    "FEATURE_NEW_PORTS": "Enable new ports/adapters (Phase 2)",
    "FEATURE_NEW_SERVICES": "Enable new services structure (Phase 3)",
    "FEATURE_NEW_CONTROLLERS": "Enable new controllers structure (Phase 3)",
    "EMERGENCY_DISABLE_REFACTOR": "Emergency disable all refactoring features"
}