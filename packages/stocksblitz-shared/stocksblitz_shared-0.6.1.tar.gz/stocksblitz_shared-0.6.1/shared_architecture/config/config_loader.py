import os
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Enhanced configuration loader that integrates with the hierarchical
    configuration system while maintaining backward compatibility.
    """
    
    def __init__(self):
        self._config_manager = None
        self._loaded_service = None
        self.env_config = dict(os.environ)
        
    def _get_config_manager(self):
        """Get or create configuration manager instance"""
        if self._config_manager is None:
            try:
                from infrastructure.config.config_manager import get_configuration_manager
                self._config_manager = get_configuration_manager()
                
                # Auto-load environment if ENVIRONMENT is set
                environment = os.getenv("ENVIRONMENT", "development")
                if not self._config_manager._loaded:
                    self._config_manager.load_environment(environment)
                    logger.info(f"Auto-loaded configuration for environment: {environment}")
                    
            except ImportError:
                logger.warning("New configuration system not available, falling back to legacy")
                self._config_manager = None
        
        return self._config_manager

    def load(self, service_name: str):
        """
        Load configuration for a specific service.
        Now uses the hierarchical configuration system.
        """
        self._loaded_service = service_name
        
        config_manager = self._get_config_manager()
        if config_manager:
            # Use new configuration system
            logger.debug(f"Using new configuration system for service: {service_name}")
            return
        
        # Fallback to legacy YAML-based system (for backward compatibility)
        logger.warning("Using legacy configuration system")
        self._load_legacy_yaml(service_name)
    
    def _load_legacy_yaml(self, service_name: str):
        """Legacy YAML configuration loading (for backward compatibility)"""
        base_path = "/app/configmaps" if os.path.exists("/app/configmaps") else "/home/stocksadmin/stocksblitz/configmaps"
        
        # Legacy implementation preserved for compatibility
        paths = {
            "common": f"{base_path}/common-config.yaml",
            "shared": f"{base_path}/shared-config.yaml", 
            "private": f"{base_path}/{service_name}-config.yaml",
        }
        
        self.common_config = {}
        self.shared_config = {}
        self.private_config = {}
        
        for name, path in paths.items():
            if os.path.exists(path):
                try:
                    import yaml
                    with open(path, "r") as f:
                        data = yaml.safe_load(f) or {}
                        if name == "common":
                            self.common_config.update(data)
                        elif name == "shared":
                            self.shared_config.update(data)
                        elif name == "private":
                            self.private_config.update(data)
                except Exception as e:
                    logger.error(f"Failed to load legacy config file {path}: {e}")

    def get(self, key: str, default: Optional[Any] = None, scope: str = "all") -> Any:
        """
        Get configuration value with hierarchical precedence.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            scope: Configuration scope (private, shared, common, all)
            
        Returns:
            Configuration value
        """
        config_manager = self._get_config_manager()
        
        if config_manager and config_manager._loaded:
            # Use new configuration system
            return config_manager.get(key, default)
        
        # Fallback to legacy system
        if scope == "private":
            return getattr(self, 'private_config', {}).get(key, self.env_config.get(key, default))
        elif scope == "shared":
            return getattr(self, 'shared_config', {}).get(key, self.env_config.get(key, default))
        elif scope == "common":
            return getattr(self, 'common_config', {}).get(key, self.env_config.get(key, default))
        elif scope == "all":
            # Check in order of precedence: private -> shared -> common -> env -> default
            return (
                getattr(self, 'private_config', {}).get(key) or
                getattr(self, 'shared_config', {}).get(key) or
                getattr(self, 'common_config', {}).get(key) or
                self.env_config.get(key, default)
            )
        else:
            return default
    
    def get_config_for_service(self, service_name: str) -> Dict[str, Any]:
        """
        Get all configuration parameters for a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dictionary of service configuration
        """
        config_manager = self._get_config_manager()
        
        if config_manager and config_manager._loaded:
            # Use new configuration system
            return config_manager.get_service_config(service_name)
        
        # Fallback: return environment variables with service prefix
        service_prefix = f"{service_name.upper()}_"
        service_config = {}
        
        for key, value in self.env_config.items():
            if key.startswith(service_prefix):
                config_key = key[len(service_prefix):]
                service_config[config_key] = value
        
        return service_config


# Global singleton – should be used only *after* .load(service_name) is called
config_loader = ConfigLoader()

# Compatibility function for backward compatibility
def get_env(key: str, default: Optional[Any] = None) -> Any:
    """Backward compatibility wrapper for get_env function"""
    return config_loader.get(key, default, scope="all")
