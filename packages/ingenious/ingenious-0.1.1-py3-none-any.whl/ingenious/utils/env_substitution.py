"""
Environment variable substitution utility for YAML configuration files.

This module provides functionality to replace environment variable placeholders
in YAML content with actual environment variable values using the syntax:
${VAR_NAME:default_value} or ${VAR_NAME}
"""

import os
import re


def substitute_env_vars(content: str) -> str:
    """
    Substitute environment variables in a string using ${VAR_NAME:default} syntax.

    Args:
        content: String content containing environment variable placeholders

    Returns:
        String with environment variables substituted

    Examples:
        >>> os.environ['MY_VAR'] = 'test_value'
        >>> substitute_env_vars('${MY_VAR:default}')
        'test_value'
        >>> substitute_env_vars('${MISSING_VAR:default}')
        'default'
    """

    def replace_var(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) is not None else ""
        return os.getenv(var_name, default_value)

    # Pattern matches ${VAR_NAME:default} or ${VAR_NAME}
    pattern = r"\$\{([^}:]+)(?::([^}]*))?\}"
    return re.sub(pattern, replace_var, content)


def load_yaml_with_env_substitution(file_path: str) -> str:
    """
    Load a YAML file and perform environment variable substitution.

    Args:
        file_path: Path to the YAML file

    Returns:
        YAML content with environment variables substituted
    """
    with open(file_path, "r") as file:
        content = file.read()

    return substitute_env_vars(content)
