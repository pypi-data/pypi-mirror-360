from setuptools import setup, find_packages

setup(
    name="update-docs-system",
    version="1.0.0",
    author="William Evans",
    author_email="we256681@gmail.com",
    description="Комплексная система автоматизации документации для проектов с Markdown файлами",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CoreTwin/docs_repo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "gitpython>=3.1.0",
        "watchdog>=2.1.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "update-docs=update_docs.cli:main",
        ],
    },
    include_package_data=True,
    package_data={"update_docs": ["templates/*"]},
)
