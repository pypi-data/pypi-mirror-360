from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="em05",
    version="0.1.0",
    author="Rikki",
    author_email="i@rikki.moe",
    description="Python library for Quectel EM05 cellular module SMS operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rikki/em05-sms",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Telephony",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyserial>=3.4",
    ],
    keywords="sms cellular quectel em05 at-commands",
    project_urls={
        "Bug Reports": "https://github.com/rikki/em05-sms/issues",
        "Source": "https://github.com/rikki/em05-sms",
    },
)