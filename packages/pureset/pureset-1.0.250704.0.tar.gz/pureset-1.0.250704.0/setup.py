from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__title__ = "PureSet"
__desc__ = "An immutable, homogeneous, and ordered collection type for Python."
__version__ = "1.0.250704.0"
__author__ = "gabrielmsilva00"
__contact__ = "gabrielmaia.silva00@gmail.com"
__repo__ = "https://github.com/gabrielmsilva00/PureSet"
__license__ = "Apache License 2.0"

setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__contact__,
    description=__desc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__repo__,
    project_urls={
        "Bug Tracker": __repo__ + "/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.9",
)
