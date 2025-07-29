"""
Configuration models and loading for Hydra-Logger.

This module defines comprehensive Pydantic models and utility functions for
configuring the Hydra-Logger system. It provides a robust, type-safe configuration
system that supports complex logging scenarios for enterprise applications.

Key Features:
- Pydantic-based configuration models with automatic validation
- Multi-layered logging with custom folder paths for each layer
- Multiple destinations per layer (file, console) with independent configurations
- YAML and TOML configuration file loading with error handling
- Automatic directory creation for custom log file paths
- Comprehensive validation of log levels, file paths, and configuration structure
- Default configuration generation for quick setup

The configuration system enables sophisticated logging setups where different
modules can log to different destinations with custom folder structures,
file rotation settings, and log level filtering.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Type, Union

import yaml
from pydantic import BaseModel, Field, ValidationInfo, field_validator

if TYPE_CHECKING:
    import types

    tomllib: Any
    TOMLDecodeError: Type[BaseException]
else:
    try:
        import tomllib  # type: ignore

        TOMLDecodeError = tomllib.TOMLDecodeError  # type: ignore
    except ImportError:
        import tomli as tomllib  # type: ignore

        TOMLDecodeError = tomllib.TOMLDecodeError  # type: ignore
    except AttributeError:
        TOMLDecodeError = Exception


class LogDestination(BaseModel):
    """
    Configuration for a single log destination (file or console).

    This model defines the configuration for individual logging destinations,
    supporting both file and console output with customizable settings including
    log levels, file paths, rotation settings, and backup counts.

    Attributes:
        type (Literal["file", "console"]): Type of destination (file or console).
        level (str): Logging level for this destination (default: "INFO").
        path (Optional[str]): File path, required for file destinations.
        max_size (Optional[str]): Maximum file size for rotation (e.g., '5MB',
            '1GB').
        backup_count (Optional[int]): Number of backup files to keep (default: 3).
        format (str): Log format: 'text', 'json', 'csv', 'syslog', or 'gelf'
            (default: 'text').

    The model includes comprehensive validation to ensure that file destinations
    have required paths and that log levels are valid.
    """

    type: Literal["file", "console"] = Field(description="Type of destination")
    level: str = Field(default="INFO", description="Logging level for this destination")
    path: Optional[str] = Field(
        default=None, description="File path (required for file type)"
    )
    max_size: Optional[str] = Field(
        default="5MB",
        description=("Max file size for rotation. " "E.g. '5MB', '1GB'."),
    )
    backup_count: Optional[int] = Field(default=3, description="Number of backup files")
    format: str = Field(
        default="text",
        description=("Log format: 'text', 'json', 'csv', 'syslog', or 'gelf'"),
    )

    @field_validator("path")
    @classmethod
    def validate_file_path(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """
        Ensure that file destinations have a path specified.

        Args:
            v (Optional[str]): The path value to validate.
            info (ValidationInfo): Validation context information.

        Returns:
            Optional[str]: The validated path value.

        Raises:
            ValueError: If a file destination is missing a required path.

        This validator ensures that file-type destinations have a valid path
        specified, preventing configuration errors that would cause logging
        failures at runtime.
        """
        if info.data and info.data.get("type") == "file" and not v:
            raise ValueError("Path is required for file destinations")
        return v

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization validation for file destinations.

        Args:
            __context (Any): Post-init context (unused).

        Raises:
            ValueError: If a file destination is missing a required path.

        This method provides additional validation after model initialization
        to ensure that file destinations have the required path configuration.
        """
        if self.type == "file" and not self.path:
            raise ValueError("Path is required for file destinations")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """
        Validate that the logging level is one of the allowed values.

        Args:
            v (str): The log level value to validate.

        Returns:
            str: The normalized (uppercase) log level.

        Raises:
            ValueError: If the log level is not one of the valid options.

        This validator ensures that only valid Python logging levels are used
        and normalizes them to uppercase for consistency.
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """
        Validate that the log format is one of the supported formats.

        Args:
            v (str): The format value to validate.

        Returns:
            str: The normalized (lowercase) format.

        Raises:
            ValueError: If the format is not one of the valid options.
        """
        valid_formats = ["text", "json", "csv", "syslog", "gelf"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid format: {v}. Must be one of {valid_formats}")
        return v.lower()


class LogLayer(BaseModel):
    """
    Configuration for a single logging layer.

    This model defines the configuration for a logging layer, which can contain
    multiple destinations (files, console) with different log levels and settings.
    Each layer represents a logical grouping of logging output, such as different
    modules or types of logs in an application.

    Attributes:
        level (str): Default logging level for this layer (default: "INFO").
        destinations (List[LogDestination]): List of destinations for this layer.

    A layer can have multiple destinations, allowing logs to be written to
    multiple files and/or console output simultaneously with different
    configurations for each destination.
    """

    level: str = Field(default="INFO", description="Default level for this layer")
    destinations: List[LogDestination] = Field(
        default_factory=list, description="List of destinations"
    )

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """
        Validate that the logging level is one of the allowed values.

        Args:
            v (str): The log level value to validate.

        Returns:
            str: The normalized (uppercase) log level.

        Raises:
            ValueError: If the log level is not one of the valid options.

        This validator ensures that layer log levels are valid and consistent
        with Python's standard logging levels.
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid level: {v}. Must be one of {valid_levels}")
        return v.upper()


class LoggingConfig(BaseModel):
    """
    Main configuration for Hydra-Logger.

    This is the root configuration model that defines the complete logging
    setup for an application. It contains multiple layers, each with their
    own destinations and settings, enabling sophisticated multi-layered
    logging configurations.

    Attributes:
        layers (Dict[str, LogLayer]): Dictionary of logging layers by name.
        default_level (str): Default logging level for all layers (default: "INFO").

    The configuration supports complex scenarios where different parts of an
    application can log to different destinations with custom folder structures,
    file rotation settings, and log level filtering.
    """

    layers: Dict[str, LogLayer] = Field(
        default_factory=dict, description="Logging layers configuration"
    )
    default_level: str = Field(default="INFO", description="Default logging level")

    @field_validator("default_level")
    @classmethod
    def validate_default_level(cls, v: str) -> str:
        """
        Validate that the default logging level is one of the allowed values.

        Args:
            v (str): The default log level value to validate.

        Returns:
            str: The normalized (uppercase) log level.

        Raises:
            ValueError: If the default log level is not one of the valid options.

        This validator ensures that the default log level is valid and provides
        a fallback for layers that don't specify their own level.
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(
                f"Invalid default_level: {v}. Must be one of {valid_levels}"
            )
        return v.upper()


def load_config(config_path: Union[str, Path]) -> LoggingConfig:
    """
    Load configuration from a YAML or TOML file.

    This function provides a convenient way to load Hydra-Logger configurations
    from external files, supporting both YAML and TOML formats. It includes
    comprehensive error handling and validation to ensure that loaded
    configurations are valid and complete.

    Args:
        config_path (Union[str, Path]): Path to the configuration file.

    Returns:
        LoggingConfig: Fully validated configuration instance loaded from file.

    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        ValueError: If the file format is unsupported, empty, or invalid.
        yaml.YAMLError: If YAML parsing fails due to syntax errors.
        Exception: If TOML parsing fails due to syntax errors.

    The function automatically detects the file format based on the file extension
    and applies appropriate parsing. It validates the loaded configuration using
    Pydantic's validation system to ensure all required fields are present and
    values are within acceptable ranges.

    Example:
        >>> config = load_config("logging_config.yaml")
        >>> logger = HydraLogger(config)
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    try:
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".toml":
            try:
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
            except Exception as e:
                raise ValueError(f"Failed to parse TOML configuration file: {e}") from e
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        if config_data is None:
            raise ValueError("Configuration file is empty or invalid")
        return LoggingConfig(**config_data)
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML configuration file: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}") from e


def get_default_config() -> LoggingConfig:
    """
    Get default configuration with basic setup.

    This function provides a sensible default configuration that includes
    a DEFAULT layer with both file and console destinations. It's useful
    for quick setup or as a starting point for custom configurations.

    Returns:
        LoggingConfig: Default configuration with a DEFAULT layer containing:
        - File destination: logs/app.log with 5MB rotation and 3 backups
        - Console destination: INFO level output
        - Default level: INFO for all layers

    The default configuration provides a good starting point for most
    applications and can be easily extended with additional layers
    and destinations as needed.

    Example:
        >>> config = get_default_config()
        >>> logger = HydraLogger(config)
    """
    return LoggingConfig(
        layers={
            "DEFAULT": LogLayer(
                level="INFO",
                destinations=[
                    LogDestination(
                        type="file", path="logs/app.log", max_size="5MB", backup_count=3
                    ),
                    LogDestination(type="console", level="INFO"),
                ],
            )
        },
        default_level="INFO",
    )


def create_log_directories(config: LoggingConfig) -> None:
    """
    Create log directories for all file destinations in the configuration.

    This function automatically creates all necessary directories for file-based
    log destinations in the configuration. It ensures that the logging system
    can write to the specified file paths without encountering directory-related
    errors at runtime.

    Args:
        config (LoggingConfig): LoggingConfig instance containing layer and
            destination information.

    Raises:
        OSError: If directory creation fails due to permission issues, disk
            space problems, or other filesystem-related errors.

    The function iterates through all layers and their destinations, creating
    directories for any file-based destinations. It uses os.makedirs with
    exist_ok=True to handle cases where directories already exist gracefully.

    Example:
        >>> config = load_config("logging_config.yaml")
        >>> create_log_directories(config)  # Creates all necessary directories
        >>> logger = HydraLogger(config)
    """
    for layer_name, layer_config in config.layers.items():
        for destination in layer_config.destinations:
            if destination.type == "file" and destination.path:
                # Extract directory from file path
                log_dir = os.path.dirname(destination.path)
                if log_dir:
                    try:
                        os.makedirs(log_dir, exist_ok=True)
                    except OSError as e:
                        raise OSError(
                            f"Failed to create log directory '{log_dir}' "
                            f"for layer '{layer_name}': {e}"
                        ) from e
