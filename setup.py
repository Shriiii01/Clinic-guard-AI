from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("server/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clinicguard-ai",
    version="1.0.0",
    author="ClinicGuard-AI Team",
    author_email="contact@clinicguard-ai.com",
    description="A HIPAA-compliant AI-powered call handling system for medical clinics",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Shriiii01/Clinic-guard-AI",
    project_urls={
        "Bug Tracker": "https://github.com/Shriiii01/Clinic-guard-AI/issues",
        "Documentation": "https://github.com/Shriiii01/Clinic-guard-AI/wiki",
        "Source Code": "https://github.com/Shriiii01/Clinic-guard-AI",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Telephony",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "bandit>=1.7",
            "safety>=1.10",
        ],
        "docker": [
            "docker>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clinicguard=server.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "server": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords="healthcare, ai, twilio, voice, hipaa, medical, appointment, booking",
    platforms=["any"],
    license="MIT",
    zip_safe=False,
) 