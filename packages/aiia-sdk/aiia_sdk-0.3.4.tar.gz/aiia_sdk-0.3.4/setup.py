from setuptools import setup, find_packages

setup(
    name="aiia-sdk",  # Nombre oficial para PyPI
    version="0.3.4",
    description="Official AIIA SDK for logging AI actions with legal and operational traceability - 100% Plug & Play",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="AIIA",
    author_email="javier.sanchez@aiiatrace.com",
    packages=["aiia_sdk"],  # Nombre del módulo Python
    package_dir={"aiia_sdk": "aiia_sdk"},
    package_data={
        "aiia_sdk": ["data/*.json", "cache/*.json"],
    },
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "cryptography>=39.0.0",
        "tldextract>=3.1.0"
    ],
    extras_require={
        "semantic": ["sentence-transformers>=2.2.2", "transformers>=4.0.0"]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aiia-verify=aiia_sdk.cli:verify_installation"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)