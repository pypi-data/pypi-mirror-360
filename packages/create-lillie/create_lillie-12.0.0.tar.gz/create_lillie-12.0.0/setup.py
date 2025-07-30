from setuptools import setup, find_packages

setup(
    name="create-lillie",
    version="12.0.0",
    packages=find_packages(),
    author="sarthak ghoshal",
    author_email="sarthak22.ghoshal@gmail.com",
    description="A CLI tool for creating lilliepy projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/websitedeb/create-lillie",
    py_modules=["cli"],
    include_package_data=True,
    package_data={
        "": ["templates/**/*"],
    },
    install_requires=[
        "typer[all]",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "create-lillie=cli:app",
        ],
    },
    keywords=["reactpy", "lilliepy", "create-lillie", "create-lilliepy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
