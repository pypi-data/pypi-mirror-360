# Initialize diagram-to-iac package with centralized configuration and secret management

# Initialize configuration system first
try:
    from diagram_to_iac.core.config_loader import get_config_loader
    # Initialize the global configuration loader
    config_loader = get_config_loader()
    # Pre-load configuration to catch any issues early
    config = config_loader.get_config()
except ImportError as e:
    # If config_loader can't be imported, log but continue
    print(f"⚠️ Warning: Could not import configuration system: {e}")
except Exception as e:
    # If configuration loading fails, log but continue
    print(f"⚠️ Warning: Configuration system initialization failed: {e}")

# Initialize secret management system
try:
    from diagram_to_iac.tools.sec_utils import load_secrets
    load_secrets()
except ImportError:
    # If sec_utils can't be imported, that's fine during development
    pass
except SystemExit:
    # load_secrets() calls sys.exit() on critical errors
    # In development, we don't want to crash the entire package import
    pass
except Exception as e:
    print(f"⚠️ Warning: Secret management initialization failed: {e}")

# Make configuration easily accessible
try:
    from diagram_to_iac.core.config_loader import get_config, get_config_section, get_config_value
    __all__ = ["get_config", "get_config_section", "get_config_value"]
except ImportError:
    __all__ = []
