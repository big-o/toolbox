from setuptools import find_packages, setup

setup(
    name="sqlplay",
    version="0.1.0",
    description="Generate random SQL databases from a schema.",
    url="http://github.com/big-o/toolbox/sqlplay",
    author="big-o",
    author_email="big-o@github",
    license="MIT",
    packages=find_packages(exclude="example.*"),
)
