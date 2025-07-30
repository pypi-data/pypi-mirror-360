from setuptools import setup, find_packages

setup(
    name="lightswitch_sdk_py",
    version="0.2.2",
    packages=find_packages(),
    description="SDK for interacting with the Lightswitch backend",
    author="Lightswitch Team",
    author_email="team@lightswitch.com",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "fastapi": [
            "fastapi>=0.68.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="lightswitch sdk api authentication authorization",
    project_urls={
        "Documentation": "https://github.com/lightswitch/lightswitch-sdk-py",
        "Source": "https://github.com/lightswitch/lightswitch-sdk-py",
        "Tracker": "https://github.com/lightswitch/lightswitch-sdk-py/issues",
    },
) 