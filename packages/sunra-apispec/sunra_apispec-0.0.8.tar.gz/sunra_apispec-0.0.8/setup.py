from setuptools import setup, find_packages


def read_requirements():
    """Read requirements from requirements.txt file"""
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="sunra_apispec",
    version="0.0.8",
    author="sunra.ai",
    author_email="admin@sunra.ai",
    description="A toolkit for managing and generating API specifications for various AI services",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunra-ai/APISpecToolkit",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "sunra_apispec": ["*.json", "*.yaml"],
    },
    install_requires=read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
