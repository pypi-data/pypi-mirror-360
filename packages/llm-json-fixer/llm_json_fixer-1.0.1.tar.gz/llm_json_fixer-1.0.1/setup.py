from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm_json_fixer",
    version="1.0.1",
    author="Md. Hasnain Ali",
    author_email="mdhasnainali.01@gmail.com",
    description="A simple utility to fix malformed JSON from LLM outputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mdhasnainali/llm_json_fixer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[],
    keywords="json llm fix repair malformed ai chatgpt claude",
    project_urls={
        "Bug Reports": "https://github.com/mdhasnainali/llm_json_fixer/issues",
        "Source": "https://github.com/mdhasnainali/llm_json_fixer",
        "Documentation": "https://github.com/mdhasnainali/llm_json_fixer#readme",
    },
)