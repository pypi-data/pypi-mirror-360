from setuptools import setup, find_packages

setup(
    name="chaosorg",
    version="0.1.1",
    author="Chris Jaimy Antony",
    author_email="chrisjaimyantony@gmail.com",  
    description="Because your folders deserve better",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chrisjaimyantony/chaosorg",
    project_urls={
        "Bug Tracker": "https://github.com/chrisjaimyantony/chaosorg/issues",
        "Source": "https://github.com/chrisjaimyantony/chaosorg",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all] >= 0.12.0",
    ],
    entry_points={
        "console_scripts": [
            "chaosorg = chaosorg.cli:app"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
