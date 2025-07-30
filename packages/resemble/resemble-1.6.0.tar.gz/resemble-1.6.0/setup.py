from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="resemble",
    version="1.6.0",
    packages=["resemble"],
    install_requires=["requests>2,<3"],
    python_requires=">=3.6",
    author="ResembleAI",
    author_email="team@resemble.ai",
    description="Resemble API Client Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/resemble-ai/resemble-python",
    project_urls={"Bug Tracker": "https://github.com/resemble-ai/resemble-python/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
