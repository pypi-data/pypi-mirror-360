from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nascoder",
    version="1.0.0",
    author="NasCoder Team",
    author_email="contact@nascoder.dev",
    description="AI Assistant powered by AWS Bedrock with Claude models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/freelancernasim/nascoder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.34.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "nascoder=nascoder.cli:main",
        ],
    },
    keywords="ai, aws, bedrock, claude, cli, assistant",
    project_urls={
        "Bug Reports": "https://github.com/freelancernasim/nascoder/issues",
        "Source": "https://github.com/freelancernasim/nascoder",
    },
)
