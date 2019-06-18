import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MecademicRobot",
    version="0.0.1",
    author="Alexandre Coulombe",
    author_email="alexandre.coulombe@mecademic.com",
    description="A package to control the Mecademic Robots through python",
    long_description=long_description,
    long_description_content_type="markdown",
    url="https://github.com/pypa/sampleproject#!#!@#!#!@#!",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: ",
        "Operating System :: OS Independent",
    ],
)