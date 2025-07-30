#!/usr/bin/env python3
"""
Setup script for rz-ci-robot-framework
"""

from setuptools import setup, find_packages
import os
import sys

# Read version directly since we don't have rz_ci_robot_framework structure yet
def get_version():
    return '1.0.0'

# Read README for long description
def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "RZ-CI Robot Framework - Board testing framework for Renesas RZ boards"

# Read requirements
def get_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f 
                   if line.strip() and not line.startswith('#')]
    return [
        "robotframework>=6.0.0,<7.0.0",
        "robotframework-seriallibrary>=0.3.1",
        "robotframework-sshlibrary>=3.8.0",
        "pyserial>=3.5",
        "PyYAML>=6.0",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
    ]

setup(
    name="rz-ci-robot-framework",
    version=get_version(),
    description="Robot Framework-based testing framework for Renesas RZ boards",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="RZ-CI Team",
    author_email="rz-ci@renesas.com",
    url="https://github.com/renesas/rz-ci-robot-framework",
    project_urls={
        "Documentation": "https://github.com/renesas/rz-ci-robot-framework/wiki",
        "Source": "https://github.com/renesas/rz-ci-robot-framework",
        "Tracker": "https://github.com/renesas/rz-ci-robot-framework/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Hardware",
        "Topic :: System :: Systems Administration",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
    ],
    keywords="robot framework testing renesas rz boards embedded hardware i2c spi gpio",
    entry_points={
        'console_scripts': [
            'rz-ci-test=main:main',
            'rz-ci-list-features=framework.test_handler:TestHandler.list_features_cli',
        ],
    },
    package_data={
        '': [
            'config/*.yml',
            'config/*.yaml',
            'test/**/*.robot',
            'keywords/*.robot',
            'templates/*.robot',
        ],
    },
    zip_safe=False,
)
