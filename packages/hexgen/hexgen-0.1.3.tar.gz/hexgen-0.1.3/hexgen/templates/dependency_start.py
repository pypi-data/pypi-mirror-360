from utilities.depency_injections.injection_manager import InjectionManager


def start__dependencies():
    """
    Initializes and registers all Account-related dependencies in the application's dependency injection container.

    This function should be called during the application startup phase.

    Responsibilities:
    - Configure global utility injections (e.g., logging, env vars, etc.).
    - Register repository, service, and use case dependencies for the Account domain.

    Registered Dependencies:
        - AccountRepository: Provides access to Firestore for Account entities.
        - AccountService: Contains business logic for account management.
        - AccountUseCase: Coordinates application-level logic for account operations.

    Usage:
        Call this function once at application startup (e.g., in your main.py or app entrypoint).

    Example:
        start_account_dependencies()
    """
    key="key_for_cache_gateway_io"
    value="key_for_cache_gateway_io"
    InjectionManager.add_dependency(
        key=key,
        value=value
    )
