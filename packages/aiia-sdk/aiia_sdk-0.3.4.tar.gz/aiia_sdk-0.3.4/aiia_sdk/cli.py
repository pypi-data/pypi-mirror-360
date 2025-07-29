#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI utilities for AIIA SDK
"""

import sys
import platform
import pkg_resources
import importlib.util

def verify_installation():
    """
    Verify that the AIIA SDK is installed correctly and print system information.
    This is useful for troubleshooting installation issues.
    """
    print("AIIA SDK Installation Verification")
    print("=" * 40)
    
    # System information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # SDK version
    try:
        version = pkg_resources.get_distribution("aiia_sdk").version
        print(f"AIIA SDK version: {version}")
    except pkg_resources.DistributionNotFound:
        print("AIIA SDK is not installed via pip")
    
    # Check core dependencies
    core_deps = ["requests", "python-dotenv", "cryptography", "tldextract"]
    print("\nCore Dependencies:")
    for dep in core_deps:
        try:
            version = pkg_resources.get_distribution(dep).version
            print(f"  ✓ {dep}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"  ✗ {dep}: Not found")
    
    # Check optional dependencies
    optional_deps = ["sentence-transformers", "transformers"]
    print("\nOptional Dependencies (for semantic features):")
    for dep in optional_deps:
        try:
            version = pkg_resources.get_distribution(dep).version
            print(f"  ✓ {dep}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"  ✗ {dep}: Not found (install with pip install aiia_sdk[semantic])")
    
    # Check if AIIA class is importable
    print("\nImport Check:")
    try:
        from aiia_sdk import AIIA
        print("  ✓ Successfully imported AIIA class")
    except ImportError as e:
        print(f"  ✗ Failed to import AIIA class: {str(e)}")
    
    print("\nIf you encounter any issues, please report them at:")
    print("https://github.com/aiiatrace/aiia-sdk/issues")

if __name__ == "__main__":
    verify_installation()
