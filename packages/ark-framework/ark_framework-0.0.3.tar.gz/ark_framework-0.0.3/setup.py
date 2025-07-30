import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ark-framework",
    version="0.0.3",
    author="Joby Wilson Mathews",
    author_email="jobyywilson@gmail.com",
    description="A lightweight async task framework using thread pools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jobyywilson/ark-framework",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
