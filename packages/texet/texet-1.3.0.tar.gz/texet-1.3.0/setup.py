from setuptools import setup, find_packages

setup(
    name="texet",
    version="1.3.0",
    packages=find_packages(),
    install_requires=[
        "clight",
        "openai",
        "keyboard",
        "pyautogui",
        "pyperclip",
        "googletrans"
    ],
    entry_points={
        "console_scripts": [
            "texet=texet.main:main",  # Entry point of the app
        ],
    },
    package_data={
        "texet": [
            "main.py",
            "__init__.py",
            ".system/imports.py",
            ".system/index.py",
            ".system/modules/ai.py",
            ".system/modules/speak.py",
            ".system/sources/clight.json",
            ".system/sources/ext.yml",
            ".system/sources/lng.yml",
            ".system/sources/logo.ico"
        ],
    },
    include_package_data=True,
    author="Irakli Gzirishvili",
    author_email="gziraklirex@gmail.com",
    description="TexeT is the tool you need to take your interaction and content control to the next level",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IG-onGit/TexeT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
