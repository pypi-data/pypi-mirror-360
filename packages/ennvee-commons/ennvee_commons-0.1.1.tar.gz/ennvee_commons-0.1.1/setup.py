from setuptools import setup, find_packages

setup(
    name="ennvee_commons",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "twilio>=8.0.0", 
        "loguru>=0.7.0",
        "starlette==0.47.1"
    ],
    author="Paavan Boddeda",
    # author_email="pavan.boddeda@ennvee.net",
    description="Common utilities for ennVee organization",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/yourorg/ennvee_commons",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)