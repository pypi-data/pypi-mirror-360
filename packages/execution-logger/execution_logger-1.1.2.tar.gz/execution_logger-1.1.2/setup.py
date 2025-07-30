from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="execution-logger",
    version="1.1.2",
    author="Rizwana",
    author_email="rizwana@thefruitpeople.ie",
    description="A comprehensive Python logging solution with Microsoft SharePoint and Dataverse integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/The-Fruit-People/execution-logger",
    packages=find_packages(),
    install_requires=[
        "msal>=1.20.0",
        "requests>=2.28.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.7",
    sharepoint_uploader=">=1.0.4"
)