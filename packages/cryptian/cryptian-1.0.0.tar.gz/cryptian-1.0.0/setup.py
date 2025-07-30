from setuptools import setup, find_packages

setup(
    name="cryptian",
    version="1.0.0",
    description="Cryptian - Advanced cryptography CLI and shell",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "rich",
        "pycryptodome",
        "cryptography",
        "prompt_toolkit"
    ],
    entry_points={
        "console_scripts": [
            "cryptian=cryptian.cli:main"
        ]
    },
    python_requires=">=3.7",
)