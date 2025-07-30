#!/usr/bin/env python
# Copyright 2025 NetBox Labs, Inc.
"""Version stamp."""

# These properties are injected at build time by the build process.

__commit_hash__ = "510cb36"
__track__ = "release"
__version__ = "1.2.1"


def version_display():
    """Display the version, track and hash together."""
    return f"v{__version__}-{__track__}-{__commit_hash__}"


def version_semver():
    """Semantic version."""
    return __version__
