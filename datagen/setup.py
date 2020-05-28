import os.path
from setuptools import find_packages, setup


def requirements(filename="requirements.txt"):
    # Copy dependencies from requirements file
    with open(filename, encoding='utf-8') as f:
        requirements = [line.strip() for line in f.read().splitlines()]
        requirements = [line.split('#')[0].strip() for line in requirements
                        if not line.startswith('#')]

    return requirements

def main():
    setup(
        name="datagen",
        version="0.1.0",
        description="Generate random data from a schema.",
        url="http://github.com/big-o/toolbox/datagen",
        author="big-o",
        author_email="big-o@github",
        license="MIT",
        packages=find_packages(exclude="examples"),
        install_requires=requirements(),
    )

if __name__ == "__main__":
    main()
