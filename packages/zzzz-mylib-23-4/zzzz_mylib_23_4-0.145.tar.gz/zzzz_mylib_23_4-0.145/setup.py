from setuptools import setup, find_packages

with open("README.md", mode="r") as file:
    description = file.read()

MYLIB_NAME = "zzzz_mylib_23_4"
__version__ = "0.145"  # Chỉnh phiên bản ở đây sau mỗi lần sửa code

REQUIRED_LIBS = []

setup(
    name=MYLIB_NAME,
    version=__version__,
    packages=find_packages(),
    install_requires=REQUIRED_LIBS,
    long_description=description,
    long_description_content_type="text/markdown",
)
