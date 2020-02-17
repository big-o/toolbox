from setuptools import find_packages, setup

setup(
    name="datagen",
    version="0.1.0",
    description="Generate random data from a schema.",
    url="http://github.com/big-o/toolbox/datagen",
    author="big-o",
    author_email="big-o@github",
    license="MIT",
    packages=find_packages(exclude="examples"),
)
