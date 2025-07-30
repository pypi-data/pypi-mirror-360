import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="hdsdk",
    version="0.0.10",
    author="wanggf",
    author_email="wanggf@hd.com",
    description="python sdk for hadian",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pandas',
        'numpy',
        'pymannkendall'
    ],
    python_requires='>=3',
)
