from setuptools import find_packages, setup

setup(
    name="apperror-py",
    version="0.0.1",
    author="ikonglong",
    author_email="chenlong@one2x.ai",
    description="This library implements a programming language-agnostic, enterprise application-common error model, and defines programming language-agnostic, communication protocol-agnostic error response and status code standards for enterprise application APIs, while providing extension mechanisms for status codes.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/one2x-ai/AppError-py",
    packages=find_packages(),
    python_requires=">=3.10.9",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    license="MIT",
)
