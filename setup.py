"""
Setup script for DeepThinkingChain package.
This is for backward compatibility with older pip versions.
"""

from setuptools import setup, find_packages

# This setup.py is for backward compatibility only.
# For modern installs, use the pyproject.toml file.
setup(
    name="deepthinkingchain",
    version="0.1.0",
    description="A multi-agent system for deep analytical thinking chains",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DeepThinking Contributors",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.3.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.1", 
        "pydantic>=2.10.6",
        "tqdm>=4.66.1",
        "beautifulsoup4>=4.12.3",
        "html2text>=2020.1.16",
        "litellm>=1.30.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 