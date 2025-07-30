from utilities.environment import EnvConfig

class CustomConfig(EnvConfig):
    """
    Custom configuration class for application environment variables.

    Inherits:
        EnvConfig: Base class that loads and manages environment variables.

    Purpose:
        Extend or override environment configurations if needed for this project.

    Usage:
        You can define additional properties or override methods here if custom environment logic is required.

    Example:
        config = CustomConfig()
        print(config.ENVIRONMENT)
    """

# Global singleton instance for accessing environment configurations throughout the application.
ENVIRONMENT = CustomConfig()
