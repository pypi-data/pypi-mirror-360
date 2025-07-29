from setuptools import setup, find_packages

setup(
    name="robust-syslog-wrap",  # Package name on PyPI
    version="1.0.0",  # Initial version
    description="A tool to wrap commands and forward standard out and stdin to syslog via TCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="@readwithai",
    author_email="talwrii@gmail.com",
    url="https://github.com/talwrii/syslog-wrap",  # Link to your GitHub or project repo
    packages=find_packages(),
    install_requires=[  # Dependencies
        "asyncio",  # Or any other dependencies
    ],
    entry_points={  # CLI entry point
        "console_scripts": [
            "robust-syslog-wrap=robust_syslog_wrap.main:main",
        ]
    },
    classifiers=[  # PyPI classifiers for your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
)
