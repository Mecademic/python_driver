import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MecademicRobot",
    version="1.0.1",
    author="Mecademic",
    author_email="support@mecademic.com",
    license = "MIT",
    description="A package to control the Mecademic Robots through python",
    long_description=long_description,
    long_description_content_type="markdown",
    url="https://github.com/Mecademic/python_driver/tree/master",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
