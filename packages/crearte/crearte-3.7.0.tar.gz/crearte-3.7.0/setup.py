from setuptools import setup, find_packages

setup(
    name="crearte",
    version="3.7.0",
    description="Visual Music Score Generator - Python CLI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Hirotoshi Uchida",
    author_email="github@users.noreply.github.com",
    url="https://github.com/Uchida16104/Crearte",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "crearte=cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
