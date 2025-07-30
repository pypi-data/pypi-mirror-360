from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="isend-ai",
    version="1.0.0",
    author="isend.ai",
    author_email="hi@isend.ai",
    description="Python SDK for isend.ai - Send emails easily using email connectors like SES, SendGrid, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isend-ai/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    keywords="isend, email, sdk, ses, sendgrid, mailgun, postmark",
    project_urls={
        "Bug Reports": "https://github.com/isend-ai/python-sdk/issues",
        "Source": "https://github.com/isend-ai/python-sdk",
        "Documentation": "https://github.com/isend-ai/python-sdk#readme",
    },
) 