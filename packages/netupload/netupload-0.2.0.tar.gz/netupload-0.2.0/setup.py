from setuptools import setup, find_packages

setup(
    name="netupload",
    author="Zach Grimaldi",
    version="0.2.0",
    description="Simple upload server for local network file transfers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zpg6/netupload",
    packages=find_packages(),
    install_requires=[
        "Flask==3.0.3",
        "Werkzeug==3.0.3",
    ],
    entry_points={
        "console_scripts": [
            "netupload=src.app:run_server",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
