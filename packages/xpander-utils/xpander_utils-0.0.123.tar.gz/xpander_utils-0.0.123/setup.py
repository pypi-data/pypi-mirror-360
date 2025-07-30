from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xpander_utils",
    version="0.0.123",
    author="xpanderAI",
    author_email="dev@xpander.ai",
    description="A Python utils SDK for xpander.ai services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.xpander.ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic",
        "loguru",
        "xpander-sdk",
        "httpx",
        "httpx_sse"
    ],
    extras_require={
        "smolagents": ["smolagents"],
        "llama-index": ["llama_index"],
        "chainlit": ["chainlit"],
        "agno": ["agno"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12.1",
)
