"""
Environment Variable Validation for StocksBlitz Platform
Validates required environment variables and ensures secure configuration.
"""

import os
import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """Security levels for environment variables"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EnvVarRule:
    """Rule for validating environment variables"""
    name: str
    required: bool = True
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    description: str = ""


class EnvironmentValidator:
    """Validates environment variables for security and correctness"""
    
    # Common insecure patterns
    INSECURE_PATTERNS = {
        'weak_password': r'^(password|123456|admin|test|secret|default)$',
        'placeholder': r'^(your_|replace_|change_|example_|test_)',
        'simple_pattern': r'^[a-zA-Z0-9]{1,8}$',
        'sequential': r'^(123|abc|qwe)',
        'repeated': r'^(.)\1{3,}$',
    }
    
    # Service-specific validation rules
    VALIDATION_RULES = {
        'database': [
            EnvVarRule(
                name='POSTGRES_PASSWORD',
                required=True,
                security_level=SecurityLevel.CRITICAL,
                min_length=16,
                description='PostgreSQL/TimescaleDB password'
            ),
            EnvVarRule(
                name='POSTGRES_USER',
                required=True,
                security_level=SecurityLevel.MEDIUM,
                min_length=3,
                description='PostgreSQL/TimescaleDB username'
            ),
            EnvVarRule(
                name='POSTGRES_DB',
                required=True,
                security_level=SecurityLevel.LOW,
                min_length=3,
                description='PostgreSQL/TimescaleDB database name'
            ),
        ],
        'redis': [
            EnvVarRule(
                name='REDIS_PASSWORD',
                required=True,
                security_level=SecurityLevel.CRITICAL,
                min_length=16,
                description='Redis cluster authentication password'
            ),
            EnvVarRule(
                name='REDIS_HOST',
                required=True,
                security_level=SecurityLevel.MEDIUM,
                description='Redis host/proxy address'
            ),
            EnvVarRule(
                name='REDIS_PORT',
                required=True,
                security_level=SecurityLevel.LOW,
                pattern=r'^\d{1,5}$',
                description='Redis port number'
            ),
        ],
        'jwt': [
            EnvVarRule(
                name='JWT_SECRET_KEY',
                required=True,
                security_level=SecurityLevel.CRITICAL,
                min_length=32,
                description='JWT token signing secret'
            ),
            EnvVarRule(
                name='JWT_REFRESH_SECRET',
                required=False,
                security_level=SecurityLevel.CRITICAL,
                min_length=32,
                description='JWT refresh token signing secret'
            ),
        ],
        'services': [
            EnvVarRule(
                name='USER_SERVICE_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='User service internal secret'
            ),
            EnvVarRule(
                name='TRADE_SERVICE_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='Trade service internal secret'
            ),
            EnvVarRule(
                name='TICKER_SERVICE_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='Ticker service internal secret'
            ),
            EnvVarRule(
                name='SIGNAL_SERVICE_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='Signal service internal secret'
            ),
            EnvVarRule(
                name='SUBSCRIPTION_SERVICE_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='Subscription service internal secret'
            ),
        ],
        'encryption': [
            EnvVarRule(
                name='ENCRYPTION_KEY',
                required=False,
                security_level=SecurityLevel.CRITICAL,
                min_length=32,
                description='Data encryption key'
            ),
            EnvVarRule(
                name='SESSION_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='Session encryption secret'
            ),
        ],
        'api': [
            EnvVarRule(
                name='INTERNAL_API_KEY',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=24,
                description='Internal API authentication key'
            ),
            EnvVarRule(
                name='WEBHOOK_SECRET',
                required=False,
                security_level=SecurityLevel.HIGH,
                min_length=16,
                description='Webhook validation secret'
            ),
        ]
    }
    
    def __init__(self):
        self.warnings = []
        self.errors = []
        self.security_issues = []
    
    def validate_environment(self, service_name: str = None, categories: List[str] = None) -> Dict:
        """
        Validate environment variables for a service or categories
        
        Args:
            service_name: Name of the service (for logging)
            categories: List of categories to validate (database, redis, jwt, etc.)
        
        Returns:
            Dictionary with validation results
        """
        self.warnings.clear()
        self.errors.clear()
        self.security_issues.clear()
        
        # Default to all categories if none specified
        if not categories:
            categories = list(self.VALIDATION_RULES.keys())
        
        validated_vars = {}
        
        for category in categories:
            if category not in self.VALIDATION_RULES:
                continue
                
            for rule in self.VALIDATION_RULES[category]:
                result = self._validate_single_var(rule)
                validated_vars[rule.name] = result
        
        return {
            'service': service_name,
            'validated_vars': validated_vars,
            'warnings': self.warnings,
            'errors': self.errors,
            'security_issues': self.security_issues,
            'is_valid': len(self.errors) == 0,
            'is_secure': len(self.security_issues) == 0
        }
    
    def _validate_single_var(self, rule: EnvVarRule) -> Dict:
        """Validate a single environment variable"""
        value = os.getenv(rule.name)
        result = {
            'name': rule.name,
            'exists': value is not None,
            'value_length': len(value) if value else 0,
            'security_level': rule.security_level.value,
            'is_valid': True,
            'is_secure': True,
            'issues': []
        }
        
        # Check if required variable exists
        if rule.required and not value:
            self.errors.append(f"Required environment variable '{rule.name}' is not set")
            result['is_valid'] = False
            result['issues'].append('missing_required')
            return result
        
        # Skip further validation if variable doesn't exist and isn't required
        if not value:
            return result
        
        # Length validation
        if rule.min_length and len(value) < rule.min_length:
            self.security_issues.append(f"'{rule.name}' is too short (min: {rule.min_length})")
            result['is_secure'] = False
            result['issues'].append('too_short')
        
        if rule.max_length and len(value) > rule.max_length:
            self.warnings.append(f"'{rule.name}' is very long (max recommended: {rule.max_length})")
            result['issues'].append('too_long')
        
        # Pattern validation
        if rule.pattern and not re.match(rule.pattern, value):
            self.errors.append(f"'{rule.name}' does not match required pattern")
            result['is_valid'] = False
            result['issues'].append('pattern_mismatch')
        
        # Allowed values validation
        if rule.allowed_values and value not in rule.allowed_values:
            self.errors.append(f"'{rule.name}' has invalid value (allowed: {rule.allowed_values})")
            result['is_valid'] = False
            result['issues'].append('invalid_value')
        
        # Security pattern validation
        self._check_security_patterns(rule.name, value, result)
        
        return result
    
    def _check_security_patterns(self, var_name: str, value: str, result: Dict):
        """Check for common security anti-patterns"""
        value_lower = value.lower()
        
        for pattern_name, pattern in self.INSECURE_PATTERNS.items():
            if re.search(pattern, value_lower):
                self.security_issues.append(f"'{var_name}' contains insecure pattern: {pattern_name}")
                result['is_secure'] = False
                result['issues'].append(f'insecure_{pattern_name}')
        
        # Check for common weak passwords
        if any(weak in value_lower for weak in ['password', 'admin', 'test', 'secret', 'default']):
            self.security_issues.append(f"'{var_name}' appears to use a weak/default value")
            result['is_secure'] = False
            result['issues'].append('weak_value')
    
    def print_validation_report(self, validation_result: Dict):
        """Print a formatted validation report"""
        service = validation_result.get('service', 'Unknown')
        print(f"\n🔐 Security Validation Report for {service}")
        print("=" * 60)
        
        # Summary
        is_valid = validation_result['is_valid']
        is_secure = validation_result['is_secure']
        
        if is_valid and is_secure:
            print("✅ All environment variables are valid and secure")
        elif is_valid:
            print("⚠️  Environment variables are valid but have security concerns")
        else:
            print("❌ Environment variables have validation errors")
        
        # Errors
        if validation_result['errors']:
            print(f"\n❌ Errors ({len(validation_result['errors'])}):")
            for error in validation_result['errors']:
                print(f"   • {error}")
        
        # Security Issues
        if validation_result['security_issues']:
            print(f"\n⚠️  Security Issues ({len(validation_result['security_issues'])}):")
            for issue in validation_result['security_issues']:
                print(f"   • {issue}")
        
        # Warnings
        if validation_result['warnings']:
            print(f"\n⚡ Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result['warnings']:
                print(f"   • {warning}")
        
        print()


def validate_service_environment(service_name: str, categories: List[str] = None) -> Dict:
    """
    Convenience function to validate environment for a specific service
    
    Args:
        service_name: Name of the service
        categories: List of categories to validate
    
    Returns:
        Validation results dictionary
    """
    validator = EnvironmentValidator()
    return validator.validate_environment(service_name, categories)


if __name__ == "__main__":
    # Example usage
    validator = EnvironmentValidator()
    
    # Validate all categories
    result = validator.validate_environment("StocksBlitz Platform")
    validator.print_validation_report(result)