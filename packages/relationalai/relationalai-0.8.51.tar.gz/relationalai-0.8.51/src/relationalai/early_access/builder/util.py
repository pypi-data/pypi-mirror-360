"""Utility functions and classes for the builder module."""


def sanitize(name):
    """Sanitize a name for use in Rel."""
    return name.replace(" ", "_")
