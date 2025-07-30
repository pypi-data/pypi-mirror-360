from setuptools import setup, find_packages

setup(
    name="robust-syslog-wrap",
    version='1.1.1',
    description="A tool to wrap commands and forward standard out and stdin to syslog via TCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="@readwithai",
    author_email="talwrii@gmail.com",
    url="https://github.com/talwrii/syslog-wrap",
    packages=find_packages(),
    install_requires=[
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "robust-syslog-wrap=robust_syslog_wrap.main:main",
        ]
    },
    classifiers=[  # PyPI classifiers for your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
